import json
import sys

json_data = sys.stdin.read()

try:
    draw_list = json.loads(json_data)
except json.JSONDecodeError as e:
    print("Error decoding JSON:", str(e))
    exit( -1 )

# Generating the BASIC program for the PB-700
class Generator:
    line_ = 2
    string_ = '1LPRINT CHR$(28);CHR$(37):LPRINT"O0,-96"\n'

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

    def end( self ):
        self.string_ += '997LPRINT"M0,-20"\n'
        self.string_ += '998PUT"SYNC"\n'
        self.string_ += '999CHAIN\n'

    def string( self ):
        return self.string_

g = Generator()

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
g.end()

print( g.string() )

# cv2.imshow('segments', segment_img) 
# cv2.moveWindow( 'segments',size*2,size)
# cv2.imwrite('/tmp/7-segments.png', segment_img)

# cv2.imshow('motions', img3)
# cv2.moveWindow( 'motions',size*3,size)
# cv2.imwrite('/tmp/8-motions.png', img3)

# # Exiting the window if 'q' is pressed on the keyboard.
# if cv2.waitKey(0) & 0xFF == ord('q'): 
#     cv2.destroyAllWindows()

