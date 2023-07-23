#!/bin/bash

WINDOW_ID=`xdotool search --name "#general | Midjourney Discord"`

xdotool windowactivate $WINDOW_ID
xdotool mousemove --window $WINDOW_ID 400 1450
xdotool click 1
xdotool type --delay 10 "/imagine"
sleep 1
xdotool type --delay 10 " "
sleep 1
xdotool type --delay 10 "$1 black and white line art constant thickness simple children coloring book"
sleep 1
xdotool type "$(echo -ne '\r')"
