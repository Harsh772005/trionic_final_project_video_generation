#!/bin/bash
TITLE="assets/title_slide.png"
IMG="downloaded_image.png"  # Download manually from img_url
AUDIO="tts_audio.wav"
OUT="output_video.mp4"

DUR_AUDIO=$(ffprobe -i "$AUDIO" -show_entries format=duration -v quiet -of csv=p=0)

ffmpeg \
  -loop 1 -t 5 -i "$TITLE" \
  -loop 1 -t $DUR_AUDIO -i "$IMG" \
  -i "$AUDIO" \
  -filter_complex "\
    [0:v]fade=t=out:st=4:d=1,scale=1280:720[v0]; \
    [1:v]scale=1280:720,format=yuv420p[v1]; \
    [v0][v1]concat=n=2:v=1:a=0[outv]" \
  -map "[outv]" -map 2:a \
  -c:v libx264 -c:a aac -shortest "$OUT"

echo "Final video: $OUT"
