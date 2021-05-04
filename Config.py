class Config():
    colors = ['yellow', 'red', 'blue', 'green', 'custom']
    trackingTypes = ['Frame to Screen Mapping', 'Free Tracking']
    def __init__(self):
        self.selectedColor = 0

        self.lh = 15
        self.ls = 100
        self.lv = 100

        self.uh = 35
        self.us = 255
        self.uv = 255

        self.enableMouseTracking = False

        self.selectedTrackingType = 1   # 0 for Mapped Tracking, 1 for Free Tracking

        self.sensitivity = 100 # Applicable only for Free Tracking

    def selectColor(self, index):
        self.selectedColor = index
        color = Config.colors[self.selectedColor]
        if color != 'custom':
            self.setColorValues(color)

    def setColorValues(self, color):
        if color == 'yellow':
            self.lh = 15
            self.ls = 100
            self.lv = 100

            self.uh = 35
            self.us = 255
            self.uv = 255
        elif color == 'blue':
            self.lh = 90
            self.ls = 100
            self.lv = 100

            self.uh = 128
            self.us = 255
            self.uv = 255
        elif color == 'red':
            self.lh = 159
            self.ls = 100
            self.lv = 100

            self.uh = 180
            self.us = 255
            self.uv = 255
        elif color == 'green':
            self.lh = 36
            self.ls = 50
            self.lv = 70

            self.uh = 89
            self.us = 255
            self.uv = 255
