import wx
import wx.stc as stc
import re

from ide_global import *
from doc_base import DocBase

import doc_lexer

#---------------------------------------------------------------------------------------------------
class DocLua(DocBase):
    def __init__(self, parent, file_path):
        DocBase.__init__(self, parent, file_path)
        doc_lexer.lua_lexer(self)
        #self.lex_type = stc.STC_LEX_LUA
        #self.set_lua_lexer()
        #self.doc_t = lua_doc_init(self)
        #self.debugger = lua_debugger

    #-------------------------------------------------------------------
    def select_warning(self, msg):
        lst = []
        for s in msg.split(':'):            
            lst.append(s)
        if len(lst) >= 3 :
            file_path = lst[0]
            line = int(lst[1])
            #log(file_path, line)
            if file_exist(file_path):
                self.app.goto_file_line(file_path, line)
    #-------------------------------------------------------------------
    def select_debug_msg(self, msg):
        log("lua msg", msg, "\n")
        self.select_warning(msg)
    #-------------------------------------------------------------------
    def compile(self):
        return self.run_doc() # return True if it compiled ok
    #-------------------------------------------------------------------
    def run_doc(self):
        cmd = "%s %s %s" % (wxLua_path, wxLua_Param, os.path.basename(self.file_path))
        dprint("Run", cmd)
        os.chdir(os.path.dirname(self.file_path))
        log(os.getcwd(), cmd)
        self.run_cmd(cmd)
    #-------------------------------------------------------------------
    def find_func_pos(self, token):
        doc = self
        token = trim(token)
        #--log("["+token+ "]")
        #--print(token, text)
        n = doc.GetLength()
        token = "function "+token+ "[(w*)]"
        start_pos = doc.FindText(1, n, token, stc.STC_FIND_REGEXP)
        #--log(start_pos)
        end_pos = doc.FindText(start_pos, n, "\n")
        doc.set_range_visible(start_pos, end_pos)
        doc.SetSelection(start_pos, end_pos)
        return 0

    #-------------------------------------------------------------------
    def get_block(self, lst, tokens, i0):
        i = i0 + 1
        n = len(tokens)
        while i < n :
            t = tokens[i]

            if (t == "end") :
                return i
            elif (t == "if" or t == "for" or t == "while" ) :
                i = self.get_block(lst, tokens, i)

            i = i + 1

        return len(tokens)

    #-------------------------------------------------------------------
    def get_func_block(self, lst, tokens, i0):
        sublst = []
        t = tokens[i0 + 1]
        #print("func", t, i0)

        i = i0 + 1
        n = len(tokens)
        while i < n :
            t = tokens[i]

            if (t == "end") :
                lst.append(sublst)
                return i
            elif (t == "if" or t == "for" or t == "while" ) :
                i = self.get_block(sublst, tokens, i)
            elif (t  == "function") :
                if (tokens[i+1] == "(") :
                    if (tokens[i - 1] == "=") :
                        sublst.append(tokens[i-2])
                else:
                    sublst.append(tokens[i+1])

                i = self.get_func_block(sublst, tokens, i)

            i = i + 1

        return len(tokens)
    
    #-------------------------------------------------------------------
    def pre_process(self, s):
        s = re.sub("([--][^\n]+[\n])", "\n", s)         # replace line comment
        s = re.sub("%-%-%[%[[^%]|%[]+%]]%-%-", " ", s)  # replace block comment
        ##--s = re.sub("%([^%(%)]*%)", " ( ) ", s)       # replace parenthesis
        s = re.sub("\"[^\"\n]*\"", "", s)               # replace string
        s = re.sub("%[%[[^%[^%]]*%]%]", "", s)          # replace string
        s = re.sub("[\(]", " ( ", s)
        s = re.sub("[\)]", " ) ", s)
        s = re.sub("[[]", " [ ", s)
        s = re.sub("[]]", " ] ", s)
        s = re.sub(",", " , ", s)
        s = re.sub("=", " = ", s)
        return s
    #-------------------------------------------------------------------
    def get_func_list(self, tree):
        print("get_func_list")
        text = self.GetText()
        tokens = []
        f = 0
        quote = False
        keystr  = "if : else while do def for in end"

        text = self.pre_process(text)
        #print(text)

        #-- for each line
        for line in text.split('\n') :
            with_key = False
            for t in keystr.split() :
                if (line.find(t)) :
                    with_key = True
                    break

            if (with_key == True) :
                #-- for each token split by space
                for t in line.split() :
                    tokens.append(t)

                tokens.append('\n')

        #print(tokens)
        func_lst = []
        i = 0
        n = len(tokens)
        while i < n :
            t = tokens[i]
            if (t  == "function") :
                if (tokens[i+1] == "(") :
                    if (tokens[i - 1] == "=") :
                        func_lst.append(tokens[i-2])
                else:
                    func_lst.append(tokens[i+1])

                i = self.get_func_block(func_lst, tokens, i)

            i = i + 1

        #print("\n-----------------------------------------------",func_lst, "\n\n\n")
        self.func_list = func_lst
        tree.set_list(func_lst)

        return func_lst

#---------------------------------------------------------------------------------------------------
#lua_debugger = []
#def lua_debugger.init():
    #--log("create lua_debugger")

    #self.debug_run = 0
    #self.cur_debug_line = 0
    #self.cur_debug_doc = None
    #self.dbg = None

    #def set_breakpoint():
        #doc = self.cur_debug_editor
        #n = doc.GetLineCount()
        #dbg = self.dbg
        #--log("set_breakpoint", doc.file_path)
        #dbg.ClearAllBreakPoints()
        #for line = 1, n do
            #if (doc.breakpoints[line] == 1) :
                #log(dbg.AddBreakPoint(doc.file_path, line))
            #end
        #end
        #--dbg.AddBreakPoint(doc.file_path, n)
    #end

    #def clear_prev_line_marker():
        #if (self.cur_debug_editor) :
            #self.cur_debug_editor.MarkerDelete(self.cur_debug_line, MARKNUM_CURRENT_LINE)
        #end
    #end

    #def OnDebugeeConnected(self, event):
        #log("dbg Connected")
        #doc = self.cur_debug_editor

        #wxlua_debug_file_end = 0

        #self.Run(doc.file_path, doc.editor.GetText()+ "\r\n    wxlua_debug_file_end = 1\r\n")

        #self.Step()
        #self.set_breakpoint()
    #end

    #-- StopServer() -> got event OnDebuggerExit -> got event OnDebugeeDisconnected
    #def OnDebugeeDisconnected(self, event):
        #log("dbg Disconnected")

        #if (self.debug_run) :
            #--dbg.KillDebuggee()
            #dbg = self.dbg
            #dbg.Disconnect(wxlua.wxEVT_WXLUA_DEBUGGER_DEBUGGEE_CONNECTED)
            #dbg.Disconnect(wxlua.wxEVT_WXLUA_DEBUGGER_DEBUGGEE_DISCONNECTED)
            #dbg.Disconnect(wxlua.wxEVT_WXLUA_DEBUGGER_BREAK)
            #dbg.Reset()
            #dbg.debug_run = 0

            #dbg = None
            #self.dbg = None
            #--self.app.debugger = None
        #end
    #end

    #def OnDebuggerBreak(self, event):
        #line = event.GetLineNumber()
        #file_name = event.GetFileName()
        #--log("dbg Break "+str(line)+ "   "+file_name+ "  ref."+str(event.GetReference()))

        #doc = self.app.get_current_doc()

        #self.clear_prev_line_marker()

        #if (line >= doc.GetLineCount()) :
            #log("DBG. run to the end, StopServer")
            #--self.app.debugger.StopServer()
        #else:
            #doc.MarkerAdd(line, MARKNUM_CURRENT_LINE)
            #doc.GotoLine(line)
            #doc.SetSelectionStart(doc.PositionFromLine(line))
            #doc.SetSelectionEnd(doc.GetLineEndPosition(line))

            #self.cur_debug_editor = doc
            #self.cur_debug_line = line
        #end
    #end

    #def OnDebuggerExit(self, event):
        #log("*** DBG Exit."+event.GetMessage())
        #--stop_debug(event)

        #if (self.debug_run) :
            #self.debug_run = 0

            #self.dbg.KillDebuggee()
            #self.dbg.ClearAllBreakPoints()
            #self.clear_prev_line_marker()
        #end
    #end

    #def OnDebuggerPrint(self, event):
        #log("DBG Print."+event.GetMessage())
    #end

    #def OnDebuggerError(self, event):
        #log("DBG Error."+event.GetMessage())
    #end

    #def OnDebuggerStackEnum(self, event):
        #log("DBG StackEnum."+event.GetMessage())
    #end

    #def OnDebuggerStackEntryEnum(self, event):
        #log("DBG StackEntryEnum."+event.GetMessage())
    #end

    #def OnDebuggerStackTableEnum(self, event):
        #log("DBG StackTableEnum."+event.GetMessage())
    #end

    #def OnDebuggerEvalExpr(self, event):
        #log("DBG EvalExpr."+event.GetMessage())
    #end

    #def Start():
        #if (self.dbg  == None) :
            #log("create wxLuaDebuggerServer")
            #self.dbg  = wxlua.wxLuaDebuggerServer(1551)

        #end

        #--log("debugger "+str(dbg))
        #if (self.dbg ) :

            #self.debug_run = 1
            #self.cur_debug_line = 0
            #self.cur_debug_editor = self.app.get_current_doc()

            #dbg = self.dbg

            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_DEBUGGEE_CONNECTED,    self.OnDebugeeConnected)
            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_DEBUGGEE_DISCONNECTED, self.OnDebugeeDisconnected)

            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_BREAK,  self.OnDebuggerBreak)
            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_PRINT,  self.OnDebuggerPrint)
            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_ERROR,  self.OnDebuggerError)
            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_EXIT,   self.OnDebuggerExit)

            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_STACK_ENUM,       self.OnDebuggerStackEnum)
            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_STACK_ENTRY_ENUM, self.OnDebuggerStackEntryEnum)
            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_TABLE_ENUM,       self.OnDebuggerStackTableEnum)
            #dbg.Connect(wxlua.wxEVT_WXLUA_DEBUGGER_EVALUATE_EXPR,    self.OnDebuggerEvalExpr)

            #log("dbg.start server")
            #log(dbg.StartServer())

            #debuggee_pid = dbg.StartClient()
            #--log("dbg.StartClient", debuggee_pid)
        #end
        #return True
    #end

    #def Stop( ):
        #log("OnStopDebug")

        #dbg = self.dbg
        #if (dbg) :
            #dbg.StopServer()
        #end
    #end

    #def AddBreakPoint(fileName, lineNumber):
        #if (self.dbg) :
            #--log("AddBreakPoint", fileName, lineNumber, self.dbg, "\n")
            #self.dbg.AddBreakPoint(fileName, lineNumber)
        #end
    #end

    #def RemoveBreakPoint(fileName, lineNumber):
        #if (self.dbg) :
            #self.dbg.RemoveBreakPoint(fileName, lineNumber)
        #end
    #end

    #def ClearAllBreakPoints( ):
        #if (self.dbg) :
            #self.dbg.ClearAllBreakPoints()
        #end
    #end

    #def Run(fileName, buffer):
        #if (self.dbg) :
            #self.dbg.Run(fileName, buffer)
        #end
    #end

    #def Step():
        #if (self.dbg) :
            #self.dbg.Step()
        #end
    #end
    #def StepOver():
        #if (self.dbg) :
            #self.dbg.StepOver()
        #end
    #end

    #def StepOut():
        #if (self.dbg) :
            #self.dbg.StepOut()
        #end
    #end

    #def Continue():
        #if (self.dbg) :
            #log("lua_debugger continue", self.dbg)
            #return self.dbg.Continue()
        #end
    #end

    #def Break():
        #if (self.dbg) :
            #self.dbg.Break()
        #end
    #end

    #def Reset():
        #if (self.dbg) :
            #self.dbg.Reset()
        #end
    #end

    #return self
#end