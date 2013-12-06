import wx
import wx.stc as stc
import re

from ide_global import *
from doc_base import DocBase
import doc_lexer

#---------------------------------------------------------------------------------------------------
class DocJS(DocBase):
    def __init__(self, parent, file_path):
        DocBase.__init__(self, parent, file_path)
        doc_lexer.js_lexer(self)
    #-------------------------------------------------------------------
    def select_debug_msg(self, msg):
        log("js msg", msg, "\n")
        #self.select_warning(msg)        
    #-------------------------------------------------------------------
    def run_doc(self):
        path = self.file_path
        cmd = exe + " " + path
        print("Run", cmd)
        os.chdir(os.path.dirname(path))
        self.run_cmd(cmd)
    #-------------------------------------------------------------------
    def compile(self):
        pass
    #-------------------------------------------------------------------
    def get_func_list(self, tree):
        self.func_list = []
        tree.set_list(self.func_list)
    #-------------------------------------------------------------------
    def find_func_pos(self, token):
        pass

#---------------------------------------------------------------------------------------------------
class DocPython(DocBase):
    def __init__(self, parent, file_path):
        DocBase.__init__(self, parent, file_path)
        doc_lexer.python_lexer(self)
    #-------------------------------------------------------------------
    def select_debug_msg(self, msg):
        log("js msg", msg, "\n")
        #self.select_warning(msg)
    #-------------------------------------------------------------------
    def run_doc(self):
        path = self.file_path
        exe = Python_path
        cmd = exe + " " + path
        print("Run", cmd)
        os.chdir(os.path.dirname(path))
        self.run_cmd(cmd)
    #-------------------------------------------------------------------
    def compile(self):
        dprint("Precompile", "python not support compile yet, please select Run")
    #-------------------------------------------------------------------
    def get_func_list(self, tree):
        doc = self
        lst = []
        s = doc.GetText()

        #-- for each line
        for line in s.split('\n') :
            #-- for each token split by space
            for t in line.split() :
                if (t == "class" or t == "def") :
                    lst.append(line)
                break

        doc.func_list = lst
        tree.set_list(lst)

        return lst
    #-------------------------------------------------------------------
    def find_func_pos(self, token):
        doc = self
        #--token = trim(token)
        token = re.sub("\n", "", token)
        #log("["+token+ "]")
        n = doc.GetLength()
        start_pos = doc.FindText(1, n, token)
        ##--log(start_pos)
        end_pos = doc.FindText(start_pos, n, "\n")
        doc.set_range_visible(start_pos, end_pos)
        doc.SetSelection(start_pos, end_pos)
        pass    

#---------------------------------------------------------------------------------------------------
class DocDefault(DocBase):
    def __init__(self, parent, file_path):
        DocBase.__init__(self, parent, file_path)
        doc_lexer.default_lexer(self)

    #-------------------------------------------------------------------
    def run_doc(self):
        pass

    #-------------------------------------------------------------------
    def compile(self):
        pass

    #-------------------------------------------------------------------
    def get_func_list(self, tree):
        self.func_list = []
        tree.set_list(self.func_list)

    #-------------------------------------------------------------------
    def find_func_pos(self, token):
        pass
