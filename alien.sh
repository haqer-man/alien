#!/bin/zsh


while true; do

file=$(ls Alien/* | sort -R | tail -1)

duration=$((15+$RANDOM % 10))
ffmpeg -re -f lavfi -i "color=black:1920x1080:d= $duration :r=25" -rtbufsize 1G -c:v libx264 -f mpegts udp://127.0.0.1:1234

file_duration=$(ffprobe -i "$file" -show_entries format=duration -v quiet -of csv="p=0")


cutstart=$(($RANDOM % $(($file_duration-30))))
ffmpeg -y -i "$file" -ss "$cutstart" -t 30 "cutaudio.mp3"

file_duration=$(ffprobe -i "cutaudio.mp3" -show_entries format=duration -v quiet -of csv="p=0")
fade_start=$(($file_duration -1))


ffmpeg -y -stream_loop -1 -i "Alien.gif" -i "cutaudio.mp3" -vf fade=d=1,fade=out:st=$fade_start:d=1 -af afade=in:0:d=1,afade=out:st=$fade_start:d=1 -shortest -c:v libx264 -map 0:v:0 -map 1:a:0 -b 900k -acodec libmp3lame -ab 24k -ar 22050 output.mp4


ffmpeg -re -i output.mp4 -vcodec libx264 -b 900k -acodec libmp3lame -ab 24k -ar 22050 -bsf:v h264_mp4toannexb -f mpegts udp://127.0.0.1:1234

done;
