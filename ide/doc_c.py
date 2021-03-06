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
from ide_menu import Menu


#---------------------------------------------------------------------------------------------------
class DocC(DocBase):
    
    def __init__(self, parent, file_path):
        DocBase.__init__(self, parent, file_path)
        doc_lexer.c_lexer(self)
        self.app = parent.app
        self.frame = self.app.frame
        self.debugging = False
        self.running = False
        self.cmd_queue = None
        self.bid = None
        self.s_out = None
        self.process = None
        self.sim_frame = None
        
        self.config_file = self.file_path.replace('.c', '.sdcfg')
        self.dirname = os.path.dirname(file_path)
        
        self.mcu_name  = ""
        self.mcu_device = ""
        
        self.load_config()
        
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
        if hasattr(self, 'sim_frame'):
            
            if self.sim_frame is not None:
                try:
                    self.sim_frame.close()
                except:
                    print "Error: unable to close sim_frame"
                
        self.sim_frame = None

    #-------------------------------------------------------------------
    def start_debug(self):
        # set cwd to doc file_path
        os.chdir(os.path.dirname(self.file_path))
        name, ext = self.file_name.split('.')
        if self.compile_before_debug() == False:
            MsgDlg_Warn(self.app.frame, "Compile fail")
            return
        self.app.debugging = True
        self.sim_frame = sim.DebugFrame(self.app, self, 
                                  [self.file_path], 
                                  self.config_file)
        
        self.app.SetTopWindow(self.sim_frame)
        self.sim_frame.Show(True)
        
    #-------------------------------------------------------------------    
    def run_doc(self):
        if not self.compile():
            return
        
        # set cwd to doc file_path
        os.chdir(os.path.dirname(self.file_path))
        name, ext = self.file_name.split('.')

        self.app.running = True
        self.sim_frame = sim.SimFrame(self.app, self, 
                                  [self.file_path], 
                                  self.config_file)
        
        self.app.SetTopWindow(self.sim_frame)
        self.sim_frame.Show(True)
        #self.start_process(os.path.dirname(SDCC_path) + "/", "s51", name + ".ihx")
        
    #-------------------------------------------------------------------
    def sim_close(self):
        self.sim_frame = None
        self.app.running = False
        self.app.debugging = False
        
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
            
            # load breakpoints
            s = config.Read("breakpoints", "")
            if s == "":
                self.breakpoints = None
            else:
                lst = s.split(';')
                
                for t in lst:
                    path, b = t.split("=")
                    if path == self.file_path:
                        blst = eval(b)
                        self.breakpoints = blst

        else:
            del config
            self.app.set_build_option()
            return
            
        del config

    #-------------------------------------------------------------------
    def get_sdcc_path(self):
        sdcc_path = self.app.get_path('sdcc_bin')
        if os.path.exists(sdcc_path) == False:
            log('Error!!! Cannot find SDCC!')
            MsgDlg_Warn(self.app.frame, "Cannot find SDCC" , caption='Warning!')
            return None
        return sdcc_path
    
    #-------------------------------------------------------------------
    def get_gptuils_path(self):
        gputil_path = self.app.get_path('gputils')
        if os.path.exists(gputil_path) == False:
            log('Error!!! Cannot find gputils!')
            MsgDlg_Warn(self.app.frame, "Cannot find gputils" , caption='Warning!')
            return None
        return gputil_path
    
    #-------------------------------------------------------------------
    def compile_before_debug(self):
        dprint("Compile", self.file_path)
        
        # load muc_name, mcu_device, cflags and ldflags
        self.load_config()
        
        # get sdcc_bin path
        sdcc_path = self.get_sdcc_path()
        if sdcc_path == None:
            return False
        
        # if pic14/pic16 get gputils path
        if self.mcu_name.find('pic') >= 0:
            gputil_path = self.get_gptuils_path()
            if gputil_path == None:
                return False
            
        # chdir to source path
        os.chdir(self.dirname)
        
        # set flag
        flag = "  --debug " + self.app.cflags + " " + self.app.ldflags + " " 
        
        # check mcu do the compilation
        mcu = self.mcu_name
        if mcu == 'pic14' or mcu == 'pic16' :
            flag += ' -c '
            q = '\"'
            c_file = q + self.file_path + q
            cmd = q + sdcc_path + q + flag + c_file
            result = self.run_cmd(cmd)
            
            
            asm_file = c_file.replace('.c', '.asm')
            hex_file = c_file.replace('.c', '.hex')
            obj_file = c_file.replace('.c', '.o')
            
            lkr = self.app.get_path('gputils', ['lkr'], self.mcu_device + "_g.lkr")
            sdcc_lib = self.app.get_path('sdcc', ['lib', mcu], 'libsdcc.lib')
            pic_lib = self.app.get_path('sdcc', ['non-free', 'lib', mcu], "pic" + self.mcu_device + ".lib")

            sp = " "
            cmd = "gpasm -c " + asm_file + " && "
            cmd += "gplink -m -c -s " + lkr + " -o " + hex_file
            cmd += sp + pic_lib + sp + sdcc_lib 
            cmd += sp + obj_file
            
            result = self.run_cmd(cmd)
            
        else:
            # mcs51 and all the others mcu
            q = '\"'
            cmd = q + sdcc_path + q + flag + q + self.file_path + q
            
            dprint("Cmd", cmd)
            result = self.run_cmd(cmd)
            
        return result # return True if it compiled ok
    
    #-------------------------------------------------------------------
    def compile(self):
        dprint("Compile", self.file_path)
        self.load_config()

        flag = " " + self.app.cflags + " " + self.app.ldflags + " " 
        
        # get sdcc_bin path
        sdcc_path = self.get_sdcc_path()
        if sdcc_path == None:
            return False
        q = '\"'
        cmd = q + sdcc_path + q + flag + q + self.file_path + q

        dprint("Cmd", cmd)
        os.chdir(self.dirname)
        result = self.run_cmd(cmd)
        return result # return True if it compiled ok

    #-------------------------------------------------------------------
    def select_warning(self, msg):
        lst = []
        for s in msg.split(':'):
            lst.append(s)
        if len(lst) >= 4 :
            file_path = lst[0]
            s = lst[1]
            if s.isdigit():
                line = int(s)
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
            

            
