# Python code to find the co-ordinates of
# the contours detected in an image.
import numpy as np
import cv2
from skimage.morphology import skeletonize

dx = [ 1,0,-1,0, 1,1,-1,-1]
dy = [ 0,1,0,-1, -1,1,1,-1]

size = 95*5     # PB-700 size

def trace_line_from( img, x, y ):
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


source_path = "images/sample8.png"
 
# Reading image
original = cv2.imread(source_path, cv2.IMREAD_COLOR)

cv2.imshow('Original', original) 

# Reading same image in another 
# variable and converting to gray scale.
img = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
h,w = img.shape
img = img[:h//2,:w//2]

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
print( "Total points==",tot )

# # Detecting contours in image.
# contours, _= cv2.findContours(skeleton, cv2.RETR_LIST,
#                                 cv2.CHAIN_APPROX_NONE)

# # print( contours )
# print( original.shape )

img3 = 255 * np.ones(shape=(size,size,3), dtype=np.uint8)
cv2.polylines(img3, result, False, (0, 0, 0), 1)

# # cv2.drawContours(img3, contours, -1, (0, 0, 255), 1) 

# for cnt in contours:
#     # Approximate the contour to a polyline
#     # epsilon = 0.2*cv2.arcLength(cnt, True)
#     approx = cv2.approxPolyDP(cnt, 1, True)

#     # Draw the polyline
#     cv2.polylines(img3, [approx], True, (255, 0, 0), 1)

# # # Showing the final image.
cv2.imshow('Image Final', img3) 
  
# Exiting the window if 'q' is pressed on the keyboard.
if cv2.waitKey(0) & 0xFF == ord('q'): 
    cv2.destroyAllWindows()

