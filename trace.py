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

def describe_and_save( source, text, filename ):
    img = source.copy()
    h = img.shape[0]
    w = img.shape[1]
    cv2.putText( img, text, (0,int(10*h/475)), cv2.FONT_HERSHEY_SIMPLEX, (0.4*h/475), (0,0,0), int(1*h/475) )
    cv2.imwrite( filename, img )

# Reading image
original = cv2.imread(source_path, cv2.IMREAD_COLOR)
describe_and_save( original, "Original Image",'/tmp/0-original.png' )
cv2.imshow('Original', original) 

# Reading grayscale
img = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
describe_and_save( img, "Original Image (grayscale)", '/tmp/1-grayscale.png' )

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

describe_and_save( img, "Portion to trace", '/tmp/2-extract.png' )

# Resize to PB-700 resolution
img = cv2.resize( img, (size,size), interpolation = cv2.INTER_AREA)
describe_and_save( img, "Downscaled to 475x475", "/tmp/3-475px.png" )
cv2.imshow('source grayscale', img) 
cv2.moveWindow( 'source grayscale',size,0)

img = 255-img

# Converting image to a binary image
# ( black and white only image).
_, threshold = cv2.threshold(img, 55, 255, cv2.THRESH_BINARY)

threshold = 255-threshold
describe_and_save( threshold, "Pure black and white (thresholded)",'/tmp/4-threshold.png' )
cv2.imshow('thresholded', threshold) 
cv2.moveWindow( 'thresholded',size*2,0)
threshold = 255-threshold



# Erosion (erases all pixels where the 8 neighbours are not black, 'erosion' times)
# This is aking of erasing all the pixels where the 'erosion*2+1' square around is not black

def generate_convolution_matrix( iterations ):
    n = iterations*2+1
    result = np.array([[1]*n]*n)
    return result

if erosion>0:
    matrix = generate_convolution_matrix(erosion)
    eroded = cv2.filter2D(255-threshold, -1, matrix)
    _, eroded = cv2.threshold(eroded, 1, 255, cv2.THRESH_BINARY)
    threshold -= 255-eroded
    cv2.imshow('eroded',eroded)
    describe_and_save( eroded, "Erosion map", '/tmp/5-erosion.png')
    describe_and_save( 255-threshold, "Eroded image", '/tmp/6-eroded.png' )

# Turn into skeleton
skeleton = cv2.ximgproc.thinning(threshold)

skeleton = 255-skeleton
describe_and_save( skeleton, "Skeleton (using thinning)",'/tmp/7-skeleton.png' )
cv2.imshow('skeleton', skeleton) 
cv2.moveWindow( 'skeleton',size*3,0)
skeleton = 255-skeleton

# Extract lines
result = []
result_detail = []
h,w = skeleton.shape
for y in range(w):
    for x in range(h):
        if skeleton[y,x]==255:
            line = np.array(trace_line_from( skeleton, x, y ))
            result_detail.append(line)
            line = cv2.approxPolyDP(line, epsilon, False)
            result.append(line)

tot_detail = 0
for c in result_detail:
    tot_detail += len(c)

tot = 0
for c in result:
    tot += len(c)

# Draw result (detail)
result_detail_img = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)
cv2.polylines(result_detail_img, result_detail, False, (0, 0, 0), 1)
describe_and_save( result_detail_img, f"Traced image (paths: {len(result_detail)}, points: {tot_detail})",'/tmp/9-result_detail_img.png' )
cv2.imshow('result_detail_img', result_detail_img) 
cv2.moveWindow( 'result detail',size,size)

# Draw result (approx)
img3 = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)
cv2.polylines(img3, result, False, (0, 0, 0), 1)
describe_and_save( img3, f"With approximation (paths: {len(result)}, points: {tot})", '/tmp/10-result.png' )
cv2.imshow('result', img3) 
cv2.moveWindow( 'result',size,size)


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

# Generates an image with all segments in order
motion_img = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)
x = 0
y = size
i = 0
for cur in draw_list:
    # Draw all segments with different colors
    for j in range(len(cur)-1):
        c = [(255, 0, 0),(0, 255, 0),(0, 0, 255),(255,255,0),(255,0,255),(0,255,255)][i%5]
        cv2.line(motion_img, (int(cur[j][0]*5), size-int(cur[j][1]*5)), (int(cur[j+1][0]*5), size-int(cur[j+1][1]*5)), c, thickness=1)
        i = i+1

    x = int(cur[-1][0]*5)
    y = int(cur[-1][1]*5)

describe_and_save( motion_img, "All segments", '/tmp/11-all-segments.png' )


# Generates an image with segments in order and motion
motion_img = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)
x = 0
y = size
i = 0
for cur in draw_list:
    # Draw the motion
    cv2.line(motion_img, (x,size-y), (int(cur[0][0]*5),size-int(cur[0][1]*5)), (192,192,192), thickness=1)

    # Draw all segments with different colors
    c = [(255, 0, 0),(0, 255, 0),(0, 0, 255),(255,255,0),(255,0,255),(0,255,255)][i%5]
    i = i+1
    for j in range(len(cur)-1):
         cv2.line(motion_img, (int(cur[j][0]*5), size-int(cur[j][1]*5)), (int(cur[j+1][0]*5), size-int(cur[j+1][1]*5)), c, thickness=1)

    x = int(cur[-1][0]*5)
    y = int(cur[-1][1]*5)

describe_and_save( motion_img, "Motion of head and drawing", '/tmp/12-motion.png' )



print( json.dumps(draw_list) )

# if cv2.waitKey(0) & 0xFF == ord('q'): 
#     cv2.destroyAllWindows()
