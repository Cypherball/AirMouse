import numpy as np
import cv2 as cv
import pyautogui
import utilities

class processor():

    def __init__(self):
        pyautogui.FAILSAFE = False
        self.screenWidth, self.screenHeight = pyautogui.size()

        self.enableMouseTracking = False

        self.contrast = 10

        self.brightness = 128

        self.prevCursorLoc = ()
        self.mouseDown = False

        self.captureBGFlag = False
        self.remove_bg = False
        self.bg_ref = None

        self.lh = 12
        self.ls = 100
        self.lv = 100

        self.uh = 35
        self.us = 255
        self.uv = 255

    def process_frame(self, frame, config): 
        #frame = self.frame
        cv.flip(frame,1,frame)

        height, width = frame.shape[:2]

        paddingPercent = 30
        trackingRangeX = [0 + (paddingPercent/100)*(width), (100-paddingPercent)/100*(width)]
        trackingRangeY = [0 + (paddingPercent/100)*(height), (100-paddingPercent)/100*(height)]

        if self.captureBGFlag:
            self.bg_ref = frame
            print('Background Captured!')
            # self.remove_bg = True
            self.captureBGFlag = False
        
        if self.remove_bg:
            if self.bg_ref is None:
                print('Cannot Remove Background! Background Ref Not Set.')
                self.remove_bg = False
            else:
                frame = utilities.remove_image_background(frame, self.bg_ref)

        img = frame
        cv.convertScaleAbs(frame, img, alpha=self.contrast/10, beta=self.brightness-128)

        # Lowerbound and Upperbound for color detection
        l_b = np.array([config.lh,config.ls,config.lv])
        u_b = np.array([config.uh,config.us,config.uv])

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
        # Get only the first two largest rectangles if there are more than two
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
        
        if config.enableMouseTracking:
            if cursorLoc:
                if len(points) == 2 and not self.mouseDown:
                    pyautogui.mouseDown()
                    self.mouseDown = True
                elif len(points) == 1 and self.mouseDown:
                    pyautogui.mouseUp()
                    self.mouseDown = False

                # Mapped Tracking 
                if config.selectedTrackingType == 0:
                    newMouseX = int(utilities.linear_interpolate(cursorLoc[0], trackingRangeX, [0, self.screenWidth]))
                    newMouseY = int(utilities.linear_interpolate(cursorLoc[1], trackingRangeY, [0, self.screenHeight]))
                    # Ignore micromovements
                    if abs(currentMouseX - newMouseX) > 5 or abs(currentMouseY - newMouseY) > 5:
                        pyautogui.moveTo(newMouseX, newMouseY)

                # Free Tracking (Indpendent of tracked object on the camera)
                elif config.selectedTrackingType == 1 and self.prevCursorLoc:
                    cursor_deviation_x = cursorLoc[0] - self.prevCursorLoc[0]
                    cursor_deviation_y = cursorLoc[1] - self.prevCursorLoc[1]

                    # Ignore micromovements
                    if abs(cursor_deviation_x) < 3: cursor_deviation_x = 0
                    if abs(cursor_deviation_y) < 3: cursor_deviation_y = 0

                    pyautogui.moveTo((currentMouseX + cursor_deviation_x) * config.sensitivity/100, (currentMouseY + cursor_deviation_y) * config.sensitivity/100)
                 
            elif len(points) == 0 and self.mouseDown:
                pyautogui.mouseUp()
                self.mouseDown = False

        if cursorLoc:
            self.prevCursorLoc = cursorLoc
        
        return [frame, maskFinal]