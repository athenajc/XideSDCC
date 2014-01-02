import wx
import wx.stc as stc
import re
import time

from ide_global import *

#---------------------------------------------------------------------------------------------------
class LogNB(wx.Notebook):
    def __init__(self, app, frame, size):
        if wx.Platform == '__WXMSW__' :
            style = wx.NB_BOTTOM
        else:
            style = wx.NB_LEFT
        wx.Notebook.__init__(self, frame, wx.ID_ANY, wx.DefaultPosition, size, style)
        self.app = app
        
        self.logger = LogTextCtrl(self)
        self.search_result = SearchResultList(self)
        self.debug_info = DebugInfoList(self)
        
        app.logger = self.logger
        app.search_result = self.search_result
        app.debug_info = self.debug_info
        
    #-------------------------------------------------------------------
    def show_log(self):
        self.SetSelection(0)
        
    #-------------------------------------------------------------------
    def show_search_result(self):
        self.SetSelection(1)    
        
    #-------------------------------------------------------------------
    def show_debug(self):
        self.SetSelection(2)
        self.debug_info.scroll_to_end()
        
    #-------------------------------------------------------------------
    def clear_debug(self):
        self.debug_info.clear()


#---------------------------------------------------------------------------------------------------
class LogTextCtrl(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, ID_ANY, "",
                           wx.DefaultPosition, wx.Size(-1, -1),
                           wx.TE_READONLY + wx.TE_MULTILINE )

        parent.AddPage(self, wxT("log"))
    
    #-------------------------------------------------------------------
    def write_args(self, *args):
        msg = (' '.join(map(str, args))) 
        self.write(msg)
        
    #-------------------------------------------------------------------
    def write(self, text):
        hhmmss = time.strftime('%H:%M:%S', time.gmtime(12345))
        s = hhmmss + text
        self.WriteText(s)
        
        
#---------------------------------------------------------------------------------------------------
class SearchResultList(wx.ListCtrl):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT+wx.BORDER_NONE)

        self.InsertColumn(0, "File", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(1, "Line")
        self.InsertColumn(2, "Text")

        self.SetColumnWidth(0, 80)
        self.SetColumnWidth(1, 80)
        self.SetColumnWidth(2, 800)

        parent.AddPage(self, wxT("Search result"))
        self.add_item(["test", "test ok", ""])
        self.Update()
        
    #-------------------------------------------------------------------
    def add_item(self, lst):
        n = self.GetItemCount()
        n = self.InsertStringItem(n, lst[0])
        self.SetStringItem(n, 1, lst[1])
        self.SetStringItem(n, 2, lst[2])
        return n
    
    #-------------------------------------------------------------------
    def Clear(self):
        self.DeleteAllItems()

#-----------------------------------------------------------------------
class Menu(wx.Menu):
    def __init__(self, parent, menu_lst=[]):
        wx.Menu.__init__(self)
        menu = self
        for m in menu_lst:
            if m == []:
                menu.AppendSeparator()
            else:
                id_name = m[0]
                id = get_id(id_name)
                setattr(self, id_name, id)
                obj = menu.Append(id, m[1], m[2])
                parent.Bind(wx.EVT_MENU, m[3], obj)
                
#---------------------------------------------------------------------------------------------------
class DebugInfoList(wx.ListCtrl):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.BORDER_NONE)
        self.app = parent.app
        
        self.InsertColumn(0, "Time", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(1, "Event")
        self.InsertColumn(2, "Message")
        
        self.SetColumnWidth(0, 80)
        self.SetColumnWidth(1, 80)
        self.SetColumnWidth(2, wx.GetDisplaySize().GetWidth())

        parent.AddPage(self, wxT("Debug Info"))

        self.write("init", "init ok")
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        
        menu_lst = [
            ["ID_COPY", "Copy selection",  "Copy the selection lines to clipboare", self.OnCopy],
        ]
        self.pop_menu = Menu(self, menu_lst)
        
        # bind popup menu events
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        
    #-------------------------------------------------------------------
    def OnRightDown(self, event):
        self.PopupMenu(self.pop_menu, event.GetPosition())
    
    #-------------------------------------------------------------------
    def OnCopy(self, event):
        i = self.GetFirstSelected()
        if i == -1:
            return
        text = self.GetItem(i, 2).GetText()
        copy_to_clipboard(text)
            
    #-------------------------------------------------------------------
    def scroll_to_end(self):
        log("scroll_to_end", self.GetItemCount())
        item = self.GetItemCount()
        self.EnsureVisible(item)
        self.Focus(item)
    
    #-------------------------------------------------------------------
    def OnItemSelected(self, event):
        i = event.m_itemIndex
        doc = self.app.get_doc()
        doc.deselection()
        msg = self.GetItem(i, 2).GetText()
        doc.select_debug_msg(msg)
        
    #-------------------------------------------------------------------
    def OnDoubleClick(self, event):
        print "OnDoubleClick"
        
    #-------------------------------------------------------------------
    def add_item(self, lst):
        print(lst)
        n = self.GetItemCount()
        n = self.InsertStringItem(n, lst[0])
        self.SetStringItem(n, 1, str(lst[1]))
        self.SetStringItem(n, 2, str(lst[2]))
        if n % 2 == 1 :
            self.SetItemBackgroundColour(n, wx.Colour(240,230,240))
        return n
    
    #-------------------------------------------------------------------
    def write(self, s1, s2):
        dt =  wx.DateTime.Now()
        t = "%02d:%02d:%02d" % (dt.Hour, dt.Minute, dt.Second)
        limit = 200
        if len(s2) > limit:
            i = 0
            self.add_item([t, s1, s2[i:i+limit]])
            i += limit
            while i < len(s2):
                self.add_item(["", "", s2[i:i+limit]])
                i += limit
        else:
            self.add_item([t, s1, s2])
        self.Update()
        
    #-------------------------------------------------------------------
    def clear(self):
        self.DeleteAllItems()