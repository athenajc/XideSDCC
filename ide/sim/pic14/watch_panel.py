import wx
from utils import tohex, get_sfr_addr

#----------------------------------------------------------------------------------
USE_BUFFER = ('wxMSW' in wx.PlatformInfo) # use buffered drawing on Windows


#---------------------------------------------------------------------------------------------------
class WatchPane(wx.CollapsiblePane):
    def __init__(self, parent, parent_sizer, title):
        self.sim = None
        self.parent = parent
        self.label1 = "Click here to Show " + title
        self.label2 = "Click here to Hide " + title
        
        wx.CollapsiblePane.__init__(self, parent, label=self.label1,
                                          style=wx.CP_DEFAULT_STYLE |wx.CP_NO_TLW_RESIZE)
        #self.cp = cp = wx.CollapsiblePane(parent, label=self.label1,
        #                                  style=wx.CP_DEFAULT_STYLE |wx.CP_NO_TLW_RESIZE)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, self)

        parent_sizer.Add(self, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def OnPaneChanged(self, evt=None):
        # redo the layout
        self.parent.Layout()

        # and also change the labels
        if self.IsExpanded():
            self.SetLabel(self.label2)
        else:
            self.SetLabel(self.label1)
            


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
        if USE_BUFFER:
            self.Bind(wx.EVT_SIZE, self.OnSize)

    #----------------------------------------------------------------------------
    def OnSize(self, evt):
        self.init_buffer()
        evt.Skip()
        
    #----------------------------------------------------------------------------
    def OnPaint(self, evt):
        if USE_BUFFER:
            # The buffer already contains our drawing, so no need to
            # do anything else but create the buffered DC.  When this
            # method exits and dc is collected then the buffer will be
            # blitted to the paint DC automagically
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
        self.Refresh()
        
        
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
        self.select_port = "PORTA"
        
        cb_sizer = wx.BoxSizer(wx.VERTICAL)
        pins = ['RA0','RA1','RA2','RA3','RA4','RA5','RA6','RA7',
                        'RB0','RB1','RB2','RB3','RB4','RB5','RB6','RB7',
                        'RC0','RC1','RC2','RC3','RC4','RC5','RC6','RC7',]
        self.cb_lst = [None] * 7
        s = ["a", "b", "c", "d", "e", "f", "g"]
        for i in range(7):
            self.cb_lst[i] = cb = ComboBox(panel, cb_sizer, s[i], pins)
            cb.SetValue(pins[i])
            if i == 0:
                cb.Bind(wx.EVT_COMBOBOX, self.OnSelectPin0)
            else:
                cb.Bind(wx.EVT_COMBOBOX, self.OnSelectPin)
        
        sizer.Add(self.led, 0, wx.EXPAND)
        sizer.Add(cb_sizer, 0, wx.EXPAND)
        
        panel.SetSizer(sizer)
        panel.Layout()
        self.Expand()
        
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
        for i in range(1,7):
            s = self.cb_lst[i].GetValue()
            
            
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
        
        
#---------------------------------------------------------------------------------------------------
class SfrTextCtrl(wx.TextCtrl):
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, sz1=(40,-1), sz2=(35,-1)):
        wx.TextCtrl.__init__(self, parent, -1, "", size=sz2, style=wx.TE_READONLY)
        box = wx.BoxSizer(wx.HORIZONTAL)

        self.label = wx.StaticText(parent, -1, label_str, pos=(0,0), size=sz1, style=wx.ALIGN_RIGHT)
        box.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 0)
        
        text = self
        text.SetValue(default_str)
        text.SetHelpText(help_str)
        text.SetBackgroundColour((185,185,185))
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.RIGHT, 0)

        sizer.Add(box, 0, flag, 0)
        
    def set_value(self, v):
        self.SetValue(tohex(v, 2))
        if v == 0:
            self.SetBackgroundColour((185,185,185))
        else:
            self.SetBackgroundColour((235,235,235))   
            
            
#---------------------------------------------------------------------------------------------------
class SfrTextCtrlList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer, title, lst):
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.HORIZONTAL)
        box_sizer = self
                    
        panel = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        p_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.text_list = []
        h = 0
        for t in lst:
            obj = SfrTextCtrl(panel, p_sizer, t[0], hex(t[1]), '00')
            self.text_list.append([t[0], t[1], obj])
            
        panel.SetSizer(p_sizer)
        panel.Layout()
         
        box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        
        for t in self.text_list:
            i = t[1]
            v = sim.get_reg(t[0].lower())
            text = t[2]
            if type(v) == type(u'a'):
                text.SetValue(v)
            else:
                text.SetValue(tohex(v, 2))
            if v == 0:
                text.SetBackgroundColour((185,185,185))
            else:
                text.SetBackgroundColour((235,235,235))


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
class PcDptrTextCtrlList(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "PC ADDR")
        #title = ''
        #box = wx.StaticBox(parent, wx.ID_ANY, title)
        #wx.StaticBoxSizer.__init__(self, box, wx.HORIZONTAL)
        #box_sizer = self
                    
        panel = self.GetPane() #wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
            
        self.pc_text = LabelTextCtrl(panel, sizer, 'PC ', '', '00', size=(60, -1))
        self.dptr_text = LabelTextCtrl(panel, sizer, '  FSR0 ', '', '00', size=(60, -1))
        self.sp_text = LabelTextCtrl(panel, sizer, '  SP ', '', '00', size=(30, -1))
        panel.SetSizer(sizer)
        panel.Layout()
        self.Expand()
        #box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        #parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        self.pc_text.set_value(sim.get_reg('PC'), 4)
        self.dptr_text.set_value(sim.get_reg('FSR0'), 4)
        self.sp_text.set_value(sim.get_reg('SP'), 2)
        

        
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
        
    #------------------------------------------------------------------------
    def set_value(self, v):
        self.text.SetValue(tohex(v, 2))
        c = [(180, 180, 180), (255, 255, 100)]
        for i in range(8):
            b = (v >> (7 - i)) & 1
            t = self.bit_obj_list[i]
            t.SetValue(b)
            #t.SetBackgroundColour(c[b])
            
        

#---------------------------------------------------------------------------------------------------
class PortTextCtrlList(WatchPane):
    def __init__(self, parent, parent_sizer):
        WatchPane.__init__(self, parent, parent_sizer, "Port Data")
        
        panel = self.GetPane()

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.p0_text = PortTextCtrl(panel, sizer, 'PORTA ', '', '00', size=(30, -1))
        self.p1_text = PortTextCtrl(panel, sizer, 'PORTB ', '', '00', size=(30, -1))
        self.p2_text = PortTextCtrl(panel, sizer, 'PORTC ', '', '00', size=(30, -1))
        self.t0_text = TrisCtrl(panel, sizer, 'TRISA ', '', '00', size=(30, -1))
        self.t1_text = TrisCtrl(panel, sizer, 'TRISB ', '', '00', size=(30, -1))
        self.t2_text = TrisCtrl(panel, sizer, 'TRISC ', '', '00', size=(30, -1))     
        
        panel.SetSizer(sizer)
        panel.Layout()

        self.Expand()

    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return

        self.p0_text.set_value(sim.get_reg('PORTA'))
        self.p1_text.set_value(sim.get_reg('PORTB'))
        self.p2_text.set_value(sim.get_reg('PORTC'))
        self.t0_text.set_value(sim.get_reg('TRISA'))
        self.t1_text.set_value(sim.get_reg('TRISB'))
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

        self.Expand()

        
        
#---------------------------------------------------------------------------------------------------
class UartTextViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,200), style = wx.TAB_TRAVERSAL)
                
        self.SetMinSize(wx.Size(300,100))
        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Uart Viewer"), wx.VERTICAL)

        self.inst_text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.HSCROLL)
        
        sbSizer1.Add(self.inst_text, 1, wx.EXPAND, 5)
        self.SetSizer(sbSizer1)
        sbSizer1.Layout()
        
    #------------------------------------------------------------------------
    def update_inst(self, sim, sbuf): 
        self.inst_text.SetValue('')
        s = "file = " + sim.c_file + "\n"
        s += "line = " + str(sim.c_line) + "\n\n"
        
        s += str(sbuf) + '\n'
        s1 = ''.join(chr(i) for i in sbuf)
        s += s1 
        s += 'bank = ' + str(sim.bank_addr) + '\n'
        
        if sim.debug:
            for a in sim.mem_access_list:
                s += 'mem ' + hex(a) + ' = ' + hex(sim.mem[a]) + '\n'
            
        #s += 'sbuf list = ' + str(sim.sbuf_list) + '\n'
            
        self.inst_text.WriteText(s)
        
        

#---------------------------------------------------------------------------------------------------
class WatchPanel (wx.Panel):
    
    def __init__(self, parent, mcu_name, mcu_device):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(500,300), style = wx.TAB_TRAVERSAL)
        
        self.sim = None
        self.frame = parent.frame
        self.mcu_name = mcu_name
        self.mcu_device = mcu_device
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.pc_dptr_viewer = PcDptrTextCtrlList(self, sizer)
        self.port_panel = PortTextCtrlList(self, sizer)
        self.watch_led = WatchLed(self, sizer)
        InputCtrlList(self, sizer)
        #watch_panel = self.sfr_watch = SfrWatchPanel(self)
        text_view = self.uart_text_view = UartTextViewer(self)
        
        #sizer.Add(watch_panel, 0, wx.EXPAND, 5)
        sizer.Add(text_view, 1, wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.Layout()
       
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
                print c, hex(ord(c))
                self.sim.set_input('uart', ord(c))
                
    #------------------------------------------------------------------------
    def get_sim(self):
        return self.sim

    #------------------------------------------------------------------------
    def update(self, sim):
        if self.sim == None:
            self.sim = sim
        self.pc_dptr_viewer.update(sim)
        self.port_panel.update(sim)
        self.watch_led.update(sim)
        #self.sfr_watch.update(sim)
        
    #------------------------------------------------------------------------
    def update_inst(self, sim, sbuf): 
        #print 'update_inst ', sim.c_line
        self.uart_text_view.update_inst(sim, sbuf)
        
    #------------------------------------------------------------------------
    def OnIdle(self, event):
        self.splitter.SetSashPosition(0)
        self.splitter.Unbind(wx.EVT_IDLE)
        
    #------------------------------------------------------------------------
    def __del__(self):
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
    