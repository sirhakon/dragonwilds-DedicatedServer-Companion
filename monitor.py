import subprocess
import re
import threading
import time
import config
from state import set_player, remove_player, update_field, add_event, clear_players
from database import log_event, player_join, player_leave


def container_running():
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", config.CONTAINER],
        capture_output=True,
        text=True
    )

    return result.returncode == 0 and result.stdout.strip() == "true"


def parse_line(line):
    added = re.search(r"Player ADDED to session \[(.*?)\]-\[(.*?)\]", line)
    if added:
        account = added.group(1)
        name = added.group(2)

        set_player(account, name)
        player_join(account, name)
        log_event(f"{name} joined")
        return

    removed = re.search(r"Player Removed from session \[(.*?)\]-\[(.*?)\]", line)
    if removed:
        account = removed.group(1)
        name = removed.group(2)
        remove_player(account, name)
        player_leave(account)
        log_event(f"{name} left")
        return

    world = re.search(r"Save completed SUCCESSFULLY \(slot:\s*(.*?)\)", line)
    if world:
        update_field("world", world.group(1))
        return

    project_version = re.search(r"LogNetVersion:\s*Set ProjectVersion\s+to\s+([0-9]+(?:\.[0-9]+)*)\.", line, )
    if project_version:
        update_field("version", project_version.group(1))
        print(f"Detected ProjectVersion: {project_version.group(1)}", flush=True)
        return

def load_recent_logs():
    cmd = ["docker", "logs", "--tail", config.LOG_LINES_ON_START, config.CONTAINER]
    result = subprocess.run(cmd, capture_output=True, text=True)
    logs = result.stdout + "\n" + result.stderr
    for line in logs.splitlines():
        parse_line(line)

def follow_logs_forever():
    was_running = False

    while True:
        if not container_running():
            if was_running:
                clear_players()
                add_event("Server stopped")
                log_event("Server stopped")
                update_field("status", "offline")
                was_running = False

            time.sleep(5)
            continue

        if not was_running:
            clear_players()
            add_event("Server started")
            log_event("Server started")
            update_field("status", "online")
            was_running = True

        process = subprocess.Popen(
            ["docker", "logs", "-f", "--tail", "0", config.CONTAINER],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        try:
            for line in process.stdout:
                parse_line(line)
        except Exception as e:
            add_event(f"Log watcher error: {e}")

        clear_players()
        add_event("Log stream reconnecting")
        time.sleep(5)

def capture_startup_version():
    """Read full startup logs to find ProjectVersion"""
    try:
        result = subprocess.run(
            ["docker", "logs", config.CONTAINER],
            capture_output=True,
            text=True,
            timeout=10
        )
        logs = result.stdout + "\n" + result.stderr

        for line in logs.splitlines():
            project_version = re.search(
                r"LogNetVersion:\s*Set ProjectVersion\s+to\s+([0-9]+(?:\.[0-9]+)*)\.",
                line,
            )
            if project_version:
                version = project_version.group(1)
                update_field("version", version)
                print(f"Captured startup ProjectVersion: {version}", flush=True)
                return
    except Exception as e:
        print(f"Error capturing startup version: {e}", flush=True)

def start_monitor():
    capture_startup_version()  # <-- Find ProjectVersion from full startup logs
    if container_running():
        load_recent_logs()

    thread = threading.Thread(target=follow_logs_forever, daemon=True)
    thread.start()
