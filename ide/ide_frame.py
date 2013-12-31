import wx

#import project's python modules
from ide_global import *
import ide_menu
import ide_toolbar

from ide_prj_mgr import PrjMgr
from ide_log_nb import LogNB
from ide_doc_book import DocBook


#---------------------------------------------------------------------------------------------------
class IdeFrame (wx.Frame):
    def __init__(self, app):
        #sz = wx.GetDisplaySize()
        wx.Frame.__init__ (self, None,
                            id = wx.ID_ANY,
                            title = app.name,
                            pos = wx.DefaultPosition,
                            size = wx.DefaultSize,
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL| wx.MAXIMIZE)
        self.app = app
        #print wx.GetDisplaySize() 
  
        frame = self
        self.log = None
        self.deact_time = time.time()
        self.SetMinSize(wx.Size(1024, 768))
        
        icon = wx.Icon(self.app.dirname + 'images' + os.sep + 'frame.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        #-- tell wxAuiManager to manage this frame
        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(frame)
        
        ide_menu.menubar(frame)

        self.CreateStatusBar(1)
        
        self.SetStatusText('Welcome to ' + self.Title + '.')

        app.toolbar = ide_toolbar.__init__(frame, self.mgr)

        #-- add a bunch of panes
        app.doc_book = DocBook(app, frame)
        app.prj_mgr = PrjMgr(app, frame)
        app.log_nb = LogNB(app, frame)

        self.mgr.AddPane(app.doc_book, wx.aui.AuiPaneInfo() .Left() .PinButton(True).Dock().Resizable().FloatingSize(wx.Size(298,206)).DockFixed(False).Layer(0).CentrePane())
        self.mgr.AddPane(app.prj_mgr, wx.aui.AuiPaneInfo() .Left() .PinButton(True).Dock().Resizable().FloatingSize(wx.DefaultSize).DockFixed(False).DefaultPane())
        self.mgr.AddPane(app.log_nb, wx.aui.AuiPaneInfo() .Bottom() .PinButton(True).Dock().Resizable().FloatingSize(wx.DefaultSize).DockFixed(False).DefaultPane())
        
        self.log = app.log_nb.logger
        
        #-- make some default perspectives
        self.perspective_default = self.mgr.SavePerspective()

        app.load_config()
        
        # "commit" all changes made to wxAuiManager
        self.mgr.Update()
        
        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        
        self.Bind(wx.EVT_MENU, self.OnMenuDebugSelected, id=ID_RUN)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugSelected, id=ID_COMPILE)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugSelected, id=ID_DBG_START)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugSelected, id=ID_DBG_STOP)
        
    #-------------------------------------------------------------------
    def OnMenuDebugSelected(self, event):
        #log("AppFrame.OnMenuDebugSelected")
        obj = event.GetEventObject()
        event_id = event.GetId()
        self.menu_debug.update_ui(event_id)
        
        #update menu and toolbar
        #if obj != self.menu_debug:
            #wx.PostEvent(self.menu_debug, event)
        #if obj != self.app.toolbar.tb2:
            #wx.PostEvent(self.app.toolbar.tb2, event)
        
        #do real action
        wx.PostEvent(self.app.doc_book, event)
        
    #-------------------------------------------------------------------
    def OnActivate(self, event):
        if event.GetActive():
            now = time.time()
            if self.app.doc_book :
                self.app.doc_book.check_docs_modified(self.deact_time)
        else:
            self.deact_time = time.time()

        event.Skip()
        
    #-------------------------------------------------------------------
    # Virtual event handlers, override them in your derived class
    def OnClose(self, event):
        self.app.doc_book.close()
        self.app.exit()
        self.app.save_config()

        if self.app.doc_modified :
            ans = self.app.save_on_exit(event)
            if ans == wx.ID_CANCEL:
                return
            elif ans == wx.ID_NO or ans == wx.ID_YES :
                self.Destroy()
            else:
                if not event.CanVeto():  # Test if we can veto this deletion
                    self.Destroy()
                else:
                    event.Veto()  # Notify the calling code that we didn't delete the frame.

        #-- ensure the event is skipped to allow the frame to close
        event.Skip()
        
    #-------------------------------------------------------------------
    def __del__(self):
        print "del ide frame"
        pass
        #self.mgr.UnInit()
        
