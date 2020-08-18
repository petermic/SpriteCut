"""
rectanglecutter.py
Author: Michael Peters

Splits a spritesheet where sprites are surrounded by rectangles of a uniform color into individual sprite images.
Also changes background color of spritesheet to transparent.
"""

from PIL import Image
import sys
from operator import itemgetter

# Make sure input format is correct; if not, exit
if len(sys.argv) != 2:
    print("Usage: python3 blacksquarecutter.py <input image>")
    sys.exit()

# open image file
inputFile = sys.argv[1]
inputImage = Image.open(inputFile)

# print diagnostic image info
print("name: "+inputFile)
print("format: "+inputImage.format)
print("size: "+str(inputImage.size))

# Modify these parameters to fit your spritesheet.
rectangleThickness = 1                 # thickness of rectangle, in pixels
rectangleColor = (0,0,0,255)           # RGBA value of rectangle color
minimumSpriteSize = (10,10)            # reject rectangles below this size

# find background color, assumed to be the most common color in the image
color_list = inputImage.getcolors()
most_common_entry = max(color_list,key=itemgetter(0))
background_color = most_common_entry[1]
print("background color:")
print("RGBA = "+str(background_color))

# turn image into list of pixel values
pixelList = list(inputImage.getdata()) #1D list of pixel values
imageWidth = inputImage.size[0]
imageHeight = inputImage.size[1]
pixel2DList = [pixelList[i:i+imageWidth] for i in range(0,imageWidth*imageHeight,imageWidth)] # list of pixels by (row, column)

# make background color transparent
for (r,row) in enumerate(pixel2DList):
    for (c,pixelcolor) in enumerate(row):
        if pixelcolor == background_color:
            pixel2DList[r][c] = (0,0,0,0)

# determines if a pixel (row,col) in 2D list plist is in the upper-left corner of a rectangle
def isUpperLeft(plist,row,col):
    p = plist[row][col]
    if p != rectangleColor: # pixel is not same color as rectangle
        return False
    elif plist[row+1][col+1] == rectangleColor: # pixel's lower-right neighbor is in rectangle
        return False
    elif plist[row+1][col] != rectangleColor or plist[row][col+1] != rectangleColor: # pixels directly below and to the right are not in rectangle
        return False
    else:
        failedcheck = False
        for t in range(rectangleThickness):
            for u in range(rectangleThickness):
                if plist[row-t][col-u] != rectangleColor: # pixels above and to the left are not in rectangle
                    failedcheck = True
        return not(failedcheck)
    
# find upper-left corners
corners = []
for (r,row) in enumerate(pixel2DList):
    for (c,pixelcolor) in enumerate(row):
        if isUpperLeft(pixel2DList,r,c):
            corners.append((r,c))
print("number of rectangle candidates: "+str(len(corners)))

# follow rectangles down to lower-right corner
rectangles = []
for c in corners:
    row = c[0]
    col = c[1]
    col_offset = 1 # start with the pixel immediately to the right
    # follow edge until you see the top-right corner
    while pixel2DList[row][col+col_offset]==rectangleColor and pixel2DList[row+1][col+col_offset]!=rectangleColor:
        col_offset += 1
    # now follow edge until you see the bottom-left corner
    row_offset = 1
    while pixel2DList[row+row_offset][col+col_offset]==rectangleColor and pixel2DList[row+row_offset][col+col_offset-1]!=rectangleColor:
        row_offset += 1
    rectangles.append((row,col,row+row_offset,col+col_offset))

# create and save new image
flatpixelList = [p for row in pixel2DList for p in row]
outputImage = Image.new(inputImage.mode,inputImage.size)
outputImage.putdata(flatpixelList)
outputImage.save("transparent_bkgd.png")

# for each rectangle, create and save an image with the contents of that rectangle
sprite_counter = 0
for r in rectangles:
    rec_xy = (r[1]+1,r[0]+1,r[3],r[2])
    if abs(rec_xy[2]-rec_xy[0]) < minimumSpriteSize[0] or abs(rec_xy[3]-rec_xy[1]) < minimumSpriteSize[1]:
        continue
    sprite_img = outputImage.crop(rec_xy)
    sprite_counter += 1
    sprite_img.save("sprite_"+str(sprite_counter)+".png")

print("found "+str(sprite_counter)+" sprites.")

