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
        self.app = app
        
        # Load config before create frame, for preload pos and size settings
        self.config_file = app.config_file
        self.load_config()
        
        # If frame_size = -1, -1, set Maxmize style
        if self.frame_size == (-1, -1):
            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL|wx.MAXIMIZE
        else:
            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
            
        # Create the frame
        wx.Frame.__init__ (self, None,
                            id = wx.ID_ANY,
                            title = app.name,
                            pos = self.frame_pos,
                            size = self.frame_size,
                            style = style) 
        
        frame = self
        app.frame = self
        self.log = None
        self.deact_time = time.time()
        
        # Size - set min size and max size, avoid too big or too small
        self.SetMaxSize(wx.GetDisplaySize())
        self.SetMinSize(wx.Size(1024, 768))
        
        # Icon
        icon = wx.Icon(self.app.dirname + 'images' + os.sep + 'frame.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # Tell wxAuiManager to manage this frame
        self.mgr = wx.aui.AuiManager()
        self.mgr.SetManagedWindow(frame)
        
        # Menu Bar
        ide_menu.menubar(frame)

        # Satatus Bar
        self.CreateStatusBar(1)
        self.SetStatusText('Welcome to ' + self.Title + '.')

        # Tool Bar
        app.toolbar = ide_toolbar.__init__(frame, self.mgr)
        
        # Set w and h for sub panels
        sz = self.GetSize()
        w = sz.GetWidth()
        h = sz.GetHeight()
        
        # init panel size
        if self.left_panel_width > 80:
            w1 = self.left_panel_width
        else:        
            w1 = w / 4
            if w1 > 200:
                w1 = 200
            self.left_panel_width = w1
            
        if self.bottom_panel_height > 80:
            h1 = self.bottom_panel_height
        else:
            h1 = h / 5
            if h1 > 160:
                h1 = 160
            self.bottom_panel_height = h1
                
        # Create Doc Book notebook
        self.doc_book = app.doc_book = DocBook(app, frame, (w - w1, h - h1))
        
        # Create Project Manager notebook
        self.prj_mgr = app.prj_mgr = PrjMgr(app, frame, (w1, h - h1))
        
        # Create Log notebook
        self.log_nb = app.log_nb = LogNB(app, frame, (w, h1))

        # Add Panes to AuiMgr
        self.mgr.AddPane(self.doc_book, wx.aui.AuiPaneInfo() .Left() .PinButton(True).Dock().Resizable().FloatingSize(wx.Size(298,206)).DockFixed(False).Layer(0).CentrePane())
        self.mgr.AddPane(self.prj_mgr, wx.aui.AuiPaneInfo() .Left() .PinButton(True).Dock().Resizable().FloatingSize(wx.DefaultSize).DockFixed(False).DefaultPane())
        self.mgr.AddPane(self.log_nb, wx.aui.AuiPaneInfo() .Bottom() .PinButton(True).Dock().Resizable().FloatingSize(wx.DefaultSize).DockFixed(False).DefaultPane())
        
        self.log = self.log_nb.logger
        
        #-- make some default perspectives
        self.perspective_default = self.mgr.SavePerspective()

        # "commit" all changes made to wxAuiManager
        self.mgr.Update()
        
        # Connect Frame Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        
        # Connect Debug Menu Events
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
                
        #do real action
        wx.PostEvent(self.doc_book, event)
        
    #-------------------------------------------------------------------
    def OnActivate(self, event):
        if event.GetActive():
            #now = time.time()
            if self.doc_book :
                self.doc_book.check_docs_modified(self.deact_time)
        else:
            self.deact_time = time.time()

        event.Skip()
        
    #-------------------------------------------------------------------
    # Virtual event handlers, override them in your derived class
    def OnClose(self, event):
        # Save frame config
        self.save_config()
        
        # Save app config
        self.app.save_config()
        
        # Check if any doc modified
        if self.doc_book.if_doc_modified() :
            
            # If yes, ask if save 
            ans = self.doc_book.save_on_exit(event)
            if ans == wx.ID_CANCEL:
                # If user press Cancel, skip close application frame
                return
            
            elif ans == wx.ID_NO or ans == wx.ID_YES :
                self.doc_book.close()
                self.Destroy()
            else:
                if not event.CanVeto():  # Test if we can veto this deletion
                    self.doc_book.close()
                    self.Destroy()
                else:
                    event.Veto()  # Notify the calling code that we didn't delete the frame.

        # Ensure the event is skipped to allow the frame to close
        event.Skip()
        
    #-------------------------------------------------------------------
    def load_config(self):
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)
        
        if config:
            # Load Frame Rect
            s = config.Read("ide_frame_rect", "")
            if s == "":
                x = y = w = h = -1
            else:
                x, y, w, h = eval(s)
            
            rect = wx.Rect(x, y, w, h)
            self.frame_pos = rect.GetPosition()
            self.frame_size = rect.GetSize()
            
            # Load panel width and height
            self.left_panel_width = config.ReadInt("left_panel_width", 0)
            self.bottom_panel_height = config.ReadInt("bottom_panel_height", 0)

        else:
            self.left_panel_width = 0
            self.bottom_panel_height = 0
            self.frame_sz = (-1, -1)

        del config
        
    #-------------------------------------------------------------------
    def save_config(self):
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)
        
        if config:
            # Get frame rect
            rect = self.GetRect()
            x = rect.GetLeft()
            y = rect.GetTop()
            w = rect.GetWidth()
            h = rect.GetHeight()
            
            # Check if x, y out of left-top boundary
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            
            # Check if x, y out of right-bottom boundary
            x_max = wx.GetDisplaySize().GetWidth() / 2
            y_max = wx.GetDisplaySize().GetHeight() / 2
            if x > x_max:
                x = x_max
            if y > y_max:
                y = y_max
                
            # Save frame rect
            config.Write("ide_frame_rect", str((x, y, w, h)))
                
            # Save panel width and height settings
            config.WriteInt("left_panel_width", self.prj_mgr.GetSize().GetWidth())
            config.WriteInt("bottom_panel_height", self.log_nb.GetSize().GetHeight())
            
        del config
                

        
