test: prog.wav
	play prog.wav

prog.wav: prog.bin
	casutil/linux/wave850 -b prog.bin prog.wav

prog.bin: prog.bas
	casutil/linux/bas850 -b prog.bas prog.bin

prog.bas: json2basic.py prog.json
	python json2basic.py < prog.json > prog.bas

prog.json: trace.py images/sample3.png
	python trace.py --input images/sample11.png --erosion 3 > prog.json

