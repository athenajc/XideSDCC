import wx
import sys

from ide_global import *
from ide_build_opt import BuildOptionDialog

#-----------------------------------------------------------------------
class Menu(wx.Menu):
    def __init__(self, parent, menu_lst=[]):
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
                if len(m) > 3 and m[3]:
                    parent.Bind(wx.EVT_MENU, m[3], id = menu_id)

#---------------------------------------------------------------------------------------------------
# Debug event handler at ide_doc_book.py
class MenuDebug(Menu):
    def __init__(self, frame, menubar):
        menu_lst = [
            [ID_RUN,       "Run\tF6",         "Run the program simulation"],
            [ID_COMPILE,   "Compile",         "Compile current file"],
            [],
            [ID_DBG_START, "Debug run\tF5",   "Run at debugger mode"],
            [ID_DBG_STOP,  "Stop Debug",      "Stop and destroy debugger"],
            ]
        Menu.__init__(self, frame, menu_lst)
        
        self.app = frame.app
        frame.menu_debug = self

        menubar.Append(self, "&Debug")

        self.Enable(ID_DBG_STOP, False)
        
    #--------------------------------------------------------------------------------
    def update_ui(self, event_id):
        if event_id == ID_RUN:
            self.Enable(ID_DBG_STOP, True)
        elif event_id == ID_DBG_START:
            self.Enable(ID_DBG_STOP, True)
        elif event_id == ID_DBG_STOP:
            self.Enable(ID_DBG_STOP, False)
        
        
#---------------------------------------------------------------------------------------------------
class MenuEdit(Menu):
    def __init__(self, frame, menubar):
        menu_lst = [
            [ID_UNDO,      "&Undo\tCtrl-Z",       "Undo the editing",   self.OnUndo],    
            [ID_REDO,      "&Redo\tCtrl-Y",       "Redo the undo editing", self.OnRedo],  
            [],                                                                           
            [ID_CUT,       "Cu&t\tCtrl-X",        "Cut selected text to clipboard", self.OnCut], 
            [ID_COPY,      "&Copy\tCtrl-C",       "Copy selected text to the clipboard", self.OnCopy],       
            [ID_PASTE,     "&Paste\tCtrl-V",      "Paste text from clipboard", self.OnPaste],
            [ID_SELECTALL, "Select A&ll\tCtrl-A", "Select all text", self.OnSelectAll],      
            [],                                                                             
            [ID_FIND,      "&Find\tCtrl-F",       "Find string", self.OnShowFind],          
            [ID_FINDNEXT,  "Find Next\tF3",       "Find next match string", self.OnFindNext],
            [ID_REPLACE,   "Replace\tCtrl-H",     "Replace string", self.OnShowReplace],
            #[],
            #[ID_FOLD,      "&Fold/Expand all\tF12", "Fold or Expand all code folds")
            ]
        Menu.__init__(self, frame, menu_lst)
        menubar.Append(self, "&Edit")

        self.app = frame.app
        frame.menu_edit = self
        self.latest_pos = 1
        self.find_flags = 0
        self.find_str = ""
        self.frame = frame
        
    #-------------------------------------------------------------------
    def bind_find_event(self):    
        #-- connect event handler
        frame = self.frame
        frame.Bind(wx.EVT_FIND,             self.OnFind)
        frame.Bind(wx.EVT_FIND_NEXT,        self.OnFind)
        frame.Bind(wx.EVT_FIND_REPLACE,     self.OnReplace)
        frame.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAll)
        frame.Bind(wx.EVT_FIND_CLOSE,       self.OnFindClose)
        
    #-------------------------------------------------------------------
    def unbind_find_event(self):    
        #-- connect event handler
        frame = self.frame
        frame.Unbind(wx.EVT_FIND,             handler=self.OnFind)
        frame.Unbind(wx.EVT_FIND_NEXT,        handler=self.OnFind)
        frame.Unbind(wx.EVT_FIND_REPLACE,     handler=self.OnReplace)
        frame.Unbind(wx.EVT_FIND_REPLACE_ALL, handler=self.OnReplaceAll)
        frame.Unbind(wx.EVT_FIND_CLOSE,       handler=self.OnFindClose)
        
    #-------------------------------------------------------------------
    def find_check_direction(self, event):
        flags = event.GetFlags() % 2
        #--log(flags)
        #--log(wx.FR_DOWN)

        if flags == wx.FR_DOWN :
            return 1
        else:
            return 0
        
    #-------------------------------------------------------------------
    #-- wxFindReplaceDialog flags are different from wxStc FindText flags
    def get_stcflags(self, fr_flags):
        stc_flags = 0

        if hasbit(fr_flags, wx.FR_WHOLEWORD) :
            stc_flags = stc_flags | stc.STC_FIND_WHOLEWORD
        
        if hasbit(fr_flags, wx.FR_MATCHCASE) :
            stc_flags = stc_flags | stc.STC_FIND_MATCHCASE
        
        return stc_flags
    
    #-------------------------------------------------------------------
    def find_prev_token(self, doc, token, flags):
        #-- get the doc text length for range setting
        n = doc.GetLength()
        stc_flags = self.get_stcflags(flags)

        #-- check if rearch the start, do the search from the end
        if self.latest_pos <= 1 :
            self.latest_pos = n

        #-- do the first search from the last time postion
        start_pos = doc.FindText(self.latest_pos, 1, token, stc_flags)

        #-- if can't find it, search from the end
        if start_pos < 0 :
            start_pos = doc.FindText(n, 1, token, stc_flags)

        #-- make founded token visible
        doc.set_range_visible(start_pos, start_pos + len(token))

        #-- store the latest position
        doc.SetSelection(start_pos, start_pos + len(token))

        self.latest_pos = start_pos - 1
        self.latest_line = doc.LineFromPosition(start_pos)
        return 0
    
    #-------------------------------------------------------------------
    def find_next_token(self, doc, token, flags):
        #-- get the text length for range setting
        n = doc.GetLength()
        stc_flags = self.get_stcflags(flags)

        if self.latest_pos > n :
            self.latest_pos = 1

        #-- do the first search from the last time postion
        start_pos = doc.FindText(self.latest_pos, n, token, stc_flags)

        #-- if can't find it, search from the start
        if start_pos < 0 or start_pos >= n :
            start_pos = doc.FindText(1, n, token, stc_flags)
            #-- if still can't find it, skip the search
            if (start_pos < 0 or start_pos >= n) :
                return -1

        #-- make founded token visible
        doc.set_range_visible(start_pos, start_pos + len(token))

        #-- highlight the selection
        doc.SetSelection(start_pos, start_pos + len(token))

        #-- store the latest position
        self.latest_pos = start_pos + len(token)
        self.latest_line = doc.LineFromPosition(start_pos)
        return 0
    
    #-------------------------------------------------------------------
    def OnReplaceAll(self, event):
        #--log("OnReplaceAll "+event.GetFindString()+ "  with  "+event.GetReplaceString() )

        doc = self.app.get_doc()
        #-- get the text length for range setting
        n = doc.GetLength()
        self.replace_str = event.GetReplaceString()
        self.find_str = event.GetFindString()
        self.find_flags = event.GetFlags()

        self.latest_pos = doc.GetSelectionStart()
        self.latest_line = doc.LineFromPosition(self.latest_pos)
        text = doc.GetText()
        match = text.find(self.find_str)
        if (match):
            text = re.sub(self.find_str, self.replace_str, text)
            doc.SetText(text)
            
        #-- select line the by replace str
        self.find_next_token(doc, self.replace_str, self.find_flags)
        
    #-------------------------------------------------------------------
    def OnFind(self, event):
        self.find_flags = event.GetFlags()
        self.find_str = event.GetFindString()        
        self.find_next_token(self.app.get_doc(), self.find_str, self.find_flags)
        log(self.find_flags, self.find_str, self.latest_line)
        
    #-------------------------------------------------------------------
    def OnFindClose(self, event):
        log("OnFindClose")
        self.unbind_find_event()
        event.GetDialog().Destroy()
        
    #-------------------------------------------------------------------
    def OnUndo(self, event):
        doc = self.app.get_doc()
        if (doc and doc.CanUndo()) :
            doc.Undo()            
            
    #-------------------------------------------------------------------
    def OnRedo(self, event):
        doc = self.app.get_doc()
        if (doc and doc.CanRedo()) :
            doc.Redo()
            
    #-------------------------------------------------------------------
    def OnCut(self, event):
        doc = self.app.get_doc()
        if (doc) :
            doc.Cut()
            
    #-------------------------------------------------------------------
    def OnCopy(self, event):
        doc = self.app.get_doc()
        if (doc) :
            doc.Copy()
            
    #-------------------------------------------------------------------
    def OnPaste(self, event):
        doc = self.app.get_doc()
        if (doc) :
            doc.Paste()
            
    #-------------------------------------------------------------------
    def OnSelectAll(self, event):
        doc = self.app.get_doc()
        if (doc) :
            doc.SelectAll()
            
    #-------------------------------------------------------------------
    def OnFindNext(self, event):
        if (find_string == "") :
            OnShowFind(event)
        else:
            self.find_next_token(self.app.get_doc(), find_str, find_flags)
            
    #-------------------------------------------------------------------
    def OnReplace(self, event):
        log("OnReplace", event.GetFindString(), event.GetReplaceString())
        doc = self.app.get_doc()

        #-- do the replace text action
        doc.ReplaceSelection(event.GetReplaceString())

        #-- auto jump to next match text
        self.find_flags = event.GetFlags()
        self.find_str = event.GetFindString()
        self.find_next_token(doc, self.find_str, self.find_flags)
        
    #-------------------------------------------------------------------
    def OnShowFind(self, event):
        #-- get current doc
        doc = self.app.get_doc()

        #-- create wxFindReplaceData for search
        self.find_data = wx.FindReplaceData()

        #-- initial the find string by selection
        token = doc.GetSelectedText()
        #--log("find "+token)
        self.find_data.SetFindString(token)

        find_dlg = wx.FindReplaceDialog(self.app.frame, self.find_data, "Find")
        self.bind_find_event()
        #-- initial the latest position for start position
        self.latest_pos = doc.GetSelectionStart()
        
        find_dlg.Show(True)
        
    #-------------------------------------------------------------------
    def OnShowReplace(self, event):
        #--log("OnShowReplace")
        #-- get current doc editor
        doc = self.app.get_doc()

        #-- create wxFindReplaceData for replace
        self.find_data = wx.FindReplaceData()

        #-- initial the find string by selection
        token = doc.GetSelectedText()
        #--log("replace "+token)
        self.find_data.SetFindString(token)

        #-- create dialog
        find_dlg = wx.FindReplaceDialog(self.app.frame, self.find_data, "Replace", wx.FR_REPLACEDIALOG)
        self.bind_find_event()
        
        #-- initial the latest position for start position
        self.latest_pos = doc.GetSelectionStart()

        find_dlg.Show(True)
        
    #-------------------------------------------------------------------
    def OnPy2Lua(self, event):
        doc = self.app.get_doc()
        s = doc.GetText()
        #s = py2lua(s)
        #doc.SetText(s)


#---------------------------------------------------------------------------------------------------
class MenuProject(wx.Menu):
    def __init__(self, frame, menubar):
        wx.Menu.__init__(self)
        
        self.app = frame.app
        self.frame = frame
        
        ID_NEW_PRJ = wx.NewId()
        ID_OPEN_PRJ = wx.NewId()
        ID_SAVE_PRJ = wx.NewId()
        ID_SAVE_AS_PRJ = wx.NewId()
        ID_CLOSE_PRJ = wx.NewId()
        
        ID_ADD_NEW_FILE = wx.NewId()
        ID_ADD_DIR = wx.NewId()
        ID_ADD_FILES = wx.NewId()
        ID_REMOVE_FILES = wx.NewId()
        ID_CONFIG_PRJ = wx.NewId()
        
        self.Append(ID_NEW_PRJ,      "New Project",    "Create a project")
        self.Append(ID_OPEN_PRJ,     "Open Project",   "Open an existing project")
        self.sub_menu = wx.Menu()
        self.AppendSubMenu(self.sub_menu, "Recent Projects")
        self.AppendSeparator()
        
        self.Append(ID_SAVE_PRJ,     "Save Project",   "Save current project")
        #self.Append(ID_SAVE_AS_PRJ,  "Save as project", "Save project as different name")
        self.AppendSeparator()
        
        self.Append(ID_CLOSE_PRJ,    "Close project",  "Close the current project")
        self.AppendSeparator()
        
        #self.Append(ID_ADD_NEW_FILE, "Add New File",  "Create new file and add to the project")
        self.Append(ID_ADD_FILES,    "Add Existing Files",  "Add files to the project")
        #self.Append(ID_ADD_DIR,      "Add Existing Directory",  "Add files to the project")        
        #self.Append(ID_REMOVE_FILES, "Select and Remove Files",  "Remove files from the project")
        self.AppendSeparator()
        
        self.Append(ID_CONFIG_PRJ,   "Project settings",  "Configure the current project")
        
        menubar.Append(self, ("Project"))
        
        frame.Bind(wx.EVT_MENU, self.OnNewProject,  id=ID_NEW_PRJ)
        frame.Bind(wx.EVT_MENU, self.OnOpenProject,  id=ID_OPEN_PRJ)
        frame.Bind(wx.EVT_MENU, self.OnSaveProject,  id=ID_SAVE_PRJ)
        frame.Bind(wx.EVT_MENU, self.OnCloseProject,  id=ID_CLOSE_PRJ)
        frame.Bind(wx.EVT_MENU, self.OnAddFiles,      id=ID_ADD_FILES)
        
        # and a project history
        self.app.proj_history = self
        self.proj_history_list = []
        self.ID_PROJ = []
        for i in range(10):
            self.ID_PROJ.append(wx.NewId())
        
    #-------------------------------------------------------------------
    def add_proj_history(self, path):
        # clear sub_menu first
        n = len(self.proj_history_list)
        if n > 0:
            for i in range(n):
                self.frame.Unbind(wx.EVT_MENU, id=self.ID_PROJ[i])
                self.sub_menu.Remove(self.ID_PROJ[i])
                
        # if path exist in history list, remove it
        if path in self.proj_history_list:
            self.proj_history_list.remove(path)
            
        # insert the new path to history list
        self.proj_history_list.insert(0, path)
        
        # get history item count
        n = len(self.proj_history_list)
        
        # bind menu event
        for i in range(n):
            self.sub_menu.Append(self.ID_PROJ[i], self.proj_history_list[i])
            self.frame.Bind(wx.EVT_MENU, self.OnProjectHistory, id=self.ID_PROJ[i])
            
    #-------------------------------------------------------------------
    def get_proj_history(self):
        return self.proj_history_list
    
    #-------------------------------------------------------------------
    def OnProjectHistory(self, event):
        # get the file based on the menu ID
        index = event.GetId() - self.ID_PROJ[0]
        path = self.proj_history_list[index]
        log("You selected proj %s\n" % path)
        
        self.app.open_project(path)
    
    #-------------------------------------------------------------------
    def CheckProjectDirty(self):
        """Were the current project changed? If so, save it before."""
        open_it = True
        if self.app.prj and self.app.prj.dirty:
            # save the current project file first.
            result = MsgDlg_YesNoCancel(self.frame, 'The project has been changed.  Save?')
            if result == wx.ID_YES:
                self.app.save_project()
            if result == wx.ID_CANCEL:
                open_it = False
        return open_it
    
    #-------------------------------------------------------------------
    def OnAddFiles(self, event):
        self.app.prj_tree.add_files()
            
    #-------------------------------------------------------------------
    def OnNewProject(self, event):
        self.app.prj_tree.new_prj()
        
    #-------------------------------------------------------------------
    def OnOpenProject(self, event):
        """Open a SDCC project file."""
        open_it = self.CheckProjectDirty()
        if open_it:
            dlg = wx.FileDialog(self.frame, 'Choose a project to open', '.', '', '*.sdprj', wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.app.open_project(dlg.GetPath())
            dlg.Destroy()
    
    #-------------------------------------------------------------------
    def OnSaveProject(self, event):
        """Save a SDCC project file."""
        self.app.save_project()
        
    #-------------------------------------------------------------------
    def OnCloseProject(self, event):
        """Close current SDCC project file."""
        self.app.close_project()    
        
        
#---------------------------------------------------------------------------------------------------
class MenuExample(wx.Menu):
    def __init__(self, parent):
        self.app = parent.app
        wx.Menu.__init__(self)
        dirname = self.app.dirname.replace("ide" + os.sep, "examples" + os.sep)
        lst = os.listdir(dirname)
        i = 0
        self.examples = {}
        
        for d in lst:
            menu = wx.Menu()
            sub_lst = os.listdir(dirname + d)
            
            for d1 in sub_lst:
                _id = wx.NewId()
                m = menu.Append(_id, d1)
                parent.frame.Bind(wx.EVT_MENU, self.OnOpenFile, id = _id)
                path = dirname + d + os.sep + d1 + os.sep
                self.examples[_id] = path
                
            self.AppendSubMenu(menu, d)
                        
    #-------------------------------------------------------------------
    def OnOpenFile(self, event):
        path = self.examples[event.GetId()]
        for f in os.listdir(path):
            if f.endswith(".c") > 0:
                self.app.open_file(path + f)
    
    
#---------------------------------------------------------------------------------------------------
class MenuFile(wx.Menu):
    def __init__(self, frame, menubar):
        self.app = frame.app
        self.frame = frame
        wx.Menu.__init__(self)

        self.Append(ID_NEW_FILE,     "&New\tCtrl-N",   "Create an empty file")
        self.Append(ID_OPEN,    "&Open...\tCtrl-O",    "Open an existing file")
        self.sub_menu = wx.Menu()
        self.AppendSubMenu(self.sub_menu, "Recent files")
        
        self.example_menu = MenuExample(self)
        self.AppendSubMenu(self.example_menu, "Examples")
        self.Append(ID_CLOSE,   "&Close file\tCtrl+W", "Close the current file")
        self.AppendSeparator()
        self.Append(ID_SAVE,    "&Save\tCtrl-S",       "Save the current document")
        self.Append(ID_SAVEAS,  "Save &As...\tAlt-S",  "Save the current document to a file with a new name")
        self.Append(ID_SAVEALL, "Save A&ll...\tCtrl-Shift-S", "Save all open documents")
        self.AppendSeparator()
        
        self.Append(ID_EXIT,    "E&xit\tAlt-X",        "Exit Program")
        
        menubar.Append(self, ("File"))
        
        
        frame.Bind(wx.EVT_MENU, self.OnNewFile,  id=ID_NEW_FILE)
        frame.Bind(wx.EVT_MENU, self.OnOpenFile,  id=ID_OPEN)
        frame.Bind(wx.EVT_MENU, self.OnSaveFile,  id=ID_SAVE)
        frame.Bind(wx.EVT_MENU, self.OnSaveAsFile,  id=ID_SAVEAS)
        frame.Bind(wx.EVT_MENU, self.OnSaveAllFile,  id=ID_SAVEALL)
        frame.Bind(wx.EVT_MENU, self.OnExit,  id=ID_EXIT)                
        
        # and a file history
        self.app.file_history = wx.FileHistory()
        self.app.file_history.UseMenu(self.sub_menu)

        # and finally the event handler bindings
        frame.Bind(wx.EVT_MENU_RANGE, self.OnFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
        
    #-------------------------------------------------------------------
    def OnFileHistory(self, event):
        # get the file based on the menu ID
        index = event.GetId() - wx.ID_FILE1
        #log(index, wx.ID_FILE1, wx.ID_PROJ1)
        path = self.app.file_history.GetHistoryFile(index)
        if os.path.exists(path):
            s = "existed"
        else:
            s = "not existed"
        log("You selected %s %s\n" % (path, s))
        
        self.app.open_file(path)
        
        # add it back to the history so it will be moved up the list
        #self.app.filehistory.AddFileToHistory(path)
        
    #-------------------------------------------------------------------
    def OnOpenFile(self, event):
        fileDialog = wx.FileDialog(self.frame,
                                   "Open Lua file",
                                   "",
                                   "",
                                   "C files(*.c,*.h)|*.c;*.h|Python files(*.py)|*.py|Lua files(*.lua)|*.lua|All files(*)|*",
                                   wx.FD_OPEN | wx.FILE_MUST_EXIST)
        result = False
        if fileDialog.ShowModal() == wx.ID_OK :
            file_name = fileDialog.GetPath()
            result = self.app.open_file(file_name)

        fileDialog.Destroy()
        return result
    
    #-------------------------------------------------------------------
    def OnSaveAsFile(self, event):
        doc = self.app.get_doc()
        path, ext = doc.file_path.split('.')
        
        default_dir = os.path.dirname(doc.file_path)
        default_file = doc.file_path

        if ext == 'c' or ext == 'h' :
            wild_card = "C files(*.c,*.h)|*.c;*.h"
        elif ext == 'py' :
            wild_card = "Python files(*.py)|*.py|Lua files(*.lua)|*.lua"
        elif ext == 'lua' :
            wild_card = "Lua files(*.lua)|*.lua|Python files(*.py)"
            
        wild_card += "|All files(*)|*"
        
        fileDialog = wx.FileDialog(self.app.frame,
                                   "Save as file",
                                   default_dir,
                                   default_file,
                                   wild_card,
                                   wx.FD_SAVE)

        result = False
        if fileDialog.ShowModal() == wx.ID_OK :
            file_path = fileDialog.GetPath()
            result = doc.SaveFile(file_path)
            if result :
                self.app.open_file(file_path)
                log(file_path + " saved.")
            else:
                log("fail to save "+file_path)

        fileDialog.Destroy()
        return result

    #-------------------------------------------------------------------
    def OnSaveFile(self, event):
        doc = self.app.get_doc()
        file_name = doc.file_path

        if (doc == None) :
            log("no file to save...")
            return

        if file_name is None or file_name == "" :
            return OnSaveAsfile(event)

        #--log("Save"+ "   index="+str(self.app.doc_index))
        log("Save "+file_name)
        if (doc.GetModify() == False) :
            log(file_name+ " not modified.")
        elif (doc.SaveFile(file_name)) :
            log(file_name+ " saved.")
            doc.modified = False
            #doc.get_func_list(self.app.functree)
        else:
            log("fail to save "+file_name)
            
    #-------------------------------------------------------------------
    def OnSaveAllFile(self, event):
        for path, doc in self.docs:
            if (doc.GetModify() == False) :
                log(file_name+ " not modified.")
            elif (doc.SaveFile(file_name)) :
                doc.modified = False
                log(file_name+ " saved.")
            else:
                log("fail to save "+file_name)
                
    #-------------------------------------------------------------------
    def OnNewFile(self, event):
        log("new file")
        self.app.new_file()
        
    #-------------------------------------------------------------------
    def OnExit(self, event):
        self.app.frame.Close()


#---------------------------------------------------------------------------------------------------
class MenuSetting(wx.Menu):
    def __init__(self, frame, menubar):
        wx.Menu.__init__(self)
        
        self.frame = frame
        self.app = frame.app
        self.log = frame.log
        id_build_option = self.app.id('BUILD_OPTION')
        self.Append(id_build_option, "SDCC Build Options")
        menubar.Append(self, "Settings")
        
        frame.Bind(wx.EVT_MENU, self.OnBuildOption, id=id_build_option)
        
    #-------------------------------------------------------------------
    def OnBuildOption(self, event):
        self.app.set_build_option()
        

#---------------------------------------------------------------------------------------------------
class MenuHelp(wx.Menu):
    def __init__(self, frame, menubar):
        wx.Menu.__init__(self)
        
        ID_INSPECT = wx.NewId()
        self.Append(ID_ABOUT, "About...")
        self.AppendSeparator()
        self.Append(ID_INSPECT, "Inspect")
        
        menubar.Append(self, "Help")
        self.frame = frame
        frame.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        frame.Bind(wx.EVT_MENU, self.OnInspect, id=ID_INSPECT)
    #-------------------------------------------------------------------
    def OnAbout(self, event):
        msg = "A Mcu IDE with wxPython - Athena"
        dlg = wx.MessageDialog(self.frame, msg, "About Small Python IDE",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
    #-------------------------------------------------------------------
    def OnInspect(self, event):
        wx.lib.inspection.InspectionTool().Show()
        
        
#---------------------------------------------------------------------------------------------------
def menubar(frame):
    '''Create menu bar of IDE Main Frame'''
    menubar = wx.MenuBar(0)

    MenuFile(frame, menubar)
    MenuEdit(frame, menubar)
    MenuProject(frame, menubar)
    MenuDebug(frame, menubar)
    MenuSetting(frame, menubar)
    MenuHelp(frame, menubar)

    frame.SetMenuBar(menubar)
    


#---------------------------------------------------------------------------
class MyDialog(wx.Dialog):
    
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        pass
    
    #-------------------------------------------------------------------
    def add_static_line(self, sizer):
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        
    #-------------------------------------------------------------------
    def add_text_entry(self, sizer, label_str, help_str="", default_str=""):
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, label_str)
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        text = wx.TextCtrl(self, -1, "", size=(80,-1))
        text.SetValue(default_str)
        text.SetHelpText(help_str)
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        return text
    
    #-------------------------------------------------------------------
    def add_combo_box(self, sizer, label_str, lst):
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, label_str)
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        cbox = wx.ComboBox(self, pos=(150, 90), size=(95, -1), choices=lst, style=wx.CB_DROPDOWN)
        
        box.Add(cbox, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        return cbox
    
    #-------------------------------------------------------------------
    def add_ok_cancel_button(self, sizer):
        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        self.btn_cancel = btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        
        self.btn_ok = btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)
        
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)    
    
    #-------------------------------------------------------------------
    def __del__( self ):
        pass


#---------------------------------------------------------------------------
class ProjectSettingDialog(MyDialog):
    def __init__(self, parent, id, title):
        MyDialog.__init__ ( self, parent, id, title)
        
        self.log = parent.log
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        #--------------------------------------------------------------------
        self.text_prj_title    = self.add_text_entry(sizer, "Project Title :", "Please input a project title name")
        self.text_prj_filename = self.add_text_entry(sizer, "Project File Name :", "Please input a project file name to store")
        
        self.dbb = filebrowse.DirBrowseButton(
            self, -1, size=(450, -1),
            style = wx.TAB_TRAVERSAL,
            labelText = 'Project directory:',
            buttonText = 'Browse',
            toolTip = 'Type directory name or browse to select',
            dialogTitle = '',
            startDirectory = '.',
            changeCallback = self.dbbCallback,
            dialogClass = wx.DirDialog,
            newDirectory = False,
            name = 'dirBrowseButton')
    
        sizer.Add(self.dbb, 0, wx.ALL, 5)
        self.add_static_line(sizer)
        
        #--------------------------------------------------------------------
        self.add_ok_cancel_button(sizer)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Centre( wx.BOTH )
        
        self.Bind(wx.EVT_TEXT, self.OnChange, self.text_prj_title)
        self.Bind(wx.EVT_CHAR, self.OnKeyPress, self.text_prj_title)
        
    #--------------------------------------------------------------------
    def OnCpuComboBox(self, event):
        s = event.GetString()
        self.log.write(s)

    #--------------------------------------------------------------------
    def OnCpuBoxKeyUpdate(self, event):
        s = event.GetString()
        self.log.write(s)
    
    #--------------------------------------------------------------------
    def OnChange(self, event):
        s = event.GetString()
        self.text_prj_filename.SetValue(s + '.sdprj')
        
    #--------------------------------------------------------------------
    def OnKeyPress(self, event):
        self.log.write('EvtChar: %d\n' % event.GetKeyCode())
        event.Skip()
    
    #--------------------------------------------------------------------
    def dbbCallback(self, evt):
        self.log.write('DirBrowseButton: %s\n' % evt.GetString())
        

##---------------------------------------------------------------------------
#class BuildOptionDialog(MyDialog):
    #def __init__(self, parent, id, title):
        #MyDialog.__init__ ( self, parent, id, title)
        
        #self.log = parent.log
        #self.SetInitialSize((500, -1))
        #sizer = wx.BoxSizer(wx.VERTICAL)
        
        ##--------------------------------------------------------------------
        
        #mcu_family_list = ['8051', 'z80', 'pic16', 'pic18']
        #self.mcu_cbox = self.add_combo_box(sizer, "Select MCU Family :", mcu_family_list)
        #self.mcu_model_text = self.add_text_entry(sizer, "MCU Model :", "")
        ##mcu_8051_list = ['8051', '8052', '89C2051']
        ##self.cpu_cbox = self.add_combo_box(sizer, "Select MCU Model  :", mcu_8051_list)
        
        ##self.Bind(wx.EVT_COMBOBOX, self.OnCpuComboBox, self.cpu_cbox)
        ##self.Bind(wx.EVT_TEXT, self.OnCpuBoxKeyUpdate, self.cpu_cbox)
        
        ##cflag_list = ['--debug --stack-after-data', '--model-small', '--model-medium', '--model-large', '--model-huge']
        ##self.cflag_cbox = self.add_combo_box(sizer, "CFLAGS :", cflag_list)
        #self.cflags_text = self.add_text_entry(sizer, "CFLAGS :", "", '--debug -mmcs51')
        #self.ldflags_text = self.add_text_entry(sizer, "LDFLAGS :", "")

        #self.add_static_line(sizer)

        ##--------------------------------------------------------------------
        #self.add_ok_cancel_button(sizer)
        
        #self.SetSizer(sizer)
        #sizer.Fit(self)
        #self.Centre( wx.BOTH )
        
    ##-------------------------------------------------------------------
    #def add_model_selection(self, sizer):
        #wx.StaticBox(self, -1, 'test Info', (5, 5), size=(240, 170))
        
        #wx.CheckBox(self, -1 ,'c1', (15, 30))
        #wx.CheckBox(self, -1 ,'c2', (15, 55))
        #wx.StaticText(self, -1, 'aaa', (15, 95))
        #wx.SpinCtrl(self, -1, '1', (55, 90), (60, -1), min=1, max=120)
        #wx.Button(self, 1, 'Ok', (90, 185), (60, -1))
 
        #self.Bind(wx.EVT_BUTTON, self.OnClose, id=1)

        #sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        #return cbox
    
    ##--------------------------------------------------------------------
    #def OnCpuComboBox(self, event):
        #s = event.GetString()
        #self.log.write(s)

    ##--------------------------------------------------------------------
    #def OnCpuBoxKeyUpdate(self, event):
        #s = event.GetString()
        #self.log.write(s)
    
    ##--------------------------------------------------------------------
    #def OnKeyPress(self, event):
        #self.log.write('EvtChar: %d\n' % event.GetKeyCode())
        #event.Skip()

        
#---------------------------------------------------------------------------

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)

    def show_dialog(self):
        #dlg = ProjectSettingDialog(self, -1, "Project Settings", size=(800, 600))
        dlg = BuildOptionDialog(self, -1, "SDCC Build Options")
        dlg.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()
    
        if val == wx.ID_OK:
            self.log.WriteText("You pressed OK\n")
        else:
            self.log.WriteText("You pressed Cancel\n")

        dlg.Destroy()
        

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None, pos=wx.Point(400, 400))

    sizer = wx.BoxSizer(wx.VERTICAL)
    
    log = wx.TextCtrl(frame, size=wx.Size(300, 200), style = wx.TE_MULTILINE)
    test_panel = TestPanel(frame,  log)
    
    sizer.Add(test_panel, 0, wx.ALL, 5)
    sizer.Add(log, 0, wx.ALL, 5)
    
    frame.SetSizer(sizer)
    sizer.Fit(frame)
    
    app.SetTopWindow(frame)
    frame.Show(True)   
    
    test_panel.show_dialog()
    
    app.MainLoop()