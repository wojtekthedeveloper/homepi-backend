import subprocess
import os

SCRIPT_DIR_PATH = os.path.join(os.path.dirname(__file__), "scripts")

def script_path(script_name):
    return os.path.join(SCRIPT_DIR_PATH, script_name)

def add_playlist(name, url):
    subprocess.run([script_path('add_playlist.sh'), name, url])

def append_playlist(name, url):
    subprocess.run([script_path('append_to_playlist.sh'), name, url])
