import json, os, threading
from typing import Any, Dict

CONFIG_PATH = "/data/config.json"
STATE_PATH = "/data/state.json"
_lock = threading.Lock()

DEFAULT_CONFIG: Dict[str, Any] = {
    "power_source_entity": "",      # e.g., sensor.<meter_power_w>
    "energy_target_kw": 10.0,
    "mode": "nettleie",             # nettleie | pris | flex
    "category1": [],                # list of entity_ids, ordered by priority
    "category2": [],
    "category3": [],
}

DEFAULT_STATE: Dict[str, Any] = {
    "hvac_restore": {},             # {entity_id: "auto"}
    "last_gap_w": 0.0,
    "devices_off": [],              # list of entity_ids currently off by EMS
}

def load_json(path: str, default: Dict[str, Any]) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default.copy()

def save_json(path: str, data: Dict[str, Any]) -> None:
    tmp = path + ".tmp"
    with _lock:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)

def load_config() -> Dict[str, Any]:
    return load_json(CONFIG_PATH, DEFAULT_CONFIG)

def save_config(cfg: Dict[str, Any]) -> None:
    save_json(CONFIG_PATH, cfg)

def load_state() -> Dict[str, Any]:
    return load_json(STATE_PATH, DEFAULT_STATE)

def save_state(st: Dict[str, Any]) -> None:
    save_json(STATE_PATH, st)
