import json
import os
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt


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


load_env()

BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")
TOPIC_CONTROL = "pi/control"
TOPIC_STATUS = "pi/status"

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received: {payload}")
    except json.JSONDecodeError:
        return
    client.publish(
        TOPIC_STATUS,
        json.dumps(
            {
                "ack": True,
                "command": payload.get("command"),
                "received": datetime.utcnow().isoformat(),
            }
        )
    )
client = mqtt.Client()
if USERNAME:
    client.username_pw_set(USERNAME, PASSWORD or "")
client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(TOPIC_CONTROL)

client.loop_forever()
