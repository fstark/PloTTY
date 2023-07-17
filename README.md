# casdraw


[![Watch the video](https://img.youtube.com/vi/nTQUwghvy5Q/default.jpg)](https://youtu.be/nTQUwghvy5Q)

https://youtu.be/sSLVlxQoVYE

CasDraw is a work in progress to create a PB-700 plotter magic drawing program.

The ultimate goal is to produce a program that can be run on a PB-700 with a FA-10 plotter, and produce an image from an input text.

There are a few challenges, but all of them can be overcome.

The objective is to create such images, it is understood that it will absolutely not be practical at all.

# Status



# Architecture

The pb-700 will need to be connected to a linux PC by a two-way audio transmition, with the PC acting like a tape recorder. (Note: it should be possible to save drawing programs on tape).

The first operation will be to execute a ``LOAD,A`` on the PB-700, and start the server on the PC.

The server will serve a BASIC program doing the prompting on the machine, and listen to the audio input.

User will enter its short prompt, and the basic program will use a ``PUT A$`` to write it to the PC. It will then use a ``CHAIN,A`` to execute the next basic program read.

The PC will read and decode the input, and use midjourney to generate a suitable image, with the following prompt:

``<<SOMETHING>> black and white line art constant thickness simple children coloring book``

The top left resulting image will the be transformed into a series of BASIC programs that will draw that exact shape.

The basic programs will then be encoded and played back to the computer. Each basic program but the last end up with a ``CHAIN,A`` command. As the server goes back to the main loop, it will serve the initial basic program, enabling the slighlt older user to perform another drawing.

# Challenges

* Fixing my CA-10
* Writing programs to the pb-700
* Decoding input from pb-700
* Generating the image
* Generating the basic instructions
* Interfacing with midjourney

# Architecture

While it would be better to have a nice self-contained software, the current end result is probably going to be a mix of bash shell scripts, python command lines, ``casutil`` commands, and various linux specific commands, meaning it will be quite fragile.

# Challenge 1: Fixing my CA-10s

*In Progress*

# Challenge 2: Writing programs to the pb-700

The following ``casutil``` commands can write a program to the PB-700

```
casutil/linux/bas850 -b prog.bas prog.bin
casutil/linux/wave850 -b prog.bin prog.wav
play prog.wav
```

# Challenge 3: Decoding input from pb-700

*In Progress*

# Challenge 4: Generating the images

Midjourney generates 2048x2048 images:

![4 line art cats](images/sample3.png)

This is the resulting traced image:

![A cat](images/sample3-out.png)

The test.py program does the generation from the top-left quarter of a midjourney supplied image.

It extracts the top-left corner, threshold it to black and white, resize it to 475x475 (as the pb-700 has 95mm accessible with a 0.2mm step), uses opencv ``skeleton`` to thin lines, a custom tracing algorithm and an opencv polygon optimisation.

Above image is a 

## Installing test.py

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test/py --input images/sample3.png
```

Should display the cat image.

# Challenge 5: Generating the basic instructions

Print is accessed via ``LPRINT`` statements. Every statement is line terminated (not sent to the printer until line end). Not two statement on the same line. BASIC limits line length to be 79 characters, it is unclear how long can a printer instruction be.

First implementation is to directly send a basic program with ``LPRINT`` instructions. We could probably do better with a set of ``DATA`` lines, in particular as it seems that there are only 256 positions x and y on the printer, so we could get close to 2 bytes per coordinates.

In order to simplify, we will consider the following characters ``nn LPRINT "D"`` necessary for printing (basic line number, ``LPRINT`` instruction, quotes, and ``D``(raw) command). This is 13 characters, do we have 66 characters available for coordinates. Each coordinate takes 5 characters, so a first implementation is to split the drawing into a sequence of 6 segment lines.

Code for activating the printer ``LPRINT CHR$(28);CHR$(37)``

Code for printing ``LPRINT "D12.3,45.6,78.9,1.2,34.5"``

# Challenge 6: Interfacing with midjourney

It seems that the "midjourney API" is discord. Which is quite a WTF. *In Progress*.
