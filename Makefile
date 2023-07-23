test: prog.wav
	play prog.wav

prog.wav: prog.bin
	casutil/linux/wave850 -b prog.bin prog.wav

prog.bin: prog.bas
	casutil/linux/bas850 -b -t7 prog.bas prog.bin

prog.bas: pb-700/json2basic.py prog.json
	python pb-700/json2basic.py < prog.json > prog.bas

prog.json: trace.py images/sample3.png
	python trace.py --input images/sample11.png --erosion 3 > prog.json

listen: pb-700/listen.py
	python pb-700/listen.py
	sox recorded_audio.wav -r 44100 -c 1 -b 8 out.wav
	casutil/linux/wav2raw -b out.wav out.bin
	python pb-700/extract-data.py


send: pb-700/plotty.wav
	play pb-700/plotty.wav

pb-700/plotty.wav: pb-700/plotty.bin
	casutil/linux/wave850 -b pb-700/plotty.bin pb-700/plotty.wav

pb-700/plotty.bin: pb-700/plotty.bas
	casutil/linux/bas850 -b -t7 pb-700/plotty.bas pb-700/plotty.bin
