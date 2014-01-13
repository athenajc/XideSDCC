import wx


#----------------------------------------------------------------------------------
WINDOWS = ('wxMSW' in wx.PlatformInfo)
USE_BUFFER = WINDOWS # use buffered drawing on Windows



#----------------------------------------------------------------------------------
class PinScope(wx.Panel):
    """ Pin Scope View """
    def __init__(self, parent, lst):
        self._buffer = None
        self.back_color = (0, 50, 0)
        self.grid_size = 3
        self.scale = 128

        self.tmin = -1
        self.tmax = -1
        self.time_len = 1000
        self.vlst = lst
        self.enabled = False
        wx.Panel.__init__(self, parent, -1, size=(-1, 40))
        self.SetBackgroundColour(self.back_color)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font.SetWeight(wx.LIGHT)
        
        
    #----------------------------------------------------------------------------
    def OnPaint(self, evt):
        """ """
        if not self.enabled:
            return
        
        if USE_BUFFER:
            # The buffer already contains our drawing, so no need to
            # do anything else but create the buffered DC.  When this
            # method exits and dc is collected then the buffer will be
            # blitted to the paint DC automagically
            self.init_buffer()
            dc = wx.BufferedPaintDC(self, self._buffer)
        else:
            # Otherwise we need to draw our content to the paint DC at
            # this time.
            dc = wx.PaintDC(self)
            self.gc = gc = self.make_gc(dc)
            self.draw(gc)
            
    #----------------------------------------------------------------------------
    def make_gc(self, dc):
        try:
            gc = wx.GraphicsContext.Create(dc)
        except NotImplementedError:
            dc.DrawText("This build of wxPython does not support the wx.GraphicsContext "
                        "family of classes.",
                        25, 25)
            return None
        return gc
    
    #----------------------------------------------------------------------------
    def init_buffer(self):
        """ """
        sz = self.GetClientSize()
        sz.width = max(1, sz.width)
        sz.height = max(1, sz.height)
        self._buffer = wx.EmptyBitmap(sz.width, sz.height, 32)

        dc = wx.MemoryDC(self._buffer)
        dc.SetTextForeground((220,220,220))
        dc.SetBackground(wx.Brush(self.back_color))
        dc.Clear()
        self.gc = gc = self.make_gc(dc)
        self.draw(gc)
                        
    #----------------------------------------------------------------------------
    def draw_grid(self, gc):
        """ Draw background green line grid of scope """
        gc.SetPen(wx.Pen((0,80,0), 1))
        
        sz = self.GetSize()
        w = sz.GetWidth()
        h = sz.GetHeight()

        w1 = self.grid_size * 8
        for x in range(0, w, w1):
            gc.StrokeLine(x, 0, x, h)
        
        gc.SetPen(wx.Pen("green", 1))
        w1 *= 8
        for x in range(0, w, w1):
            gc.StrokeLine(x, 0, x, h)
            
    #----------------------------------------------------------------------------
    def set_scale(self, scale):
        """ Change the view scale of scope """
        self.scale = scale
    
    #----------------------------------------------------------------------------
    def draw_pin_log(self, gc):
        """ Normal play, draw pin log """
        gc.SetPen(wx.Pen("yellow", 2))
        #gc.SetBrush(wx.Brush("black"))
        w = self.GetSize().GetWidth()
        
        prev = 0
        w1 = self.grid_size
        x = w 
        
        # lst of [time_stamp, bit value]
        #self.vlst = [[10,1],[1,0],[1,1],[5,0]]
        scale = self.scale
        for t, t0, bit in self.vlst:
            t1 = t - t0
            
            if bit:
                y = 14
            else:
                y = 34
            
            w2 = (w1 * t1) / scale
            x1 = x - w2
            if x1 < 0:
                x1 = 0

            gc.StrokeLine(x1, y, x, y)
            
            if bit != prev:
                gc.StrokeLine(x, 14, x, 34)
                
            x -= w2
            if x < 0:
                break
            
            prev = bit


    #----------------------------------------------------------------------------
    def draw_pin_log_range(self, gc, tmin, tmax):
        """ User change view range - draw pin log by range """
        # Set line color
        gc.SetPen(wx.Pen("yellow", 2))

        # Get Scope view width
        w = self.GetSize().GetWidth()
        
        # Init prev bit value
        prev = 0
        
        # Get grid size
        w1 = self.grid_size
        
        # Get view scale 
        scale = self.scale
        
        # Caculate x max - right, min - left
        right = (tmax * w1) / scale
        left = (tmin * w1) / scale
        x = right
        
        # Start to draw, from right-most draw to left-most
        # vlst is a list of [time_stamp, bit value]
        for t, t0, bit in self.vlst:
            # Get time offset
            t1 = t - t0
            
            if bit:
                y = 14
            else:
                y = 34
            
            # Get pos offset
            d = (w1 * t1) / scale
            x1 = x - d
            
            if x1 < 0:
                x1 = 0
            gc.StrokeLine(x1, y, x, y)
            
            if bit != prev:
                gc.StrokeLine(x, 14, x, 34)
                
            x -= d
            if x < 0:
                break
            
            prev = bit
        
    #----------------------------------------------------------------------------
    def draw_hex(self, gc):
        """ Draw text in gc """
        gc.SetFont(self.font, "grey")
        w1 = self.grid_size * 8
        x = 4
        for v in self.vlst:
            s = "%02X" % v
            gc.DrawText(s, x, 2)
            x += w1

    #----------------------------------------------------------------------------
    def draw(self, gc):
        """ Call by OnPaint """
        self.draw_grid(gc)
        if self.vlst and self.vlst != []:
            if self.tmax < 0:
                self.draw_pin_log(gc)
            else:
                self.draw_pin_log_range(gc, self.tmin, self.tmax)
            
    #----------------------------------------------------------------------------
    def update(self, scale, tmin, tmax):
        """ Call by sim.step() -> ScopePanelList.update """
        self.scale = scale
        self.tmin = tmin
        self.tmax = tmax
        self.Refresh()
        
    #----------------------------------------------------------------------------
    def get_time_len(self):
        """ Get visible time length """
        self.time_len = (self.GetSize().GetWidth() * self.scale) / self.grid_size
        return self.time_len


#----------------------------------------------------------------------------------
class PinScopePanel(wx.Panel):
    """ Pin Scope Panel, include checkbox and pin config combo and scope view """
    def __init__(self, parent, label, sim, checked):
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Default pin config
        self.pin = label
        
        # Checkbox set pin view enable/disable
        self.cbox = wx.CheckBox(self, -1, "", size=(25, -1), pos=(10, -1))
        self.cbox.Value = checked
        sizer.Add(self.cbox, 0)
        
        # Pin config combobox
        self.combo = wx.ComboBox(self, -1, label, size=(80, 30), choices=sim.pin_out)
        sizer.Add(self.combo, 0)
        
        # Scope view 
        self.scope = PinScope(self, [])
        self.scope.enabled = checked
        sizer.Add(self.scope, 1, wx.EXPAND) 
        
        # Set sizer and layout
        self.SetSizer(sizer)
        sizer.Layout()
        
        # Connect the event 
        self.cbox.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.cbox)
        self.combo.Bind(wx.EVT_COMBOBOX, self.OnSelectPin, self.combo)
    
    #-------------------------------------------------------------------
    def OnCheckBox(self, event):
        """ Set scope view enable or disable """
        self.scope.enabled = self.cbox.Value
    
    #-------------------------------------------------------------------
    def OnSelectPin(self, event):
        """ Event handler of select pin config combobox """
        self.pin = event.GetString()
                
    #-------------------------------------------------------------------
    def update(self, sim, scale, tmin, tmax):
        """ Call by sim.step() -> ScopePanelList.update """
        if self.cbox.Value:
            self.scope.vlst = sim.get_pin_log(self.pin)
            self.scope.update(scale, tmin, tmax)
            
    #-------------------------------------------------------------------
    def get_pin_config(self):
        """ Before sim close, save pin config, called by sim.save_config -> ScopePanelList.get_pin_config -> this """
        return self.pin, str(self.cbox.Value)
        
        
#----------------------------------------------------------------------------------
class ControlPanel(wx.Panel):
    """ Control items to control scope view """
    def __init__(self, parent):
        self.log = None
        wx.Panel.__init__(self, parent, -1)
        
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Time Slider for time searching
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        txt = wx.StaticText(self, -1, "     Time", size=(100, -1))
        sizer1.Add(txt, 0, wx.ALIGN_CENTRE)
        self.time_slider = t = wx.Slider(self, -1, 0, 1, 100, (0, 0), (800, -1),  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        t.SetTickFreq(8, 1)
        t.Bind(wx.EVT_SCROLL_CHANGED, self.OnTimeChanged)
        sizer1.Add(t, 1, wx.EXPAND | wx.GROW | wx.ALIGN_RIGHT)
        sizer.Add(sizer1, 1, wx.EXPAND | wx.GROW)
        
        # Scale Slider for scale setting
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        txt = wx.StaticText(self, -1, "     Scale", size=(100, -1))
        sizer2.Add(txt, 0, wx.ALIGN_CENTRE)
        self.scale_slider = s = wx.Slider(self, -1, 128, 1, 512, (30, 60), (400, -1),  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        s.SetTickFreq(8, 1)
        s.Bind(wx.EVT_SCROLL_CHANGED, self.OnScaleChanged)
        sizer2.Add(s, 0)
        sizer.Add(sizer2, 1, wx.EXPAND | wx.GROW)

        # Set sizer and layout
        self.SetSizer(sizer)
        sizer.Layout()
        
    #--------------------------------------------------------
    def OnScaleChanged(self, evt):
        """ Event handler of scale slider """
        #print('changed: %d' % evt.EventObject.GetValue())
        self.parent.set_scale(evt.EventObject.GetValue())
            
    #--------------------------------------------------------
    def OnTimeChanged(self, evt):
        """ Event handler of time slider """
        #print('changed: %d' % evt.EventObject.GetValue())
        self.parent.set_time(evt.EventObject.GetValue())
        
    #--------------------------------------------------------
    def set_time_stamp(self, max_v):
        """ Set sim time total length, sim.step() -> ScopePanelList update -> this function """
        #self.time_slider.SetValue(value)
        self.time_slider.SetMax(max_v)
        

#----------------------------------------------------------------------------------
class ScopePanelList(wx.Panel):
    """  """
    def __init__(self, parent, sim, pin_configs, pin_checked):

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.sim = sim
        self.sim_frame = parent
        self.scale = 128
        
        # initial scope panel list
        self.scope_lst = []
        if pin_configs == []:
            pins = sim.pins
        else:
            pins = pin_configs
            
        # Create PinScopePanel list and add to sizer
        for i in range(8):
            name = pins[i]

            scope = PinScopePanel(self, name, sim, pin_checked[i])
            sizer.Add(scope, 0, wx.EXPAND, 2)
            self.scope_lst.append(scope)
            
            line = wx.StaticLine(self, -1)
            sizer.Add(line)
        
        self.scope0 = self.scope_lst[0].scope
        
        # Add control panel - with scale, time settings
        self.ctrl = ControlPanel(self)
        sizer.Add(self.ctrl)
        
        # Set sizer and layout
        self.SetSizer(sizer)
        sizer.Layout()

    #-------------------------------------------------------------------
    def update(self, sim):
        """ Call by sim step """
        self.sim = sim
        tlen = self.scope0.get_time_len()
        t = sim.time_stamp - tlen
        if t < 100:
            t = 100
        for obj in self.scope_lst:
            obj.update(sim, self.scale, -1, -1)
            
    #-------------------------------------------------------------------
    def set_scale(self, scale):
        """ User click scale_slider, to change scope view scale """
        #sz = self.scope0.GetSize()
        self.scale = scale
        
        # Update scope drawing
        for obj in self.scope_lst:
            obj.scope.scale = scale
            obj.update(self.sim, scale, -1, -1)
            
    #-------------------------------------------------------------------
    def set_time(self, time):
        """ User click time_slider, forward and backward """
        #sz = self.scope0.GetSize()
        sim = self.sim
        
        # Pause sim 
        self.sim_frame.pause = True
        
        # get visible time length
        tlen = self.scope0.get_time_len()
        t = sim.time_stamp
        if t < 100:
            t = 100
        self.ctrl.set_time_stamp(t)
        
        # time_stamp is latest current time
        ts = sim.time_stamp
        t1 = -time + 1
        t2 = t1 + ts
        
        # Update scope drawing
        scale = self.scale
        for obj in self.scope_lst:
            obj.update(sim, scale, t1, t2)
            
    #-------------------------------------------------------------------
    def get_pin_config(self):
        """ Before sim close, save pin config, called by sim.save_config """
        pin_lst = []
        check_lst = []
        for scope in self.scope_lst:
            pin, checked = scope.get_pin_config()
            pin_lst.append(pin)
            check_lst.append(checked)
            
        return pin_lst, check_lst