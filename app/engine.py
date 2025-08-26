import asyncio
import logging
from typing import List

from ha import HA

_LOG = logging.getLogger("smarti_ems")

VALID_HVAC = ["off","dry","heat","auto","heat_cool","fan_only","cool"]

class Engine:
    def __init__(self, ha: HA, delay_seconds: int = 90):
        self.ha = ha
        self.delay = delay_seconds
        self._lock = asyncio.Lock()

    async def _get_number(self, entity_id: str, default=0.0) -> float:
        s = await self.ha.get_state(entity_id)
        try:
            return float((s or {}).get("state"))
        except Exception:
            return default

    async def _get_list_from_input_select(self, entity_id: str) -> List[str]:
        s = await self.ha.get_state(entity_id)
        opts = (s or {}).get("attributes", {}).get("options", []) or []
        return [o for o in opts if o and o != "No devices added"]

    async def _store_hvac_mode(self, slot: int, mode: str):
        await self.ha.set_input_text(f"input_text.hvac_mode_{slot}", mode)

    async def _restore_hvac_mode(self, entity_id: str, slot: int):
        s = await self.ha.get_state(f"input_text.hvac_mode_{slot}")
        mode = (s or {}).get("state", "auto")
        if mode not in VALID_HVAC:
            mode = "auto"
        await self.ha.call_service("climate", "set_hvac_mode", {"entity_id": entity_id, "hvac_mode": mode})

    async def _turn_off_entity(self, entity_id: str, slot: int):
        if entity_id.startswith("climate."):
            st = await self.ha.get_state(entity_id)
            current_mode = (st or {}).get("state", "off")
            if current_mode not in VALID_HVAC:
                current_mode = "off"
            await self._store_hvac_mode(slot, current_mode)
            await self.ha.call_service("climate", "set_hvac_mode", {"entity_id": entity_id, "hvac_mode": "off"})
        elif entity_id.startswith("switch."):
            await self.ha.call_service("homeassistant", "turn_off", {"entity_id": entity_id})
        await self.ha.set_input_boolean(f"input_boolean.device_turned_off_{slot}", True)

    async def _turn_on_entity(self, entity_id: str, slot: int):
        if entity_id.startswith("climate."):
            await self._restore_hvac_mode(entity_id, slot)
        elif entity_id.startswith("switch."):
            await self.ha.call_service("homeassistant", "turn_on", {"entity_id": entity_id})
        await self.ha.set_input_boolean(f"input_boolean.device_turned_off_{slot}", False)

    async def step_category1(self):
        # Serialize steps to avoid races
        async with self._lock:
            energy_target_kw = await self._get_number("input_number.energy_target", 0.0)
            target_w = energy_target_kw * 1000.0
            dyn = await self._get_number("sensor.dynamic_power_sensor", 0.0)

            devices = await self._get_list_from_input_select("input_select.category_1_devices")
            if not devices:
                _LOG.debug("No Category 1 devices found")
                return

            if dyn > target_w:
                power_gap = dyn - target_w
                _LOG.info(f"Over target: {dyn:.0f}W > {target_w:.0f}W, gap {power_gap:.0f}W")
                for i, entity_id in enumerate(devices[:20], start=1):
                    if power_gap <= 0:
                        break
                    await self._turn_off_entity(entity_id, i)
                    await asyncio.sleep(self.delay)
                    dyn = await self._get_number("sensor.dynamic_power_sensor", 0.0)
                    power_gap = dyn - target_w
                    await asyncio.sleep(self.delay)
            else:
                # Turn on all flagged devices one by one
                _LOG.info(f"Under target: {dyn:.0f}W <= {target_w:.0f}W, restoring devices if any")
                for i, entity_id in enumerate(devices[:20], start=1):
                    flag = await self.ha.get_state(f"input_boolean.device_turned_off_{i}")
                    if (flag or {}).get("state") == "on":
                        await self._turn_on_entity(entity_id, i)
                        await asyncio.sleep(self.delay)
