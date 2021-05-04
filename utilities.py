import numpy as np
import cv2 as cv
import wx

kernelDilation = np.ones((5,5),np.uint8)
kernelOpen = np.ones((5,5))
kernelClose = np.ones((9,9))


def preprocess_image(img):
    processed = cv.GaussianBlur(img, (9,9), 0)
    processed = cv.medianBlur(processed, 5)
    return processed


def process_mask(mask):
    '''
    Perform noise reduction and other processing for a given mask/image
    '''
    mask = cv.dilate(mask, kernelDilation, iterations=3)
    #morphology
    mask_open = cv.morphologyEx(mask, cv.MORPH_OPEN, kernelOpen)
    mask_close = cv.morphologyEx(mask_open, cv.MORPH_CLOSE, kernelClose)
    return mask_close


def nothing(x=None):
    # Literally does nothing
    pass


def bounding_areas_from_contours(contours):
    '''
    Takes in a list of contours and returns a dictionary whose keys are the bounding areas and values are the coordinates of that particular contour
    '''
    bounding_areas = {}
    for cnt in contours:
        x,y,w,h = cv.boundingRect(cnt)
        area = w*h
        # Store area as key and the coordinates as value
        bounding_areas[area] = [x,y,w,h,area]
    return bounding_areas


def sort_dict_by_keys(data, reverse=False):
    '''
    Sort a dictionary by key
    '''
    return dict(sorted(data.items(), key=lambda item: item[0], reverse=reverse))


def linear_interpolate(num, old_range, new_range):
    '''
    Perform linear interpolation for a number in a given range to a different range
    '''
    return ((new_range[1] - new_range[0]) * (num - old_range[0])/(old_range[1] - old_range[0])) + new_range[0]


def remove_image_background(img, bg_ref):
    diff1 = cv.subtract(img, bg_ref)
    diff2 = cv.subtract(bg_ref, img)
    diff = diff1 + diff2
    diff[abs(diff) < 15.0] = 0
    gray = cv.cvtColor(diff.astype(np.uint8), cv.COLOR_BGR2GRAY)
    gray[np.abs(gray) < 10] = 0
    fgmask = gray.astype(np.uint8)
    fgmask[fgmask>0]=255
    #use the masks to extract the FG
    fgimg = cv.bitwise_and(img, img, mask = fgmask)
    return fgimg


def get_bitmap_from_array(width=32, height=32, colour = (0,0,0) ):
   array = np.zeros( (height, width, 3),'uint8')
   array[:,:,] = colour
   image = wx.EmptyImage(width,height)
   image.SetData( array.tostring())
   wxBitmap = image.ConvertToBitmap()  # OR:  wx.BitmapFromImage(image)
   return wxBitmap
