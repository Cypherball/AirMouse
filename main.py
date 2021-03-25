import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

def nothing(x=None):
    pass

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Couldn't open the Camera")
    exit()

cv.namedWindow('frame')

cap.set(3, 1280)
cap.set(4, 720)

resolution = 'Width: ' + str(cap.get(cv.CAP_PROP_FRAME_WIDTH)) + ' Height: ' + str(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

contrast = 10
def updateContrast(x):
    global contrast
    contrast = x

brightness = 128
def updateBrightness(x):
    global brightness
    brightness = x

cv.createTrackbar('Contrast', 'frame', 10, 30, updateContrast)
cv.createTrackbar('Brightness', 'frame', 128, 256, updateBrightness)

cv.namedWindow('Tracking')

cv.createTrackbar('LH', 'Tracking', 12, 255, nothing)
cv.createTrackbar('LS', 'Tracking', 100, 255, nothing)
cv.createTrackbar('LV', 'Tracking', 100, 255, nothing)

cv.createTrackbar('UH', 'Tracking', 35, 255, nothing)
cv.createTrackbar('US', 'Tracking', 255, 255, nothing)
cv.createTrackbar('UV', 'Tracking', 255, 255, nothing)

kernelOpen=np.ones((5,5))
kernelClose=np.ones((9,9))

while True:
    ret, frame = cap.read()
    if not ret:
        print("Couldn't retreive the frame. Exiting...")
        break
    cv.flip(frame,1,frame)

    img = frame
    cv.convertScaleAbs(frame, img, alpha=contrast/10, beta=brightness-128)

    lh = cv.getTrackbarPos('LH', 'Tracking')
    ls = cv.getTrackbarPos('LS', 'Tracking')
    lv = cv.getTrackbarPos('LV', 'Tracking')
    uh = cv.getTrackbarPos('UH', 'Tracking')
    us = cv.getTrackbarPos('US', 'Tracking')
    uv = cv.getTrackbarPos('UV', 'Tracking')

    l_b = np.array([lh,ls,lv])
    u_b = np.array([uh,us,uv])

    processed = cv.GaussianBlur(img, (9,9), 0)
    processed = cv.medianBlur(processed, 5)
    processedHSV= cv.cvtColor(processed,cv.COLOR_BGR2HSV)
    mask = cv.inRange(processedHSV, l_b, u_b)
    mask = cv.dilate(mask, np.ones((5,5),np.uint8), iterations=3)
    #morphology
    maskOpen=cv.morphologyEx(mask, cv.MORPH_OPEN, kernelOpen)
    maskClose=cv.morphologyEx(maskOpen, cv.MORPH_CLOSE, kernelClose)

    maskFinal = maskClose
    conts,h = cv.findContours(maskFinal.copy(),cv.RETR_LIST,cv.CHAIN_APPROX_NONE)
    #print("Number of contours:" + str(len(conts)))

    #cv.drawContours(maskFinal, conts, -1, (255,0,0), 3)
    boundingAreas = {}
    for cnt in conts:
        x,y,w,h = cv.boundingRect(cnt)
        area = w*h
        # Store area as key and the coordinates as value
        boundingAreas[area] = [x,y,w,h,area]
    # Sort the areas in descending order
    boundingAreas = dict(sorted(boundingAreas.items(), key=lambda item: item[0], reverse=True))
    # Get the sorted bounding coordinates
    rects = list(boundingAreas.values())
    lenRects = len(rects)
    # Get only the firs two largest rectangles if there are more than two
    if lenRects > 2:
        lenRects = 2
    points = []
    for i in range(lenRects):
        x,y,w,h,area = rects[i]
        if i > 0 and area < 0.2*rects[0][4]:
            break
        frame = cv.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 3)
        x_center = x+int(w/2)
        y_center = y+int(h/2)
        points.append((x_center, y_center))
        frame = cv.circle(frame, (x_center, y_center), radius=5, color=(0,0,255), thickness=-1)
    
    if len(points) == 2:
        frame = cv.line(frame, points[0], points[1], color=(0,255,0), thickness=3)
        x_center = int((points[0][0] + points[1][0]) / 2)
        y_center = int((points[0][1] + points[1][1]) / 2)
        frame = cv.circle(frame, (x_center, y_center), radius=5, color=(255,0,0), thickness=-1)
    
    cv.imshow('frame', frame)
    #cv.imshow('mask', mask)
    cv.imshow('Processed Mask', maskFinal)
    
    if cv.waitKey(1) == ord('q'):
        print('Exiting...')
        break

cap.release()
cv.destroyAllWindows()