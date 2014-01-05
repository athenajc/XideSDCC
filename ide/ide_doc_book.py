import os
import sys
import wx
import wx.stc as stc

from ide_global import *

import doc_scripts
import doc_c
import doc_lua

DocC       = doc_c.DocC
DocLua     = doc_lua.DocLua
DocPython  = doc_scripts.DocPython
DocJS      = doc_scripts.DocJS
DocDefault = doc_scripts.DocDefault

#---------------------------------------------------------------------------------------------------
class DocBook(wx.aui.AuiNotebook):
    
    def __init__(self, app, frame, size):
        wx.aui.AuiNotebook.__init__(self, frame, wx.ID_ANY,
                                    wx.DefaultPosition,
                                    size,
                                    wx.aui.AUI_NB_DEFAULT_STYLE | wx.aui.AUI_NB_TAB_EXTERNAL_MOVE |
                                    wx.NO_BORDER)
        self.nb = self
        self.docs  = []
        self.cur_doc = None
        self.new_file_index = 0
        self.app = app

        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChange)
        
        self.Bind(wx.EVT_MENU, self.OnRun,       id=ID_RUN)
        self.Bind(wx.EVT_MENU, self.OnCompile,   id=ID_COMPILE)
        self.Bind(wx.EVT_MENU, self.OnStartDebug,id=ID_DBG_START)
        self.Bind(wx.EVT_MENU, self.OnStopDebug, id=ID_DBG_STOP)
                
        
    #-------------------------------------------------------------------
    def get_target_doc(self):
        log("DocBook.get_target_doc")
        file_path = self.app.toolbar.get_target()
        #log('compile', file_path)
        
        # check if select prj, if yes compile project
        if file_path.find('sdprj') > 0 and self.app.prj :
            #self.app.prj.compile_project()
            return 'prj'
        
        # get toolbar selected target at first
        if file_path != "":            
            doc = self.search_doc(file_path)
            if doc != self.get_doc():
                self.open_file(file_path)
                
        # try current open doc
        if doc is None:
            doc = self.app.get_doc()
            if doc.file_path.find(".c") < 0:
                strs = doc.file_path + " not a valid C file, can't be compiled."
                dlg = wx.MessageDialog(self.app.frame, strs, msg, wx.YES_NO)
                result = dlg.ShowModal()
                dlg.Destroy()
                
        if doc.modified:
            dprint("AutoSave", doc.file_path)
            doc.save_file()
            
        return doc
    
    #-------------------------------------------------------------------
    def OnRun(self, event):
        log("DocBook.OnRun")
        doc = self.get_target_doc()
        if doc is None:
            return
        elif doc == 'prj':
            self.app.prj_mgr.run_project()
            return
            
        self.app.running = True
        self.app.doc_running = doc
        self.app.clear_debug()
                    
        dprint("Run", doc.file_path)
        doc.run_doc()
        self.app.show_debug()
    
    #-------------------------------------------------------------------
    def OnCompile(self, event):
        log("DocBook.OnCompile")
        self.app.clear_debug()
        doc = self.get_target_doc()
        if doc is None:
            return
        elif doc == 'prj':
            self.app.prj.compile_project()
        else:
            doc.compile()
            self.app.show_debug()
        
    #-------------------------------------------------------------------
    def OnStartDebug(self, event):
        log("DocMgr.OnStartDebug")
        doc = self.get_target_doc()
        if doc is None:
            return
        elif doc == 'prj':
            self.app.prj_mgr.debug_project()
            return
        
        app = self.app
        doc = app.get_doc()
        
        if doc.debugging:
            doc.send_debug_cmd('continue')
            return
        
        app.debugging = True
        app.doc_debugging = doc
        app.clear_debug()
        app.show_debug()
        doc.start_debug()
        
    #-------------------------------------------------------------------
    def OnStopDebug(self, event):
        doc = self.app.get_doc()
        doc.stop()
        #if doc.debugging:
        #    doc.send_debug_cmd('quit')
            
    #-------------------------------------------------------------------
    def close(self):
        for path, doc in self.docs:
            doc.close()
            print "del", doc
            del doc
            
    #-------------------------------------------------------------------
    def search_doc(self, file_path):
        for path, doc in self.docs:
            if path == file_path:
                return doc
        return None

    #-------------------------------------------------------------------
    def create_doc_editor(self, file_path):
        ext = get_filename_ext(file_path)

        # create new document editor
        if ext == "lua":
            doc = DocLua(self, file_path)
        elif ext == "c" or ext == "cpp" or ext == "cc" or ext == "h" or ext == "hpp":
            doc = DocC(self, file_path)
        elif ext == "py":
            doc = DocPython(self, file_path)
        elif ext == "js":
            doc = DocJS(self, file_path)
        else:
            doc = DocDefault(self, file_path)

        #print("load", doc, doc.file_path)
        #print(os.path.dirname(file_path))
        if file_path == "":
            file_path = "untitled"

        self.docs.append([file_path, doc])

        # add page to center notebook
        self.AddPage(doc, doc.file_name, False)

        # store page index for selection
        doc.page_index = self.GetPageIndex(doc)

        return doc

    #-------------------------------------------------------------------
    def get_new_filename(self):        
        cwd = os.getcwd()
        file_path = cwd + "/untitled" + str(self.new_file_index) + ".c"
        log("get_new_filename", cwd, self.new_file_index)
        self.new_file_index += 1
        while file_exist(file_path):
            file_path = cwd + "/untitled" + str(self.new_file_index) + ".c"
            self.new_file_index += 1
        
        log("new", file_path)
        return file_path

    #-------------------------------------------------------------------
    def new_file(self):
        file_path = self.get_new_filename()
        doc = self.create_doc_editor(file_path)
        self.SetSelection(doc.page_index)
        doc.get_func_list(self.app.functree)
        doc.modified = False
        self.cur_doc = doc
        return doc

    #-------------------------------------------------------------------
    def open_file(self, file_path):
        if not file_exist(file_path):
            return None

        doc = self.search_doc(file_path)

        if doc is None:
            doc = self.create_doc_editor(file_path)

        page_i = doc.page_index
        self.SetSelection(page_i)

        if file_path != "":
            doc.open_file(file_path)
        else :
            doc.SetText("")

        self.cur_doc = doc

        return doc

    #-------------------------------------------------------------------
    def check_docs_modified(self, dt):
        for path, doc in self.docs:
            doc.check_modified(dt)

    #-------------------------------------------------------------------
    def update_nb_page_title(self, file_name):
        #-- get notebook selected page index
        page_i = self.GetSelection()

        if file_name == "":
            self.SetPageText(page_i, wxT("untitled.c"))
        else:
            name = get_filename(file_name)
            self.SetPageText(page_i, wxT(name))

    #-------------------------------------------------------------------
    def update_current_doc(self):
        #-- get notebook selected page index
        page_i = self.GetSelection()
        if page_i < 0:
            return None
        
        #-- get doc by page index
        doc = self.GetPage(page_i)
        if doc is None:
            log("doc is None", doc, page_i)
            return None

        self.cur_doc = self.search_doc(doc.file_path)
        return self.cur_doc

    #-------------------------------------------------------------------
    def get_doc(self):
        return self.update_current_doc()

    #-------------------------------------------------------------------
    def get_current_file(self):
        doc = self.get_doc()
        if doc:
            return doc.file_path
        else:
            return ""

    #-------------------------------------------------------------------
    def print_docs(self):
        for path, doc in self.docs:
            print(path, doc)

    #-------------------------------------------------------------------
    def remove_doc(self, doc):
        log("remove doc  ", doc, len(self.docs))
        i = 0
        for path, d in self.docs :
            if path == doc.file_path:
                self.docs.pop(i)
            i += 1
        log("after remove", len(self.docs))

    #-------------------------------------------------------------------
    def save_on_close_file(self, doc):
        #-- print(self, event)
        result = wx.ID_YES
        if doc.modified :
            result = doc.ask_if_save("Save on close")
            
        self.remove_doc(doc)
        return result

    #-------------------------------------------------------------------
    def save_on_exit(self, event):
        #print(self, "save_on_exit")
        for path_key, doc in self.docs :
            if doc is None :
                continue
            if hasattr(doc, 'debugging') and doc.debugging :
                doc.send_debug_cmd('quit')
            if doc.modified :
                return doc.ask_if_save("Save on exit")

        return wx.ID_YES

    #-------------------------------------------------------------------
    def update_function_list(self):
        doc = self.update_current_doc()
        if doc is None:
            return

        lst = doc.func_list
        if doc.file_name != "":
            self.app.functree.set_list(doc.func_list)

    #-------------------------------------------------------------------
    def OnPageClose(self, event):
        i = event.GetSelection()
        page_text = self.GetPageText(i)

        if page_text == "Information":
            self.update_current_doc()
        else:
            log("OnPageClose", self.GetPage(event.GetSelection()).file_name)
            doc = self.cur_doc
            self.save_on_close_file(doc)
            
        if self.get_doc() == None:
            self.new_file()
            
        event.Skip()

    #-------------------------------------------------------------------
    def OnPageChange(self, event):
        i = event.GetSelection()
        page_text = self.GetPageText(i)

        if page_text == "Information":
            self.cur_doc = None
            self.app.set_title(page_text)
        else:
            self.update_function_list()
            doc = self.cur_doc
            if doc:
                path = doc.file_path
                self.app.toolbar.select_file(path)
            else:
                doc = self.new_file()
                path = "untitled"
            
            self.app.set_title(path)

        self.app.OnDocPageChange(event)
        
        event.Skip()
        
    #-------------------------------------------------------------------
    def save_as_file(self, doc, file_path):
        if doc:
            old_path = doc.file_path
            i = 0
            for p, d in self.docs:
                if d == doc:
                    self.docs[i] = [file_path, doc]
                    break
                i += 1
                
            self.open_file(file_path)
            
            doc.LoadFile(file_path)
            doc.set_unmodified()
            doc.file_path = file_path
            doc.file_name = os.path.basename(file_path)
            
            page = self.GetPageIndex(doc)
            self.SetPageText(page, doc.file_name)
 
            #self.app.toolbar.select_file(path)
            self.app.set_title(file_path)
            
        
    #-------------------------------------------------------------------
    def close_file(self, doc):
        if doc:
            self.save_on_close_file(doc)
            page = self.GetPageIndex(doc)
            self.RemovePage(page)
            del doc
                        
    #-------------------------------------------------------------------
    def OnCloseFile(self, event):
        doc = self.app.get_doc()
        if doc:
            self.close_file(doc)
            
        if self.get_doc() == None:
            self.new_file()
        
    #-------------------------------------------------------------------
    def OnCloseAllFile(self, event):
        lst = []
        for path, doc in self.docs:
            lst.append(doc)
            
        for doc in lst:
            self.close_file(doc)
            
        self.new_file()
        
        

        


