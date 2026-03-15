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

if [ -z "$THUMBNAILS_DIR_PATH" ]; then
  echo "Error: THUMBNAILS_DIR_PATH is not set in .env or environment."
  exit 1
fi

TMP_DIR="/tmp/$NAME"
MUSIC_DIR="$MPD_DATA_PATH/music/$NAME"
PLAYLIST_FILE="$MPD_DATA_PATH/playlists/$NAME.m3u"


mkdir -p "$TMP_DIR" "$MUSIC_DIR" "$THUMBNAILS_DIR_PATH"
rm -f "$PLAYLIST_FILE"

# Download playlist as mp3 into temp dir
$YTDLP_EXE \
  --js-runtimes deno:$DENO_EXE \
  --restrict-filenames \
  --embed-metadata \
  --embed-thumbnail \
  --extract-audio --audio-format mp3 \
  -o "$TMP_DIR/%(title)s.%(ext)s" \
  "$URL"

if ! compgen -G "$TMP_DIR/*.mp3" > /dev/null; then
    echo "no mp3 found in $TMP_DIR"
    rmdir "$TMP_DIR" 2>/dev/null || true
    exit 1
fi

# Extract thumbnail from first mp3
FIRST_MP3=$(ls "$TMP_DIR"/*.mp3 | head -n 1)
if [ -n "$FIRST_MP3" ]; then
    echo "Extracting thumbnail from $FIRST_MP3"
    ffmpeg -y -i "$FIRST_MP3" -an -c:v copy "$THUMBNAILS_DIR_PATH/$NAME.jpg"
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
