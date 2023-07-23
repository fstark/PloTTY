import json
import sys
import argparse

# Use --input to specify input file
def parse_arguments():
    parser = argparse.ArgumentParser(description='Filename Parser')
    parser.add_argument('--size', default='8000', help='Size of every chunk in bytes')
    parser.add_argument('--output', default='prog', help='Prefix of output (prog0.bas, prog1.bas, etc)')
    args = parser.parse_args()
    return args

args = parse_arguments()
size_chunk = int(args.size)
output_filename = args.output
file_index = 0

json_data = sys.stdin.read()

try:
    draw_list = json.loads(json_data)
except json.JSONDecodeError as e:
    print("Error decoding JSON:", str(e))
    exit( -1 )

# Generating the BASIC program for the PB-700
class Generator:
    last_count_ = 0
    count_ = 0
    line_ = 3
    string_ = '2LPRINT CHR$(28);CHR$(37):LPRINT"O0,-96"\n'

    def add_small_segment( self, s ):
        self.string_ += str(self.line_)+'LPRINT"D'
        self.line_ += 1
        sep = ""
        for p in s:
            self.string_ += sep
            sep = ","
            self.string_ += str(p[0])+","+str(p[1])
        self.string_ += '"\n'

    def add_segment( self, s ):
        while (len(s)>1):
            self.add_small_segment( s[:6] )
            s = s[5:]
        self.count_ += 1

    def oversize( self ):
        "True if the basic file is over specified size"
        return len(self.string_)+100>=size_chunk

    def partial_end( self ):
        global draw_list
        self.string_ += '997LPRINT"M0,0"\n998PRINT"Request next";:A$="NEXT":PUTA$\n999PRINT" loading";:CHAIN\n'
        self.string_ = '1CLS:PRINT"Lines '+str(self.last_count_+1)+'-'+str(self.count_)+'/'+str(len(draw_list))+'"\n' + self.string_
        self.last_count_ = self.count_

    def reset( self ):
        self.line_ = 1
        self.string_ = ""

    def end( self ):
        global draw_list
        self.string_ += '997LPRINT"M0,-20"\n'
        self.string_ += '998PRINT"--Finished --":A$="NEXT":PUTA$\n999PRINT"Loading PloTTY...":CHAIN\n'
        self.string_ = '1CLS:PRINT"Lines '+str(self.last_count_+1)+'-'+str(self.count_)+'/'+str(len(draw_list))+'"\n' + self.string_
        self.last_count_ = self.count_

    def string( self ):
        return self.string_

g = Generator()

def prog_print( prog_str ):
    global file_index
    filename = output_filename+str(file_index)+'.bas'
    with open( filename, 'w') as file:
        file.write(prog_str)
        file_index += 1
        print( "    "+filename+" ("+str(len(prog_str))+" bytes)" )

# segment_img = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)
# x = 0
# y = 0
# i = 0
for cur in draw_list:
    g.add_segment( cur )

    # Draw the motion
    # cv2.line(img3, (x, y), (cur[0][0], cur[0][1]), (192,192,192), thickness=1)

    # Draw all segments with different colors
    # c = [(255, 0, 0),(0, 255, 0),(0, 0, 255),(255,255,0),(255,0,255)][i%5]
    # i = i+1
    # for j in range(len(cur)-1):
    #     # cv2.polylines(img3, [cur], False, c, 1)
    #     cv2.line(img3, (cur[j][0], cur[j][1]), (cur[j+1][0], cur[j+1][1]), c, thickness=1)
    #     cv2.line(segment_img, (cur[j][0], cur[j][1]), (cur[j+1][0], cur[j+1][1]), c, thickness=1)

    # x = cur[-1][0]
    # y = cur[-1][1]
    if (g.oversize()):
        g.partial_end()
        prog_print( g.string() )
        g.reset()

g.end()
prog_print( g.string() )

# cv2.imshow('segments', segment_img) 
# cv2.moveWindow( 'segments',size*2,size)
# cv2.imwrite('/tmp/7-segments.png', segment_img)

# cv2.imshow('motions', img3)
# cv2.moveWindow( 'motions',size*3,size)
# cv2.imwrite('/tmp/8-motions.png', img3)

# # Exiting the window if 'q' is pressed on the keyboard.
# if cv2.waitKey(0) & 0xFF == ord('q'): 
#     cv2.destroyAllWindows()

