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

#---------------------------------------------------------------------------------------------------
class StyledTextPanel (wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,300), style = wx.TAB_TRAVERSAL)
        
        self.SetMinSize(wx.Size(300,300))

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.text = doc_base.StyledText(self)
        
        sizer.Add(self.text, 1, wx.EXPAND)
        
        self.SetSizer(sizer)
        sizer.Layout()
    
    def __del__(self):
        pass
    
#---------------------------------------------------------------------------------------------------
class TextPanel (wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,300), style = wx.TAB_TRAVERSAL)
        
        self.SetMinSize(wx.Size(300,300))

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.HSCROLL)         
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
class MemViewer(wx.StaticBoxSizer):
    def __init__(self, parent):
        wx.StaticBoxSizer.__init__(self, wx.StaticBox(self, wx.ID_ANY, u"Memory"), wx.VERTICAL)
        self.mem_text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.HSCROLL)
        self.Add(self.mem_text, 1, wx.EXPAND, 5)
        
    #------------------------------------------------------------------------
    def update(self, sim):       
        s = ""
        for i in range(256):
            s = s + tohex(sim.mem[i], 2) + " "
            if i % 16 == 15:
                s += "\n"
                        
        self.mem_text.SetValue(s)
        

    
#---------------------------------------------------------------------------------------------------
class DebugFrame (wx.Frame):

    def __init__(self, app, parent, file_list, config_file):
        wx.Frame.__init__ (self, parent, id = wx.ID_ANY, title = file_list[0], 
                            pos = wx.DefaultPosition, size = wx.Size(1280,800), 
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        self.app = app
        self.parent = parent
        self.sim = None
        self.log_queue = Queue.Queue()
        self.config_file = config_file
        self.mcu_name = "mcs51"
        self.mcu_device = ""
        
        self.breakpoints = []  #breakpoints
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
        
        if self.mcu_name == "mcs51":
            panel = self.reg_panel = mcs51.WatchPanel(nb2)
        elif self.mcu_name == "pic16":
            panel = self.reg_panel = pic16.WatchPanel(nb2, self.mcu_name, self.mcu_device)
        elif self.mcu_name == "pic14":
            panel = self.reg_panel = pic14.WatchPanel(nb2, self.mcu_name, self.mcu_device)            
        else:
            panel = self.reg_panel = mcs51.WatchPanel(nb2)
        nb2.AddPage(panel, u"Watches")
        
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
        self.Bind(wx.EVT_TOOL, self.OnRun,     id=ID_RUN)
        self.Bind(wx.EVT_TOOL, self.OnContinue, id=ID_DBG_CONTINUE)
        self.Bind(wx.EVT_TOOL, self.OnPause,   id=ID_DBG_PAUSE)
        self.Bind(wx.EVT_TOOL, self.OnStop,    id=ID_DBG_STOP)
        self.Bind(wx.EVT_TOOL, self.OnPause,   id=ID_DBG_PAUSE)
        self.Bind(wx.EVT_TOOL, self.OnStep,    id=ID_DBG_STEP)
        self.Bind(wx.EVT_TOOL, self.OnStepOver, id=ID_DBG_STEP_OVER)
        self.Bind(wx.EVT_TOOL, self.OnStepOut,  id=ID_DBG_STEP_OUT)
                
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
        self.pause = False
        #event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_RUN)
        #wx.PostEvent(self.toolbar, event)    
        
    #-------------------------------------------------------------------
    def OnTimer1Timer(self, event):  
        self.SetStatusText(time.asctime())
        if self.command == 'run' or self.command == 'debug':
            self.timer1.Stop()
            self.sim_run(self.command)
            self.timer1.Start(100)
            if self.command == 'run':
                self.pause = False
                self.running = True
            else:
                self.pause = True
            self.command = None
        
        if self.sim is None:
            return
        
        if self.sim.stopped:
            self.sim_stop()
            return
        
        if self.pause:
            return
        
        self.sim_update()
        
    #-------------------------------------------------------------------
    def OnTimer2Timer(self, event):
        if self.pause:
            return
        
        sim = self.sim
        if sim and not sim.stopped :
            sim.step()
            
            doc = self.get_doc(sim.c_file)
            if doc:
                if sim.c_line in doc.breakpoints:
                    doc.goto_line(self.sim.c_line)
                    doc.Update()
                    self.log(str(sim.c_line))
                    self.log(str(doc.breakpoints))
                    self.pause = True
                    self.toolbar.btn_pause()
        
            
    #-------------------------------------------------------------------
    def sim_run(self, command):
        
        if self.mcu_name == "mcs51":
            self.sim = mcs51.Sim(self, self.ihx_path, self.file_list, command)
            s = self.sim.get_records_string()
        elif self.mcu_name == 'pic16':
            self.sim = pic16.Sim(self, self.ihx_path, self.file_list, self.mcu_name, self.mcu_device)
            s = self.sim.disassembly()
        elif self.mcu_name == 'pic14':
            self.sim = pic14.Sim(self, self.ihx_path, self.file_list, self.mcu_name, self.mcu_device)
            s = self.sim.disassembly()
            
        self.asm_view.SetText(s)
        self.sim.start()
        self.running = True
        if self.debug_mode:
            self.pause = True
            self.toolbar.btn_pause()
            #return
            
        #if not self.debug_mode:
        self.timer2 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer2Timer, self.timer2)
        self.timer2.Start(10)
        self.sim_update()
        #self.toolbar.btn_run()
        
    #-------------------------------------------------------------------
    def sim_stop(self):
        if self.running:
            self.running = False
            if hasattr(self, 'timer2'):
                self.Unbind(event=wx.EVT_TIMER, source=self.timer2, handler=self.OnTimer2Timer)
                self.timer2.Stop()
                del self.timer2
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
        
        s = '%04X' % sim.pc
        self.asm_view.search_addr(s)
        
        s = '%06x' % sim.pc
        for t in self.doc_book.docs:
            if t[1].file_path.endswith('st'):
                t[1].search_addr(s)
            
        #uart sbuf
        for ch in sim.sbuf_list:
            self.sbuf.append(ch)
            
        sim.sbuf_list = []
            
        doc = self.get_doc(sim.c_file)
        if doc:
            doc.goto_line(sim.c_line)
            doc.Update()
            #self.doc_book.SetSelection(doc.page_index)
            
        self.reg_panel.update_inst(sim, self.sbuf)
        self.reg_panel.update(sim)
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
    def OnRun(self, event):
        self.pause = False
        self.command = None
        self.debug_mode = False
        #self.sim_run('run')
        
    #-------------------------------------------------------------------
    def OnPause(self, event):
        self.pause = True
        
    #-------------------------------------------------------------------
    def OnContinue(self, event):
        self.pause = False
        
    #-------------------------------------------------------------------
    def OnStep(self, event):
        if self.sim and not self.sim.stopped :
            #self.sim.step_c_line()
            self.sim.step()
            self.sim_update()
            
    #-------------------------------------------------------------------
    def OnStepOver(self, event):
        if self.sim and not self.sim.stopped :
            result = self.sim.step_over()
            if result == 'not finished':
                pass
            self.sim_update()
            
    #-------------------------------------------------------------------
    def OnStepOut(self, event):
        if self.sim and not self.sim.stopped :
            self.sim.step_out()
            self.sim_update()
            
    #-------------------------------------------------------------------
    def OnStop(self, event):
        if self.sim is not None:
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
        self.log_view.WriteText(s)
        
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
    def open_file(self, file_path):
        print(file_path)
        path = os.path.dirname(file_path)
        if path != '':
            os.chdir(path)
            
        path, ext = file_path.split('.')
        
        if os.path.exists(path + '.c'):
            doc = self.doc_book.open_file(path + '.c')
            #doc.add_breakpoints(self.breakpoints)
            self.doc_list.append(doc)
        
        #self.doc_asm = self.doc_book.open_file(path + '.asm')
        if self.mcu_name == 'pic16' or self.mcu_name == 'pic14':
            if os.path.exists(path + '.lst'):
                self.doc_book.open_file(path + '.lst')
            elif os.path.exists(path + '.asm'):
                self.doc_book.open_file(path + '.asm')
                
            if os.path.exists(path + '.hex'):
                self.doc_book.open_file(path + '.hex')
                self.ihx_path = path + '.hex'
                self.doc_c = doc            
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
                self.doc_c = doc
            elif os.path.exists(path + '.hex'):
                self.doc_book.open_file(path + '.hex')
                self.ihx_path = path + '.hex'
                self.doc_c = doc
        self.doc_book.SetSelection(0)
        
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
            
        
        del config
        
    #-------------------------------------------------------------------
    def stop(self):
        print "stop"
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
        self.Destroy()
        
    #-------------------------------------------------------------------
    def __del__(self):
        print "__del__"
        try:
            if self.parent is not None:
                self.parent.sim_close()
        except:
            print "Error: unable to UnInit SimFrame.mgr"

    #-------------------------------------------------------------------
    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        print "OnClose"
        self.stop()
        event.Skip()
        
        

#---------------------------------------------------------------------------------------------------
class SimFrame (wx.Frame):

    def __init__(self, app, parent, file_list, config_file):
        wx.Frame.__init__ (self, parent, id = wx.ID_ANY, title = file_list[0], 
                            pos = wx.DefaultPosition, size = wx.Size(1280,800), 
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        self.app = app
        self.parent = parent
        self.sim = None
        self.log_queue = Queue.Queue()
        self.config_file = config_file
        self.mcu_name = "mcs51"
        self.mcu_device = ""
        
        self.breakpoints = []  #breakpoints
        self.sbuf = []
        
        self.load_config()
        
        self.SetSizeHintsSz(wx.Size(640,480), wx.DefaultSize)
        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(self)
        self.mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT)

        self.statusbar = self.CreateStatusBar()

        #add tool bar
        self.toolbar = SimToolbar(self, self.mgr)
        
        #add doc notebook for source code review
        self.doc_book = DocBook(app, self)
        self.doc_book.SetMinSize(wx.Size(120,-1))
        
        #add doc_book to AuiManager
        self.mgr.AddPane(self.doc_book, wx.aui.AuiPaneInfo().Right().PinButton(True).Dock().Resizable().FloatingSize(wx.Size(298,206)).DockFixed(False).Layer(0).CentrePane())

        #add debug information panel notebook
        nb2 = wx.aui.AuiNotebook(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(300,-1), wx.aui.AUI_NB_DEFAULT_STYLE)
        nb2.SetMinSize(wx.Size(200,-1))
        
        if self.mcu_name == "mcs51":
            panel = self.reg_panel = mcs51.WatchPanel(nb2)
        elif self.mcu_name == "pic16":
            panel = self.reg_panel = pic16.WatchPanel(nb2, self.mcu_name, self.mcu_device)
        elif self.mcu_name == "pic14":
            panel = self.reg_panel = pic14.WatchPanel(nb2, self.mcu_name, self.mcu_device)            
        else:
            panel = self.reg_panel = mcs51.WatchPanel(nb2)
        nb2.AddPage(panel, u"Watches")
        
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
        self.Bind(wx.EVT_TOOL, self.OnRun,     id=ID_RUN)
        self.Bind(wx.EVT_TOOL, self.OnContinue, id=ID_DBG_CONTINUE)
        self.Bind(wx.EVT_TOOL, self.OnPause,   id=ID_DBG_PAUSE)
        self.Bind(wx.EVT_TOOL, self.OnStop,    id=ID_DBG_STOP)
                
        file_list = self.find_included_source(file_list)
        self.file_list = file_list
        self.file_path = file_list[0]
        for f in file_list:
            f1 = f.replace('.c', '.ihx')
            f2 = f.replace('.c', '.hex')
            if os.path.exists(f1):
                self.ihx_path = f1
                break
            elif os.path.exists(f2):
                self.ihx_path = f2
                break
            
        self.command = 'run' 

        self.debug_mode = False
        self.toolbar.btn_run()
            
        self.sim = None
        self.timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer1Timer, self.timer1)
        self.timer1.Start(800)
        self.pause = False
        #event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_RUN)
        #wx.PostEvent(self.toolbar, event)    
        
    #-------------------------------------------------------------------
    def OnTimer1Timer(self, event):  
        self.SetStatusText(time.asctime())
        if self.command == 'run':
            self.timer1.Stop()
            self.sim_run(self.command)
            self.timer1.Start(100)

            self.pause = False
            self.running = True

            self.command = None
        
        if self.sim is None:
            return
        
        if self.sim.stopped:
            self.sim_stop()
            return
        
        if self.pause:
            return
        
        self.sim_update()
        
    #-------------------------------------------------------------------
    def OnTimer2Timer(self, event):
        if self.pause:
            return
        
        sim = self.sim
        if sim and not sim.stopped :
            sim.step()

        
    #-------------------------------------------------------------------
    def sim_run(self, command):
        
        if self.mcu_name == "mcs51":
            self.sim = mcs51.Sim(self, self.ihx_path, self.file_list, command)
        elif self.mcu_name == 'pic16':
            self.sim = pic16.Sim(self, self.ihx_path, self.file_list, self.mcu_name, self.mcu_device)
        elif self.mcu_name == 'pic14':
            self.sim = pic14.Sim(self, self.ihx_path, self.file_list, self.mcu_name, self.mcu_device)

        self.sim.start()
        self.running = True
            
        #if not self.debug_mode:
        self.timer2 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer2Timer, self.timer2)
        self.timer2.Start(10)
        self.sim_update()
        self.toolbar.btn_run()
        
    #-------------------------------------------------------------------
    def sim_stop(self):
        if self.running:
            self.running = False
            if hasattr(self, 'timer2'):
                self.Unbind(event=wx.EVT_TIMER, source=self.timer2, handler=self.OnTimer2Timer)
                self.timer2.Stop()
                del self.timer2
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
                
        #uart sbuf
        for ch in sim.sbuf_list:
            self.sbuf.append(ch)
            
        sim.sbuf_list = []
            
        self.reg_panel.update_inst(sim, self.sbuf)
        self.reg_panel.update(sim)
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
        self.toolbar.btn_reset()
        
    #-------------------------------------------------------------------
    def OnRun(self, event):
        self.pause = False
        self.command = None
        self.sim_run('run')
        
    #-------------------------------------------------------------------
    def OnPause(self, event):
        self.pause = True
        
    #-------------------------------------------------------------------
    def OnContinue(self, event):
        self.pause = False
        
    #-------------------------------------------------------------------
    def OnStep(self, event):
        if self.sim and not self.sim.stopped :
            #self.sim.step_c_line()
            self.sim.step()
            self.sim_update()
            
    #-------------------------------------------------------------------
    def OnStepOver(self, event):
        if self.sim and not self.sim.stopped :
            self.sim.step_over()
            self.sim_update()
            
    #-------------------------------------------------------------------
    def OnStepOut(self, event):
        if self.sim and not self.sim.stopped :
            self.sim.step_out()
            self.sim_update()
            
    #-------------------------------------------------------------------
    def OnStop(self, event):
        if self.sim is not None:
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
        pass
        #self.log_view.WriteText(s)
        
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
            
        
        del config
        
    #-------------------------------------------------------------------
    def stop(self):
        print "stop"
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
        self.Destroy()
        
    #-------------------------------------------------------------------
    def __del__(self):
        print "__del__"
        try:
            if self.parent is not None:
                self.parent.sim_close()
        except:
            print "Error: unable to UnInit SimFrame.mgr"

    #-------------------------------------------------------------------
    # Virtual event handlers, overide them in your derived class
    def OnClose(self, event):
        print "OnClose"
        self.stop()
        event.Skip()
        
        

        

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    app = wx.PySimpleApp()    
    
    #lst = ["/home/athena/src/8051/BlinkLEDs/main.c"]    
    #lst = ["/home/athena/src/8051/blink_c/blink1.c","/home/athena/src/8051/blink_c/delay_ms.c","/home/athena/src/8051/blink_c/paulmon2.c"]
    if wx.Platform == '__WXMSW__' :
        lst = ["c:/src/8051/t0/t0.c"]
    else:
        #lst = ["/home/athena/src/8051/t0/t0.c"]
        test = 2
        if test == 1:
            lst = ["/home/athena/src/8051/BlinkLEDs/main.c"]
            config_file = "/home/athena/src/8051/BlinkLEDs/main.sdcfg"
        else:
            lst = ["/home/athena/src/pic/test1/test.c"]
            config_file = "/home/athena/src/pic/test1/test.sdcfg"
    frame = SimFrame(app, None, lst, config_file, 'debug')
    
    app.SetTopWindow(frame)
    frame.Show(True)    
    
    app.MainLoop()