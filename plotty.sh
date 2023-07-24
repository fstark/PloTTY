#!/bin/bash

echo "Starting Plotty -- check the PB-700 is connected to the audio ports"
echo "Verify that you entered 'CHAIN' in the PB-700"
echo

while true; do
    # Send plotty to the PB-700

    echo "-- Generating plotty.bas binary file"
    casutil/linux/bas850 -b -t7 pb-700/plotty.bas plotty.bin >> log.txt
    echo "-- Creating plotty.wav"
    casutil/linux/wave850 -b plotty.bin plotty.wav >> log.txt
    echo "-- Sending plotty.wav to PB-700"
    play plotty.wav

    PROMPT=""
    while [[ $PROMPT == "" ]]
        do
        # Listen and decode answer
        echo "-- Plotty.wav sent, waiting for reply"
        python pb-700/listen.py
        sox recorded_audio.wav -r 44100 -c 1 -b 8 out.wav
        casutil/linux/wav2raw -b out.wav out.bin
        PROMPT=`python pb-700/extract-data.py`
    done

    # #### TODO: MANAGE /VARIATION
    VARIATION=`echo $PROMPT | sed -e 's/.*\/\([^\/\]*\)/\1/g'`
    PROMPT=`echo $PROMPT | sed -e 's/\\/[0-9]*$//g'`

    echo "PROMPT: [$PROMPT] VARIATION: $VARIATION"

    # See if the image is in the cache
    PROMPT_FILE=`echo cache/$PROMPT.jpg | sed -e 's/ /_/g'`

    echo "PROMPT FILE USED: [$PROMPT_FILE]"

    if [ ! -e "$PROMPT_FILE" ]; then
        # Ask midjourney for the file and trace resulting image
        echo "Sending prompt to midjourney:"
        midjourney/sendrequest.sh "$PROMPT" &&                                                                                                                                                                                                      
        cp image.jpg $PROMPT_FILE
    fi

    echo "-- Tracing file [$PROMPT_FILE]"
    python trace.py --input $PROMPT_FILE --erosion 3 --corner $VARIATION > prog.json
    rm -f prog*.bas

    echo -n "-- Generating BASIC programs:"
    python pb-700/json2basic.py < prog.json

    for f in prog*.bas
    do
        echo "-- Transforming [$f] into binary"
        casutil/linux/bas850 -b -t7 "$f" prog.bin >> log.txt
        echo "-- Generating wav for [$f]"
        casutil/linux/wave850 -b prog.bin prog.wav >> log.txt
        echo "-- Sending [$f] to PB-700"
        play prog.wav

        COMMAND=""
        while [[ $COMMAND != "NEXT" ]]
        do
            echo "-- [$f] sent, waiting for reply"
            python pb-700/listen.py
            echo "-- Re-encoding response as 8 bits mono"
            sox recorded_audio.wav -r 44100 -c 1 -b 8 out.wav
            echo "-- Decoding response"
            casutil/linux/wav2raw -b out.wav out.bin
            echo "-- Extracting response content"
            COMMAND=`python pb-700/extract-data.py`
            echo "Response is [$COMMAND]"
            # We check that we got "NEXT": sometimes there is noise on the line and the command thinks the pb-700 is ready when it is not
        done
    done
done
