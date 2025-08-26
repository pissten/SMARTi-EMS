# SMARTi EMS (from scratch)

This add-on is a *from-scratch* EMS engine + UI. It **does not use your existing Home Assistant helpers, sensors, or automations**.
It keeps its own configuration and state under `/data/` and talks to Home Assistant via the Supervisor API for:
- listing entities
- reading a selected power source entity (e.g., your meter power sensor)
- calling services to turn devices on/off

## Features (v1)
- Ingress UI for configuration
- Keeps config in `/data/config.json` (no HA helpers)
- Manages **Category 1** devices with ordered priority, with action delay to let load settle
- Stores & restores HVAC modes **per entity** in `/data/state.json` (no input_text helpers)
- Periodic loop (default 30s) + manual "Run step now" control

> Note: You still need **a real power source** reading from somewhere (e.g., your meter integration). EMS reads that entity directly via the HA API.
> Nothing else is required from HA side.

## Install
1. Put this folder in an add-on repo (or use the provided zip).
2. In Home Assistant: Settings → Add-ons → Add-on Store → ⋮ → Repositories → add your repo.
3. Install **SMARTi EMS**, Start, and open Ingress.
4. In the UI, pick your **Power source entity** (any sensor in W/kW), set your **Energy target (kWh)**, and select devices for **Category 1**.

## Roadmap
- Category 2/3 logic (e.g., price-aware power saver)
- Optional MQTT Discovery (publish EMS entities via `mqtt.publish` service)
- Advanced tariff models and price feeds
- Device priorities and time windows
