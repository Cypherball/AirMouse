import wx
import cv2
import constants
from FrameProcessor import processor
from Config import Config

class AirMouse(wx.Frame):
    def __init__(self, cam_list, capture, *args, **kw):
        # ensure the parent's __init__ is called
        super(AirMouse, self).__init__(*args, **kw)

        self.config = Config()

        self.cam_list = cam_list

        self.capture = capture

        if self.capture:
            ret, frame = self.capture.read()

            self.frame_processor = processor()
            [processed_frame, processed_mask] = self.frame_processor.process_frame(frame, self.config)

            processed_frame = cv2.resize(processed_frame, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)

            processed_mask = cv2.resize(processed_mask, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)

            height, width = processed_frame.shape[:2]

            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            self.bmp = wx.Bitmap.FromBuffer(width, height, processed_frame)

            processed_mask = cv2.cvtColor(processed_mask, cv2.COLOR_BGR2RGB)
            self.mask = wx.Bitmap.FromBuffer(width, height, processed_mask)

        self.InitUI()

    def InitUI(self):
         # create a panel in the frame
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#FFFACD')

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)

        font.SetPointSize(12)

        sizer = wx.GridBagSizer(10, 10)

        row = 0

        colorLabel = wx.StaticText(panel, label='Color')
        self.colorsCB = wx.ComboBox(panel, choices=Config.colors, style=wx.CB_READONLY)
        self.colorsCB.Bind(wx.EVT_COMBOBOX, self.onColorSelect)
        self.colorsCB.SetSelection(0)
        sizer.Add(colorLabel, pos=(row, 0), span=(1,1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(self.colorsCB, pos=(row, 1), span=(1,1), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        cameraSourceLabel = wx.StaticText(panel, label='Camera Source')
        cameraSourceCB = wx.ComboBox(panel, choices=list(map(lambda x: 'Cam '+str(x), self.cam_list )), style=wx.CB_READONLY)
        cameraSourceCB.Bind(wx.EVT_COMBOBOX, self.onCamSelect)
        cameraSourceCB.SetSelection(0)
        sizer.Add(cameraSourceLabel, pos=(row, 2), span=(1,1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(cameraSourceCB, pos=(row, 3), span=(1,1), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        row += 1

        self.cam = wx.StaticBitmap(panel, wx.ID_ANY, self.bmp)
        sizer.Add(self.cam, pos=(row, 0), span=(1,2), flag=wx.EXPAND|wx.ALL, border=10)

        self.mask_bitmap = wx.StaticBitmap(panel, wx.ID_ANY, self.mask)
        sizer.Add(self.mask_bitmap, pos=(row, 2), span=(1,2), flag=wx.EXPAND|wx.ALL, border=10)

        row += 1

        self.mouseTrackingToggle = wx.ToggleButton(panel, label='ENABLE MOUSE TRACKING')
        self.mouseTrackingToggle.Bind(wx.EVT_TOGGLEBUTTON, self.ToggleMouseTracking)
        sizer.Add(self.mouseTrackingToggle, pos=(row, 0), span=(1,4), flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, border=30)

        row += 1
        
        # Tracking and Sensitivity Options

        trackingTypeLabel = wx.StaticText(panel, label='Tracking Type')
        self.trackingCB = wx.ComboBox(panel, choices=Config.trackingTypes, style=wx.CB_READONLY)
        self.trackingCB.Bind(wx.EVT_COMBOBOX, self.onTrackingTypeSelect)
        self.trackingCB.SetSelection(1)
        sizer.Add(trackingTypeLabel, pos=(row, 0), span=(1,1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(self.trackingCB, pos=(row, 1), span=(1,1), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        sensitivityLabel = wx.StaticText(panel, label='Sensitivity (Free Mode Only)')
        self.sensitivitySlider = wx.Slider(panel, wx.ID_ANY, minValue=10, maxValue=300, value=100, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        self.sensitivitySlider.Bind(wx.EVT_SCROLL, self.OnSensitivitySliderScroll)
        sizer.Add(sensitivityLabel, pos=(row, 2), span=(1,1), flag=wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(self.sensitivitySlider, pos=(row, 3), span=(1,1), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        row += 1

        # Lower and Upper Hue Combo Boxes and Labels

        lhLabel = wx.StaticText(panel, label='Lower Hue')
        sizer.Add(lhLabel, pos=(row, 0), span=(1,2), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
        uhLabel = wx.StaticText(panel, label='Upper Hue')
        sizer.Add(uhLabel, pos=(row, 2), span=(1,2), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
        row += 1

        self.lhSlider = wx.Slider(panel, wx.ID_ANY, minValue=0, maxValue=255, value=15, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        self.lhSlider.Bind(wx.EVT_SCROLL, self.On_lhScroll)
        sizer.Add(self.lhSlider, pos=(row, 0), span=(1,2), flag=wx.EXPAND|wx.ALL, border=10)
       
        self.uhSlider = wx.Slider(panel, wx.ID_ANY, minValue=0, maxValue=255, value=15, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        self.uhSlider.Bind(wx.EVT_SCROLL, self.On_uhScroll)
        sizer.Add(self.uhSlider, pos=(row, 2), span=(1,2), flag=wx.EXPAND|wx.ALL, border=10)

        row += 1

        # Lower and Upper Saturation Combo Boxes and Labels

        lsLabel = wx.StaticText(panel, label='Lower Saturation')
        sizer.Add(lsLabel, pos=(row, 0), span=(1,2), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
        usLabel = wx.StaticText(panel, label='Upper Saturation')
        sizer.Add(usLabel, pos=(row, 2), span=(1,2), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
        row += 1

        self.lsSlider = wx.Slider(panel, wx.ID_ANY, minValue=0, maxValue=255, value=100, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        self.lsSlider.Bind(wx.EVT_SCROLL, self.On_lsScroll) 
        sizer.Add(self.lsSlider, pos=(row, 0), span=(1,2), flag=wx.EXPAND|wx.ALL, border=10)

       
        self.usSlider = wx.Slider(panel, wx.ID_ANY, minValue=0, maxValue=255, value=100, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        self.usSlider.Bind(wx.EVT_SCROLL, self.On_usScroll)
        sizer.Add(self.usSlider, pos=(row, 2), span=(1,2), flag=wx.EXPAND|wx.ALL, border=10)

        row += 1

        # Lower and Upper Value Combo Boxes and Labels

        lvLabel = wx.StaticText(panel, label='Lower Value')
        sizer.Add(lvLabel, pos=(row, 0), span=(1,2), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
        uvLabel = wx.StaticText(panel, label='Upper Value')
        sizer.Add(uvLabel, pos=(row, 2), span=(1,2), flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)
        row += 1


        self.lvSlider = wx.Slider(panel, wx.ID_ANY, minValue=0, maxValue=255, value=100, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        self.lvSlider.Bind(wx.EVT_SCROLL, self.On_lvScroll)
        sizer.Add(self.lvSlider, pos=(row, 0), span=(1,2), flag=wx.EXPAND|wx.ALL, border=10)

        
        self.uvSlider = wx.Slider(panel, wx.ID_ANY, minValue=0, maxValue=255, value=100, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        self.uvSlider.Bind(wx.EVT_SCROLL, self.On_uvScroll)
        sizer.Add(self.uvSlider, pos=(row, 2), span=(1,2), flag=wx.EXPAND|wx.ALL, border=10)

        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableCol(2)
        sizer.AddGrowableCol(3)

        panel.SetSizer(sizer)

        sizer.SetSizeHints(self)
        panel.Layout()
        panel.SetFocus()

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to Air Mouse!")

        self.Centre()

        #start a timer that's handler grabs a new frame and updates the image widgets
        self.timer = wx.Timer(self)
        self.fps = 60
        self.timer.Start(1000/self.fps)

        #bind timer events to the handler
        self.Bind(wx.EVT_TIMER, self.NextFrame)

    def NextFrame(self, event):
        if self.capture:
            ret, self.orig_frame = self.capture.read()
            if ret:
                [processed_frame, processed_mask] = self.frame_processor.process_frame(self.orig_frame, self.config)

                processed_frame = cv2.resize(processed_frame, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)

                processed_mask = cv2.resize(processed_mask, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)

                processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                self.bmp.CopyFromBuffer(processed_frame)
                self.cam.SetBitmap(self.bmp)

                processed_mask = cv2.cvtColor(processed_mask, cv2.COLOR_BGR2RGB)
                self.mask.CopyFromBuffer(processed_mask)
                self.mask_bitmap.SetBitmap(self.mask)

    def ToggleMouseTracking(self, e):
        self.config.enableMouseTracking = e.GetEventObject().GetValue()

    def onCamSelect(self, e):
        self.capture = cv2.VideoCapture(self.cam_list[e.GetSelection()])

    def onColorSelect(self, e):
        self.config.selectColor(e.GetSelection())
        self.lhSlider.SetValue(self.config.lh)
        self.lsSlider.SetValue(self.config.ls)
        self.lvSlider.SetValue(self.config.lv)
        self.uhSlider.SetValue(self.config.uh)
        self.usSlider.SetValue(self.config.us)
        self.uvSlider.SetValue(self.config.uv)

    def onTrackingTypeSelect(self, e):
        self.config.selectedTrackingType = e.GetSelection()
    
    def OnSensitivitySliderScroll(self, e):
        self.config.sensitivity = e.GetEventObject().GetValue()
    
    def On_lhScroll(self, e):
        val = e.GetEventObject().GetValue()
        # Set color to 'custom'
        self.colorsCB.SetSelection(4)
        self.config.selectColor(4)
        self.config.lh = val
    
    def On_uhScroll(self, e):
        val = e.GetEventObject().GetValue()
        # Set color to 'custom'
        self.colorsCB.SetSelection(4)
        self.config.selectColor(4)
        self.config.uh = val

    def On_lsScroll(self, e):
        val = e.GetEventObject().GetValue()
        # Set color to 'custom'
        self.colorsCB.SetSelection(4)
        self.config.selectColor(4)
        self.config.ls = val

    def On_usScroll(self, e):
        val = e.GetEventObject().GetValue()
        # Set color to 'custom'
        self.colorsCB.SetSelection(4)
        self.config.selectColor(4)
        self.config.us = val

    def On_lvScroll(self, e):
        val = e.GetEventObject().GetValue()
        # Set color to 'custom'
        self.colorsCB.SetSelection(4)
        self.config.selectColor(4)
        self.config.lv = val

    def On_uvScroll(self, e):
        val = e.GetEventObject().GetValue()
        # Set color to 'custom'
        self.colorsCB.SetSelection(4)
        self.config.selectColor(4)
        self.config.uv = val

    def makeMenuBar(self):
        fileMenu = wx.Menu()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)
        instructionsItem = helpMenu.Append(wx.ID_ANY, '&Instructions')

        # Make the menu bar and add the two menus to it
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.OnInstructions, instructionsItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox(constants.aboutText,
                      "About Air Mouse",
                      wx.OK|wx.ICON_INFORMATION)

    def OnInstructions(self, event):
        """Display an About Dialog"""
        wx.MessageBox(constants.helpText,
                        "Air Mouse Instructions",
                        wx.OK|wx.ICON_INFORMATION)

cam_id = 0
cam_list = []
# Get a list of working cameras connected to the device
for i in range(5):
    capture = cv2.VideoCapture(cam_id)
    if (capture and capture.isOpened()):
        cam_list.append(cam_id)
    cam_id += 1

# Select the first working camera by default
if len(cam_list) > 0: capture = cv2.VideoCapture(cam_list[0])
else: capture = None

app = wx.App()
frm = AirMouse(cam_list, capture, None, title='Air Mouse')
frm.Show()
app.MainLoop()
