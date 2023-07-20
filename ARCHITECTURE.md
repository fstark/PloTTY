# PloTTY architecture

Components of PloTTY are of various quality, due to some limitations of the underlying technology. Surprisingly, the biggest limitations don't come from where we expect them

# High-level overview

Overall the goal is to have a program runing on the pb-700 inputing a midjournet prompt, sending it to a backend, that will generate an image and trace it, then send the data back to the pb-700 to be plotted on the FA-10.

Let's go over those steps one by one to see how they have been implemented:

The pb-700 original program is served by the linux machine, to avoid having to type anything, using tape emulation (ie: connecting audio IN of the PB-700 to the stereo out of the PC)

After having send the program, the PC waits for data to be sent by the PB-700.

As there is no serial port or any form of communication, the input of the user is saved to tape, with the audio OUT of the pb-700 connected to the PC.

After saving this data, the pb-700 waits for the next program sent by the pc and execute it.

The PC reads the data and sends it to midjourney, using discord.

When the image is generated, it is downlaoded from discord and passed to a set of python scripts that will generate a trace suitable for the pb-700.

That trace is then transformed into a basic program, and sent to the pb-700. After this, the pc will wait for data from the pb-700.

The pb-700 recieves the program and executes it. It will draw the specified image on the plotter.

At the end of the program, the pb-700 send arbitrary data to the pc and wait for another program. The pc will detect this data, and serve back the original program, making the full circle.

# Low-level horrors

