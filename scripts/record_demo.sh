#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p docs/demo_video_script
OUT="docs/demo_video_script/demo_recording.mp4"
if command -v ffmpeg >/dev/null 2>&1; then
  echo "Recording with FFmpeg to $OUT"
  echo "Linux example: ffmpeg -video_size 1280x720 -framerate 30 -f x11grab -i :0.0 -c:v libx264 -preset veryfast -crf 28 $OUT"
  echo "Windows example: ffmpeg -f gdigrab -framerate 30 -i desktop -vf scale=1280:-2 -c:v libx264 -crf 28 $OUT"
elif command -v vlc >/dev/null 2>&1; then
  echo "Use VLC Media > Convert/Save > Capture Device > Desktop, save H.264 MP4 to $OUT"
else
  echo "Install FFmpeg or VLC. Recommended: H.264 MP4, 720p, under 50 MB where required."
fi

