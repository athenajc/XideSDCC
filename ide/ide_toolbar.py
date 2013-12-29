import wx
from ide_global import *
import utils

#---------------------------------------------------------------------------------------------------
def __init__(frame, aui_mgr):
    return ToolBarMgr(frame, aui_mgr)


#---------------------------------------------------------------------------------------------------
class ToolBar(wx.ToolBar):
    def __init__(self, parent, frame, aui_mgr, name, lst):
        if wx.Platform == '__WXMSW__' :
            h = 28            
        else:
            h = -1
        wx.ToolBar.__init__(self, frame, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, h), wx.TB_HORIZONTAL)
        self.SetToolBitmapSize(wx.Size(16,16))
        self.app = frame.app
        self.parent = parent
        self.frame = frame
        
        tb = self
        for i, t in enumerate(lst):
            if len(t) == 0:
                tb.AddSeparator()
            else:
                bmp = get_bitmap(t[2])
                tb.AddLabelTool(t[0], t[1], bmp, wx.NullBitmap, wx.ITEM_NORMAL, t[3], wx.EmptyString, None )
                
        tb.Realize()
        i = len(parent.controls)
        aui_mgr.AddPane(tb, wx.aui.AuiPaneInfo().
                          Name(name).Caption("").
                          ToolbarPane().Top().Row(1).
                          LeftDockable(False).RightDockable(False))
        parent.controls.append(tb)
    

#---------------------------------------------------------------------------------------------------
class GotoLineCombo(wx.ComboBox):
    def __init__( self, parent ):
        wx.ComboBox.__init__(self, parent, ID_ANY, "",
                            wx.DefaultPosition, wx.DefaultSize,
                            [],
                            wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_TEXT, self.OnKeyUpdate)
        self.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.Append("0")
        self.Append("100")

        self.app = parent.app

    #-------------------------------------------------------------------
    def set_select_items(self):
        doc = self.app.get_doc()
        n = doc.GetLineCount()

        self.Clear()
        
        if n > 1000:
            div = n / 10
        else:
            div = 100
            
        for i in range(10) :
            self.Append(str(i * div))
            if i * div > n:
                break
            
    #-------------------------------------------------------------------
    def OnKeyPress(self, event):
        key = chr(event.GetKeyCode())
        if key >= '0' and key <= '9':
            event.Skip()
            
    #-------------------------------------------------------------------
    def OnKeyUpdate(self, event):
        #--print("OnKeyUpdate", event.GetString(), event.GetId(), event.GetEventType(), event.GetEventObject())
        s = event.GetString().strip()
        if (s is None or s == "" or len(s) == 0) :
            return
        doc = self.app.get_doc()
        try:
            line = int(s)

            n = doc.GetLineCount() - 1
            if line > n:
                line = n
                self.SetValue(str(n))
        except:
            line = 0
            
        log(line)
        doc.goto_line(line)
        
    #-------------------------------------------------------------------
    def OnDocPageChange(self):
        self.set_select_items()
        
        
#---------------------------------------------------------------------------------------------------
class GotoComboToolBar(wx.ToolBar):
    def __init__(self, parent, frame, aui_mgr):
        wx.ToolBar.__init__(self, frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL)
        self.SetToolBitmapSize(wx.Size(16,16))
        self.app = frame.app
        self.parent = parent
        self.frame = frame
        tb = self
        
        tb.AddControl(wx.StaticText(tb, ID_ANY, " Goto Line "))
        cb = GotoLineCombo(tb)
        tb.AddControl(cb)
        
        self.goto_line_combo = cb
        self.app.goto_line_combo = self.goto_line_combo
        
        tb.Realize()
        i = len(parent.controls)
        aui_mgr.AddPane(tb, wx.aui.AuiPaneInfo().
                          Name('GotoLine').Caption("").
                          ToolbarPane().Top().Row(1).
                          LeftDockable(False).RightDockable(False))
        parent.controls.append(tb)
        

#---------------------------------------------------------------------------------------------------
class TargetCombo(wx.ComboBox):
    def __init__( self, parent ):
        wx.ComboBox.__init__(self, parent, ID_ANY, "",
                            wx.DefaultPosition, wx.DefaultSize,
                            [],
                            wx.CB_READONLY)

        self.app = parent.app
        self.file_list = []
        self.select_target_prj = False
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect)
    
    #-------------------------------------------------------------------
    def OnSelect(self, event):
        item = event.GetSelection()
        file_path = self.file_list[item]
        log('select', file_path)
        if file_path.find('sdprj') > 0:
            self.select_target_prj = True
        else:
            self.select_target_prj = False
        self.app.set_title(file_path)
            
    #-------------------------------------------------------------------
    def get_target(self):
        item = self.GetCurrentSelection()
        if item == -1:
            return ""
        file_path = self.file_list[item]
        log('target ' + file_path)
        return file_path
    
    #-------------------------------------------------------------------
    def add_project(self, file_path):
        file_name = os.path.basename(file_path)
        self.file_list.insert(0, file_path)
        self.Insert(file_name, 0)
        self.SetSelection(0)
        self.select_target_prj = True
        
    #-------------------------------------------------------------------
    def add_file(self, file_path):
        file_name = os.path.basename(file_path)
        self.file_list.append(file_path)
        self.Append(file_name)
        
    #-------------------------------------------------------------------
    def select_file(self, file_path):
        if self.select_target_prj:
            return
        
        if file_path in self.file_list:
            index = self.file_list.index(file_path)
            self.SetSelection(index)
            self.app.set_title(file_path)
        
#---------------------------------------------------------------------------------------------------
class TargetToolBar(wx.ToolBar):
    def __init__(self, parent, frame, aui_mgr):
        wx.ToolBar.__init__(self, frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL)
        self.SetToolBitmapSize(wx.Size(16,16))
        self.app = frame.app
        self.parent = parent
        self.frame = frame
        tb = self
        
        tb.AddControl(wx.StaticText(tb, ID_ANY, " Target "))
        cb = TargetCombo(tb)
        tb.AddControl(cb)
        
        self.cb = cb
        bmp = get_bitmap(self.app.dirname + "images/option.png")
        id_build_option = self.app.id('BUILD_OPTION')
        tb.AddLabelTool(id_build_option, "BuildOption", bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Setting SDCC build options", wx.EmptyString, None )
        
        tb.Realize()
        i = len(parent.controls)
        aui_mgr.AddPane(tb, wx.aui.AuiPaneInfo().
                          Name('BuildTarget').Caption("").
                          ToolbarPane().Top().Row(1).
                          LeftDockable(False).RightDockable(False))
        parent.controls.append(tb)
        
        
#---------------------------------------------------------------------------------------------------
class DebugToolBar(ToolBar):
    def __init__(self, parent, frame, aui_mgr):
        self.app = frame.app
        self.debugging = None
        id_build_option = self.app.id('BUILD_OPTION')
        p = self.app.dirname
        debug_lst = [
            #[id_build_option,  "BuildOption", "images/option.png",     "Setting SDCC build options"],
            [ID_COMPILE,       "Compile",     p + "images/compile.png",    "Compile"],
            [],
            [ID_RUN,           "Run",         p + "images/run1.png",       "Build and Run"],
            [],
            [ID_DBG_START,     "Debug",       p + "images/bug.png",        "Start Debug"],
            [ID_DBG_STOP,      "Stop Debug",  p + "images/dbgstop.png",    "Stop debugger"],
        ]        
        ToolBar.__init__(self, parent, frame, aui_mgr, "debug toolbar", debug_lst)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate)
        

    #-------------------------------------------------------------------
    def OnUpdate(self, event):
        if self.debugging == self.app.debugging :
            return
        self.debugging = self.app.debugging

        if self.debugging:
            self.EnableTool(ID_DBG_START, False)
            self.EnableTool(ID_DBG_STOP, True)             
        else:
            self.EnableTool(ID_DBG_START, True) 
            self.EnableTool(ID_DBG_STOP, False)            
                
        
#---------------------------------------------------------------------------------------------------
class EditToolBar(ToolBar):
    def __init__(self, parent, frame, aui_mgr):
        edit_lst = [
            [ID_NEW_FILE,"New",      wx.ART_NORMAL_FILE, "Create an empty document"],
            [ID_OPEN,    "Open",     wx.ART_FILE_OPEN,   "Open an existing document"],
            [ID_SAVE,    "Save",     wx.ART_FILE_SAVE,   "Save the current document"],
            [ID_SAVEALL, "Save All", wx.ART_NEW_DIR,     "Save all documents"],
            [],
            [ID_CUT,     "Cut",      wx.ART_CUT,         "Cut the selection"],
            [ID_COPY,    "Copy",     wx.ART_COPY,        "Copy the selection"],
            [ID_PASTE,   "Paste",    wx.ART_PASTE,       "Paste text from the clipboard"],
            [],
            [ID_UNDO,    "Undo",     wx.ART_UNDO,        "Undo last edit"],
            [ID_REDO,    "Redo",     wx.ART_REDO,        "Redo last undo"],
            [],
            [ID_FIND,    "Find",     wx.ART_FIND,        "Find string"],
            [ID_REPLACE, "Replace",  wx.ART_FIND_AND_REPLACE, "Find and replace string"],
        ]   
        ToolBar.__init__(self, parent, frame, aui_mgr, "Edit toolbar", edit_lst)


#---------------------------------------------------------------------------------------------------
class ToolBarMgr():
    def __init__(self, frame, aui_mgr):
        self.app = frame.app
        self.controls = []

        if wx.Platform == '__WXMSW__' :
            self.tb_edit = EditToolBar(self, frame, aui_mgr) 
            self.tb_goto = GotoComboToolBar(self, frame, aui_mgr)
            self.tb_target = TargetToolBar(self, frame, aui_mgr)
            self.tb_debug = DebugToolBar(self, frame, aui_mgr)
        else:            
            self.tb_debug = DebugToolBar(self, frame, aui_mgr)
            self.tb_target = TargetToolBar(self, frame, aui_mgr)
            self.tb_goto = GotoComboToolBar(self, frame, aui_mgr)
            self.tb_edit = EditToolBar(self, frame, aui_mgr)
            
        self.app = frame.app
        
    #-------------------------------------------------------------------
    def add_file(self, file_path):
        if file_path.find(".c") >= 0:
            if utils.check_if_with_main(file_path):
                self.tb_target.cb.add_file(file_path)
        if file_path.find(".sdprj") >= 0:
            self.tb_target.cb.add_project(file_path)
            self.select_file(file_path)
            
    #-------------------------------------------------------------------
    def get_target(self):
        return self.tb_target.cb.get_target()

    #-------------------------------------------------------------------
    def select_file(self, file_path):
        if file_path.find(".c") >= 0:
            self.tb_target.cb.select_file(file_path)
        
