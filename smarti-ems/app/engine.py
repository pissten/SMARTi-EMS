import asyncio
import logging
from typing import List, Dict

from ha import HA
from store import load_config, save_config, load_state, save_state

_LOG = logging.getLogger("smarti_ems")

VALID_HVAC = ["off","dry","heat","auto","heat_cool","fan_only","cool"]

class Engine:
    def __init__(self, ha: HA, delay_seconds: int = 90):
        self.ha = ha
        self.delay = delay_seconds
        self._lock = asyncio.Lock()

    async def _get_number_state(self, entity_id: str) -> float:
        st = await self.ha.get_state(entity_id)
        if not st: return 0.0
        try:
            v = float(st.get("state", 0.0))
            unit = st.get("attributes", {}).get("unit_of_measurement")
            if unit and unit.lower() == "kw":
                return v * 1000.0
            return v
        except Exception:
            return 0.0

    async def read_dynamic_power_w(self) -> float:
        cfg = load_config()
        src = cfg.get("power_source_entity") or ""
        if not src:
            return 0.0
        return await self._get_number_state(src)

    async def _turn_off(self, eid: str, st: Dict):
        # Store restore mode for climates
        if eid.startswith("climate."):
            s = await self.ha.get_state(eid)
            mode = (s or {}).get("state", "off")
            if mode not in VALID_HVAC:
                mode = "off"
            st["hvac_restore"][eid] = mode
            await self.ha.call_service("climate", "set_hvac_mode", {"entity_id": eid, "hvac_mode": "off"})
        elif eid.startswith("switch."):
            await self.ha.call_service("homeassistant", "turn_off", {"entity_id": eid})
        if eid not in st["devices_off"]:
            st["devices_off"].append(eid)

    async def _turn_on(self, eid: str, st: Dict):
        if eid.startswith("climate."):
            mode = st["hvac_restore"].get(eid, "auto")
            if mode not in VALID_HVAC:
                mode = "auto"
            await self.ha.call_service("climate", "set_hvac_mode", {"entity_id": eid, "hvac_mode": mode})
        elif eid.startswith("switch."):
            await self.ha.call_service("homeassistant", "turn_on", {"entity_id": eid})
        if eid in st["devices_off"]:
            st["devices_off"].remove(eid)
        st["hvac_restore"].pop(eid, None)

    async def step(self):
        async with self._lock:
            cfg = load_config()
            st = load_state()

            dyn_w = await self.read_dynamic_power_w()
            target_kw = float(cfg.get("energy_target_kw", 0.0))
            target_w = target_kw * 1000.0
            st["last_gap_w"] = dyn_w - target_w

            cat1: List[str] = list(cfg.get("category1", []))

            if not cat1:
                save_state(st)
                return

            if dyn_w > target_w:
                gap = dyn_w - target_w
                _LOG.info(f"Over target: {dyn_w:.0f}W > {target_w:.0f}W (gap {gap:.0f}W). Turning off Category 1 in order.")
                for eid in cat1:
                    if gap <= 0:
                        break
                    await self._turn_off(eid, st)
                    save_state(st)
                    await asyncio.sleep(self.delay)
                    dyn_w = await self.read_dynamic_power_w()
                    gap = dyn_w - target_w
                    await asyncio.sleep(self.delay)
            else:
                # Restore those we previously turned off, in reverse order
                _LOG.info(f"Under target: {dyn_w:.0f}W ≤ {target_w:.0f}W. Restoring devices if any.")
                for eid in list(reversed(cat1)):
                    if eid in st["devices_off"]:
                        await self._turn_on(eid, st)
                        save_state(st)
                        await asyncio.sleep(self.delay)

            save_state(st)
