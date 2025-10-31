import subprocess

def list_playlists():
    process = subprocess.run(["mpc", "lsplaylists"], capture_output=True, text=True)
    return process.stdout.strip().splitlines()

def load_playlist(playlist_name):
    subprocess.run(["mpc", "clear"])
    process = subprocess.run(["mpc", "load", playlist_name], capture_output=True, text=True)
    play()
    return process.stdout.strip()

def set_volume(level):
    subprocess.run(["mpc", "volume", str(level)])

def play():
    subprocess.run(["mpc", "play"])

def pause():
    subprocess.run(["mpc", "pause"])

def stop():
    subprocess.run(["mpc", "stop"])

def next():
    subprocess.run(["mpc", "next"])

def previous():
    subprocess.run(["mpc", "prev"])

def status():
    process = subprocess.run(["mpc", "status"], capture_output=True, text=True)
    return process.stdout.strip()
