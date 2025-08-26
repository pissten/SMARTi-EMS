import os
import asyncio
import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from ha import HA
from engine import Engine

logging.basicConfig(level=os.environ.get("LOG_LEVEL","INFO").upper())
_LOG = logging.getLogger("smarti_ems")

app = FastAPI()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)

ha = HA()
engine = Engine(ha, delay_seconds=int(os.environ.get("EMS_DELAY","90")))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    dyn = await engine._get_number("sensor.dynamic_power_sensor", 0.0)
    target = await engine._get_number("input_number.energy_target", 0.0)
    cat1 = await engine._get_list_from_input_select("input_select.category_1_devices")
    tmpl = env.get_template("index.html")
    return tmpl.render(dynamic_power=dyn, energy_target=target, cat1=cat1)

@app.get("/api/status")
async def status():
    dyn = await engine._get_number("sensor.dynamic_power_sensor", 0.0)
    target = await engine._get_number("input_number.energy_target", 0.0)
    return {"dynamic_power_w": dyn, "energy_target_kw": target}

@app.post("/api/step")
async def step():
    await engine.step_category1()
    return JSONResponse({"ok": True})

async def loop():
    # Poll + react every 30s
    interval = int(os.environ.get("EMS_LOOP_INTERVAL","30"))
    while True:
        try:
            await engine.step_category1()
        except Exception as e:
            _LOG.exception("Engine step failed: %s", e)
        await asyncio.sleep(interval)

@app.on_event("startup")
async def on_start():
    asyncio.create_task(loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT","8099")))
