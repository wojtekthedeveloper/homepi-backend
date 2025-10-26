import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

import hifi_service


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

TOPIC_CONTROL = "pi/control"
TOPIC_STATUS = "pi/status"
TOPIC_MPD_CONTROL = "pi/mpd/control"
TOPIC_MPD_STATUS = "pi/mpd/status"
TOPIC_BT_CONTROL = "pi/bluetooth/control"
TOPIC_BT_STATUS = "pi/bluetooth/status"


def publish(client: mqtt.Client, topic: str, payload: Dict[str, Any]) -> None:
    client.publish(topic, json.dumps(payload, default=str))


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


def handle_control_command(client: mqtt.Client, payload: Dict[str, Any]) -> None:
    command = payload.get("command")
    args = payload.get("args") or {}

    if command == "status":
        publish(client, TOPIC_STATUS, {**gather_status(), "source": "pi"})
        return

    if command == "hifi_power":
        action = args.get("state")
        if action == "on":
            hifi_service.turn_on()
            publish(client, TOPIC_STATUS, ack_payload(command, True, message="Hi-Fi turned on"))
        elif action == "off":
            hifi_service.turn_off()
            publish(client, TOPIC_STATUS, ack_payload(command, True, message="Hi-Fi turned off"))
        elif action == "status":
            status = hifi_service.check_state()
            publish(client, TOPIC_STATUS, ack_payload(command, True, status=status))
        else:
            publish(client, TOPIC_STATUS, ack_payload(command, False, message="Invalid action for hifi_power command"))
        return

    publish(
        client,
        TOPIC_STATUS,
        ack_payload(command, False, message="Unknown control command"),
    )


def handle_bluetooth_command(client: mqtt.Client, payload: Dict[str, Any]) -> None:
    command = payload.get("command")
    if command != "toggle_bluetooth":
        publish(
            client,
            TOPIC_BT_STATUS,
            ack_payload(command, False, message="Unknown Bluetooth command"),
        )
        return

    enable = (payload.get("args") or {}).get("state", "toggle")
    enable_str = str(enable).lower()
    # Placeholder for Bluetooth control:
    # subprocess.run(["/usr/local/bin/bluetooth_toggle.sh", enable_str], check=False)
    publish(
        client,
        TOPIC_BT_STATUS,
        ack_payload(command, True, bluetooth_state=enable_str),
    )


def handle_mpd_command(client: mqtt.Client, payload: Dict[str, Any]) -> None:
    command = payload.get("command")

    if command in {"play", "pause", "stop"}:
        # subprocess.run(["/usr/local/bin/mpd_control.sh", command], check=False)
        publish(
            client,
            TOPIC_MPD_STATUS,
            ack_payload(command, True, state=command),
        )
        return

    if command == "status":
        publish(
            client,
            TOPIC_MPD_STATUS,
            {
                "source": "pi",
                "state": "stopped",
                "song": None,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        publish(
            client,
            TOPIC_MPD_STATUS,
            ack_payload(command, True),
        )
        return

    if command == "list_playlists":
        playlists = ["Morning Mix", "Evening Chill"]  # Replace with `mpc lsplaylists`
        publish(
            client,
            TOPIC_MPD_STATUS,
            ack_payload(command, True, playlists=playlists),
        )
        return

    publish(
        client,
        TOPIC_MPD_STATUS,
        ack_payload(command, False, message="Unknown MPD command"),
    )


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received on {msg.topic}: {payload}")
    except json.JSONDecodeError:
        print("Invalid JSON payload; ignoring.")
        return

    if msg.topic == TOPIC_CONTROL:
        handle_control_command(client, payload)
    elif msg.topic == TOPIC_MPD_CONTROL:
        handle_mpd_command(client, payload)
    elif msg.topic == TOPIC_BT_CONTROL:
        handle_bluetooth_command(client, payload)
    else:
        publish(
            client,
            TOPIC_STATUS,
            ack_payload(payload.get("command"), False, message="Unhandled topic"),
        )


client = mqtt.Client()
if USERNAME and PASSWORD:
    client.username_pw_set(USERNAME, PASSWORD)
else:
    print("Warning: No MQTT credentials set.")
    raise SystemExit(1)

client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(TOPIC_CONTROL)
client.subscribe(TOPIC_MPD_CONTROL)
client.subscribe(TOPIC_BT_CONTROL)

print("MQTT control service running...")
client.loop_forever()
