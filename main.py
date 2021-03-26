import numpy as np
import cv2 as cv
import pyautogui
from matplotlib import pyplot as plt
import utilities

pyautogui.FAILSAFE = False
screenWidth, screenHeight = pyautogui.size()

enableMouseTracking = False

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Couldn't open the Camera")
    exit()

cv.namedWindow('frame')

cap.set(3, 1280)
cap.set(4, 720)

paddingPercent = 30
trackingRangeX = [0 + (paddingPercent/100)*(cap.get(cv.CAP_PROP_FRAME_WIDTH)), (100-paddingPercent)/100*(cap.get(cv.CAP_PROP_FRAME_WIDTH))]
trackingRangeY = [0 + (paddingPercent/100)*(cap.get(cv.CAP_PROP_FRAME_HEIGHT)), (100-paddingPercent)/100*(cap.get(cv.CAP_PROP_FRAME_HEIGHT))]

resolution = 'Width: ' + str(cap.get(cv.CAP_PROP_FRAME_WIDTH)) + ' Height: ' + str(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

contrast = 10
def update_contrast(x):
    global contrast
    contrast = x

brightness = 128
def update_brightness(x):
    global brightness
    brightness = x

sensitivity = 100
def update_sensitivity(x):
    global sensitivity
    sensitivity = x

cv.createTrackbar('Contrast', 'frame', 10, 30, update_contrast)
cv.createTrackbar('Brightness', 'frame', 128, 256, update_brightness)
cv.createTrackbar('Sensitivity', 'frame', 100, 1000, update_sensitivity)

cv.namedWindow('Tracking')

cv.createTrackbar('LH', 'Tracking', 12, 255, utilities.nothing)
cv.createTrackbar('LS', 'Tracking', 100, 255, utilities.nothing)
cv.createTrackbar('LV', 'Tracking', 100, 255, utilities.nothing)

cv.createTrackbar('UH', 'Tracking', 35, 255, utilities.nothing)
cv.createTrackbar('US', 'Tracking', 255, 255, utilities.nothing)
cv.createTrackbar('UV', 'Tracking', 255, 255, utilities.nothing)

prevCursorLoc = ()
mouseDown = False

frameCount = 0
captureBGFlag = False
remove_bg = False
bg_ref = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Couldn't retreive the frame. Exiting...")
        break
    frameCount += 1

    cv.flip(frame,1,frame)

    if captureBGFlag:
        bg_ref = frame
        print('Background Captured!')
        #remove_bg = True
        captureBGFlag = False
    
    if remove_bg:
        if bg_ref is None:
            print('Cannot Remove Background! Background Ref Not Set.')
            remove_bg = False
        else:
            frame = utilities.remove_image_background(frame, bg_ref)

    img = frame
    cv.convertScaleAbs(frame, img, alpha=contrast/10, beta=brightness-128)

    lh = cv.getTrackbarPos('LH', 'Tracking')
    ls = cv.getTrackbarPos('LS', 'Tracking')
    lv = cv.getTrackbarPos('LV', 'Tracking')
    uh = cv.getTrackbarPos('UH', 'Tracking')
    us = cv.getTrackbarPos('US', 'Tracking')
    uv = cv.getTrackbarPos('UV', 'Tracking')

    # Lowerbound and Upperbound for color detection
    l_b = np.array([lh,ls,lv])
    u_b = np.array([uh,us,uv])

    processedHSV= cv.cvtColor(utilities.preprocess_image(img), cv.COLOR_BGR2HSV)
    mask = cv.inRange(processedHSV, l_b, u_b)
    
    maskFinal = utilities.process_mask(mask)
    contours, h = cv.findContours(maskFinal.copy(), cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

    # Draw Tracking Area Range Box
    #frame = cv.rectangle(frame, (trackingRangeX[0], trackingRangeY[0]), (trackingRangeX[1], trackingRangeY[1]), (0,0,255), 3)

    boundingAreas = utilities.bounding_areas_from_contours(contours)

    # Sort the areas in descending order
    boundingAreas = utilities.sort_dict_by_keys(boundingAreas, reverse=True)
    # Get the sorted bounding coordinates
    rects = list(boundingAreas.values())
    lenRects = len(rects)
    # Get only the firs two largest rectangles if there are more than two
    if lenRects > 2:
        lenRects = 2

    points = []
    for i in range(lenRects):
        x,y,w,h,area = rects[i]
        # Discard if subsequent boxes are less than 20% of the largest box
        if i > 0 and area < 0.2*rects[0][4]:
            break
        # Draw rectangle to show bounding box
        frame = cv.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 3)
        x_center = x+int(w/2)
        y_center = y+int(h/2)
        points.append((x_center, y_center))
        # Draw circle to show center of bounding box
        frame = cv.circle(frame, (x_center, y_center), radius=5, color=(0,0,255), thickness=-1)
    
    cursorLoc = ()
    if len(points) == 1:
        cursorLoc = points[0]
    # If there are two bounding boxes, Draw a line through their centers
    if len(points) == 2:
        frame = cv.line(frame, points[0], points[1], color=(0,255,0), thickness=3)
        x_center = int((points[0][0] + points[1][0]) / 2)
        y_center = int((points[0][1] + points[1][1]) / 2)
        cursorLoc = (x_center, y_center)
        # Draw circle to show center of the line
        frame = cv.circle(frame, cursorLoc, radius=5, color=(255,0,0), thickness=-1)

    currentMouseX, currentMouseY = pyautogui.position()
    #if prevCursorLoc and cursorLoc:
        #cursor_deviation_x = cursorLoc[0] - prevCursorLoc[0]
        #cursor_deviation_y = cursorLoc[1] - prevCursorLoc[1]
        #pyautogui.moveTo((currentMouseX + cursor_deviation_x) * sensitivity/100, (currentMouseY + cursor_deviation_y) * sensitivity/100)
    
    if enableMouseTracking:
        if cursorLoc:
            if len(points) == 1 and not mouseDown:
                pyautogui.mouseDown()
                mouseDown = True
            elif len(points) == 2 and mouseDown:
                pyautogui.mouseUp()
                mouseDown = False
            #if frameCount%5 == 0:
            newMouseX = int(utilities.linear_interpolate(cursorLoc[0], trackingRangeX, [0, screenWidth]))
            newMouseY = int(utilities.linear_interpolate(cursorLoc[1], trackingRangeY, [0, screenHeight]))
            if frameCount%30 == 0:
                print('Mouse:', newMouseX, newMouseY)
                print('Screen:', screenWidth, screenHeight)
                print('Cap:', cap.get(cv.CAP_PROP_FRAME_WIDTH), cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            # Ignore micromovements
            if abs(currentMouseX - newMouseX) > 2 or abs(currentMouseY - newMouseY) > 2:
                pyautogui.moveTo(newMouseX, newMouseY)#, duration=0.5, tween=pyautogui.easeOutQuad)
        elif len(points) == 0 and mouseDown:
            pyautogui.mouseUp()
            mouseDown = False

    if cursorLoc:
        prevCursorLoc = cursorLoc
    
    cv.imshow('frame', frame)
    #cv.imshow('mask', mask)
    cv.imshow('Processed Mask', maskFinal)

    key = cv.waitKey(1)
    if key == ord('m'):
        enableMouseTracking = not enableMouseTracking
        print('Mouse Tracking:', enableMouseTracking)
    elif key == ord('b'):
        print('Capturing Background...')
        captureBGFlag = True
    elif key == ord('r'):
        if remove_bg:
            print('Adding Background...')
            remove_bg = False
        else:
            print('Removing Background...')
            remove_bg = True
    elif key == ord('q'):
        print('Exiting...')
        break

cap.release()
cv.destroyAllWindows()