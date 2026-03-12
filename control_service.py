import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

import hifi_service
import mpd_service
import misc_service


def load_env(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env(Path(__file__).with_name(".env"))
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")

# TOPIC_CONTROL = "pi/control"
# TOPIC_STATUS = "pi/status"
# TOPIC_MPD_CONTROL = "pi/mpd/control"
# TOPIC_MPD_STATUS = "pi/mpd/status"
# TOPIC_BT_CONTROL = "pi/bluetooth/control"
# TOPIC_BT_STATUS = "pi/bluetooth/status"
# TOPIC_MISC_CONTROL = "pi/misc/control"
# TOPIC_MISC_STATUS = "pi/misc/status"

# New topics for refactored client
TOPIC_HOMEPI_HIFI_CONTROL = "homepi/hifi/control"
TOPIC_HOMEPI_HIFI_STATUS = "homepi/hifi/status"
TOPIC_HOMEPI_PLAYLIST_CONTROL = "homepi/playlists/control"
TOPIC_HOMEPI_PLAYLIST_STATUS = "homepi/playlists/status"
TOPIC_HOMEPI_MPD_CONTROL = "homepi/mpd/control"
TOPIC_HOMEPI_MPD_STATUS = "homepi/mpd/status"


def publish(client: mqtt.Client, topic: str, payload: Dict[str, Any]) -> None:
    client.publish(topic, json.dumps(payload, default=str))


def publish_hifi_status(client: mqtt.Client) -> None:
    """Publishes HiFi status in the new format for the refactored client."""
    state = hifi_service.check_state()
    publish(client, TOPIC_HOMEPI_HIFI_STATUS, {"hifi_status": state == "on"})


def publish_playlist_status(client: mqtt.Client) -> None:
    """Publishes the list of playlists for the refactored client."""
    playlists = mpd_service.list_playlists()
    publish(client, TOPIC_HOMEPI_PLAYLIST_STATUS, {"playlists": playlists})


def publish_mpd_status(client: mqtt.Client) -> None:
    """Publishes MPD status for the refactored client."""
    status = mpd_service.status()
    # Provide structured status for the new client
    lines = status.splitlines()
    state = "stopped"
    volume = -1
    
    if len(lines) > 1:
        if "[playing]" in lines[1]:
            state = "playing"
        elif "[paused]" in lines[1]:
            state = "paused"
            
    # Parse volume from status string (e.g., "volume: 50%   repeat: off ...")
    for line in lines:
        if line.startswith("volume:"):
            try:
                # Extract digits from the volume part
                vol_part = line.split()[1]
                volume = int("".join(filter(str.isdigit, vol_part)))
            except (IndexError, ValueError):
                pass
            break
    
    if volume == -1:
        publish(client, TOPIC_HOMEPI_MPD_STATUS, {"status": status, "state": state})
    else:
        publish(client, TOPIC_HOMEPI_MPD_STATUS, {"status": status, "state": state, "volume": volume})


def ack_payload(command: Optional[str], success: bool, message: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ack": success,
        "command": command,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if message:
        payload["message"] = message
    payload.update(extra)
    return payload


def get_cpu_temperature(path: str = '/sys/class/thermal/thermal_zone0/temp') -> Optional[float]:
    """Reads CPU temperature from a sysfs file."""
    try:
        temp_str = Path(path).read_text().strip()
        return float(temp_str) / 1000.0
    except (FileNotFoundError, ValueError):
        return None


def gather_status() -> Dict[str, Any]:
    # Replace with actual telemetry collection as needed.
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_temp": get_cpu_temperature(),
        "hostname": os.uname().nodename,
    }


# def handle_control_command(client: mqtt.Client, payload: Dict[str, Any]) -> None:
#
#     command = payload.get("command")
#     args = payload.get("args") or {}
#
#     if command == "status":
#         publish(client, TOPIC_STATUS, {**gather_status(), "source": "pi"})
#         return
#
#     if command == "hifi_power":
#         action = args.get("state")
#         if action == "on":
#             hifi_service.turn_on()
#             publish(client, TOPIC_STATUS, ack_payload(command, True, message="Hi-Fi turned on"))
#             publish_hifi_status(client)
#         elif action == "off":
#             hifi_service.turn_off()
#             publish(client, TOPIC_STATUS, ack_payload(command, True, message="Hi-Fi turned off"))
#             publish_hifi_status(client)
#         elif action == "status":
#             status = hifi_service.check_state()
#             publish(client, TOPIC_STATUS, ack_payload(command, True, status=status))
#             publish_hifi_status(client)
#         else:
#             publish(client, TOPIC_STATUS, ack_payload(command, False, message="Invalid action for hifi_power command"))
#         return
#
#     publish(
#         client,
#         TOPIC_STATUS,
#         ack_payload(command, False, message="Unknown control command"),
#     )


# def handle_bluetooth_command(client: mqtt.Client, payload: Dict[str, Any]) -> None:
#     command = payload.get("command")
#     if command != "toggle_bluetooth":
#         publish(
#             client,
#             TOPIC_BT_STATUS,
#             ack_payload(command, False, message="Unknown Bluetooth command"),
#         )
#         return
#
#     enable = (payload.get("args") or {}).get("state", "toggle")
#     enable_str = str(enable).lower()
#     # Placeholder for Bluetooth control:
#     # subprocess.run(["/usr/local/bin/bluetooth_toggle.sh", enable_str], check=False)
#     publish(
#         client,
#         TOPIC_BT_STATUS,
#         ack_payload(command, True, bluetooth_state=enable_str),
#     )


# def handle_mpd_command(client: mqtt.Client, payload: Dict[str, Any]) -> None:
#     command = payload.get("command")
#
#     if command == "play":
#         mpd_service.play()
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, state="play"))
#     elif command == "pause":
#         mpd_service.pause()
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, state="pause"))
#     elif command == "stop":
#         mpd_service.stop()
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, state="stop"))
#     elif command == "previous":
#         mpd_service.previous()
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, state="previous"))
#     elif command == "next":
#         mpd_service.next()
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, state="next"))
#     elif command == "status":
#         status = mpd_service.status()
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, status=status))
#     elif command == "list_playlists":
#         playlists = mpd_service.list_playlists()
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, playlists=playlists))
#     elif command == "set_volume":
#         args = payload.get("args") or {}
#         volume = args.get("level")
#         if volume is None or not isinstance(volume, int) or not (0 <= volume <= 100):
#             publish(client, TOPIC_MPD_STATUS, ack_payload(command, False, message="Invalid volume level"))
#             return
#         mpd_service.set_volume(volume)
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, volume=volume))
#     elif command == "load_playlist":
#         args = payload.get("args") or {}
#         playlist_name = args.get("name")
#         if not playlist_name:
#             publish(client, TOPIC_MPD_STATUS, ack_payload(command, False, message="Playlist name not provided"))
#             return
#         status = mpd_service.load_playlist(playlist_name)
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, True, message=f"Loaded playlist {playlist_name}", status=status))
#     else:
#         publish(client, TOPIC_MPD_STATUS, ack_payload(command, False, message="Unknown MPD command"))


# def handle_misc_command(client: mqtt.Client, payload: Dict[str, Any]) -> None:
#     command = payload.get("command")
#     if command == "add_playlist":
#         args = payload.get("args") or {}
#         name = args.get("playlist_name")
#         url = args.get("playlist_url")
#         status = misc_service.add_playlist(name, url)
#         publish(client, TOPIC_MISC_STATUS, ack_payload(command, True, status=status))
#     else:
#         publish(client, TOPIC_MISC_STATUS, ack_payload(command, False, message="Unknown MISC command"))


def handle_hifi_mqtt_command(client: mqtt.Client, payload: Any) -> None:
    """Handles commands for the new HiFi control topic using the CommandMessage format."""
    if not isinstance(payload, dict):
        # Support raw string 'status' for convenience
        if str(payload).lower() == "status":
            publish_hifi_status(client)
        return

    command = payload.get("command")
    args = payload.get("args") or {}

    if command == "hifi_power":
        state = args.get("state")
        if state == "on":
            hifi_service.turn_on()
        elif state == "off":
            hifi_service.turn_off()
        else:
            return
    elif command == "status":
        pass  # Just publish status below
    else:
        return

    publish_hifi_status(client)


def handle_playlist_command(client: mqtt.Client, payload: Any) -> None:
    """Handles commands for the new playlist control topic."""
    if not isinstance(payload, dict):
        if str(payload).lower() == "status":
            publish_playlist_status(client)
        return

    command = payload.get("command")
    args = payload.get("args") or {}

    if command == "get_playlists":
        publish_playlist_status(client)
    elif command == "play_playlist":
        name = args.get("name")
        if name:
            mpd_service.load_playlist(name)
            publish(client, TOPIC_HOMEPI_PLAYLIST_STATUS, ack_payload(command, True, message="playlist loaded"))
            # publish_playlist_status(client)
    else:
        return


def handle_homepi_mpd_command(client: mqtt.Client, payload: Any) -> None:
    """Handles commands for the new homepi/mpd control topic."""
    if not isinstance(payload, dict):
        if str(payload).lower() == "status":
            publish_mpd_status(client)
        return

    command = payload.get("command")
    args = payload.get("args") or {}

    if command == "play":
        mpd_service.play()
    elif command == "pause":
        mpd_service.pause()
    elif command == "toggle_play_pause":
        mpd_service.toggle()
    elif command == "stop":
        mpd_service.stop()
    elif command == "next":
        mpd_service.next()
    elif command == "previous":
        mpd_service.previous()
    elif command == "shuffle":
        state = args.get("state")
        if state in ["on", "off"]:
            mpd_service.shuffle(state)
    elif command == "repeat":
        state = args.get("state")
        if state in ["on", "off"]:
            mpd_service.repeat(state)
    elif command == "set_volume":
        level = args.get("level")
        if level is not None and isinstance(level, int):
            mpd_service.set_volume(level)
    elif command == "status":
        pass
    else:
        return

    publish_mpd_status(client)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received on {msg.topic}: {payload}")
    except json.JSONDecodeError:
        payload = msg.payload.decode()
        print(f"Received on {msg.topic} (raw): {payload}")

    # if msg.topic == TOPIC_CONTROL:
    #     handle_control_command(client, payload)
    # elif msg.topic == TOPIC_MPD_CONTROL:
    #     handle_mpd_command(client, payload)
    # elif msg.topic == TOPIC_BT_CONTROL:
    #     handle_bluetooth_command(client, payload)
    # elif msg.topic == TOPIC_MISC_CONTROL:
    #     handle_misc_command(client, payload)
    if msg.topic == TOPIC_HOMEPI_HIFI_CONTROL:
        handle_hifi_mqtt_command(client, payload)
    elif msg.topic == TOPIC_HOMEPI_PLAYLIST_CONTROL:
        handle_playlist_command(client, payload)
    elif msg.topic == TOPIC_HOMEPI_MPD_CONTROL:
        handle_homepi_mpd_command(client, payload)
    # else:
    #     publish(
    #         client,
    #         TOPIC_STATUS,
    #         ack_payload(payload.get("command") if isinstance(payload, dict) else None, False, message="Unhandled topic"),
    #     )


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker at {BROKER}:{PORT}")
        # client.subscribe(TOPIC_CONTROL)
        # client.subscribe(TOPIC_MPD_CONTROL)
        # client.subscribe(TOPIC_BT_CONTROL)
        # client.subscribe(TOPIC_MISC_CONTROL)
        client.subscribe(TOPIC_HOMEPI_HIFI_CONTROL)
        client.subscribe(TOPIC_HOMEPI_PLAYLIST_CONTROL)
        client.subscribe(TOPIC_HOMEPI_MPD_CONTROL)
        # Initial status updates
        publish_hifi_status(client)
        publish_playlist_status(client)
        publish_mpd_status(client)
    else:
        print(f"Failed to connect, return code {rc}")


client = mqtt.Client()
if USERNAME and PASSWORD:
    client.username_pw_set(USERNAME, PASSWORD)
else:
    print("Warning: No MQTT credentials set.")
    raise SystemExit(1)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)

print("MQTT control service running...")
client.loop_forever()
