#!/bin/bash

echo "Starting Plotty -- check the PB-700 is connected to the audio ports"
echo "Enter 'CHAIN' in the PB-700"

while true; do
    # Send plotty to the PB-700
    casutil/linux/bas850 -b -t7 pb-700/plotty.bas plotty.bin
    casutil/linux/wave850 -b plotty.bin plotty.wav
    play plotty.wav

    # Listen and decode answer
    python pb-700/listen.py
    sox recorded_audio.wav -r 44100 -c 1 -b 8 out.wav
    casutil/linux/wav2raw -b out.wav out.bin
    PROMPT=`python pb-700/extract-data.py`

    # See if the image is in the cache
    PROMPT_FILE=`echo cache/$PROMPT.jpg | sed -e 's/ /_/g'`

    echo $PROMPT_FILE

    if [ ! -e "$PROMPT_FILE" ]; then
        # Ask midjourney for the file and trace resulting image
        # midjourney/sendrequest.sh "$PROMPT" && python midjourney/midjourney.py
        cp image.jpg $PROMPT_FILE
    fi

    python trace.py --input $PROMPT_FILE --erosion 3 > prog.json
    rm -f prog*.bas
    python pb-700/json2basic.py < prog.json
    for f in prog*.bas
    do
        casutil/linux/bas850 -b -t7 "$f" prog.bin
        casutil/linux/wave850 -b prog.bin prog.wav
        play prog.wav

        COMMAND=""
        while [[ $COMMAND != "NEXT" ]]
        do
            python pb-700/listen.py
            sox recorded_audio.wav -r 44100 -c 1 -b 8 out.wav
            casutil/linux/wav2raw -b out.wav out.bin
            COMMAND=`python pb-700/extract-data.py`
            # We check that we got "NEXT": sometimes there is noise on the line and the command thinks the pb-700 is ready when it is not
        done
    done

    # Wait for end of plot and start again
    # python pb-700/listen.py
done
