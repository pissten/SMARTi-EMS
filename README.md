# SMARTi EMS (Home Assistant Add-on)

A minimal add-on skeleton for the SMARTi Energy Management System with an Ingress UI.

## What it does (v1)
- Connects to Home Assistant Core via Supervisor proxy (REST + WebSocket token)
- Polls `sensor.dynamic_power_sensor` and compares to `input_number.energy_target`
- Controls Category 1 devices listed in `input_select.category_1_devices`
- Stores/restores HVAC modes in `input_text.hvac_mode_1..20`
- Uses 90s backoff between actions and serializes steps to avoid races
- Simple Ingress UI to see status and trigger a step

> This version *reuses your existing helpers* to keep migration easy.

## Install

1. Push this folder to a repository (or use the zip directly in a local add-on repo)
2. In Home Assistant: **Settings → Add-ons → Add-on Store → ⋮ → Repositories**
3. Add your repo URL. Find **SMARTi EMS**, install, start
4. Open the web UI (Ingress) and verify values

## Important

- Disable overlapping YAML automations that also toggle Category 1 devices,
  or you may get race conditions. Let the add-on manage Category 1.
- Keep `input_select.category_1_devices` order stable while using the slot-based hvac storage.
- Next step (v2) is moving to JSON state (`/data/state.json`) and mapping modes per entity, not per slot.

## Dev

- App runs FastAPI with uvicorn in s6 service:
  - `/` shows the UI
  - `POST /api/step` triggers one control step
  - `GET /api/status` shows current numbers

## Config

See `config.yaml` for add-on options and schema. ENV vars:
- `EMS_DELAY` (default 90) – delay seconds between device actions
- `EMS_LOOP_INTERVAL` (default 30) – polling interval seconds
