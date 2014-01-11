import os
import wx

#import ide's modules
from ide_global import *
from ide_frame import IdeFrame
from ide_build_opt import BuildOptionDialog

VERSION = "v0.1.0"

#---------------------------------------------------------------------------------------------------
class IdeConfig(wx.FileConfig):
    def __init__(self, file_path):
        wx.FileConfig.__init__(self, '', '', file_path, '', wx.CONFIG_USE_LOCAL_FILE)
        
    #-------------------------------------------------------------------
    def save_lst(self, name, lst):
        self.Write(name, ';'.join(lst))
    
    #-------------------------------------------------------------------
    def load_lst(self, name):
        s = self.Read(name, '')
        if s == '':
            return []
        else:
            lst = s.split(';')
            return lst
    
    #-------------------------------------------------------------------
    def save_lst_int(self, name, lst):
        self.Write(name, str(lst))
    
    #-------------------------------------------------------------------
    def load_lst_int(self, name):
        s = self.Read(name, '')
        if s == '':
            return []
        else:
            lst = eval(s)
            return lst
        
    #-------------------------------------------------------------------
    def save_dict(self, name, dict):
        lst = dict.keys() 
        self.save_lst(name + '_keys', lst)
        for k, v in dict.items():
            self.Write(name + '_' + k, str(v))
    
    #-------------------------------------------------------------------
    def load_dict(self, name):
        lst = self.load_lst(name)
        if lst == []:
            return {}
        else:
            dict = {}
            for k in lst:
                s = self.Read(name + '_' + k, "")
                dict[k] = s
            return dict


#---------------------------------------------------------------------------------------------------
class IdeApp(wx.App):
    
    def OnInit(self):
        set_app(self)
        
        self.version = VERSION
        self.name = 'Xide SDCC ' + VERSION
        
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if cur_dir.find('library.zip') > 0:
            if cur_dir.find('library.zip' + os.sep) > 0:
                cur_dir = cur_dir.replace('library.zip' + os.sep, '')
            else:
                cur_dir = cur_dir.replace('library.zip', '') 
            if cur_dir.find('ide') < 0:
                if cur_dir.endswith(os.sep) == False:
                    cur_dir += os.sep
                cur_dir += 'ide'
            
        upper_dir = os.path.dirname(cur_dir) + os.sep
        self.dirname = cur_dir + os.sep
        
        self.set_tool_path()
        self.config_file = upper_dir + 'xide.ini'
        self.cflags = ""
        self.ldflags = ""
        
        self.work_dir = upper_dir + 'examples'
        self.load_pre_config()
        self.logger = None
        self.debugging = False
        self.running = False


        self.project_dirty = False
        self.prj = None
        self.last_file_count = 0
          
        self.frame = IdeFrame(self)
        
        self.load_config()
        
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
                
        if self.doc_book.get_doc() == None:
            self.doc_book.new_file()
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
        #print(file_path)
        # add it to the history
        self.file_history.AddFileToHistory(file_path)
        
        # add file_path to toolbar target selection combo
        if self.toolbar:
            skip = False
            # if file is one of project file, skip add
            if self.prj:
                dirname = self.prj.dirname
                for f in self.prj.file_list:
                    if dirname + f == file_path:
                        skip = True
                        break
            if not skip:
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
    def get_opened_files(self):
        """ For save config, get latest opend file path list """
        lst = [] 
        for path, doc in self.doc_book.docs:
            lst.append(path)
        return lst
        
    #-------------------------------------------------------------------
    def get_history_files(self):
        """ For save config, get history file list """
        lst = [] 
        n = self.file_history.GetCount()
        for i in range(n):
            lst.append(self.file_history.GetHistoryFile(i))
        return lst
    
    #-------------------------------------------------------------------
    def save_config(self):
        """ Save config to xide.ini """
        #log("save config - " + self.config_file)
        config = IdeConfig(self.config_file)
        
        # Save IDE version
        config.Write("XideVersion", self.version)
        
        # Save working path
        config.Write("WorkDir", self.work_dir)
        
        # Save last opened project file path
        if self.prj:
            config.Write("LastProject", self.prj.file_path)
        else:
            config.Write("LastProject", "")
            
        # Save opened file path
        config.save_lst("LastOpenFiles", self.get_opened_files())
        
        # Save File History
        config.save_lst("HistoryFiles", self.get_history_files())
                
        # Save external tool path
        config.save_dict('ToolPath', self.tool_path)
        
        del config
        
    #-------------------------------------------------------------------
    def load_pre_config(self):
        """ Load config from xide.ini, before frame created """
        # Open Config File
        config = IdeConfig(self.config_file)

        if config and config.Exists("WorkDir"):
            
            # Load working path
            s = config.Read("WorkDir", "")
            if s != "":
                self.work_dir = s
                
    #-------------------------------------------------------------------
    def load_config(self):
        """ Save config to xide.ini, after frame created """
        # Open Config File
        config = IdeConfig(self.config_file)

        if config and config.Exists("XideVersion"):
                
            # Load latest opened project file
            path = config.Read("LastProject", "")
            if path != "" and os.path.exists(path):
                self.open_project(path)
                
            # Load latest open files 
            lst = config.load_lst("LastOpenFiles")
            for path in lst:
                if os.path.exists(path):
                    self.open_file(path)
                    
            # Load File History
            n = int(config.Read("HistoryFileCount", "0"))
            for i in range(n):
                path = config.Read("HistoryFile" + str(i), "")
                self.file_history.AddFileToHistory(path)
                
            # Read external tool path setting
            dict = config.load_dict('ToolPath')
            if dict != {}:
                self.tool_path = dict
                       
        del config
                 
    #-------------------------------------------------------------------
    def set_tool_path(self):
        if wx.Platform == '__WXMSW__' :
            self.tool_path = {
                'wxlua':"C:\\wx\\wxLua\\bin\\wxLua.exe",
                'wxLua_Param':" --nostdout /c ",
                'python':"C:\\Python27\\python.exe",
                'sdcc'    : "C:\\tools\\SDCC",
                'sdcc_bin': "C:\\tools\\SDCC\\bin\\sdcc.exe",
                'nodejs'  : "C:\\tools\\nw\\nw.exe",
                'gputils'  : "C:\\Program Files\\gputils",
                }
        else:
            self.tool_path = {
                'wxlua'   :"/usr/local/bin/wxLua",
                'wxLua_Param':"",
                'python'  : "/usr/bin/python2",
                'sdcc'    : "/usr/local/share/sdcc",
                'sdcc_bin': "/usr/local/bin/sdcc",
                'nodejs'  : "/usr/local/bin/nw",
                'gputils'  : "/usr/local/share/gputils",
                }
       
    #-------------------------------------------------------------------
    def search_path(self, name, path):
        if os.path.exists(path):
            return path
        
        if wx.Platform == '__WXMSW__' :
            if name == 'sdcc':
                name = 'SDCC'
            dir_lst = ['c:\\Tools\\', 'c:\\Program Files\\', 'c:\\Program Files (x86)\\', 'C:\\', 'D:\\']
            for d in dir_lst:
                path = d + name
                if os.path.exists(path):
                    return path
                
            for d in dir_lst:
                path = search_file(d, name)
                if path != "":
                    return path
            
        else:
            dir_lst = ['/usr/bin/', '/usr/local/bin/', '/usr/local/share/', '/usr', '/bin', '/sbin', '/']
            for d in dir_lst:
                path = search_file(d, name)
                if path != "":
                    return path
    
        return ""
    
    #-------------------------------------------------------------------
    def get_sdcc_inc_path(self):
        if wx.Platform == '__WXMSW__' :
            sdcc_path = self.get_path('sdcc')
            path = sdcc_path + os.sep + "include"
        else:
            path = "/usr/local/share/sdcc/include"
            
        if path.find(' ') > 0:
            q = "\""
            path = q + path + q
            
        self.tool_path['sdcc_inc'] = path
        return path

    #-------------------------------------------------------------------
    def get_sdcc_lib_path(self):
        if wx.Platform == '__WXMSW__' :
            sdcc_path = self.get_path('sdcc')
            path = sdcc_path + os.sep + "lib" 
        else:
            path = "/usr/local/share/sdcc/lib"
            
        if path.find(' ') > 0:
            q = "\""
            path = q + path + q
            
        self.tool_path['sdcc_lib'] = path
        return path
            
    #-------------------------------------------------------------------
    def get_path(self, name, path_lst=None, file_name=None):
        if wx.Platform == '__WXMSW__' :
            q = "\""
        else:
            q = ""
        sp = " "
        sep = os.sep
        # get path from default tool_path dict at first
        path = self.tool_path.get(name, "")
                
        # if can't find, do auto search
        if path == "" or not os.path.exists(path):
            if name == 'sdcc_bin':
                path = search_sdcc_bin()
                if os.path.exists(path):
                    self.tool_path['sdcc_bin'] = path
            elif name == 'sdcc_inc' :
                return self.get_sdcc_inc_path()
            elif name == 'sdcc_lib' :
                return self.get_sdcc_lib_path()
            else:
                path = self.search_path(name, path)
                if os.path.exists(path):
                    self.tool_path[name] = path
                    
        # if search top forlder only, exit and return path
        if path_lst == None:
            return path
        
        # if no sep at the end, add it
        if path.endswith(sep) == False:
            path += sep

        # join sub folders in path_lst
        path += sep.join(path_lst)
        
        # append file name 
        if file_name:
            path += sep + file_name
        
        # check if file exists
        if os.path.exists(path):
            # if space inside, add quote
            if path.find(' ') >= 0:
                return q + path + q
            else:
                return path
        else:
            MsgDlg_Warn(self.frame, 'File ' + path  + ' not exists')
            return ""
        
    #-------------------------------------------------------------------
    def OnDocPageChange(self, event):
        self.goto_line_combo.OnDocPageChange()        
        
    #-------------------------------------------------------------------
    def log(self, s):
        if self.logger is None:
            return
        self.logger.AppendText(s)
        
    #-------------------------------------------------------------------
    def warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(self.frame, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

