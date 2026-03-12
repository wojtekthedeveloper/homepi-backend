import subprocess


def get_current_song_title():
    process = subprocess.run(["mpc", "-f", "%title%", "current"], capture_output=True, text=True)
    return process.stdout.strip()

def get_current_song_filename():
    process = subprocess.run(["mpc", "-f", "%file%", "current"], capture_output=True, text=True)
    return process.stdout.strip()

def get_current_song_artist():
    process = subprocess.run(["mpc", "-f", "%artist%", "current"], capture_output=True, text=True)
    return process.stdout.strip()

def get_current_song_album():
    process = subprocess.run(["mpc", "-f", "%album%", "current"], capture_output=True, text=True)
    return process.stdout.strip()

def get_current_song_current_time():
    process = subprocess.run(["mpc", "status", "%currenttime%"], capture_output=True, text=True)
    return process.stdout.strip()

def get_current_song_total_time():
    process = subprocess.run(["mpc", "status", "%totaltime%"], capture_output=True, text=True)
    return process.stdout.strip()

def list_playlists():
    process = subprocess.run(["mpc", "lsplaylists"], capture_output=True, text=True)
    return process.stdout.strip().splitlines()

def load_playlist(playlist_name):
    subprocess.run(["mpc", "clear"])
    process = subprocess.run(["mpc", "load", playlist_name], capture_output=True, text=True)
    play()
    return process.stdout.strip()

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

def toggle():
    subprocess.run(["mpc", "toggle"])

def shuffle(state: str):
    subprocess.run(["mpc", "random", state])

def get_shuffle_state():
    process = subprocess.run(["mpc", "status", "%random%"], capture_output=True, text=True)
    return process.stdout.strip()

def repeat(state: str):
    subprocess.run(["mpc", "repeat", state])

def get_repeat_state():
    process = subprocess.run(["mpc", "status", "%repeat%"], capture_output=True, text=True)
    return process.stdout.strip()

def single(state: str):
    subprocess.run(["mpc", "single", state])

def get_single_state():
    process = subprocess.run(["mpc", "status", "%single%"], capture_output=True, text=True)
    return process.stdout.strip()

def volume(level):
    subprocess.run(["mpc", "volume", str(level)])

def get_volume():
    process = subprocess.run(["mpc", "status", "%volume%"], capture_output=True, text=True)
    return int(process.stdout.strip().rstrip('%'))

def seek(position: str):
    subprocess.run(["mpc", "seek", position])

def status():
    process = subprocess.run(["mpc", "status"], capture_output=True, text=True)
    return process.stdout.strip()
