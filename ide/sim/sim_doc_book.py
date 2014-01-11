import os
import sys
import wx
import wx.stc as stc

from sim_global import *

from sim_doc import Doc
from sim_doc_base import DocBase

#---------------------------------------------------------------------------------------------------
class DocBook(wx.aui.AuiNotebook):
    
    def __init__(self, app, frame):
        wx.aui.AuiNotebook.__init__(self, frame, wx.ID_ANY,
                                    wx.DefaultPosition,
                                    wx.DefaultSize,
                                    wx.aui.AUI_NB_DEFAULT_STYLE | wx.aui.AUI_NB_TAB_EXTERNAL_MOVE |
                                    wx.NO_BORDER)
        self.nb = self
        self.docs  = []
        self.cur_doc = None
        self.new_file_index = 0
        self.app = app

        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChange)
        
    #-------------------------------------------------------------------
    def get_breakpoints(self):
        lst = []
        for path, doc in self.docs:
            s = doc.get_breakpoints()
            if s:
                lst.append(path + "=" + s)
                
        return lst
        
    #-------------------------------------------------------------------
    def close(self):
        for path, doc in self.docs:
            doc.close()
            del doc
            
    #-------------------------------------------------------------------
    def search_doc(self, file_path):
        for path, doc in self.docs:
            if path == file_path:
                return doc
        return None

    #-------------------------------------------------------------------
    def create_doc_editor(self, file_path):
        doc = Doc(self, file_path)

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
    def open_file(self, file_path):
        if not os.path.exists(file_path):
            return None

        doc = self.search_doc(file_path)

        if doc is None:
            doc = self.create_doc_editor(file_path)

        page_i = doc.page_index
        self.SetSelection(page_i)

        #print("Open", file_path, page_i)
        doc.LoadFile(file_path)
        #print("LoadFile" + doc.GetText())
        doc.SetReadOnly(True)
        self.cur_doc = doc

        return doc

    #-------------------------------------------------------------------
    def update_current_doc(self):
        #-- get notebook selected page index
        page_i = self.GetSelection()

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
    def OnPageClose(self, event):
        self.update_current_doc()
        event.Skip()

    #-------------------------------------------------------------------
    def OnPageChange(self, event):
        self.update_current_doc()

