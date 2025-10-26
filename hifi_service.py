
import subprocess
import os

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "scripts", "power.sh")

def turn_on():
    subprocess.run([SCRIPT_PATH, "on"])

def turn_off():
    subprocess.run([SCRIPT_PATH, "off"])

def check_state():
    process = subprocess.run([SCRIPT_PATH, "status"], capture_output=True, text=True)
    return process.stdout.strip()
