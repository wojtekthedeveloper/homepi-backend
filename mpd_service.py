import subprocess

def list_playlists():
    process = subprocess.run(["mpc", "lsplaylists"], capture_output=True, text=True)
    return process.stdout.strip().splitlines()

def load_playlist(playlist_name):
    subprocess.run(["mpc", "clear"])
    process = subprocess.run(["mpc", "load", playlist_name], capture_output=True, text=True)
    return process.stdout.strip()

def play():
    subprocess.run(["mpc", "play"])

def pause():
    subprocess.run(["mpc", "pause"])

def stop():
    subprocess.run(["mpc", "stop"])

def status():
    process = subprocess.run(["mpc", "status"], capture_output=True, text=True)
    return process.stdout.strip()
