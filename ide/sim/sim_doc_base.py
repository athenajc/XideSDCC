import os.path
import sys
import wx
import wx.stc as stc
import subprocess

from sim_global import *
import sim_doc_lexer as doc_lexer

import re


#---------------------------------------------------------------------------------------------------
class DocPopMenu(wx.Menu):
    def __init__(self, frame, doc):
        menu_lst = [
            [ID_RUN,       "Run\tF6",         "Run the program simulation"],
            [ID_COMPILE,   "Compile",         "Compile current file"],
            [],
            [ID_DBG_START, "Debug run\tF5",   "Run at debugger mode"],
            [ID_DBG_STOP,  "Stop Debug",      "Stop and destroy debugger"],
            [],
            [ID_UNDO,      "&Undo\tCtrl-Z",       "Undo the editing"],    
            [ID_REDO,      "&Redo\tCtrl-Y",       "Redo the undo editing"],  
            [],
            [ID_CUT,       "Cu&t\tCtrl-X",        "Cut selected text to clipboard"], 
            [ID_COPY,      "&Copy\tCtrl-C",       "Copy selected text to the clipboard"],
            [ID_PASTE,     "&Paste\tCtrl-V",      "Paste text from clipboard"],
            [ID_SELECTALL, "Select A&ll\tCtrl-A", "Select all text"],
            [],
            [ID_FIND,      "&Find\tCtrl-F",       "Find string"],
            [ID_FINDNEXT,  "Find Next\tF3",       "Find next match string"],
            [ID_REPLACE,   "Replace\tCtrl-H",     "Replace string"],
            
            [],
            [ID_SAVE,    "&Save\tCtrl-S",       "Save the current document"],
            [ID_SAVEAS,  "Save &As...\tAlt-S",  "Save the current document to a file with a new name"],
            [ID_SAVEALL, "Save A&ll...\tCtrl-Shift-S", "Save all open documents"], 
            [],
            [ID_CLOSE,   "&Close file\tCtrl+W",  "Close the current file"],
            [ID_CLOSEALL,   "Close all files",  "Close all current opened files"],
            [],
            ]
        wx.Menu.__init__(self)
        menu = self
        for m in menu_lst:
            if m == []:
                menu.AppendSeparator()
            else:
                if type(m[0]) == type('str'):
                    menu_id = get_id(m[0])
                else:
                    menu_id = m[0]
                menu.Append(menu_id, m[1], m[2])

        self.app = frame.app
        self.frame = frame
        self.doc = doc
        
    #-------------------------------------------------------------------
    def popup(self):
        doc = self.doc
        self.Enable(ID_UNDO, doc.CanUndo())
        self.Enable(ID_REDO, doc.CanRedo())
        self.Enable(ID_PASTE,  doc.CanPaste())
        
        
#---------------------------------------------------------------------------------------------------
class StyledText(stc.StyledTextCtrl):
    def __init__(self, parent):
        stc.StyledTextCtrl.__init__(self, parent, wx.NewId(), pos=wx.DefaultPosition, size=wx.DefaultSize, style=0)
        doc_lexer.init_default_style(self)
        doc_lexer.c_lexer(self)
        self.SetSelBackground(True, wx.Colour(0xff, 0xff, 0))
        
        self.ID_FIND = wx.NewId()
        self.ID_FIND_NEXT = wx.NewId()
        #menu = wx.Menu()        
        #menu.Append(self.ID_FIND,      "&Find\tCtrl-F",       "Find string")
        #menu.Append(self.ID_FIND_NEXT,  "Find Next\tF3",       "Find next match string")
        #self.pop_menu = menu
        
        # bind events
        #self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)       
        self.Bind(wx.EVT_MENU, self.OnShowFind,   id=self.ID_FIND)
        self.Bind(wx.EVT_MENU, self.OnFindNext,   id=self.ID_FIND_NEXT)
        
        self.register_hot_key()
        self.Bind(wx.EVT_HOTKEY, self.OnHotKey, id=self.hotKeyId)
        randomId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onKeyCombo, id=randomId)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('F'), randomId )])
        self.SetAcceleratorTable(accel_tbl)

    #----------------------------------------------------------------------
    def onKeyCombo(self, event):
        """"""
        #print "You pressed CTRL+F!"
        self.OnShowFind(event)

    def register_hot_key(self):
        """
        This function registers the hotkey Alt+F1 with id=100
        """
        self.hotKeyId = wx.NewId()
        self.RegisterHotKey(
            self.hotKeyId, #a unique ID for this hotkey
            wx.ACCEL_CTRL, #the modifier key
            ord('F')) #the key to watch for
        
    def OnHotKey(self, event):
        """
        Prints a simple message when a hotkey event is received.
        """
        print "do hot key actions"        
        self.OnShowFind(event)

    #-------------------------------------------------------------------
    def OnRightDown(self, event):
        self.PopupMenu(self.pop_menu, event.GetPosition())    
        
    #-------------------------------------------------------------------
    def bind_find_event(self):    
        #-- connect event handler
        self.Bind(wx.EVT_FIND,             self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT,        self.OnFind)
        self.Bind(wx.EVT_FIND_CLOSE,       self.OnFindClose)
        
    #-------------------------------------------------------------------
    def unbind_find_event(self):    
        #-- connect event handler
        self.Unbind(wx.EVT_FIND,             handler=self.OnFind)
        self.Unbind(wx.EVT_FIND_NEXT,        handler=self.OnFind)
        self.Unbind(wx.EVT_FIND_CLOSE,       handler=self.OnFindClose)
        
    #-------------------------------------------------------------------
    def OnShowFind(self, event):
        #-- create wxFindReplaceData for search
        self.find_data = wx.FindReplaceData()

        #-- initial the find string by selection
        token = self.GetSelectedText()
        #--log("find "+token)
        self.find_data.SetFindString(token)

        find_dlg = wx.FindReplaceDialog(self, self.find_data, "Find")
        self.bind_find_event()
        
        #-- initial the latest position for start position
        self.latest_pos = self.GetSelectionStart() + len(token) #self.GetSelectionStart()
        
        find_dlg.Show(True)    
        
    #-------------------------------------------------------------------
    def find_next(self, flag, s):
        #set the search anchor
        self.SetCurrentPos(self.latest_pos)
        self.SearchAnchor()
                    
        pos = self.SearchNext(flag, s) 
        if pos < 0:
            self.DocumentStart()
            self.SearchAnchor()
            pos = self.SearchNext(flag, s)
        
        self.latest_pos = pos + len(s)
            
        self.EnsureCaretVisible()

    #-------------------------------------------------------------------
    def OnFindNext(self, event):
        if (self.find_str == "") :
            OnShowFind(event)
        else:
            self.find_next(self.find_flags, self.find_str)
            
    #-------------------------------------------------------------------
    def OnFind(self, event):
        self.find_flags = event.GetFlags()
        self.find_str = event.GetFindString()
        pos = self.find_next(self.find_flags, self.find_str)
        
    #-------------------------------------------------------------------
    def OnFindClose(self, event):
        self.unbind_find_event()
        event.GetDialog().Destroy()
        
    #-------------------------------------------------------------------
    def WriteText(self, s):
        self.SetText(s)
        
    #-------------------------------------------------------------------
    def goto_line(self, line):
        #log("goto ", line)
        if line > 0:
            line = line - 1
        self.EnsureVisibleEnforcePolicy(line)
        self.GotoLine(line)
        p1 = self.PositionFromLine(line)
        p2 = self.GetLineEndPosition(line)

        self.SetSelection(p1, p2)
        
    #-------------------------------------------------------------------
    def search_addr(self, token):
        text = self.GetText()
        i = 0
        token = token.upper()
        for line in text.split('\n'):
            i += 1
            n = line.find(token)
            if n >= 0 and n < 20:
                self.goto_line(i)
                return i
            
            
        return 0
  
#---------------------------------------------------------------------------------------------------
class DocBase(StyledText):
    def __init__(self, parent, file_path):
        StyledText.__init__(self, parent)
        
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)

        doc_lexer.init_default_style(self)
        
        #self.SetSelectionMode
        self.SetSelBackground(True, wx.Colour(0xff, 0xff, 0))

        # init pop menu
        self.pop_menu = DocPopMenu(self.frame, self)
        # init include file list
        self.inc_lst = []
        
        # bind popup menu event
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

    #-------------------------------------------------------------------
    def OnRightDown(self, event):
        # append include file path to pop menu
        if self.inc_lst == []:
            self.find_include_file()
        self.pop_menu.popup()
        self.PopupMenu(self.pop_menu, event.GetPosition() + wx.Point(10, 0))
            
    #-------------------------------------------------------------------
    def find_include_file(self):
        self.inc_lst = []
        s = self.GetText()
        
        # if select include file
        if s.find("#include") >= 0 :
            m = wx.Menu()

            self.pop_menu.AppendSubMenu(m, "Open include files")
            matches = re.findall(r'\#include\s+\<(.+?)\>', s)
            for name in matches:
                name = name.strip()
                name = os.path.basename(name)
                
                nid = wx.NewId()
                self.inc_lst.append([nid, name, 'global'])
                m.Append(nid, '&Open ' + name, 'Search and Open header file')
                self.Bind(wx.EVT_MENU, self.OnOpenHeaderFile,  id=nid)
            
            matches = re.findall(r'\#include\s+\"(.+?)\"', s)
            for name in matches:
                name = name.strip()
                name = os.path.basename(name)
                nid = wx.NewId()
                self.inc_lst.append([nid, name, 'local'])
                m.Append(nid, '&Open ' + name, 'Search and Open header file')
                self.Bind(wx.EVT_MENU, self.OnOpenHeaderFile,  id=nid)
  

    #-------------------------------------------------------------------
    def OnOpenHeaderFile(self, event):
        local_path = self.dirname
        
        obj = event.GetEventObject()
        nid = event.GetId()
        
        for t in self.inc_lst:
            if nid == t[0]:
                inc_name = t[1]
                print inc_name
                path = search_file(local_path, inc_name)
                if path == "":
                    path = search_file(SDCC_inc_path, inc_name)
                if path == "":
                    path = search_file('/home/', inc_name)
                if path != "":
                    print path
                    self.app.open_file(path)
                    
    #-------------------------------------------------------------------
    def get_selected_line_text(self):
        return self.GetSelectedTextRaw()
    
    #-------------------------------------------------------------------
    def get_selected_text(self):
        return self.GetSelectedText()
    
    #-------------------------------------------------------------------
    def deselection(self):
        self.SetSelection(0, 0)
        
    #-------------------------------------------------------------------
    def set_range_visible(self, pos_start, pos_end):
        if pos_start > pos_end :
            pos_start, pos_end = pos_end, pos_start

        line_start = self.LineFromPosition(pos_start)
        line_end   = self.LineFromPosition(pos_end) + 2
        for line in range(line_start, line_end):
            self.EnsureVisibleEnforcePolicy(line)
            
    #-------------------------------------------------------------------
    def goto_position(self, pos):
        line = self.LineFromPosition(pos)
        self.goto_line(line + 1)
        
    #-------------------------------------------------------------------
    def goto_line(self, line):
        #log("goto ", line)
        if line > 0:
            line = line - 1
        self.EnsureVisibleEnforcePolicy(line)
        self.GotoLine(line)
        p1 = self.PositionFromLine(line)
        p2 = self.GetLineEndPosition(line)

        self.SetSelection(p1, p2)
        
    #-------------------------------------------------------------------
    def search_text(self, token):
        p1 = self.FindText(1, self.GetLength(), token, 0)
        p2 = p1 + len(token)
        self.set_range_visible(p1, p2)
        self.SetSelection(p1, p2)
        return 0
    


