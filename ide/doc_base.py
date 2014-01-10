import os.path
import sys
import wx
import wx.stc as stc
import subprocess

from ide_global import *
import doc_lexer


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
        name = doc.file_name
        is_c_file = name.find('.c') > 0
            
        self.Enable(ID_RUN, is_c_file)
        self.Enable(ID_COMPILE, is_c_file)
            
        self.Enable(ID_DBG_START, is_c_file)
        self.Enable(ID_DBG_STOP, is_c_file)
            
        
#---------------------------------------------------------------------------------------------------
class StyledText(stc.StyledTextCtrl):
    """ Inherit from stc.StyledTextCtrl, extent with CRTL-F find """
    
    def __init__(self, parent):
        stc.StyledTextCtrl.__init__(self, parent, wx.NewId(), pos=wx.DefaultPosition, size=wx.DefaultSize, style=0)
        doc_lexer.init_default_style(self)
        doc_lexer.c_lexer(self)
        self.SetSelBackground(True, wx.Colour(0xff, 0xff, 0))
        
        self.ID_FIND = wx.NewId()
        self.ID_FIND_NEXT = wx.NewId()
        menu = wx.Menu()        
        menu.Append(self.ID_FIND,      "&Find\tCtrl-F",       "Find string")
        menu.Append(self.ID_FIND_NEXT,  "Find Next\tF3",       "Find next match string")
        self.pop_menu = menu
        
        # bind events
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)       
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

    #----------------------------------------------------------------------
    def register_hot_key(self):
        """
        This function registers the hotkey Crtl+F with id=self.hotKeyId
        """
        self.hotKeyId = wx.NewId()
        self.RegisterHotKey(
            self.hotKeyId, #a unique ID for this hotkey
            wx.ACCEL_CTRL, #the modifier key
            ord('F')) #the key to watch for
        
    #----------------------------------------------------------------------
    def OnHotKey(self, event):
        """
        On user press Ctrl_F, show find dialog
        """
        #print "do hot key actions"        
        self.OnShowFind(event)

    #-------------------------------------------------------------------
    def OnRightDown(self, event):
        """
        On user press mouse Right button, show popup menu
        """        
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
        p1 = self.FindText(1, self.GetLength(), token, 0)
        line = self.LineFromPosition(p1)
        self.goto_line(line)
        return line
    
    #-------------------------------------------------------------------
    def get_line(self):
        return self.LineFromPosition(self.GetCurrentPos())
    
    
#---------------------------------------------------------------------------------------------------
class DocBase(StyledText):
    def __init__(self, parent, file_path):
        StyledText.__init__(self, parent)
        #print("doc_base", file_path)
        
        self.modified = None
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.breakpoints = []
        self.func_list = []
        self.app = parent.app
        self.frame = self.app.frame
        
        doc_lexer.init_default_style(self)
        
        #self.SetSelectionMode
        self.SetSelBackground(True, wx.Colour(0xff, 0xff, 0))

        #-- connect event with doc modified
        self.Bind(stc.EVT_STC_SAVEPOINTLEFT, self.OnDocModified)
        self.Bind(stc.EVT_STC_CHARADDED, self.OnDocKeyPressed)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnDocMarginClick)

        self.dt = FileDropTarget(self)
        self.SetDropTarget(self.dt)
        
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
    def stop(self):
        pass
    
    #-------------------------------------------------------------------
    def close(self):
        self.stop()

    #-------------------------------------------------------------------
    def drop_file(self, x, y, file_name):
        log("Dropfile", file_name)
        self.app.open_file(file_name)
        
    #-------------------------------------------------------------------
    def exec_cmd(self, cmd):
        os.chdir(os.path.dirname(self.file_path))
        wx.Shell(cmd)
        
    #----------------------------------------------------------------------
    def run_cmd(self, cmd):
        proc = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc is None:
            return False
        
        warn_count = 0
        err_count = 0
        
        for line in proc.stdout.readlines():
            if line == "\n":
                dprint("", line)
            elif line.find("warning") >= 0:
                log("find warning", line.find("warning"))
                warn_count += 1
                dprint("Warning", line)
            elif line.find("error") >= 0:
                err_count += 1
                dprint("Error", line)                
            else:
                dprint("Info", line)

        for line in proc.stderr.readlines():
            if line == "\n":
                dprint("", line)
            else:
                err_count += 1
                dprint("Error", line)

        dprint("Done", self.file_path + " compilation done.")
        if err_count == 0 :
            r = "Pass"
        else:
            r = "Fail"

        dprint(r, "Error:" + str(err_count) + ", Warning:" + str(warn_count))
        self.app.show_debug()
        if err_count > 0:
            return False
        else:
            return True
        
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
        log("goto ", line)
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
    
    #-------------------------------------------------------------------
    def check_modified(self, dt):
        if file_exist(self.file_path) == False :
            return
        
        ft = os.path.getmtime(self.file_path)
        if ft > dt :
            if self.check_file_content_changed():
                self.ask_if_reload("Save on modified outside")
                
    #-------------------------------------------------------------------
    def set_unmodified(self):
        self.modified = False
        doc_book = self.app.doc_book
        doc_book.SetPageText(self.page_index, self.file_name)
        
    #-------------------------------------------------------------------
    def load_config(self):
        pass
    
    #-------------------------------------------------------------------
    def open_file(self, file_path):
        #print("Open", file_path, self.page_index)
        self.LoadFile(file_path)
        self.get_func_list(self.app.functree)
        self.set_unmodified()
            
    #-------------------------------------------------------------------
    def save_file(self):
        if self.modified :
            self.SaveFile(self.file_path)
            self.set_unmodified()
            
    #-------------------------------------------------------------------
    def read_file(self):
        with open(self.file_path, 'r') as content_file:
            content = content_file.read()
        return content
    
    #-------------------------------------------------------------------
    def check_file_content_changed(self):
        s = self.read_file()
        if s == self.GetText():
            return False
        else:
            return True
        
    #-------------------------------------------------------------------
    def ask_if_reload(self, msg):
        strs = self.file_path + " is modified by other application. Do you want to reload?"
        dlg = wx.MessageDialog(self, strs, msg, wx.YES_NO)
        result = dlg.ShowModal()
        dlg.Destroy()
        #log("ask if reload %x, %x, %x, %x" % (result, wx.ID_YES, wx.ID_CANCEL, wx.ID_NO))
        if result == wx.ID_YES :
            #--print("load ", self.file_path)
            self.save_file()
            return wx.ID_YES
        else:
            return wx.ID_NO

    #-------------------------------------------------------------------
    def ask_if_save(self, msg):
        strs = self.file_path+ " is modified. Do you want to save?"
        dlg = wx.MessageDialog(self, strs, msg, wx.YES_NO)
        result = dlg.ShowModal()
        dlg.Destroy()
        #log("ask_if_save return=", result, "yes=", wx.ID_YES, "no=", wx.ID_NO)
        if result == wx.ID_YES :
            self.save_file()
            return wx.ID_YES
        else:
            return wx.ID_NO
        
    #-------------------------------------------------------------------
    def save_if_modified(self):
        path = self.file_path
        if (self.GetModify() == False) :
            log(path + " not modified.")
            return

        if (self.check_file_content_changed()):
            if (self.SaveFile(path)) :
                self.set_unmodified()
                log(path + " saved.")
            else:
                log("fail to save " + path)
            
    #-------------------------------------------------------------------
    def clear_cur_line_marker(self, line):
        self.MarkerDelete(line, MARKNUM_CURRENT_LINE)

    #-------------------------------------------------------------------
    def toggle_breakpoint(self, line):
        markers = self.MarkerGet(line)

        if not line in self.breakpoints:
            self.MarkerAdd(line, MARKNUM_BREAK_POINT)
            self.breakpoints.append(line)
        else:
            self.MarkerDelete(line, MARKNUM_BREAK_POINT)
            self.breakpoints.remove(line)

        #--print(self.breakpoints)
        
    #-------------------------------------------------------------------
    def OnDocMarginClick(self, event):
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
                    
    #-------------------------------------------------------------------
    def OnDocModified(self, event):
        m = self.modified
        self.modified = self.GetModify()
        if self.modified :
            self.app.doc_modified = True
            
            # means first modified
            if m == False:
                doc_book = self.app.doc_book
                doc_book.SetPageText(self.page_index, self.file_name + " *")
    
    #-------------------------------------------------------------------
    def auto_indent(self):
        """ check prev line content, set the new line indent """
        
        # get current pos and line
        pos = self.GetCurrentPos()
        line = self.LineFromPosition(pos)
        
        # i is indent
        i = self.GetIndent()
        
        # if not first line, get previous indent
        if line > 1:
            # get previous indent
            i = self.GetLineIndentation(line - 1)
            
            # check previous line content
            s = self.GetLine(line - 1)
            s = s.strip()
            if s.endswith(';'):
                # new indent same as prev line
                pass
            elif s.endswith('{') or s.endswith(':'):
                i += self.GetIndent()
                
        # set new line indentation
        self.SetLineIndentation(line, i)
        
        # move caret
        self.GotoPos(pos + i)
        
    #-------------------------------------------------------------------
    def OnDocKeyPressed(self, event):
        if self.CallTipActive() :
            self.CallTipCancel()

        key = event.GetKey()
        #print key
        if key == 10 or key == wx.stc.STC_KEY_RETURN:
            self.auto_indent()

        event.Skip()
        
        
#---------------------------------------------------------------------------------------------------
# Define File Drop Target class
class FileDropTarget(wx.FileDropTarget):    
    """ This object implements Drop Target functionality for Files """
    
    def __init__(self, obj):
        """ Initialize the Drop Target, passing in the Object Reference to
          indicate what should receive the dropped files """
        
        # Initialize the wxFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        # Store the Object Reference for dropped files
        self.obj = obj

    def OnDropFiles(self, x, y, filenames):
        """ OnDropFiles - filenames is a list of the file names dropped"""
        #log("%d file(s) dropped at %d, %d:\n" % (len(filenames), x, y))
        for fn in filenames:
            log(fn + '\n')
            self.obj.drop_file(x, y, fn)