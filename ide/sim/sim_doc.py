import os
import signal
import sys
import time
import subprocess
import wx
import wx.stc as stc
import re
import Queue

from sim_doc_base import DocBase
import sim_doc_lexer as doc_lexer
#test_cmd = {"break 30\n", "break 40\n", "run\n", "continue\n", 
#        "step\n", "step\n",  "step\n", "step\n", "step\n", "step\n", "step\n", "quit\n",}

#-- Markers for editor marker margin
MARKNUM_BREAK_POINT   = 1
MARKVAL_BREAK_POINT   = 1
MARKNUM_CURRENT_LINE  = 2
MARKVAL_CURRENT_LINE  = 4

#---------------------------------------------------------------------------------------------------
class Doc(DocBase):
    
    def __init__(self, parent, file_path):
        DocBase.__init__(self, parent, file_path)
        doc_lexer.c_lexer(self)
        
        path, ext = file_path.split('.')
        if ext == 'c':
            self.breakpoints = []
            
            #-- connect event with doc margin click to toggle breakpoint
            self.Bind(stc.EVT_STC_MARGINCLICK, self.OnDocMarginClick)
        else:
            self.breakpoints = None

    #-------------------------------------------------------------------
    def add_breakpoints(self, b_lst):
        if self.breakpoints is None:
            return
        for line in b_lst:
            if not line in self.breakpoints:
                self.MarkerAdd(line, MARKNUM_BREAK_POINT)
                self.breakpoints.append(line)
        
    #-------------------------------------------------------------------
    def clear_cur_line_marker(self, line):
        self.MarkerDelete(line, MARKNUM_CURRENT_LINE)

    #-------------------------------------------------------------------
    def toggle_breakpoint(self, line):
        markers = self.MarkerGet(line)
        c_line = line + 1
        if not c_line in self.breakpoints:
            self.MarkerAdd(line, MARKNUM_BREAK_POINT)
            self.breakpoints.append(c_line)
        else:
            self.MarkerDelete(line, MARKNUM_BREAK_POINT)
            self.breakpoints.remove(c_line)

        #--print(self.breakpoints)
        
    #-------------------------------------------------------------------
    def OnDocMarginClick(self, event):
        if self.breakpoints is None:
            return
        
        line = self.LineFromPosition(event.GetPosition())
        margin = event.GetMargin()
        #log(margin)
        if margin == 1 :
            #log("toggle")
            self.toggle_breakpoint(line)
        elif margin == 2 :
            if wx.GetKeyState(wx.WXK_SHIFT) and wx.GetKeyState(wx.WXK_CONTROL) :
                FoldSome()
            else:
                level = self.GetFoldLevel(line)
                if hasbit(level, stc.STC_FOLDLEVELHEADERFLAG) :
                    self.ToggleFold(line)