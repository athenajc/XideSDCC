import wx

BIT0 = 1
BIT1 = 2
BIT2 = 4
BIT3 = 8
BIT4 = 0x10
BIT5 = 0x20
BIT6 = 0x40
BIT7 = 0x80
#----------------------------------------------------------------------------------
WINDOWS = ('wxMSW' in wx.PlatformInfo)
USE_BUFFER = WINDOWS # use buffered drawing on Windows


#----------------------------------------------------------------------------------
class PinScope(wx.Panel):
    def __init__(self, parent, lst):
        self._buffer = None
        self.back_color = (0, 50, 0)
        self.grid_size = 10
        self.vlst = lst
        wx.Panel.__init__(self, parent, -1, size=(-1, 40))
        self.SetBackgroundColour(self.back_color)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font.SetWeight(wx.LIGHT)
        
        
    #----------------------------------------------------------------------------
    def OnPaint(self, evt):
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
        sz = self.GetClientSize()
        sz.width = max(1, sz.width)
        sz.height = max(1, sz.height)
        self._buffer = wx.EmptyBitmap(sz.width, sz.height, 32)

        dc = wx.MemoryDC(self._buffer)
        dc.SetTextForeground((220,220,220))
        dc.SetBackground(self.back_color)
        dc.Clear()
        self.gc = gc = self.make_gc(dc)
        self.draw(gc)
                        
    #----------------------------------------------------------------------------
    def draw_grid(self, gc):
        gc.SetPen(wx.Pen((0,80,0), 1))
        
        sz = self.GetSize()
        w = sz.GetWidth()
        h = sz.GetHeight()
        begins = []
        ends = []
        w1 = self.grid_size
        for x in range(0, w, w1):
            begins.append((x, 0))
            ends.append((x, h))
            
        gc.StrokeLineSegments(begins, ends)
        
        gc.SetPen(wx.Pen("green", 1))
        begins = []
        ends = []
        w1 = self.grid_size
        for x in range(0, w, w1*8):
            begins.append((x, 0))
            ends.append((x, h))
            
        gc.StrokeLineSegments(begins, ends)
    
    #----------------------------------------------------------------------------
    def draw_pin_log(self, gc):
        gc.SetPen(wx.Pen("yellow", 2))
        #gc.SetBrush(wx.Brush("black"))
        sz = self.GetSize()
        w = sz.GetWidth()
        h = sz.GetHeight()
        begins = []
        ends = []
        x = 0
        prev = 0
        w1 = self.grid_size
        for v in self.vlst:
            s = "%02X" % v
            gc.DrawText(s, x, 20)
            for i in range(7, -1, -1):
                bit = (v >> i) & 1
                if bit:
                    y = 14
                else:
                    y = 34
                begins.append((x, y))
                ends.append((x + w1, y))
                
                if bit != prev:
                    begins.append((x, 14))
                    ends.append((x, 34))
                    
                x += w1
                prev = bit
            
        gc.StrokeLineSegments(begins, ends)   
        

    #----------------------------------------------------------------------------
    def draw(self, gc):
        self.draw_grid(gc)
        self.draw_pin_log(gc)
        
        gc.SetFont(self.font, "grey")
        w1 = self.grid_size * 8
        x = 4
        for v in self.vlst:
            s = "%02X" % v
            gc.DrawText(s, x, 2)
            x += w1


#----------------------------------------------------------------------------------
class PinScopePanel(wx.Panel):
    def __init__(self, parent, label, lst):
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.cb_target = wx.CheckBox(self, -1, label, size=(80, 40))
        sizer.Add(self.cb_target, 0)
        scope = PinScope(self, lst)
        sizer.Add(scope, 1, wx.EXPAND) 
        
        self.SetSizer(sizer)
        sizer.Layout()
        
        
#----------------------------------------------------------------------------------
class TestPanel(wx.Panel):
    def __init__(self, parent, sim):
        self.log = None
        wx.Panel.__init__(self, parent, -1)
        
        self.scope_lst = []
        sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(8):
            name = 'RB' + str(i)
            scope = PinScopePanel(self, name, sim.get_pin_log(name))
            sizer.Add(scope, 0, wx.EXPAND, 2)
            self.scope_lst.append(scope)
            
            line = wx.StaticLine(self, -1)
            sizer.Add(line)
                    
        self.SetSizer(sizer)
        sizer.Layout()

