import os
import signal
import sys
import time
import subprocess
from threading import Thread
import wx
import wx.stc as stc
import re
import Queue

from ide_global import *
from doc_base import DocBase
import doc_lexer
import sim
import ide_build_opt

#test_cmd = {"break 30\n", "break 40\n", "run\n", "continue\n", 
#        "step\n", "step\n",  "step\n", "step\n", "step\n", "step\n", "step\n", "quit\n",}

def search_file(root_dir, search_name):
    #print root_dir
    for root, dirnames, filenames in os.walk(root_dir):
        for file_name in filenames :
            if file_name == search_name:
                path = root + os.sep + file_name
                print "found at ", path
                return path
        for dir_name in dirnames:
            path = search_file(root_dir + dir_name, search_name)
            if path != "":
                return path
            
    return ""

#---------------------------------------------------------------------------------------------------
class DocC(DocBase):
    
    def __init__(self, parent, file_path):
        DocBase.__init__(self, parent, file_path)
        doc_lexer.c_lexer(self)
        self.debugging = False
        self.running = False
        self.cmd_queue = None
        self.bid = None
        self.s_out = None
        self.process = None
        self.sim_frame = None
        self.pop_menu = wx.Menu()
        self.pop_menu.Append(101, '&Open', 'Open a new document')
        self.pop_menu.Append(102, '&Save', 'Save the document')
        self.config_file = self.file_path.replace('.c', '.sdcfg')
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.mcu_name  = ""
        self.mcu_device = ""
        
    #-------------------------------------------------------------------
    def OnRightDown(self, event):
        #self.PopupMenu(self.pop_menu, event.GetPosition())
        s = self.GetSelectedTextRaw()
        
        if s.find("#include") >= 0 :
            self.inc_lst = []
            m = wx.Menu()
            matches = re.findall(r'\#include\s+\<(.+?)\>', s)
            for name in matches:
                name = name.strip()
                nid = wx.NewId()
                self.inc_lst.append([nid, name, 'global'])
                m.Append(nid, '&Open ' + name, 'Search and Open header file')
                self.Bind(wx.EVT_MENU, self.OnOpenHeaderFile,  id=nid)
            
            matches = re.findall(r'\#include\s+\"(.+?)\"', s)
            for name in matches:
                name = name.strip()
                nid = wx.NewId()
                self.inc_lst.append([nid, name, 'local'])
                m.Append(nid, '&Open ' + name, 'Search and Open header file')
                self.Bind(wx.EVT_MENU, self.OnOpenHeaderFile,  id=nid)
            self.PopupMenu(m, event.GetPosition() + wx.Point(10, 0))
    
    #-------------------------------------------------------------------
    def OnOpenHeaderFile(self, event):
        local_path = os.path.dirname(self.file_path)
        
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
    def OnIdle(self, event):
        if self.process is None:
            return
  
        # do process output stream (wx.Process input stream!)
        stream = self.process.GetInputStream()
        while stream.CanRead():
            text = stream.readline()
            if (text == '\xff'):
                print text
                return
            dprint("read", text)
  
        #clear any process output waiting to be read
        stream = self.process.GetErrorStream()
        if stream.CanRead():
            text = stream.read()
            if (text == '\xff'):
                print text
                return            
            dprint("err", text)
        
        if self.cmd_queue and not self.cmd_queue.empty():
            s = self.cmd_queue.get()
            print("get", s) 
            stream = self.process.GetOutputStream()
            stream.write(s + "\n") 
            #os.kill(self.pid, signal.SIGINT)
            
    #-------------------------------------------------------------------
    def OnProcessEnded(self, event):
        pid = event.GetPid()
        exitcode = event.GetExitCode()
  
        #clear any process output waiting to be read
        stream = self.process.GetInputStream()
        if stream.CanRead():
            text = stream.read()
            dprint("read", text)

        #clear any process output waiting to be read
        stream = self.process.GetErrorStream()
        if stream.CanRead():
            text = stream.read()
            dprint("err", text)
        
        #write message
        text = '\nProcess (pid: '+str(pid)+') ended.\n'
        log(text)
        text ='Exit code: '+str(exitcode)+'\n'
        log(text)
        text = 'Runtime: ' +str(time.time() - self.runtime)+'\n'
        log(text)
  
        #destroy process
        self.process.Destroy()
        self.process = None
        self.pid = None
  
        self.Unbind( wx.EVT_IDLE, handler=self.OnIdle)
        
        self.app.debugging = False
        self.debugging = False
        self.cmd_queue = None 
        
    #-------------------------------------------------------------------
    def start_process(self, path, cmd, args):
        self.process = wx.Process(self)
        self.process.Redirect()
        
        #bind events
        self.process.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)

        self.pid = wx.Execute(path + cmd + " " + args, wx.EXEC_ASYNC|wx.EXEC_NOHIDE, self.process)
        
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.runtime = time.time()
  
        text = 'Executing: '+cmd +'\n(Process pid: '+str(self.pid)+')\n'
        dprint("start", text)
        return self.process
    
    #-------------------------------------------------------------------
    def kill_process(self):
        if self.process is not None:
            self.process.CloseOutput()
            #try to terminate, then kill
            if wx.Process.Kill(self.pid, wx.SIGTERM) != wx.KILL_OK:
                wx.Process.Kill(self.pid, wx.SIGKILL, flags=wx.KILL_CHILDREN)

    #-------------------------------------------------------------------
    def send_debug_cmd(self, s):        
        #dprint("put", s)
        if self.cmd_queue :
            self.cmd_queue.put(s)

    #-------------------------------------------------------------------
    def stop(self):
        if self.sim_frame is not None:
            self.sim_frame.close()
            self.sim_frame = None

    #-------------------------------------------------------------------
    def start_debug(self):
        # set cwd to doc file_path
        os.chdir(os.path.dirname(self.file_path))
        name, ext = self.file_name.split('.')
        
        self.sim_frame = sim.SimFrame(self.app, self, 
                                  [self.file_path], 
                                  self.config_file, 'debug')
        
        self.app.SetTopWindow(self.sim_frame)
        self.sim_frame.Show(True)
        
    #-------------------------------------------------------------------    
    def run_doc(self):
        if not self.compile():
            return
        
        # set cwd to doc file_path
        os.chdir(os.path.dirname(self.file_path))
        name, ext = self.file_name.split('.')

        #self.cmd_queue = Queue.Queue()
        #mcu_name = sdcc.get_mcu_from_config(self.file_path)
        #if mcu_name == 'pic14':
            #sim = sim_pic14
        #else:
            
        self.sim_frame = sim.SimFrame(self.app, self, 
                                  [self.file_path], 
                                  self.config_file, 'run')
        
        self.app.SetTopWindow(self.sim_frame)
        self.sim_frame.Show(True)
        #self.start_process(os.path.dirname(SDCC_path) + "/", "s51", name + ".ihx")
        
    #-------------------------------------------------------------------
    def sim_close(self):
        self.sim_frame = None
        self.app.toolbar.debug_stopped()
        
    #-------------------------------------------------------------------
    def c_pre_process(self, s):
        s = re.sub("/\*[^\*]*\*/", "[$BC]", s)        # replace block comment
        s = re.sub("([//][^\n]*[\n])", "[$LC]\n", s)  # replace line comment
        s = re.sub("\([^\(\)]*\)", " () ", s)         # replace parenthesis
        s = re.sub("\"[^\"\n]*\"", "[$ST]", s)        # replace string
        
        p_blk = "{[^{^}]*}"
        match = re.search(p_blk, s)
        if (match):
            s = re.sub(p_blk, "[$BLK]", s)
            while (match) :
                s = re.sub(p_blk, "[$BLK]", s)
                match = re.search(p_blk, s)

        s = re.sub(",", " , ", s)
        s = re.sub("=", " = ", s)
        return s
    
    #-------------------------------------------------------------------
    def get_func_list(self, tree):
        doc = self
        lst = []
        s = doc.GetText()
        s = self.c_pre_process(s)
        
        match = re.findall(r"\w+\s+\(\)\s+[\[]+", s)
        #log(match)
        for t in match :
            t = re.sub("[\[\n\(\)]", "", t)
            lst.append(t)

        doc.func_list = lst
        #log(lst)
        tree.set_list(self.func_list)
        return lst
    
    #-------------------------------------------------------------------
    def find_func_pos(self, token):
        doc = self
        token = trim(token)
        #--log("[" +token+ "]")
        n = doc.GetLength()
        t1 = "^"+token+ " ("
        start_pos = doc.FindText(1, n, t1, stc.STC_FIND_REGEXP)
        if (start_pos < 0) :
            t1 = "^[a-zA-Z0-9_*)]+ "+token+ " ("
            start_pos = doc.FindText(1, n, t1, stc.STC_FIND_REGEXP)
            if (start_pos < 0) :
                t1 = "[a-zA-Z0-9_)]+ [a-zA-Z0-9_*)]+ "+token+ " ("
                start_pos = doc.FindText(1, n, t1, stc.STC_FIND_REGEXP)
                if (start_pos < 0) :
                    start_pos = doc.FindText(1, n, token, stc.STC_FIND_REGEXP)
                #end
            #end
        #end

        end_pos = doc.FindText(start_pos, n, "\n")
        doc.set_range_visible(start_pos, end_pos)
        doc.SetSelection(start_pos, end_pos)
        return 0
    
    #-------------------------------------------------------------------
    def load_config(self):
        #print("load config - sdcc.cfg")
        config_file = self.file_path.replace('.c', '.sdcfg')
        if not os.path.exists(config_file):
            self.app.set_build_option()
            return
        
        config = wx.FileConfig("", "", config_file, "", wx.CONFIG_USE_LOCAL_FILE)

        if config.Exists("mcu_name"):
            self.app.cflags  = config.Read("cflags", "")
            self.app.ldflags = config.Read("ldflags", "")
            self.mcu_name  = config.Read("mcu_name", "")
            self.mcu_device = config.Read("mcu_device", "")            
        else:
            del config
            self.app.set_build_option()
            return
            
        del config
    
    #-------------------------------------------------------------------
    def compile(self):
        result = 0
        dprint("Compile", self.file_path)
        self.load_config()
        #-- do the compilation
        # --model-small --code-loc 0x2000 --data-loc 0x30 --stack-after-data --xram
        #flag = " --debug --peep-asm " #" --disable-warning 59 "
        flag = " " + self.app.cflags + " " + self.app.ldflags + " " 
        
        SDCC_bin_path = get_sdcc_bin_path()    
        
        if self.mcu_name == 'pic16' :
            flag += ' -c '
            cmd = '\"' + SDCC_bin_path + '\"' + flag + self.file_path 
    
            dprint("Cmd", cmd)
            os.chdir(os.path.dirname(self.file_path))
            result = self.run_cmd(cmd)            

            c_file = self.file_path
            asm_file = c_file.replace('.c', '.asm')
            hex_file = c_file.replace('.c', '.hex')
            obj_file = c_file.replace('.c', '.o')
            
            cmd = "gpasm -c " + asm_file + " && "
            cmd += "gplink -m -s /usr/local/share/gputils/lkr/" + self.mcu_device + "_g.lkr -o " + hex_file
            cmd += " /usr/local/share/sdcc/non-free/lib/pic16/libdev" + self.mcu_device + ".lib /usr/local/share/sdcc/lib/pic16/libsdcc.lib " + obj_file
            self.run_cmd(cmd)
        elif self.mcu_name == 'pic14' :
            flag += ' -c '
            cmd = '\"' + SDCC_bin_path + '\"' + flag + self.file_path 
    
            dprint("Cmd", cmd)
            os.chdir(os.path.dirname(self.file_path))
            result = self.run_cmd(cmd)            

            c_file = self.file_path
            asm_file = c_file.replace('.c', '.asm')
            hex_file = c_file.replace('.c', '.hex')
            obj_file = c_file.replace('.c', '.o')
            lkr = " /usr/local/share/gputils/lkr/" + self.mcu_device + "_g.lkr "
            sdcc_lib = " /usr/local/share/sdcc/lib/pic14/libsdcc.lib "
            pic14_lib = " /usr/local/share/sdcc/non-free/lib/pic14/pic" + self.mcu_device + ".lib "
            
            cmd = "gpasm -c " + asm_file + " && "
            cmd += "gplink -m -s " + lkr + " -o " + hex_file
            cmd += pic14_lib + sdcc_lib + obj_file
            
            self.run_cmd(cmd)

        else:
            cmd = '\"' + SDCC_bin_path + '\"' + flag + self.file_path 
    
            dprint("Cmd", cmd)
            os.chdir(os.path.dirname(self.file_path))
            result = self.run_cmd(cmd)            
        return result # return True if it compiled ok

    #-------------------------------------------------------------------
    def select_warning(self, msg):
        lst = []
        for s in msg.split(':'):
            lst.append(s)
        if len(lst) >= 4 :
            file_path = lst[0]
            line = int(lst[1])
            #log(file_path, line)
            if file_exist(file_path):
                self.app.goto_file_line(file_path, line)
                
    #-------------------------------------------------------------------
    def select_undefined(self, msg):
        #pattern 1:  ?ASlink-Warning-Undefined Global '_pm2_phex' referenced by module 'blink1'
        lst = []
        for s in msg.split(' ') :
            lst.append(s)
            log(len(lst) - 1, s, "\n")
        #print msg.find("?ASlink-Warning-Undefined")
        if lst[0] == "?ASlink-Warning-Undefined" :
            s = lst[2]
            s = re.sub('\'', '', s)
            s = re.sub('_', '', s, 1)
            log(lst[2], s)
            doc = self.app.get_doc()
            doc.search_text(s)
            
    #-------------------------------------------------------------------
    def select_debug_msg(self, msg):
        #log("OnItemSelected", i, msg, "\n")
        if msg[0:1] == '?' :
            self.select_undefined(msg)
        else:
            self.select_warning(msg)
