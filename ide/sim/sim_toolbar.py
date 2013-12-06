import os
import wx
from sim_global import *


#---------------------------------------------------------------------------------------------------
class Toolbar():
    def __init__(self, frame, aui_mgr):

        self.path = os.path.dirname(os.path.realpath(__file__)) + os.sep
        
        tb2_lst = [
            [ID_DBG_STOP,      "Stop Debug", "images/stop.png",       "Stop debugger"],
            [ID_DBG_RESET,     "Reset Debug","images/reset.png",      "Restart"],
            #[ID_RUN,           "Run",        "images/play.png",       "Run"],
            [],            
            [ID_DBG_CONTINUE,  "Debug",      "images/play.png",       "Continue"],
            [ID_DBG_PAUSE,     "Pause Debug","images/pause.png",      "Pause"],
            [],
            [ID_DBG_STEP,      "Step",       "images/dbgstep.png",    "Next Step"],
            [ID_DBG_STEP_OVER, "Step Over",  "images/dbgnext.png",    "Step over function"],
            [ID_DBG_STEP_OUT,  "Step Out",   "images/dbgstepout.png", "Step out current function"],
        ]

        self.tb2 = self.add_tools(frame, aui_mgr, "debug toolbar", tb2_lst)
        
        self.tb2.Bind(wx.EVT_TOOL, self.OnReset, id=ID_DBG_RESET)
        self.tb2.Bind(wx.EVT_TOOL, self.OnContinue, id=ID_DBG_CONTINUE)
        self.tb2.Bind(wx.EVT_TOOL, self.OnPause, id=ID_DBG_PAUSE)
        self.tb2.Bind(wx.EVT_TOOL, self.OnStop, id=ID_DBG_STOP)
        
    def btn_run(self):
        self.btn_continue()

    def btn_reset(self):
        self.btn_pause()
            
    def btn_stop(self):
        self.tb2.EnableTool(ID_DBG_RESET, True)
        #self.tb2.EnableTool(ID_RUN, True)
        self.tb2.EnableTool(ID_DBG_PAUSE, False)
        self.tb2.EnableTool(ID_DBG_CONTINUE, False)
        self.tb2.EnableTool(ID_DBG_STOP, False)
        
        self.tb2.EnableTool(ID_DBG_STEP, False)
        self.tb2.EnableTool(ID_DBG_STEP_OVER, False)
        self.tb2.EnableTool(ID_DBG_STEP_OUT, False)

    def btn_pause(self):
        self.tb2.EnableTool(ID_DBG_RESET, True) 
        #self.tb2.EnableTool(ID_RUN, False)
        self.tb2.EnableTool(ID_DBG_PAUSE, False)
        self.tb2.EnableTool(ID_DBG_CONTINUE, True)
        self.tb2.EnableTool(ID_DBG_STOP, True) 
        
        self.tb2.EnableTool(ID_DBG_STEP, True)
        self.tb2.EnableTool(ID_DBG_STEP_OVER, True)
        self.tb2.EnableTool(ID_DBG_STEP_OUT, True)
        
    def btn_continue(self):
        self.tb2.EnableTool(ID_DBG_RESET, False)
        #self.tb2.EnableTool(ID_RUN, False)
        self.tb2.EnableTool(ID_DBG_PAUSE, True)
        self.tb2.EnableTool(ID_DBG_CONTINUE, False)
        self.tb2.EnableTool(ID_DBG_STOP, True)
        
        self.tb2.EnableTool(ID_DBG_STEP, False)
        self.tb2.EnableTool(ID_DBG_STEP_OVER, False)
        self.tb2.EnableTool(ID_DBG_STEP_OUT, False)
        
    def enable_step_out(self, bool_flag):
        self.tb2.EnableTool(ID_DBG_STEP_OUT, bool_flag)

    def OnRun(self, event):
        self.btn_run()
        if event is not None:
            event.Skip()
        
    def OnReset(self, event):
        self.btn_reset()
        if event is not None:
            event.Skip()
            
    def OnStop(self, event):
        self.btn_stop()
        if event is not None:
            event.Skip()
        
    def OnPause(self, event):
        self.btn_pause()
        if event is not None:
            event.Skip()
        
    def OnContinue(self, event):
        self.btn_continue()
        
        if event is not None:
            event.Skip()
                
        
    #-------------------------------------------------------------------
    def toolbar(self, frame):
        tb = wx.ToolBar(frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL)
        tb.SetToolBitmapSize(wx.Size(16,16))
        return tb
    
    #-------------------------------------------------------------------
    def add_to_aui(self, tb, aui_mgr, name):
        tb.Realize()
        aui_mgr.AddPane(tb, wx.aui.AuiPaneInfo().
                          Name(name).Caption("").
                          ToolbarPane().Top().Row(1).
                          LeftDockable(False).RightDockable(False))
        
    #-------------------------------------------------------------------
    def get_bitmap(self, icon):
        if icon[0:2] == "wx":
            bmp = wx.ArtProvider.GetBitmap(icon, wx.ART_TOOLBAR, wx.Size(16,16))
        else:
            bmp = wx.Bitmap(self.path + icon)
        return bmp
        
    #-------------------------------------------------------------------
    def add_tools(self, frame, aui_mgr, name, lst):
        tb = self.toolbar(frame)        
        for i, t in enumerate(lst):
            if len(t) == 0:
                tb.AddSeparator()
            else:
                bmp = self.get_bitmap(t[2])
                tb.AddLabelTool(t[0], t[1], bmp, wx.NullBitmap, wx.ITEM_NORMAL, t[3], wx.EmptyString, None)
                
        if aui_mgr is not None:
            self.add_to_aui(tb, aui_mgr, name)
            
        return tb
    
    
#---- for testing -------------------------------------------------------------
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None)
    Toolbar(frame, None)
    app.SetTopWindow(frame)
    f.Show(True)
    app.MainLoop()