# Python code to find the co-ordinates of
# the contours detected in an image.
import numpy as np
import cv2
from skimage.morphology import skeletonize
import argparse

# Use --input to specify input file
def parse_arguments():
    parser = argparse.ArgumentParser(description='Filename Parser')
    parser.add_argument('--input', default='images/sample1.png', help='Input filename')
    args = parser.parse_args()
    return args

args = parse_arguments()
source_path = args.input

# Directions for path find
dx = [ 1,0,-1,0, 1,1,-1,-1]
dy = [ 0,1,0,-1, -1,1,1,-1]

size = 95*5     # PB-700 size

def trace_single_line_from( img, x, y ):
    "Remove from image a path starting from x,y and returns it in array"
    h,w = img.shape
    result = []

    img[y,x] = 0
    result.append( [x,y] )
    finished = False
    while not finished:
        finished = True
        for d in range(8):
            vx = x+dx[d]
            vy = y+dy[d]
            if not (vx<0 or vx>=h or vy<0 or vy>=w):
                if img[vy,vx]==255:
                    x = vx
                    y = vy
                    img[y,x] = 0
                    result.append( [x,y] )
                    finished = False
                    break
    return result

def trace_line_from( img, x, y ):
    "Remove from image a path containing x,y and returns it in array"
    h,w = img.shape
    result = []

    result = trace_single_line_from( img, x, y )
    result.reverse()
    result = result + trace_single_line_from( img, x, y )[1:]

    return result

 
# Reading image
original = cv2.imread(source_path, cv2.IMREAD_COLOR)

cv2.imshow('Original', original) 

# Reading same image in another 
# variable and converting to gray scale.
img = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
h,w = img.shape
img = img[:h//2,:w//2]


# height, width = img.shape[:2]
# start_row = height//2
# end_row = height
# start_col = 0
# end_col = width//2
# img = img[start_row:end_row, start_col:end_col]


img = cv2.resize( img, (size,size), interpolation = cv2.INTER_AREA)



cv2.imshow('source grayscale', img) 

img = 255-img

# Converting image to a binary image
# ( black and white only image).
_, threshold = cv2.threshold(img, 55, 255, cv2.THRESH_BINARY)

cv2.imshow('thresholded', threshold) 

# skeleton = skeletonize(threshold)
skeleton = cv2.ximgproc.thinning(threshold)

h,w = skeleton.shape
for y in range(w):
    for x in range(h):
        c = skeleton[x,y]
        if c!=0 and c!=255:
            exit(-1)

skeleton = 255-skeleton
cv2.imshow('skeleton', skeleton) 
skeleton = 255-skeleton


result = []
for y in range(w):
    for x in range(h):
        if skeleton[y,x]==255:
            line = np.array(trace_line_from( skeleton, x, y ))
            line = cv2.approxPolyDP(line, 1.5, False)
            result.append(line)

skeleton = 255-skeleton

tot = 0
for c in result:
    tot += len(c)
# print( "Total points==",tot )

# # Detecting contours in image.
# contours, _= cv2.findContours(skeleton, cv2.RETR_LIST,
#                                 cv2.CHAIN_APPROX_NONE)

# # print( contours )
# print( original.shape )

img3 = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)
cv2.polylines(img3, result, False, (0, 0, 0), 1)

i = 0
for l in result:
    c = [(0, 0, 0),(255, 0, 0),(0, 255, 0),(0, 0, 255)][i%4]
    cv2.polylines(img3, [l], False, (0,0,0), 1)
    i = i+1

# # cv2.drawContours(img3, contours, -1, (0, 0, 255), 1) 

# for cnt in contours:
#     # Approximate the contour to a polyline
#     # epsilon = 0.2*cv2.arcLength(cnt, True)
#     approx = cv2.approxPolyDP(cnt, 1, True)

#     # Draw the polyline
#     cv2.polylines(img3, [approx], True, (255, 0, 0), 1)

# # # Showing the final image.
cv2.imshow('Image Final', img3) 

cv2.imwrite('output.png', img3)

# Segment list for sorting

def distance2( p0, p1 ):
    return (p0[0]-p1[0])*(p0[0]-p1[0])+(p0[1]-p1[1])*(p0[1]-p1[1])

class SegmentList:
    segments_ = []

    def __init__( self, segments ):
        for seg in segments:
                # Segments are one level too deep, for whatever reason
            self.segments_.append( list([p[0][0], p[0][1]] for p in seg) )

    def closest( self, x, y ):
        d = 10240*10240
        index = 0
        for i in range(len(self.segments_)):
            d0 = distance2( self.segments_[i][0], (x,y) )
            d1 = distance2( self.segments_[i][-1], (x,y) )
            if (d0<d):
                index = i
                d = d0

            if (d1<d):
                index = i
                d = d1
                self.segments_[i].reverse()

        return self.segments_.pop(index)

    def done( self ):
        return len(self.segments_)==0

sl = SegmentList( result )

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
            self.string_ += str(p[0]/5)+","+str((size-p[1])/5)
        self.string_ += '"\n'

    def add_segment( self, s ):
        while (len(s)>1):
            self.add_small_segment( s[:6] )
            s = s[5:]

    def end( self ):
        self.string_ += '999LPRINT"M0,-20"\n'

    def string( self ):
        return self.string_

g = Generator()

# for c in result:
#     g.add_segment( list([p[0][0], p[0][1]] for p in c) )

img4 = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)


x = 0
y = 0
while not sl.done():
    cur = sl.closest( x, y )
    g.add_segment( cur )

    cv2.line(img3, (x, y), (cur[0][0], cur[0][1]), (0,0,0), thickness=1)

    x = cur[-1][0]
    y = cur[-1][1]

g.end()

print( g.string() )

cv2.imshow('Optimized', img3)

# Exiting the window if 'q' is pressed on the keyboard.
if cv2.waitKey(0) & 0xFF == ord('q'): 
    cv2.destroyAllWindows()

