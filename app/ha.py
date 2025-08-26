import os
import json
import httpx
import websockets
from typing import Any, Dict, List, Optional

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HA_REST = "http://supervisor/core/api"
HA_WS   = "ws://supervisor/core/websocket"
HEADERS = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}", "Content-Type": "application/json"}

class HA:
    def __init__(self):
        self.http = httpx.AsyncClient(timeout=30.0, headers=HEADERS)

    async def get_states(self) -> List[Dict[str, Any]]:
        r = await self.http.get(f"{HA_REST}/states")
        return r.json() if r.status_code == 200 else []

    async def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        r = await self.http.get(f"{HA_REST}/states/{entity_id}")
        return r.json() if r.status_code == 200 else None

    async def list_entities(self, domains: List[str]=None) -> List[Dict[str, Any]]:
        domains = domains or []
        data = await self.get_states()
        if not domains:
            return data
        return [s for s in data if (s.get("entity_id","").split(".")[0] in domains)]

    async def call_service(self, domain: str, service: str, data: Dict[str, Any]):
        return await self.http.post(f"{HA_REST}/services/{domain}/{service}", json=data)

    async def mqtt_publish(self, topic: str, payload: str, retain: bool=True):
        data = {"topic": topic, "payload": payload, "retain": retain}
        return await self.call_service("mqtt", "publish", data)

    async def ws_events(self):
        async with websockets.connect(HA_WS, extra_headers={"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}) as ws:
            hello = json.loads(await ws.recv())
            assert hello.get("type") == "auth_required"
            await ws.send(json.dumps({"type": "auth", "access_token": SUPERVISOR_TOKEN}))
            auth_ok = json.loads(await ws.recv())
            assert auth_ok.get("type") == "auth_ok"
            await ws.send(json.dumps({"id": 1, "type": "subscribe_events", "event_type": "state_changed"}))
            ack = json.loads(await ws.recv())
            assert ack.get("success")
            while True:
                msg = json.loads(await ws.recv())
                yield msg
