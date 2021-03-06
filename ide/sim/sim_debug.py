import wx
import wx.lib.colourselect as csel
import wx.aui
import wx.richtext

import os
import sys
import Queue
import time


from sim_global import *
from sim_doc_book import DocBook
from sim_toolbar import SimToolbar, DebugToolbar
import mcs51
import pic16
import pic14

import sim_doc_lexer as doc_lexer
import sim_doc_base as doc_base
from sim_doc_base import StyledText

#---------------------------------------------------------------------------------------------------
class AsmView(StyledText):
    def __init__(self, parent):
        StyledText.__init__(self, parent)
        
    #-------------------------------------------------------------------
    def get_addr_text(self, s):
        s = s.strip()[0:6]
        if s == '':
            return None
        for c in s:
            if c not in '0123456789abcdefABCDEF' :
                return None
        return s
    
    #-------------------------------------------------------------------
    def set_text(self, text):
        self.addr_lst = [0]
                
        for line in text.split('\n'):
            addr = 0
            s = self.get_addr_text(line)
            if s != None:
                addr = int('0x' + s, 16)
            
            self.addr_lst.append(addr)
        print self.addr_lst
        self.SetText(text)
        
    #-------------------------------------------------------------------
    def goto_addr(self, addr):
        if addr in self.addr_lst:
            line = self.addr_lst.index(addr)
            self.goto_line(line)
            return line
    
    
#---------------------------------------------------------------------------------------------------
class StyledTextPanel (wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,300), style = wx.TAB_TRAVERSAL)
        
        self.SetMinSize(wx.Size(300,300))

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.text = AsmView(self)
        
        sizer.Add(self.text, 1, wx.EXPAND)
        
        self.SetSizer(sizer)
        sizer.Layout()
    
    def __del__(self):
        pass
    
    
#---------------------------------------------------------------------------------------------------
class TextCtrl(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, style = wx.TE_MULTILINE|wx.HSCROLL)
        self.default_style = wx.TextAttr()
        self.default_style.SetTextColour((0, 0, 0))
        lst = [(0, 65, 120), (0, 120, 65), (120, 120, 0), (120, 0, 65)]
        self.styles = []
        self.style = None
        for t in lst:
            style = wx.TextAttr()
            style.SetTextColour(t)
            self.styles.append(style)
            
        self.style_index = 0
        
    def get_size(self):
        return len(self.GetValue())    
    
    def set_style(self, i):
        if i == None:
            self.style = None
        else:
            self.style = self.styles[i]
            
    def set_next_style(self):
        self.style_index += 1
        self.style = self.styles[self.style_index % 4]
        
    def log(self, s):
        p0 = self.get_size()
        self.WriteText(s)
        if self.style :
            self.SetStyle(p0, p0 + len(s), self.style)
            self.style = None
        
        
#---------------------------------------------------------------------------------------------------
class TextPanel (wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,300), style = wx.TAB_TRAVERSAL)
        
        self.SetMinSize(wx.Size(300,300))

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.text = TextCtrl(self)
        sizer.Add(self.text, 1, wx.EXPAND)
        
        self.SetSizer(sizer)
        sizer.Layout()
    
    def __del__(self):
        pass


#---------------------------------------------------------------------------------------------------
class PanelSplitter (wx.Panel):
    
    def __init__(self, parent, p_class1, p_class2, flag = wx.VERTICAL):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(500,300), style = wx.TAB_TRAVERSAL)
                
        sizer = wx.BoxSizer(flag)
        
        self.splitter = wx.SplitterWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D)
        self.splitter.Bind(wx.EVT_IDLE, self.OnIdle)
        
        self.p1 = p1 = p_class1(self.splitter)
        self.p2 = p2 = p_class2(self.splitter)
        
        if flag == wx.VERTICAL:
            self.splitter.SplitVertically(p1, p2, 0)
        else:
            self.splitter.SplitHorizontally(p1, p2, 0)
            
        sizer.Add(self.splitter, 1, wx.EXPAND, 5)
                
        self.SetSizer(sizer)
        self.Layout()
    
    def __del__(self):
        pass
    
    #------------------------------------------------------------------------
    def OnIdle(self, event):
        self.splitter.SetSashPosition(0)
        self.splitter.Unbind(wx.EVT_IDLE)

        
#---------------------------------------------------------------------------------------------------
class MemViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,200), style = wx.TAB_TRAVERSAL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.mem_text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.HSCROLL)
        
        if wx.Platform == '__WXMSW__':
            font_name = u'Courier New'
        else:
            font_name = u'Courier 10 Pitch'
            
        font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, font_name)
        self.mem_text.SetFont(font1)
        
        sizer.Add(self.mem_text, 1, wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.Layout()
        
        self.bins = []
        for i in range(256):
            s = bin(i)
            s = '0000000' + s[2:]
            s = s[-8:]
            self.bins.append(s)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        lst = []
        lst.append("ADDR  00 01 02 03  04 05 06 07")
        
        hor_line = "--------------------------------"
        lst.append(hor_line)
        sz = len(sim.mem)
        if sz > 0x200:
            sz = 0x200
        m = sim.mem
        i = 0
        for a in range(0, sz, 8):
            lst.append('%04X  %02X %02X %02X %02X  %02X %02X %02X %02X' % 
                       (a, m[a], m[a+1], m[a+2], m[a+3], m[a+4], m[a+5], m[a+6], m[a+7]))
            
            if i == 7:
                i = 0
                lst.append(hor_line)
            else:
                i += 1
       
        s = '\n'.join(lst)
        self.mem_text.SetValue(s)
        

#---------------------------------------------------------------------------------------------------
class SfrViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,200), style = wx.TAB_TRAVERSAL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.mem_text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.HSCROLL)
        
        if wx.Platform == '__WXMSW__':
            font_name = u'Courier New'
        else:
            font_name = u'Courier 10 Pitch'
            
        font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, font_name)
        self.mem_text.SetFont(font1)
        
        sizer.Add(self.mem_text, 1, wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.Layout()
                
        
    #------------------------------------------------------------------------
    def update(self, sim):
        s = sim.get_sfr_view_text()
        self.mem_text.SetValue(s)
        
    
#---------------------------------------------------------------------------------------------------
class DebugFrame (wx.Frame):

    def __init__(self, app, parent, file_list, config_file):
        sz = wx.GetDisplaySize() 
        w = sz.GetWidth() - 64
        h = sz.GetHeight() -32
        x = (sz.GetWidth() - w) / 2
        y = (sz.GetHeight() - h) / 2
        
        wx.Frame.__init__ (self, parent, id = wx.ID_ANY, title = file_list[0], 
                            pos=(x, y), size=(w, h), 
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        self.app = app
        self.parent = parent
        sep = os.sep
        icon = wx.Icon(self.app.dirname + 'sim' + sep + 'images' + sep + 'dbg_frame.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        self.sim = None
        self.log_queue = Queue.Queue()
        self.config_file = config_file
        self.mcu_name = "mcs51"
        self.mcu_device = ""
        self.c_file = ""
        self.doc_c = None
        
        self.breakpoints = {}  #breakpoints
        self.sbuf = []
        
        self.load_config()
        
        self.SetSizeHintsSz(wx.Size(640,480), wx.DefaultSize)
        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(self)
        self.mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)

        self.statusbar = self.CreateStatusBar()

        #add tool bar
        self.toolbar = DebugToolbar(self, self.mgr)
        
        #add doc notebook for source code review
        self.doc_book = DocBook(app, self)
        self.doc_book.SetMinSize(wx.Size(120,-1))
        
        #add doc_book to AuiManager
        self.mgr.AddPane(self.doc_book, wx.aui.AuiPaneInfo().Right().PinButton(True).Dock().Resizable().FloatingSize(wx.Size(298,206)).DockFixed(False).Layer(0).CentrePane())

        #add debug information panel notebook
        nb2 = wx.aui.AuiNotebook(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(300,-1), wx.aui.AUI_NB_DEFAULT_STYLE)
        nb2.SetMinSize(wx.Size(200,-1))
        nb2.frame = self
        if self.mcu_name == "mcs51":
            panel = self.reg_panel = mcs51.WatchPanel(nb2)
        elif self.mcu_name == "pic16":
            panel = self.reg_panel = pic16.WatchPanel(nb2, self.mcu_name, self.mcu_device, self.config_file)
        elif self.mcu_name == "pic14":
            panel = self.reg_panel = pic14.WatchPanel(nb2, self.mcu_name, self.mcu_device, self.config_file)
        else:
            panel = self.reg_panel = mcs51.WatchPanel(nb2)
        nb2.AddPage(panel, u"Watches")
        
        self.mem_view = MemViewer(nb2)
        nb2.AddPage(self.mem_view, u"Memory")
        
        self.sfr_view = SfrViewer(nb2)
        nb2.AddPage(self.sfr_view, u"SFR")
        
        self.mgr.AddPane(nb2, wx.aui.AuiPaneInfo() .Left() .PinButton(True).Dock().Resizable().FloatingSize(wx.Size(93,102)).DockFixed(False))

        panel = PanelSplitter(self, TextPanel, StyledTextPanel, wx.VERTICAL)
        self.panel_log = panel.p1
        self.panel_asm = panel.p2
        self.log_view = self.panel_log.text
        self.asm_view = self.panel_asm.text
                
        self.mgr.AddPane(panel, wx.aui.AuiPaneInfo() .PinButton(True).Dock().Resizable().FloatingSize(wx.DefaultSize).DockFixed(False).CentrePane())
        
        self.mgr.Update()
        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TOOL, self.OnReset,   id=ID_DBG_RESET)
        #self.Bind(wx.EVT_TOOL, self.OnRun,     id=ID_RUN)
        self.Bind(wx.EVT_TOOL, self.OnContinue, id=ID_DBG_CONTINUE)
        self.Bind(wx.EVT_TOOL, self.OnPause,   id=ID_DBG_PAUSE)
        self.Bind(wx.EVT_TOOL, self.OnStop,    id=ID_DBG_STOP)
        self.Bind(wx.EVT_TOOL, self.OnPause,   id=ID_DBG_PAUSE)
        self.Bind(wx.EVT_TOOL, self.OnStep,    id=ID_DBG_STEP)
        self.Bind(wx.EVT_TOOL, self.OnStepOver, id=ID_DBG_STEP_OVER)
        self.Bind(wx.EVT_TOOL, self.OnStepOut,  id=ID_DBG_STEP_OUT)
        
        self.ihx_path = None
        file_list = self.find_included_source(file_list)
        self.file_list = file_list
        self.file_path = file_list[0]
        self.doc_list = []
        for file_path in file_list:
            self.open_file(file_path)
            
        self.command = 'debug' #command
        if self.command == 'debug':
            self.debug_mode = True
            self.toolbar.btn_reset()
        else:
            self.debug_mode = False
            self.toolbar.btn_run()
            
        self.sim = None
        self.timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer1Timer, self.timer1)
        self.timer1.Start(800)
        self.pause = True
        
        self.step_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnStepTimerTick, self.step_timer)
        #event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_RUN)
        #wx.PostEvent(self.toolbar, event)    
        self.ticks = 0
        self.cpu_clock = 1*1024*1024
        self.interval = 1.0 / self.cpu_clock
        self.tick_count = (self.cpu_clock >> 10)
        
    #-------------------------------------------------------------------
    def OnTimer1Timer(self, event):  
        self.SetStatusText(time.asctime())
        self.timer1.Stop()
        if self.ihx_path:
            self.sim_run('debug')
        else:
            MsgDlg_Warn(self, 'There is no hex file to simulation.', 'Error!')
        self.command = None
        
    #-------------------------------------------------------------------
    def OnStepTimerTick(self, event):
        sim = self.sim
        self.ticks += 1
        self.step_timer.Stop()
        
        if self.pause and not sim.step_mode:
            return

        if sim and not sim.stopped :
            self.log_view.set_next_style()

            if sim.step_mode:
                sim.step_tick()
            else :
                sim.step()

            doc = self.get_doc(sim.c_file)
            if doc:
                if sim.c_line in doc.breakpoints:
                    doc.goto_line(self.sim.c_line)
                    doc.Update()
                    self.log("Break at " + str(sim.c_line) + "\n")
                    #self.log(str(doc.breakpoints))
                    self.pause = True
                    sim.step_mode = None
                    self.toolbar.btn_pause()
                    
        if self.sim.stopped:
            self.sim_stop()
            return
            
        if self.pause and not sim.step_mode:
            return
        self.sim_update()
        self.step_timer.Start(1)

    #-------------------------------------------------------------------
    def sim_run(self, command):
        
        if self.mcu_name == "mcs51":
            self.sim = mcs51.Sim(self, self.ihx_path, self.file_list, command)
            s = self.sim.disassembly()
        elif self.mcu_name == 'pic16':
            self.sim = pic16.Sim(self, self.ihx_path, self.file_list, self.mcu_name, self.mcu_device)
            s = self.sim.disassembly()
        elif self.mcu_name == 'pic14':
            self.sim = pic14.Sim(self, self.ihx_path, self.file_list, self.mcu_name, self.mcu_device)
            s = self.sim.disassembly()
            
        self.asm_view.set_text(s)
        if self.breakpoints == None:
            self.breakpoints = {}
        for f in self.file_list:
            brks = self.breakpoints.get(f, None)
            if brks:
                doc = self.get_doc(f)
                self.breakpoints[f] = brks
                
        self.sim.breakpoints = self.breakpoints
        self.sim.enable_debug(True)
        self.sim.start()
        
        self.running = True
        if self.debug_mode:
            self.pause = True
            self.toolbar.btn_pause()
            #return
            
        #if not self.debug_mode:

        #self.step_timer.Start(1)
        self.sim_update()
        #self.toolbar.btn_run()
        
    #-------------------------------------------------------------------
    def sim_stop(self):
        if self.running:
            self.running = False
            if hasattr(self, 'step_timer'):
                self.Unbind(event=wx.EVT_TIMER, source=self.step_timer, handler=self.OnStepTimerTick)
                self.step_timer.Stop()
                #del self.step_timer
                
            self.toolbar.btn_stop()

    #-------------------------------------------------------------------
    def get_doc(self, file_path):
        for doc in self.doc_list:
            if doc.file_path == file_path:
                return doc
        return None
    
    #-------------------------------------------------------------------
    def sim_update(self):
        sim = self.sim
        
        self.asm_view.goto_addr(sim.inst_addr)
        
        s = '%06x' % sim.pc
        for t in self.doc_book.docs:
            if t[1].file_path.endswith('st'):
                t[1].search_addr(s)
            
        #uart sbuf
        for ch in sim.sbuf_list:
            self.sbuf.append(ch)
            
        sim.sbuf_list = []
        
        doc = self.doc_c
        if doc:
            doc.goto_line(sim.c_line)
            doc.Update()
            #self.doc_book.SetSelection(doc.page_index)
            
        self.reg_panel.update_inst(sim, self.sbuf)
        self.reg_panel.update(sim)
        self.mem_view.update(sim)
        self.sfr_view.update(sim)
        
        if self.pause:
            if sim.stack_depth == 0:
                self.toolbar.enable_step_out(False)
            else:
                self.toolbar.enable_step_out(True)
    
    #-------------------------------------------------------------------
    def OnReset(self, event):
        self.sim_stop()        
        self.log_view.Clear()
        self.log("Press Continue or Step functions to start simulation.\n")
        self.sim = None
        self.sim_run('debug')
        for t in self.doc_book.docs:
            t[1].goto_line(0)
        self.toolbar.btn_reset()
        
    #-------------------------------------------------------------------
    def OnPause(self, event):
        self.pause = True
        self.step_timer.Stop()
        
    #-------------------------------------------------------------------
    def OnContinue(self, event):
        self.pause = False
        self.sim.step_mode = 'run'
        self.step_timer.Start(1)
        
    #-------------------------------------------------------------------
    def OnStep(self, event):
        if self.sim and not self.sim.stopped :
            #self.sim.step_c_line()
            self.log_view.set_style(None)
            self.sim.step()
            self.sim_update()
            
    #-------------------------------------------------------------------
    def OnStepOver(self, event):
        if self.sim and not self.sim.stopped :
            self.log_view.set_style(None)
            result = self.sim.step_over()
            if result == 'not finished':
                pass
            
            self.sim_update()
            self.step_timer.Start(1)
            
    #-------------------------------------------------------------------
    def OnStepOut(self, event):
        if self.sim and not self.sim.stopped :
            self.log_view.set_style(None)
            self.sim.step_out()
            self.step_timer.Start(1)
            self.sim_update()
            
    #-------------------------------------------------------------------
    def OnStop(self, event):
        if self.sim is not None:
            self.log_view.set_next_style()
            self.log("Simulation aborted!\n")
            
            self.sim.stop()
            
    #-------------------------------------------------------------------
    def dprint(self, s1, s2):
        self.log_view.WriteText(s1 + " " + s2)
    
    #-------------------------------------------------------------------
    def write(self, s):
        self.log_view.WriteText(s)
        
    #-------------------------------------------------------------------
    def log(self, s):
        #import inspect
        #s1 = inspect.stack()[1][3] + " "
        #if self.sim.step_mode:
        #    return
        if s.find('------') >= 0:
            self.log_view.set_next_style()
        self.log_view.log(s)
        
    #-------------------------------------------------------------------
    def show_debug(self):
        pass #self.log_nb.show_debug()
        
    #-------------------------------------------------------------------
    def clear_debug(self):
        pass #self.log_nb.clear_debug()
    
    #-------------------------------------------------------------------
    def read_file_include_lines(self, file_path):
        dirname = os.path.dirname(file_path)
        f = open(file_path, 'r')
        lst = []
        for s in f.readlines():
            #print s
            if s.find('#include') >= 0 and s.find('.c') > 0:
                s = s.replace('#include', '')
                s = s.strip()
                if s.find('\"') or s.find('\''):
                    s = s.replace('\"', '')
                    s = s.replace('\'', '')
                    s = s.strip()
                    s = dirname + os.sep + s
                elif s.find('<'):
                    s = s.replace('<', '')
                    s = s.replace('>', '')
                    s = s.strip()
                lst.append(s)
        f.close()
        return lst
        
    #-------------------------------------------------------------------
    def find_included_source(self, file_list):
        new_list = []
        for fn in file_list:
            new_list.append(fn)
            lst = self.read_file_include_lines(fn)
            for t in lst:
                new_list.append(t)
        return new_list
    
    #-------------------------------------------------------------------
    def check_if_with_main(self, file_path):
        if not os.path.exists(file_path):
            return False
        
        f = open(file_path, 'r')
        s = f.read()
        f.close()
     
        if s.find('main') < 0:
            return False
        
        #s = c_pre_process(s)
        s = re.sub("/\*[^\*]*\*/", "[$BC]", s)        # replace block comment
        s = re.sub("([//][^\n]*[\n])", "[$LC]\n", s)  # replace line comment
        s = re.sub("\([^\(\)]*\)", " () ", s)         # replace parenthesis
        s = re.sub("\"[^\"\n]*\"", "[$ST]", s)        # replace string
        
        p_blk = "{[^{^}]*}"
        match = re.search(p_blk, s)
        if (match):
            s = re.sub(p_blk, "[$BLK]", s)
            while (match) :
                s = re.sub(p_blk, "[$BLK]", s)
                match = re.search(p_blk, s)
    
        s = re.sub(",", " , ", s)
        s = re.sub("=", " = ", s)

        match = re.findall(r"\w+\s+\(\)\s+[\[]+", s)
        #log(match)
        #print match
        for t in match :
            t = re.sub("[\[\n\(\)]", "", t)
            #print '------------', t
            if t.find('main') == 0:
                return True
            
        return False
            
    #-------------------------------------------------------------------
    def open_file(self, file_path):
        print(file_path)
        path = os.path.dirname(file_path)
        if path != '':
            os.chdir(path)
            
        path, ext = file_path.split('.')
        
        c_file = path + '.c'
        if os.path.exists(c_file):
            doc = self.doc_book.open_file(c_file)
            if self.breakpoints:
                brks = self.breakpoints.get(c_file, None)
                if brks:
                    doc.add_breakpoints(brks)
                    
            self.doc_list.append(doc)
            if self.check_if_with_main(c_file):
                self.doc_c = doc
        
        #self.doc_asm = self.doc_book.open_file(path + '.asm')
        if self.mcu_name == 'pic16' or self.mcu_name == 'pic14':
            if os.path.exists(path + '.lst'):
                self.doc_book.open_file(path + '.lst')
            elif os.path.exists(path + '.asm'):
                self.doc_book.open_file(path + '.asm')
                
            if os.path.exists(path + '.hex'):
                self.doc_book.open_file(path + '.hex')
                self.ihx_path = path + '.hex'
                
        else:
            if os.path.exists(path + '.rst'):
                self.doc_book.open_file(path + '.rst')
            elif os.path.exists(path + '.lst'):
                self.doc_book.open_file(path + '.lst')
            elif os.path.exists(path + '.asm'):
                self.doc_book.open_file(path + '.asm')
                
            if os.path.exists(path + '.ihx'):
                self.doc_book.open_file(path + '.ihx')
                self.ihx_path = path + '.ihx'
            elif os.path.exists(path + '.hex'):
                self.doc_book.open_file(path + '.hex')
                self.ihx_path = path + '.hex'
           
        self.doc_book.SetSelection(0)
        
    #-------------------------------------------------------------------
    def save_config(self):
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)
        
        # save breakpoints
        lst = self.doc_book.get_breakpoints()
        s = ";".join(lst)
        config.Write("breakpoints", s)
        
        ## save scope pin configs
        #if hasattr(self, "scope") and self.scope:
            #pin_lst, check_lst = self.scope.get_pin_config()
            #config.Write("scope_pins", ';'.join(pin_lst))
            #config.Write("scope_pins_checked", ';'.join(check_lst))
        
        del config
        
    #-------------------------------------------------------------------
    def load_config(self):
        print("load config - " + self.config_file)
        config_file = self.config_file
        if not os.path.exists(config_file):
            self.app.set_build_option()
            return
        
        config = wx.FileConfig("", "", config_file, "", wx.CONFIG_USE_LOCAL_FILE)

        if config.Exists("mcu_name"):
            self.mcu_name = config.Read("mcu_name", "mcs51") 
            self.mcu_device = config.Read("mcu_device", "") 

        # load breakpoints
        s = config.Read("breakpoints", "")
        if s == "":
            self.breakpoints = None
        else:
            lst = s.split(';')
            self.breakpoints = {}
            
            for t in lst:
                path, b = t.split("=")
                blst = eval(b)
                self.breakpoints[path] = blst
            
        del config
        
    #-------------------------------------------------------------------
    def stop(self):
        print "stop"
        if hasattr(self, 'step_timer'):
            if self.step_timer:
                self.step_timer.Stop()
            
        if self.sim:
            print "StopSimulation"
            self.sim.stop()
            q = self.log_queue
            if q is not None:
                while not q.empty():
                    q.get_nowait()
            self.log_queue = None
            
    #-------------------------------------------------------------------
    def close(self):
        self.stop()
        self.save_config()
        self.Destroy()
        
    #-------------------------------------------------------------------
    def __del__(self):
        #print "__del__"
        try:
            if self.parent is not None:
                self.parent.sim_close()
        except:
            print "Error: unable to UnInit SimFrame.mgr"

    #-------------------------------------------------------------------
    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        #print "OnClose"
        self.stop()
        self.save_config()
        event.Skip()
        