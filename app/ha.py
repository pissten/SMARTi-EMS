import os
import json
import httpx
import websockets
from typing import Any, Dict, Optional

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HA_REST = "http://supervisor/core/api"
HA_WS   = "ws://supervisor/core/websocket"
HEADERS = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}", "Content-Type": "application/json"}

class HA:
    def __init__(self):
        self.http = httpx.AsyncClient(timeout=30.0, headers=HEADERS)

    async def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        r = await self.http.get(f"{HA_REST}/states/{entity_id}")
        if r.status_code == 200:
            return r.json()
        return None

    async def call_service(self, domain: str, service: str, data: Dict[str, Any]):
        return await self.http.post(f"{HA_REST}/services/{domain}/{service}", json=data)

    async def set_input_text(self, entity_id: str, value: str):
        return await self.call_service("input_text", "set_value", {"entity_id": entity_id, "value": value})

    async def set_input_boolean(self, entity_id: str, turn_on: bool):
        return await self.call_service("input_boolean", "turn_on" if turn_on else "turn_off", {"entity_id": entity_id})

    async def get_addon_options(self) -> Dict[str, Any]:
        # Read add-on options via Hass.io API
        # We need the slug from config.yaml; keep in sync if you change it
        addon_slug = os.environ.get("HOSTNAME", "smarti_ems")
        # Fallback: Supervisor provides our add-on slug at /info; use /options endpoint for exact slug
        # For simplicity, use the direct 'self/options' endpoint
        r = await self.http.get("http://supervisor/addons/self/options", headers={"Authorization": f"Bearer {SUPERVISOR_TOKEN}"})
        return r.json() if r.status_code == 200 else {}
