1 DIM F$(1)*79
2 CLS
3 PRINT "PloTTY by Fred Stark";
4 PRINT "- Midjouney Prompt -";
5 INPUT "> ",F$(1)
6 INPUT "Variation (1-4): ",V$
7 F$(1) = F$(1)+"/"+V$
8 PRINT "Sending..."
9 PUT F$(1)
10 PRINT "Waiting for image..."
11 CHAIN
