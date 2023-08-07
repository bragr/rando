#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No video files specified"
fi

ffmpeg -pattern_type glob -i "frames/*.png" -c:v libx264 -r 60 -crf 20 -pix_fmt yuv420p -filter:v "setpts=0.25*PTS" $1