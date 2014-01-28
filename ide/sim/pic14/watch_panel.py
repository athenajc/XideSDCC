import wx
from utils import tohex, get_sfr_addr

#----------------------------------------------------------------------------------
WINDOWS = ('wxMSW' in wx.PlatformInfo)
USE_BUFFER = WINDOWS # use buffered drawing on Windows


#---------------------------------------------------------------------------
class StaticLine(wx.StaticLine):
    def __init__(self, parent, sizer):
        wx.StaticLine.__init__(self, parent, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(self, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
#---------------------------------------------------------------------------------------------------
class WatchPane(wx.CollapsiblePane):
    def __init__(self, parent, parent_sizer, title):
        self.sim = None
        self.parent = parent
        self.title = title
        self.label1 = "Click here to Show " + title
        self.label2 = "Click here to Hide " + title
        
        wx.CollapsiblePane.__init__(self, parent, label=self.label1,
                                          style=wx.CP_DEFAULT_STYLE |wx.CP_NO_TLW_RESIZE)
        #self.cp = cp = wx.CollapsiblePane(parent, label=self.label1,
        #                                  style=wx.CP_DEFAULT_STYLE |wx.CP_NO_TLW_RESIZE)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, self)

        parent_sizer.Add(self, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def expand(self):
        s = self.parent.get_setting(self.title)
        if s == "":
            self.Expand()
            self.parent.set_setting(self.title, True)
        elif s == "True":
            self.Expand()
        else:
            self.Collapse()
            
    #------------------------------------------------------------------------
    def OnPaneChanged(self, evt=None):
        # redo the layout
        self.parent.Layout()

        # and also change the labels
        if self.IsExpanded():
            self.SetLabel(self.label2)
            self.parent.set_setting(self.title, True)
        else:
            self.SetLabel(self.label1)
            self.parent.set_setting(self.title, False)


#----------------------------------------------------------------------------------
class Led(wx.Panel):
    def __init__(self, parent, value):
        self.d = 5
        self.w = 40
        self._buffer = None
        self.path_v = self.path_h = None
        self.value = value
        wx.Panel.__init__(self, parent, -1, size=(120, 200))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        #if USE_BUFFER:
            #self.Bind(wx.EVT_SIZE, self.OnSize)
            
        #self.Bind(wx.EVT_ERASE_BACKGROUND, self.onErase)
        
        
    #def onErase(self, event):
        #pass
        
    ##----------------------------------------------------------------------------
    #def OnSize(self, evt):
        #self.init_buffer()
        #evt.Skip()
        
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
    def init_path(self):
        gc = self.gc
        # make a path that contains a circle and some lines, centered at 0,0
        path = gc.CreatePath()
        d = self.d
        w = self.w
        d2 = d * 2
        path.MoveToPoint(0, d)
        path.AddLineToPoint(d, 0)
        path.AddLineToPoint(w + d, 0)
        path.AddLineToPoint(w + d2, d)
        path.AddLineToPoint(w + d, d2)
        path.AddLineToPoint(d, d2)
        path.AddLineToPoint(0, d)
        
        path_v = gc.CreatePath()
        path_v.MoveToPoint(0, d)
        path_v.AddLineToPoint(d, 0)
        path_v.AddLineToPoint(d2, d)
        path_v.AddLineToPoint(d2, w + d)
        path_v.AddLineToPoint(d, w + d2)
        path_v.AddLineToPoint(0, w + d)
        path_v.AddLineToPoint(0, d)
        
        self.path_h = path
        self.path_v = path_v
        
    #----------------------------------------------------------------------------
    def init_buffer(self):
        sz = self.GetClientSize()
        sz.width = max(1, sz.width)
        sz.height = max(1, sz.height)
        self._buffer = wx.EmptyBitmap(sz.width, sz.height, 32)

        dc = wx.MemoryDC(self._buffer)
        dc.SetTextForeground((220,220,220))
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
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
    def draw_led_pin(self, label, x, y, path, fill):
        gc = self.gc
        gc.PushState()
        gc.Translate(x, y)
        if not fill:
            self.gc.StrokePath(path)
            if path == self.path_v:
                gc.DrawText(label, 2, 20)
            else:
                gc.DrawText(label, 20, -1)
        else:
            self.gc.DrawPath(path)

        gc.PopState()
        
    #----------------------------------------------------------------------------
    def draw_led(self, x, y, value):
        gc = self.gc
        if self.path_h == None:
            self.init_path()
        gc.SetPen(wx.Pen("grey", 1))
        gc.SetBrush(wx.Brush("red"))
        
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.LIGHT)
        gc.SetFont(font, "grey")
        
        gc.PushState()
        d = self.d
        d2 = d + d
        w = self.w + d2
        path_h = self.path_h
        path_v = self.path_v
        gc.Translate(x, y)
        self.draw_led_pin('a', d + 2, 0, path_h, value & 1)        #A
        self.draw_led_pin('b', w + 4, d + 1, path_v, value & 0x2)  #B
        self.draw_led_pin('c', w + 4, w + d + 3, path_v, value & 0x4)  #C
        self.draw_led_pin('d', d + 2, w * 2 + 4, path_h, value & 0x8)  #D
        self.draw_led_pin('e', 0, w + d + 3, path_v, value & 0x10)     #E
        self.draw_led_pin('f', 0, d + 1, path_v, value & 0x20)      #F
        self.draw_led_pin('g', d + 2, w + 2, path_h, value & 0x40)  #G
        gc.PopState()
        
    #----------------------------------------------------------------------------
    def test(self):
        gc = self.gc
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        gc.SetFont(font)
        led_lst = [0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6D, 0x7D, 0x07, 0x7f, 0x6f]
        w1 = 100
        for i in range(10):
            x = w1 * i + 20
            self.draw_led(x, 20, led_lst[i])
            
    #----------------------------------------------------------------------------
    def draw(self, gc):
        self.draw_led(20, 20, self.value)
        
    #----------------------------------------------------------------------------
    def set_value(self, value):
        self.value = value
        self.Refresh(eraseBackground = True)
        
        
#---------------------------------------------------------------------------
class ComboBox(wx.ComboBox):
    """ usage : cbox = ComboBox(parent, sizer, "label", ['item a', 'bbb', 'c'] """
    def __init__(self, parent, sizer, label, lst, flag = wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL):
        wx.ComboBox.__init__(self, parent, pos=(150, 90), size=(95, -1), choices=lst, style=wx.CB_DROPDOWN)
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label, size=(10, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT, 5)
        box.Add(self, 0, wx.ALIGN_CENTRE|wx.ALL, 0)
        
        if sizer:
            sizer.Add(box, 0, flag, 0)
            

#---------------------------------------------------------------------------------------------------
class WatchLed(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "LED")
                    
        panel = self.GetPane() #wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.led = Led(panel, 0x00)
        
        # default select PortA RA0 - RA7
        self.select_port = parent.settings["led_port"]
        if self.select_port == "None":
            self.select_port = None
        
        cb_sizer = wx.BoxSizer(wx.VERTICAL)
        pins = ['RA0','RA1','RA2','RA3','RA4','RA5','RA6','RA7',
                        'RB0','RB1','RB2','RB3','RB4','RB5','RB6','RB7',
                        'RC0','RC1','RC2','RC3','RC4','RC5','RC6','RC7',]
        self.cb_lst = [None] * 7
        s = ["a", "b", "c", "d", "e", "f", "g"]
        for i in range(7):
            self.cb_lst[i] = cb = ComboBox(panel, cb_sizer, s[i], pins)
            #cb.SetValue(pins[i])
            cb.SetValue(parent.settings["led_p" + str(i)])
            if i == 0:
                cb.Bind(wx.EVT_COMBOBOX, self.OnSelectPin0)
            else:
                cb.Bind(wx.EVT_COMBOBOX, self.OnSelectPin)
        
        sizer.Add(self.led, 0, wx.EXPAND)
        sizer.Add(cb_sizer, 0, wx.EXPAND)
        
        panel.SetSizer(sizer)
        panel.Layout()
        
        self.expand()
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        port = self.select_port
        if port:
            self.led.set_value(sim.get_reg(port))
        else:
            v = 0
            a = sim.get_reg("PORTA")
            b = sim.get_reg("PORTB")
            c = sim.get_reg("PORTC")
            for i in range(0,7):
                s = self.cb_lst[i].GetValue() 
                s2 = s[1:2]
                pin = int(s[2:3])
                if s2 == "A":
                    bit = (a >> pin) & 1
                elif s2 == "B":
                    bit = (b >> pin) & 1
                elif s2 == "C":
                    bit = (c >> pin) & 1
                v |= bit << i
            self.led.set_value(v)
                
    #----------------------------------------------------------------------------
    def set_value(self, value):
        self.led.set_value(value)
        
    #----------------------------------------------------------------------------
    def update_select_pins(self):
        self.parent.set_setting('led_port', self.select_port)
        for i in range(0,7):
            s = self.cb_lst[i].GetValue()
            self.parent.set_setting('led_p' + str(i), s)
            
    #--------------------------------------------------------------
    def OnSelectPin0(self, event):
        key = self.cb_lst[0].GetValue()
        if key == 'RA0':
            self.select_port = "PORTA"
            for i in range(1,7):
                self.cb_lst[i].SetValue("RA" + str(i))
        elif key == 'RB0':
            self.select_port = "PORTB"
            for i in range(1,7):
                self.cb_lst[i].SetValue("RB" + str(i))
        elif key == 'RC0':
            self.select_port = "PORTC"
            for i in range(1,7):
                self.cb_lst[i].SetValue("RC" + str(i))
        else:
            self.select_port = None
        self.update_select_pins()
                
    #--------------------------------------------------------------
    def OnSelectPin(self, event):
        print event.GetString()
        #key = self.cb_lst[0].GetValue()
        self.select_port = None
        self.update_select_pins()
        
        
#---------------------------------------------------------------------------
class LabelTextCtrl(wx.TextCtrl):
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, size=(-1,-1)):
        wx.TextCtrl.__init__(self, parent, -1, "", size = size)
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label_str, style=wx.ALIGN_RIGHT)
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        
        text = self
        text.SetValue(default_str)
        text.SetHelpText(help_str)
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.RIGHT, 1)

        sizer.Add(box, 0, flag, 0)
        
    def set_value(self, v, n):
        self.SetValue(tohex(v, n))
        if v == 0:
            self.SetBackgroundColour((185,185,185))
        else:
            self.SetBackgroundColour((235,235,235))


#---------------------------------------------------------------------------------------------------
class SfrTextCtrlList(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "SFR Viewer")
                    
        panel = self.GetPane() 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.pc_text = LabelTextCtrl(panel, sizer1, 'PC ', '', '00', size=(50, -1))
        self.wreg_text = LabelTextCtrl(panel, sizer1, '  W ', '', '00', size=(30, -1))
        self.freg_text = LabelTextCtrl(panel, sizer1, '  F ', '', '00', size=(30, -1))
        self.c_text = LabelTextCtrl(panel, sizer1, ' C ', '', '0', size=(18, -1))
        self.z_text = LabelTextCtrl(panel, sizer1, ' Z ', '', '0', size=(18, -1))
        sizer.Add(sizer1)
        
        StaticLine(panel, sizer)
        
        self.s_text = PortTextCtrl(panel, sizer, 'STATUS', '', '00', size=(30, -1))
               
        panel.SetSizer(sizer)
        panel.Layout()
        self.expand()

        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        self.pc_text.set_value(sim.get_reg('PC'), 4)
        self.wreg_text.set_value(sim.get_reg('W'), 2)
        self.freg_text.set_value(sim.get_reg('F'), 2)
        
        status = sim.get_reg('STATUS')
        c = status & 1
        z = (status >> 2) & 1
        self.freg_text.set_value(sim.get_reg('C'), 1)
        self.freg_text.set_value(sim.get_reg('Z'), 1)
        
        self.s_text.set_value(sim.get_reg('STATUS'))
        
        

#---------------------------------------------------------------------------
class SpinTextCtrl():
    def __init__(self, panel, sizer, default_addr, default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, size=(-1,-1)):
        
        self.parent = panel.parent
        self.addr = default_addr
        self.addr_str = ""
        box = wx.BoxSizer(wx.HORIZONTAL)
        
        txt = self.addr_text = wx.TextCtrl(panel, -1, "1", (30, 50), (60, -1))
        h = txt.GetSize().height
        w = txt.GetSize().width + txt.GetPosition().x + 2
        self.set_addr(default_addr)
        
        self.spin = wx.SpinButton(panel, -1, (w, 50), (h*2/3, h),  wx.SP_VERTICAL)
        self.spin.SetRange(1, 512)
        self.spin.SetValue(default_addr)

        box.Add(txt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        box.Add(self.spin, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        
        self.text = wx.TextCtrl(panel, -1, default_str, size = size)

        box.Add(self.text, 0, wx.ALIGN_CENTRE|wx.RIGHT, 1)
        
        self.bit_text_list = []
        c = panel.GetBackgroundColour()
        for i in range(8):
            t = wx.TextCtrl(panel, -1, "0", size=(20, -1),style=wx.BORDER_STATIC|wx.ALIGN_CENTER|wx.TE_PASSWORD)
            t.SetBackgroundColour(c)
            self.bit_text_list.append(t)
            box.Add(t, 0, wx.ALIGN_CENTRE, 1)
            
        self.btn = wx.Button(panel, -1, '-', size=(20,20))
        box.Add(self.btn, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        
        sizer.Add(box, 0, flag, 0)
        self.sizer = box
        
        # Bind Event
        self.spin.Bind(wx.EVT_SPIN, self.OnSpin, self.spin)
        self.addr_text.Bind(wx.EVT_TEXT, self.OnAddrText, self.addr_text)
        self.btn.Bind(wx.EVT_BUTTON, self.OnRemoveButton, self.btn)
        
    #------------------------------------------------------------------------
    def OnRemoveButton(self, event):
        self.sizer.Remove(self.spin)
        self.sizer.Remove(self.addr_text)
        self.sizer.Remove(self.btn)
        self.sizer.Remove(self.text)
        self.spin.Destroy()
        self.addr_text.Destroy()
        self.btn.Destroy()
        self.text.Destroy()
        for t in self.bit_text_list:
            self.sizer.Remove(t)
            t.Destroy()
 
        self.parent.remove_view(self)
        
    #------------------------------------------------------------------------
    def OnSpin(self, event):
        self.set_addr(event.GetPosition())
        
    #------------------------------------------------------------------------
    def OnAddrText(self, event):
        s = event.GetString()
        if self.addr_str == s:
            return
        pos = self.addr_text.GetInsertionPoint() + 1
        
        s = s.lower()
        s = s[:pos] + s[(pos+1):]
        s = s.replace("0x", "")
        lst = ["0x0"]
        i = 0
        for c in s:
            if c in "0123456789abcdef":
                lst.append(c)
                i += 1
                if i > 2:
                    break
                
        s = "".join(lst)
        addr = int(s, 16)
        self.spin.SetValue(addr)
        self.set_addr(addr)
        
    #------------------------------------------------------------------------
    def set_addr(self, a):
        self.addr = a
        s = "0x%03X" % (a)
        self.addr_str = s
        self.addr_text.SetValue(s)
        self.parent.spin_change_addr()
                
    #------------------------------------------------------------------------
    def set_value(self, v):
        self.text.SetValue(tohex(v, 2))
        c = [(180, 180, 180), (255, 255, 100)]
        for i in range(8):
            b = (v >> (7 - i)) & 1
            t = self.bit_text_list[i]
            t.SetValue(str(b))
            t.SetBackgroundColour(c[b])
            
    #------------------------------------------------------------------------
    def update(self, sim):
        if self.addr < 512:
            v = sim.mem[self.addr]
            self.set_value(v)
        else:
            self.set_value(0xff)
            
            
#---------------------------------------------------------------------------------------------------
class MemTextCtrlList(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "Memory Viewer")
        self.parent = parent
        panel = self.GetPane() 
        panel.parent = self
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = sizer
        self.panel = panel
        
        StaticLine(panel, sizer)
        
        self.plst = []
        
        s = parent.get_setting('mem_view_count')
        if s == "":
            n = 4
        else:
            n = int(s)
            
        for i in range(n):
            self.add_view(i)
            
        self.btn = wx.Button(panel, -1, '+', size=(25,25))
        sizer.Add(self.btn, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        
        panel.SetSizer(sizer)
        panel.Layout()
        self.expand()
        
        self.btn.Bind(wx.EVT_BUTTON, self.OnAddButton, self.btn)
        
    #------------------------------------------------------------------------
    def OnAddButton(self, event):
        i = len(self.plst)
        self.Collapse()
        self.sizer.Remove(self.btn)
        self.add_view(i)
        self.sizer.Add(self.btn, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        self.panel.Layout()
        self.Expand()
        self.parent.set_setting('mem_view_count', len(self.plst))
        
    #------------------------------------------------------------------------
    def add_view(self, i):
        s = self.parent.get_setting("p" + str(i) + "_addr")
        if s != "":
            v = int(s, 16)
        else:
            v = 0x12C + i
        p = SpinTextCtrl(self.panel, self.sizer, v, '00', size=(30, -1))
        self.plst.append(p)
        
    #------------------------------------------------------------------------
    def remove_view(self, obj):
        self.Collapse()
        self.sizer.Remove(obj.sizer)
        self.plst.remove(obj)
        self.panel.Layout()
        self.Expand()
        self.parent.set_setting('mem_view_count', len(self.plst))
        self.spin_change_addr()
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        for p in self.plst:
            p.update(sim)
            
    #------------------------------------------------------------------------
    def spin_change_addr(self):
        i = 0
        for p in self.plst:
            self.parent.set_setting("p" + str(i) + "_addr", p.addr_str)
            i += 1
        
        
#---------------------------------------------------------------------------
class PortTextCtrl():
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, size=(-1,-1)):
        
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label_str, style=wx.ALIGN_RIGHT)
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        
        self.text = wx.TextCtrl(parent, -1, default_str, size = size)
        self.text.SetValue(default_str)
        self.text.SetHelpText(help_str)
        box.Add(self.text, 0, wx.ALIGN_CENTRE|wx.RIGHT, 1)
        
        self.bit_text_list = []
        c = parent.GetBackgroundColour()
        for i in range(8):
            t = wx.TextCtrl(parent, -1, "0", size=(20, -1),style=wx.BORDER_STATIC|wx.ALIGN_CENTER)
            t.SetBackgroundColour(c)
            self.bit_text_list.append(t)
            box.Add(t, 0, wx.ALIGN_CENTRE, 1)

        sizer.Add(box, 0, flag, 0)
        
    #------------------------------------------------------------------------
    def set_value(self, v):
        self.text.SetValue(tohex(v, 2))
        c = [(180, 180, 180), (255, 255, 100)]
        for i in range(8):
            b = (v >> (7 - i)) & 1
            t = self.bit_text_list[i]
            t.SetValue(str(b))
            t.SetBackgroundColour(c[b])
        

#---------------------------------------------------------------------------------------------------
class PortTextCtrlList(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "Port Data")
        
        panel = self.GetPane()
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.p0_text = PortTextCtrl(panel, sizer, 'PORTA ', '', '00', size=(30, -1))
        self.p1_text = PortTextCtrl(panel, sizer, 'PORTB ', '', '00', size=(30, -1))
        
        if parent.with_portc:
            self.with_portc = True
            self.p2_text = PortTextCtrl(panel, sizer, 'PORTC ', '', '00', size=(30, -1))
        else:
            self.with_portc = False
            
        panel.SetSizer(sizer)
        panel.Layout()
        self.expand()

    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        
        self.p0_text.set_value(sim.get_reg('PORTA'))
        self.p1_text.set_value(sim.get_reg('PORTB'))
        if self.with_portc :
            self.p2_text.set_value(sim.get_reg('PORTC'))
              


#---------------------------------------------------------------------------
class TrisCtrl():
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, size=(-1,-1)):
        
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label_str, style=wx.ALIGN_RIGHT)
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        
        self.text = wx.TextCtrl(parent, -1, default_str, size = size)
        self.text.SetValue(default_str)
        self.text.SetHelpText(help_str)
        box.Add(self.text, 0, wx.ALIGN_CENTRE|wx.RIGHT, 1)
        
        self.bit_obj_list = []
        c = parent.GetBackgroundColour()
        for i in range(8):
            t = wx.CheckBox(parent, -1, size=(20, -1))
            self.bit_obj_list.append(t)
            box.Add(t, 0, wx.ALIGN_CENTRE, 0)

        sizer.Add(box, 0, flag, 0)
        self.value = None
        
    #------------------------------------------------------------------------
    def set_value(self, v):
        if self.value == v:
            return
        
        self.text.SetValue(tohex(v, 2))
        c = [(180, 180, 180), (255, 255, 100)]
        for i in range(8):
            b = (v >> (7 - i)) & 1
            t = self.bit_obj_list[i]
            t.SetValue(b)
            #t.SetBackgroundColour(c[b])
            
        self.value = v


#---------------------------------------------------------------------------------------------------
class TrisTextCtrlList(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "Tris Data")
        
        panel = self.GetPane()
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.t0_text = TrisCtrl(panel, sizer, 'TRISA ', '', '00', size=(30, -1))
        self.t1_text = TrisCtrl(panel, sizer, 'TRISB ', '', '00', size=(30, -1))
        if parent.with_portc:
            self.with_portc = True        
            self.t2_text = TrisCtrl(panel, sizer, 'TRISC ', '', '00', size=(30, -1))     
        else:
            self.with_portc = False
        
        panel.SetSizer(sizer)
        panel.Layout()
        self.expand()

    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        
        self.t0_text.set_value(sim.get_reg('TRISA'))
        self.t1_text.set_value(sim.get_reg('TRISB'))
        if self.with_portc:
            self.t2_text.set_value(sim.get_reg('TRISC'))
        
        
#---------------------------------------------------------------------------------------------------
class InputCtrlList(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "Input Button")
        
        panel = self.GetPane()

        sizer = wx.BoxSizer(wx.VERTICAL)

        b_sizer1 = wx.BoxSizer(wx.HORIZONTAL) 
        pins = ['RA0','RA1','RA2','RA3','RA4','RA5','RA6','RA7',
                'RB0','RB1','RB2','RB3','RB4','RB5','RB6','RB7',
                'RC0','RC1','RC2','RC3','RC4','RC5','RC6','RC7',]
        parent.cb_int0 = cb_int0 = wx.ComboBox(panel, -1, value='RA4', pos=(-1,-1), size=(100, -1), choices=pins, style=wx.CB_DROPDOWN)
        parent.bn_int0 = bn_int0 = wx.Button(panel, 1, 'RA4')
        b_sizer1.Add(cb_int0, 1, wx.ALL, 0)
        b_sizer1.Add(bn_int0, 1, wx.ALL, 0)
        
        bn_int1 = wx.Button(panel, 2, 'INT')
        sizer.Add(b_sizer1, 1, wx.ALL, 2)
        sizer.Add(bn_int1, 1, wx.ALL, 2)
        
        parent.uart_input = wx.TextCtrl(panel, -1, "")
        sizer.Add(parent.uart_input, 1, wx.ALL|wx.EXPAND|wx.GROW, 2)
        
        cb_int0.Bind(wx.EVT_COMBOBOX, parent.OnSelectInt0, cb_int0)

        bn_int0.Bind(wx.EVT_LEFT_DOWN, parent.OnInt0Down, bn_int0)
        bn_int0.Bind(wx.EVT_LEFT_UP, parent.OnInt0Up, bn_int0)
        bn_int1.Bind(wx.EVT_BUTTON, parent.OnInt1, bn_int1)
        
        parent.uart_input.Bind(wx.EVT_TEXT, parent.OnEvtText, parent.uart_input)
        
        panel.SetSizer(sizer)
        panel.Layout()

        self.expand()


##---------------------------------------------------------------------------------------------------
#class MemWatcher(WatchPane):
    #def __init__(self, parent, parent_sizer):
        #WatchPane.__init__(self, parent, parent_sizer, "Memory Watcher")
        #panel = self.GetPane()

        #sizer = wx.BoxSizer(wx.VERTICAL)
        #panel.SetMinSize(wx.Size(300,100))
        #self.text = wx.TextCtrl(panel, -1, style = wx.TE_MULTILINE|wx.HSCROLL)
        #if wx.Platform == '__WXMSW__':
            #font_name = u'Courier New'
        #else:
            #font_name = u'Courier 10 Pitch'
        #font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, font_name)
        #self.text.SetFont(font1)
        #self.text.SetMinSize(wx.Size(300,400))
        #sizer.Add(self.text, 1, wx.ALL|wx.EXPAND|wx.GROW, 2)
        
        #panel.SetSizer(sizer)
        #panel.Layout()

        #self.expand()
        
    ##------------------------------------------------------------------------
    #def update(self, sim):
        #lst = []
        #lst.append("ADDR HEX INT     BIN")
            
        #for a in range(0x200):
            #v = a #sim.mem[a]
            #lst.append('%04x  %02x %03d  %s' % (a, v, v, bin(v)))
       
        #s = '\n'.join(lst)
        #self.text.SetValue(s)
                
                
#---------------------------------------------------------------------------------------------------
class UartWatcher(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "Uart Watcher")
        panel = self.GetPane()

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetMinSize(wx.Size(300,100))
        self.text = wx.TextCtrl(panel, -1, style = wx.TE_MULTILINE|wx.HSCROLL)

        self.text.SetMinSize(wx.Size(300,100))
        sizer.Add(self.text, 1, wx.ALL|wx.EXPAND|wx.GROW, 2)
        
        panel.SetSizer(sizer)
        panel.Layout()
        
        self.expand()
        
    #------------------------------------------------------------------------
    def update_inst(self, sim, sbuf):
        lst = []
        #lst.append("file = " + sim.c_file)
        lst.append("line = %d\n" % sim.c_line) 
        lst.append(str(sbuf))
        s1 = ''.join(chr(i) for i in sbuf)
        lst.append(s1)
               
        s = '\n'.join(lst)
        self.text.SetValue(s)
        
        
#---------------------------------------------------------------------------------------------------
class MemViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,200), style = wx.TAB_TRAVERSAL)
                
        self.SetMinSize(wx.Size(300,100))
        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Memory Viewer"), wx.VERTICAL)

        self.text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.HSCROLL)
        if wx.Platform == '__WXMSW__':
            font_name = u'Courier New'
        else:
            font_name = u'Courier 10 Pitch'
        font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, font_name)
        self.text.SetFont(font1)
        
        sbSizer1.Add(self.text, 1, wx.EXPAND, 5)
        self.SetSizer(sbSizer1)
        sbSizer1.Layout()
        
    #------------------------------------------------------------------------
    def update(self, sim):
        lst = []
        #lst.append("File = " + sim.c_file)
        #lst.append("Line = %d\n" % sim.c_line) 
        
        if sim.debug:
            bins = sim.bins
            m = sim.mem
            status = sim.get_reg('STATUS')
            bank = (status >> 5) & 3
            lst.append(' Bank   %d' % (bank))
            #lst.append(' Status %s\n' % (bins[status]))
            #c =  status & 1
            #z =  (status >> 2) & 1
            #dc = (status >> 1) & 1
            #lst.append(' Status bit 0 C  %X' % (c))
            #lst.append(' Status bit 1 DC %X' % (dc))
            #lst.append(' Status bit 2 Z  %X' % (z))
            sim.mem_access_list.sort()
            for a in sim.mem_access_list:
                v = m[a]
                
                if v < 256:
                    s = bins[v]
                else:
                    s = bin(v)
                    
                sfr = sim.sfr_name[a]
                if sfr == "":
                    lst.append(' %03X = %02X' % (a, v))
                else:
                    lst.append(' %03X = %02X %s' % (a, v, sfr))
                            
        s = '\n'.join(lst)
        self.text.SetValue(s)
        

#---------------------------------------------------------------------------------------------------
class WatchPanel (wx.Panel):
    
    def __init__(self, parent, mcu_name, mcu_device, config_file):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(500,300), style = wx.TAB_TRAVERSAL)
        
        self.sim = None
        self.frame = parent.frame
        self.mcu_name = mcu_name
        self.mcu_device = mcu_device
        self.sfr_addr = get_sfr_addr(mcu_device)
        if self.sfr_addr.get('PORTC', None) != None:
            self.with_portc = True
        else:
            self.with_portc = False
            
        self.config_file = config_file
        self.settings = {
            'led_port':'PORTA',
            'led_p0':'RA0',
            'led_p1':'RA1',
            'led_p2':'RA2',
            'led_p3':'RA3',
            'led_p4':'RA4',
            'led_p5':'RA5',
            'led_p6':'RA6',
            'led_p7':'RA7',
        }
        self.load_config()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.sfr_view = SfrTextCtrlList(self, sizer)

        self.port_panel = PortTextCtrlList(self, sizer)
        self.tris_panel = TrisTextCtrlList(self, sizer)
        self.mem_bin_view = MemTextCtrlList(self, sizer)
        
        self.watch_led = WatchLed(self, sizer)
        self.input_pane = InputCtrlList(self, sizer)
        self.uart_watch = UartWatcher(self, sizer)
        
        self.mem_view = MemViewer(self)
                
        sizer.Add(self.mem_view, 1, wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.Layout()
        
    #-------------------------------------------------------------------
    def get_setting(self, k):
        if k.find(' ') >= 0:
            k = k.replace(' ', '_')
        v = self.settings.get(k, "")
        return v
        
    #-------------------------------------------------------------------
    def set_setting(self, k, v):
        if k.find(' ') >= 0:
            k = k.replace(' ', '_')
        self.settings[k] = str(v)
        
    #-------------------------------------------------------------------
    def save_config(self):
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)
                
        lst = self.settings.keys()
        s = ";".join(lst)
        config.Write("pic14_watch_settings", s)
        for k, v in self.settings.items():
            config.Write(k, str(v))
        
        del config

    #-------------------------------------------------------------------
    def load_config(self):
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)
        
        settings = config.Read("pic14_watch_settings", "")
        if settings != "":
            for k in settings.split(";"):
                self.settings[k] = config.Read(k, "")

        del config

    #--------------------------------------------------------------
    def OnSelectInt0(self, event):
        if self.sim:
            key = self.cb_int0.GetValue()
            self.bn_int0.SetLabel(key)
            
    #--------------------------------------------------------------
    def OnInt0Down(self, event):
        if self.sim:
            key = self.cb_int0.GetValue()
            self.sim.set_input(key, 1)
        event.Skip()
        
    #--------------------------------------------------------------
    def OnInt0Up(self, event):
        if self.sim:
            key = self.cb_int0.GetValue()
            self.sim.set_input(key, 0)
        event.Skip()
            
    #--------------------------------------------------------------
    def OnInt1(self, event):
        if self.sim:
            self.sim.set_input('INT', 1)
            self.sim.set_input('INT', 0)
            
    #--------------------------------------------------------------
    def OnEvtText(self, event):
        s = event.GetString()
        if s == "":
            return
        
        self.frame.log('EvtText: %s\n' % s)
        if self.sim:
            n = len(s)
            c = s[n-1:n]
            if c != '':
                #print c, hex(ord(c))
                self.sim.set_input('uart', ord(c))
                
    #------------------------------------------------------------------------
    def get_sim(self):
        return self.sim

    #------------------------------------------------------------------------
    def update(self, sim):
        if self.sim == None:
            self.sim = sim
        self.sfr_view.update(sim)
        self.mem_bin_view.update(sim)
        self.port_panel.update(sim)
        self.tris_panel.update(sim)
        self.watch_led.update(sim)
        self.mem_view.update(sim)
        
    #------------------------------------------------------------------------
    def update_inst(self, sim, sbuf): 
        #print 'update_inst ', sim.c_line
        self.uart_watch.update_inst(sim, sbuf)
        
    #------------------------------------------------------------------------
    def OnIdle(self, event):
        self.splitter.SetSashPosition(0)
        self.splitter.Unbind(wx.EVT_IDLE)
        
    #------------------------------------------------------------------------
    def __del__(self):
        self.save_config()
        pass
    




#class TestPanel(wx.Panel):
    #def __init__(self, parent):
        #self.log = None
        #wx.Panel.__init__(self, parent, -1)
        #title = wx.Button(self, label="wx.CollapsiblePane")
        
        #title.Bind(wx.EVT_BUTTON, self.OnClickTitle, title)
        #self.cp = cp = wx.CollapsiblePane(self, label=label1,
                                          #style=wx.CP_DEFAULT_STYLE |wx.CP_NO_TLW_RESIZE)
        #self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
        #self.MakePaneContent(cp.GetPane())
        ##p = cp.GetPane()
        ##p.frame = parent
        ##WatchPanel(p, "PIC14", "pic16f883")
        #sizer = wx.BoxSizer(wx.VERTICAL)
        #self.SetSizer(sizer)
        #sizer.Add(title, 0, wx.ALL|wx.EXPAND, 0)
        #sizer.Add(cp, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 25)
        
    #def OnClickTitle(self, evt):
        #self.cp.Collapse(self.cp.IsExpanded())
        #self.OnPaneChanged()        
        
    #def OnToggle(self, evt):
        #self.cp.Collapse(self.cp.IsExpanded())
        #self.OnPaneChanged()
        

    #def OnPaneChanged(self, evt=None):
        ## redo the layout
        #self.Layout()

        ## and also change the labels
        #if self.cp.IsExpanded():
            #self.cp.SetLabel(label2)
        #else:
            #self.cp.SetLabel(label1)
        

    #def MakePaneContent(self, pane):
        #'''Just make a few controls to put on the collapsible pane'''
        #nameLbl = wx.StaticText(pane, -1, "Name:")
        #name = wx.TextCtrl(pane, -1, "");

        #addrLbl = wx.StaticText(pane, -1, "Address:")
        #addr1 = wx.TextCtrl(pane, -1, "");
        #addr2 = wx.TextCtrl(pane, -1, "");

        #cstLbl = wx.StaticText(pane, -1, "City, State, Zip:")
        #city  = wx.TextCtrl(pane, -1, "", size=(150,-1));
        #state = wx.TextCtrl(pane, -1, "", size=(50,-1));
        #zip   = wx.TextCtrl(pane, -1, "", size=(70,-1));
        
        #addrSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        #addrSizer.AddGrowableCol(1)
        #addrSizer.Add(nameLbl, 0, 
                #wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        #addrSizer.Add(name, 0, wx.EXPAND)
        #addrSizer.Add(addrLbl, 0,
                #wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        #addrSizer.Add(addr1, 0, wx.EXPAND)
        #addrSizer.Add((5,5)) 
        #addrSizer.Add(addr2, 0, wx.EXPAND)

        #addrSizer.Add(cstLbl, 0,
                #wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

        #cstSizer = wx.BoxSizer(wx.HORIZONTAL)
        #cstSizer.Add(city, 1)
        #cstSizer.Add(state, 0, wx.LEFT|wx.RIGHT, 5)
        #cstSizer.Add(zip)
        #addrSizer.Add(cstSizer, 0, wx.EXPAND)

        #border = wx.BoxSizer()
        #border.Add(addrSizer, 1, wx.EXPAND|wx.ALL, 5)
        #pane.SetSizer(border)



##----------------------------------------------------------------------------------
#class TestFrame(wx.Frame):
    #def __init__(self, parent, title):
        #wx.Frame.__init__(self, parent, title=title, size=(400, 768),
                          #style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        #self.SetMinSize(wx.Size(300,300))

        #self.sizer = wx.BoxSizer(wx.VERTICAL)
        #self.frame = self
        #p = WatchPanel(self, "PIC14", "pic16f883")
        #self.sizer.Add(p, 1, wx.EXPAND)    
        
        #self.SetSizer(self.sizer)
        #self.sizer.Layout()

            
##----------------------------------------------------------------------------------
#class TestApp(wx.App):
    #def OnInit(self):
        #frame = TestFrame(None, 'Test Frame')
        #self.SetTopWindow(frame)
        #frame.Show(True)
        #return True

    #def OnClose(self):
        #print 'TestApp onclose'
        #return true

def bit_invert(v):
    v1 = 0
    for i in range(8):
        bit = (v >> i) & 1
        j = 7 - i
        v1 |= bit << j
    return v1

##----------------------------------------------------------------------------------
if __name__ == '__main__':
    #app = TestApp(0)
    #app.MainLoop()
    led = [0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6D, 0x7D, 0x07, 0x7f, 0x6f]
    lst = []
    for v in led:
        v1 = bit_invert(v)
        lst.append(v1)
        print hex(v1), ",",
    