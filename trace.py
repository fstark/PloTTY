# Python code to find the co-ordinates of
# the contours detected in an image.
import numpy as np
import cv2
from skimage.morphology import skeletonize
import argparse
import math
import json

# Use --input to specify input file
def parse_arguments():
    parser = argparse.ArgumentParser(description='Filename Parser')
    parser.add_argument('--input', default='images/sample1.png', help='Input filename')
    parser.add_argument('--corner', default='1', help='Corner of the image (1,2,3,4 or 0 for no corner)')
    parser.add_argument('--epsilon', default='1.5', help='Epsilon (how large of an error can we make against theorical line)')
    parser.add_argument('--erosion', default='0', help='Number of erosion passes to be done to contour the large black areas')
    args = parser.parse_args()
    return args

args = parse_arguments()
source_path = args.input
corner = int(args.corner)
epsilon = float(args.epsilon)
erosion = int(args.erosion)

# Directions for path find
dx = [ 1,0,-1,0, 1,1,-1,-1]
dy = [ 0,1,0,-1, -1,1,1,-1]

size = 95*5     # PB-700 size

# Utility tracing function
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

# Main tracing function: we trace twice and join the two resulting paths
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
cv2.imwrite('/tmp/0-original.png', original)

# Reading grayscale
img = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
cv2.imwrite('/tmp/1-grayscale.png', img)

# Extract corner
h,w = img.shape
if corner!=0:
    corners = [(0,0),(0,1),(1,0),(1,1)]
    c = corners[corner-1]
    start_row = h//2 * c[0]
    end_row = start_row + h//2
    start_col = w//2 * c[1]
    end_col = start_col + w//2
    img = img[start_row:end_row, start_col:end_col]

cv2.imwrite('/tmp/2-extract.png', img)

# Resize to PB-700 resolution
img = cv2.resize( img, (size,size), interpolation = cv2.INTER_AREA)
cv2.imshow('source grayscale', img) 
cv2.moveWindow( 'source grayscale',size,0)
cv2.imwrite('/tmp/3-475px.png', img)

img = 255-img

# Converting image to a binary image
# ( black and white only image).
_, threshold = cv2.threshold(img, 55, 255, cv2.THRESH_BINARY)

threshold = 255-threshold
cv2.imshow('thresholded', threshold) 
cv2.moveWindow( 'thresholded',size*2,0)
cv2.imwrite('/tmp/4-threshold.png', threshold)
threshold = 255-threshold



# Erodes black pixels based on a 3x3 grid (center stays black if all 9 pixels are black)
# def erode_black( img ):
#     eroded = img.copy()
#     h,w = img.shape
#     eroded = np.zeros(shape=(h,w), dtype=np.uint8)

#     for x in range(h):
#         for y in range(w):
#             black = 255
#             for dx in [-1,0,1]:
#                 for dy in [-1,0,1]:
#                     x0 = x+dx
#                     y0 = y+dy
#                     if not (x0<0 or x0>=w or y0<0 or y0>=h):
#                         if black==255:
#                             black = img[y0,x0]
#             eroded[y,x] = black

#     return eroded

# if erosion>0:
#     eroded = threshold
#     for i in range(erosion):
#         eroded = erode_black(eroded)
#     threshold -= eroded
#     eroded = 255-eroded
#     cv2.imshow('eroded', eroded) 

def generate_convolution_matrix( iterations ):
    n = iterations*2+1
    result = np.array([[1]*n]*n)
    # print(result)
    return result

if erosion>0:
    matrix = generate_convolution_matrix(erosion)
    eroded = cv2.filter2D(255-threshold, -1, matrix)
    _, eroded = cv2.threshold(eroded, 1, 255, cv2.THRESH_BINARY)
    threshold -= 255-eroded
    cv2.imshow('eroded',eroded)
    cv2.imwrite('/tmp/erosion.png', eroded)
    cv2.imwrite('/tmp/eroded.png', 255-threshold)

# Turn into skeleton
skeleton = cv2.ximgproc.thinning(threshold)

skeleton = 255-skeleton
cv2.imshow('skeleton', skeleton) 
cv2.moveWindow( 'skeleton',size*3,0)
cv2.imwrite('/tmp/5-skeleton.png', skeleton)
skeleton = 255-skeleton

# Extract lines
result = []
h,w = skeleton.shape
for y in range(w):
    for x in range(h):
        if skeleton[y,x]==255:
            line = np.array(trace_line_from( skeleton, x, y ))
            line = cv2.approxPolyDP(line, epsilon, False)
            result.append(line)

tot = 0
for c in result:
    tot += len(c)
# print( "Total points==",tot )

# Draw result
img3 = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)
cv2.polylines(img3, result, False, (0, 0, 0), 1)

cv2.imshow('result', img3) 
cv2.moveWindow( 'result',size,size)
cv2.imwrite('/tmp/6-result.png', img3)


# Sort the resulting list to limit motion of plotter head


# Segment list for sorting
def distance( p0, p1 ):
    return math.sqrt((p0[0]-p1[0])*(p0[0]-p1[0])+(p0[1]-p1[1])*(p0[1]-p1[1]))

class SegmentList:
    segments_ = []

    def __init__( self, segments ):
        for seg in segments:
                # Segments are one level too deep, for whatever reason
            self.segments_.append( list([p[0][0], p[0][1]] for p in seg) )

    def closest( self, x, y ):
        d = 10240
        index = 0
        for i in range(len(self.segments_)):
            d0 = distance( self.segments_[i][0], (x,y) )
            d1 = distance( self.segments_[i][-1], (x,y) )
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

draw_list = []
x = 0
y = 0
while not sl.done():
    cur = sl.closest( x, y )
    draw_list.append( [[int(p[0])/5,int(size-p[1])/5] for p in cur] ) # Convert numpy int32 to int and scale down and invert y scale
    x = cur[-1][0]
    y = cur[-1][1]


print( json.dumps(draw_list) )

if cv2.waitKey(0) & 0xFF == ord('q'): 
    cv2.destroyAllWindows()
