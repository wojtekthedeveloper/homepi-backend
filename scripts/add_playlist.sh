#!/usr/bin/env bash

# set -e
# set -x

source $(dirname $0)/../.env

NAME="$1"
URL="$2"

if [ -z "$NAME" ] || [ -z "$URL" ]; then
  echo "Usage: $0 <name> <playlist_url>"
  exit 1
fi

TMP_DIR="/tmp/$NAME"
MUSIC_DIR="$MPD_DATA_PATH/music/$NAME"
PLAYLIST_FILE="$MPD_DATA_PATH/playlists/$NAME.m3u"


mkdir -p "$TMP_DIR" "$MUSIC_DIR"
rm -f "$PLAYLIST_FILE"

# Download playlist as mp3 into temp dir
$YTDLP_EXE \
  --js-runtimes deno:$DENO_EXE \
  --restrict-filenames \
  --extract-audio --audio-format mp3 \
  -o "$TMP_DIR/%(title)s.%(ext)s" \
  "$URL"

if ! compgen -G "$TMP_DIR/*.mp3" > /dev/null; then
    echo "no mp3 found in $TMP_DIR"
    rmdir "$TMP_DIR" 2>/dev/null || true
    exit 1
fi

# Normalize filenames to simple ASCII and move to music dir
for f in "$TMP_DIR"/*.mp3; do
  base="$(basename "$f")"

  echo "moving $f to $MUSIC_DIR/$base"
  mv "$f" "$MUSIC_DIR/$base"

  echo "$NAME/$base" >> "$PLAYLIST_FILE"
done

# Cleanup
rmdir "$TMP_DIR" 2>/dev/null || true

# Update MPD
mpc update >/dev/null

echo "Done:"
echo "- Music: $MUSIC_DIR"
echo "- Playlist: $PLAYLIST_FILE"
