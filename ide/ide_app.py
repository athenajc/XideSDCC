import os
import wx

#import ide's modules
from ide_global import get_id, set_app, log, search_sdcc_bin
from ide_frame import IdeFrame
from ide_build_opt import BuildOptionDialog

#---------------------------------------------------------------------------------------------------
class IdeApp(wx.App):
    
    def OnInit(self):
        set_app(self)
        self.name = 'Xide SDCC'
        self.config_file = 'xide.cfg'
        self.cflags = ""
        self.ldflags = ""
        self.dirname = os.path.dirname(os.path.abspath(__file__)) + os.sep
        self.work_dir = "/home/athena/"
        self.logger = None
        self.debugging = False
        self.doc_debugging = None
        self.running = False
        self.doc_running = None
        self.doc_modified = False
        self.project_dirty = False
        self.prj = None
        self.last_file_count = 0
        self.frame = None
        
        self.frame = IdeFrame(self)
    
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
                
        search_sdcc_bin()
        
        return True
            
    #-------------------------------------------------------------------
    def OnExit(self):
        print("app.OnExit")
        
    #-------------------------------------------------------------------
    def show_log(self):
        self.log_nb.show_log()
        
    #-------------------------------------------------------------------
    def show_search_result(self):
        self.log_nb.show_search_result()
        
    #-------------------------------------------------------------------
    def show_debug(self):
        self.log_nb.show_debug()
        
    #-------------------------------------------------------------------
    def clear_debug(self):
        self.log_nb.clear_debug()
        
    #-------------------------------------------------------------------
    def id(self, name):
        return get_id(name)
    
    #-------------------------------------------------------------------
    def set_title(self, file_path):
        if self.frame:
            self.frame.Title = '' + file_path + ' : ' + self.name
    
    #-------------------------------------------------------------------
    def get_target(self):
        return self.toolbar.get_target()
        
    #-------------------------------------------------------------------
    def open_file(self, file_path):
        print(file_path)
        # add it to the history
        self.file_history.AddFileToHistory(file_path)
        if self.toolbar:
            self.toolbar.add_file(file_path)
        return self.doc_book.open_file(file_path)
    
    #-------------------------------------------------------------------
    def new_file(self):
        return self.doc_book.new_file()
    
    #-------------------------------------------------------------------
    def get_doc(self):
        return self.doc_book.get_doc()
    
    #-------------------------------------------------------------------
    def goto_file_line(self, file_path, line):
        doc = self.doc_book.open_file(file_path)
        if doc:
            doc.goto_line(line)
            
    #-------------------------------------------------------------------
    def remove_doc(self, doc):
        self.doc_book.remove_doc()
        
    #-------------------------------------------------------------------
    def save_on_close_file(self, event):
        return self.doc_book.save_on_close_file(event)
    
    #-------------------------------------------------------------------
    def save_on_exit(self, event):    
        if self.doc_modified:
            return self.doc_book.save_on_exit(event)
        
    #-------------------------------------------------------------------
    def set_last_file(self, file_name):
        self.config.Write("LastFile", file_name)

    #-------------------------------------------------------------------
    def open_project(self, file_name):
        self.prj_tree.open_project(file_name)
        self.toolbar.add_file(file_name)
    
    #-------------------------------------------------------------------
    def save_project(self):
        if self.prj:
            self.prj.save_project()
            
    #-------------------------------------------------------------------
    def close_project(self):
        if self.prj:
            self.prj_tree.close_prj()
            
    #-------------------------------------------------------------------
    def set_build_option(self):
        file_path = self.get_target()
                
        dlg = BuildOptionDialog(self.frame, -1, "SDCC Build Options", file_path)
        dlg.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()
    
        if val == wx.ID_OK:
            log("You pressed OK\n")
        else:
            log("You pressed Cancel\n")
            
        if dlg.cflags and dlg.ldflags:
            self.cflags = dlg.cflags
            self.ldflags = dlg.ldflags
            log(dlg.cflags)
            log(dlg.ldflags)
            
        dlg.Destroy()        

    #-------------------------------------------------------------------
    def save_config(self):
        log("save config - " + self.config_file)
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)
        doc_lst = self.doc_book.docs
        #print(doc_lst)
        i = 0
        for path, doc in doc_lst:
            #print(path, doc)
            config.Write("LastFile" + str(i), path)
            i += 1

        config.Write("LastFileCount", str(i))

        perspective_all = self.frame.mgr.SavePerspective()
        config.Write("Perspective", perspective_all)
        config.Write("LastWorkPath", self.work_dir)
        
        n = self.file_history.GetCount()
        config.Write("HistoryFileCount", str(self.file_history.GetCount()))
        for i in range(n):
            print self.file_history.GetHistoryFile(i)
            config.Write("HistoryFile" + str(i), self.file_history.GetHistoryFile(i))
        
        if self.prj:
            config.Write("LastProject", self.prj.file_path)
        else:
            config.Write("LastProject", "")
        
        #config.Write("cflags",  self.cflags)
        #config.Write("ldflags", self.ldflags)
        del config
        
        
    #-------------------------------------------------------------------
    def load_config(self):
        log("load config - " + self.config_file)
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)

        if config.Exists("LastFileCount"):
            #--log("config exists")
            self.last_file_count = config.Read("LastFileCount", "0")
            
            n = int(self.last_file_count)
            for i in range(n):
                file_name = config.Read("LastFile" + str(i), "")
                if file_name != "":
                    self.open_file(file_name)

            perspactive = config.Read("Perspective", "")
            if perspactive != "":
                print("load perspective")
                #self.mgr.LoadPerspective(perspactive)
            self.work_dir = config.Read("LastWorkPath", "")
                        
            n = int(config.Read("HistoryFileCount", "0"))
            for i in range(n):
                path = config.Read("HistoryFile" + str(i), "")
                self.file_history.AddFileToHistory(path)

            path = config.Read("LastProject", "")
            if path != "" and os.path.exists(path):
                self.open_project(path)
                
        #self.cflags = config.Read("cflags", "")
        #self.ldflags = config.Read("ldflags", "")
        del config
        
    #-------------------------------------------------------------------
    def OnDocPageChange(self, event):
        self.goto_line_combo.OnDocPageChange()
        
    #-------------------------------------------------------------------
    def log(self, s):
        if self.logger is None:
            return
        self.logger.AppendText(s)
        
    #-------------------------------------------------------------------
    def exit(self):
        if self.debugging and self.doc_debugging is not None:
            doc = self.doc_debugging
            doc.stop()
            wx.MilliSleep(100) 
                
        if self.running and self.doc_running is not None:
            doc = self.doc_running
            doc.stop()
