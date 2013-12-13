import wx
from utils import tohex

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
class PcDptrTextCtrlList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer):
        title = ''
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.HORIZONTAL)
        box_sizer = self
                    
        panel = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
            
        self.pc_text = LabelTextCtrl(panel, sizer, 'PC ', '', '00', size=(60, -1))
        self.dptr_text = LabelTextCtrl(panel, sizer, '  DPTR ', '', '00', size=(60, -1))
        self.sp_text = LabelTextCtrl(panel, sizer, '  SP ', '', '00', size=(30, -1))
        panel.SetSizer(sizer)
        panel.Layout()
         
        box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        self.pc_text.set_value(sim.get_reg('pc'), 4)
        self.dptr_text.set_value(sim.get_reg('dptr'), 4)
        self.sp_text.set_value(sim.get_reg('sp'), 2)
        
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
        
            
    def set_value(self, v):
        self.text.SetValue(tohex(v, 2))
        c = [(180, 180, 180), (255, 255, 100)]
        for i in range(8):
            b = (v >> (7 - i)) & 1
            t = self.bit_text_list[i]
            t.SetValue(str(b))
            t.SetBackgroundColour(c[b])
        
#---------------------------------------------------------------------------------------------------
class PortTextCtrlList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer):
        
        self.sim = None
        self.parent = parent
        
        title = ''
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.VERTICAL)
        box_sizer = self
                    
        panel = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
            
        self.p0_text = PortTextCtrl(panel, sizer, 'P0 ', '', '00', size=(30, -1))
        self.p1_text = PortTextCtrl(panel, sizer, 'P1 ', '', '00', size=(30, -1))
        self.p2_text = PortTextCtrl(panel, sizer, 'P2 ', '', '00', size=(30, -1))
        self.p3_text = PortTextCtrl(panel, sizer, 'P3 ', '', '00', size=(30, -1))
        
        bn_int0 = wx.Button(panel, 1, 'INT 0')
        bn_int1 = wx.Button(panel, 2, 'INT 1')
        sizer.Add(bn_int0, 1, wx.ALL, 2)
        sizer.Add(bn_int1, 1, wx.ALL, 2)
        
        parent.frame.Bind(wx.EVT_BUTTON, parent.OnInt0, bn_int0)
        parent.frame.Bind(wx.EVT_BUTTON, parent.OnInt1, bn_int1)
        
        panel.SetSizer(sizer)
        panel.Layout()
         
        box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return

        self.p0_text.set_value(sim.get_reg('p0'))
        self.p1_text.set_value(sim.get_reg('p1'))
        self.p2_text.set_value(sim.get_reg('p2'))
        self.p3_text.set_value(sim.get_reg('p3'))
        
#---------------------------------------------------------------------------------------------------
class RegTextCtrlList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer):
        title = ''
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.HORIZONTAL)
        box_sizer = self
                    
        panel = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        size1 = (25, -1)
        size2 = (30, -1)
        self.a_text = SfrTextCtrl(panel, sizer, ' A', '', '00', sz1=size1, sz2=size2)
        self.c_text = SfrTextCtrl(panel, sizer, ' C', '', '00', sz1=size1, sz2=size2)
        self.r0_text = SfrTextCtrl(panel, sizer, 'R0', '', '00', sz1=size1, sz2=size2)
        self.r1_text = SfrTextCtrl(panel, sizer, 'R1', '', '00', sz1=size1, sz2=size2)
        self.r2_text = SfrTextCtrl(panel, sizer, 'R2', '', '00', sz1=size1, sz2=size2)
        self.r3_text = SfrTextCtrl(panel, sizer, 'R3', '', '00', sz1=size1, sz2=size2)
        self.r4_text = SfrTextCtrl(panel, sizer, 'R4', '', '00', sz1=size1, sz2=size2)
        self.r5_text = SfrTextCtrl(panel, sizer, 'R5', '', '00', sz1=size1, sz2=size2)
        self.r6_text = SfrTextCtrl(panel, sizer, 'R6', '', '00', sz1=size1, sz2=size2)
        self.r7_text = SfrTextCtrl(panel, sizer, 'R7', '', '00', sz1=size1, sz2=size2)
        
        panel.SetSizer(sizer)
        panel.Layout()
         
        box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return

        self.a_text.set_value(sim.get_reg('acc'))
        self.c_text.set_value(sim.get_reg('c'))
        self.r0_text.set_value(sim.get_reg('r0'))
        self.r1_text.set_value(sim.get_reg('r1'))
        self.r2_text.set_value(sim.get_reg('r2'))
        self.r3_text.set_value(sim.get_reg('r3'))
        self.r4_text.set_value(sim.get_reg('r4'))
        self.r5_text.set_value(sim.get_reg('r5'))
        self.r6_text.set_value(sim.get_reg('r6'))
        self.r7_text.set_value(sim.get_reg('r7'))
                    
#---------------------------------------------------------------------------------------------------
class SfrWatchPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,300), style = wx.TAB_TRAVERSAL)
                
        self.SetMinSize(wx.Size(300,300))
        #main_sizer = wx.BoxSizer(wx.VERTICAL)
        #self.pc_dptr_viewer = PcDptrTextCtrlList(self, main_sizer)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sfr_map_1 = [
            ['P0',   0x80],
            ['P1',   0x90],
            ['P2',   0xA0],
            ['P3',   0xB0],
            ['DPL',  0x82],
            ['DPH',  0x83],
            ['PSW',  0xD0],
            
            ['ACC',  0xE0],
            
            ['IE',   0xA8],
            ['IP',   0xB8],
        ]
        
        self.sfr_map_2 = [
            ['PCON', 0x87],
            ['TCON', 0x88],
            ['TMOD', 0x89],
            ['TL0',  0x8A],
            
            ['TL1',  0x8B],
            ['TH0',  0x8C],
            ['TH1',  0x8D],
            ['SCON', 0x98],
            ['SBUF', 0x99],
            ['B',    0xF0],
        ]
        
        self.watch1 = SfrTextCtrlList(self, sizer, '', self.sfr_map_1)
        self.watch2 = SfrTextCtrlList(self, sizer, '', self.sfr_map_2)
        self.reg_watch = RegTextCtrlList(self, sizer)
        
        #main_sizer.Add(sizer, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        self.SetSizer(sizer)
        self.Layout()
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        #self.pc_dptr_viewer.update(sim)
        self.watch1.update(sim)
        self.watch2.update(sim)
        self.reg_watch.update(sim)
        
        
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
        #s += 'sbuf list = ' + str(sim.sbuf_list) + '\n'
            
        self.inst_text.WriteText(s)
        
#class WatchPanel (wx.Panel):
    
    #def __init__(self, parent):
        #wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(500,300), style = wx.TAB_TRAVERSAL)
        
        #sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #self.splitter = wx.SplitterWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D)
        #self.splitter.Bind(wx.EVT_IDLE, self.OnIdle)
        
        #p1 = self.sfr_watch = SfrWatchPanel(self.splitter)
        #p2 = self.sfr_text_view = SfrTextViewer(self.splitter)

        #self.splitter.SplitHorizontally(p1, p2, 0)
            
        #sizer.Add(self.splitter, 1, wx.EXPAND, 5)
                
        #self.SetSizer(sizer)
        #self.Layout()
        
    ##------------------------------------------------------------------------
    #def update(self, sim):
        #self.sfr_watch.update(sim)
        
    ##------------------------------------------------------------------------
    #def update_inst(self, sim, sbuf): 
        #self.sfr_text_view.update_inst(sim, sbuf)
        
    ##------------------------------------------------------------------------
    #def OnIdle(self, event):
        #self.splitter.SetSashPosition(0)
        #self.splitter.Unbind(wx.EVT_IDLE)
        
    ##------------------------------------------------------------------------
    #def __del__(self):
        #pass
        
class IoPortPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        
        box = wx.StaticBox(self, -1, "This is a wx.StaticBox")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        t = wx.StaticText(self, -1, "Controls placed \"inside\" the box are really its siblings")
        bsizer.Add(t, 0, wx.TOP|wx.LEFT, 5)
        
        border = wx.BoxSizer()
        border.Add(bsizer, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(border)
        
   
    
#---------------------------------------------------------------------------------------------------
class WatchPanel (wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(500,300), style = wx.TAB_TRAVERSAL)
        
        self.sim = None
        self.frame = parent.frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.pc_dptr_viewer = PcDptrTextCtrlList(self, sizer)
        self.port_panel = PortTextCtrlList(self, sizer)
        
        watch_panel = self.sfr_watch = SfrWatchPanel(self)
        text_view = self.uart_text_view = UartTextViewer(self)
        
        sizer.Add(watch_panel, 0, wx.EXPAND, 5)
        sizer.Add(text_view, 1, wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.Layout()
        
    #--------------------------------------------------------------
    def OnInt0(self, event):
        if self.sim:
            self.sim.set_input('int0', 1)
    
    #--------------------------------------------------------------
    def OnInt1(self, event):
        if self.sim:
            self.sim.set_input('int1', 1)
            
    #------------------------------------------------------------------------
    def get_sim(self):
        return self.sim
            
    #------------------------------------------------------------------------
    def update(self, sim):
        if self.sim == None:
            self.sim = sim
        self.pc_dptr_viewer.update(sim)
        self.port_panel.update(sim)
        self.sfr_watch.update(sim)
        
    #------------------------------------------------------------------------
    def update_inst(self, sim, sbuf): 
        self.uart_text_view.update_inst(sim, sbuf)
        
    #------------------------------------------------------------------------
    def OnIdle(self, event):
        self.splitter.SetSashPosition(0)
        self.splitter.Unbind(wx.EVT_IDLE)
        
    #------------------------------------------------------------------------
    def __del__(self):
        pass