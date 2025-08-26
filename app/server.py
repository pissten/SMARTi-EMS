import os
import asyncio
import logging
from typing import List, Dict, Any

from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader

from ha import HA
from store import load_config, save_config, load_state
from engine import Engine

logging.basicConfig(level=os.environ.get("LOG_LEVEL","INFO").upper())
_LOG = logging.getLogger("smarti_ems")

app = FastAPI()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)

ha = HA()
engine = Engine(ha, delay_seconds=int(os.environ.get("ACTION_DELAY", os.environ.get("EMS_DELAY","90"))))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    cfg = load_config()
    st = load_state()
    dyn = await engine.read_dynamic_power_w()
    tmpl = env.get_template("index.html")
    return tmpl.render(cfg=cfg, st=st, dyn=dyn)

@app.get("/api/config")
async def get_config():
    return load_config()

@app.post("/api/config")
async def set_config(payload: Dict[str, Any] = Body(...)):
    cfg = load_config()
    cfg.update({
        "power_source_entity": payload.get("power_source_entity", cfg.get("power_source_entity","")),
        "energy_target_kw": float(payload.get("energy_target_kw", cfg.get("energy_target_kw", 10.0))),
        "mode": payload.get("mode", cfg.get("mode","nettleie")),
        "category1": payload.get("category1", cfg.get("category1", [])),
        "category2": payload.get("category2", cfg.get("category2", [])),
        "category3": payload.get("category3", cfg.get("category3", [])),
    })
    save_config(cfg)
    return {"ok": True, "config": cfg}

@app.get("/api/entities")
async def list_entities(domain: str = ""):
    domains = [d.strip() for d in domain.split(",") if d.strip()]
    ents = await ha.list_entities(domains or None)
    return ents

@app.get("/api/power-sources")
async def power_sources():
    # Return sensors with unit W or kW
    sensors = await ha.list_entities(["sensor"])
    out = []
    for s in sensors:
        attrs = s.get("attributes", {})
        unit = attrs.get("unit_of_measurement","")
        if str(unit).lower() in ["w","kw"]:
            out.append({"entity_id": s["entity_id"], "name": attrs.get("friendly_name", s["entity_id"]), "unit": unit})
    return out

@app.get("/api/status")
async def status():
    cfg = load_config()
    st = load_state()
    dyn = await engine.read_dynamic_power_w()
    return {"dynamic_power_w": dyn, "energy_target_kw": cfg.get("energy_target_kw", 0.0), "gap_w": st.get("last_gap_w", 0.0),
            "devices_off": st.get("devices_off", [])}

@app.post("/api/step")
async def step():
    await engine.step()
    return JSONResponse({"ok": True})

async def loop():
    interval = int(os.environ.get("EMS_LOOP_INTERVAL", os.environ.get("LOOP_INTERVAL","30")))
    while True:
        try:
            await engine.step()
        except Exception as e:
            _LOG.exception("Engine step failed: %s", e)
        await asyncio.sleep(interval)

@app.on_event("startup")
async def on_start():
    asyncio.create_task(loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT","8099")))
