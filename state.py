import time
from threading import Lock
from datetime import datetime
import config

_lock = Lock()

state = {
    "status": "online",
    "server": "Dragonwilds",
    "world": "Unknown",
    "version": "Unknown",
    "players": {},
    "cpu": "Unknown",
    "memory": "Unknown",
    "uptime": "Unknown",
    "last_save": "Unknown",
    "events": [],
    "updated": int(time.time())
}


def add_event(message):
    with _lock:
        state["events"].insert(0, {
            "timestamp": datetime.now().strftime("%I:%M:%S %p"),
           # "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": message
        })
        state["events"] = state["events"][:25]
        state["updated"] = int(time.time())


def set_player(account, name):
    with _lock:
        state["players"][account] = name
        state["updated"] = int(time.time())
    add_event(f"{name} joined")


def remove_player(account, name=None):
    with _lock:
        old_name = state["players"].pop(account, None)
        state["updated"] = int(time.time())
    add_event(f"{name or old_name or account} left")


def clear_players():
    with _lock:
        state["players"] = {}
        state["updated"] = int(time.time())


def update_field(key, value):
    with _lock:
        state[key] = value
        state["updated"] = int(time.time())


def get_state():
    with _lock:
        players = list(state["players"].values())

        return {
            "status": state["status"],
            "server": state["server"],
            "world": state["world"],
            "version": state["version"],
            "players_online": len(players),
            "max_players": config.MAX_PLAYERS,
            "players": players,
            "players_text": ", ".join(players) if players else "None",
            "cpu": state["cpu"],
            "memory": state["memory"],
            "uptime": state["uptime"],
            "last_save": state["last_save"],
            "events": state["events"],
            "updated": state["updated"]
        }
