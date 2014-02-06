import os
import sys
import re

import wx
import wx.combo
import wx.lib.scrolledpanel as scrolled
import wx.lib.filebrowsebutton as filebrowse

from ide_global import *
import utils
from ide_build_opt import Dialog, StaticLine



#---------------------------------------------------------------------------
class PathButtonTextCtrl(wx.TextCtrl):
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", btn_str="+", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL):
        wx.TextCtrl.__init__(self, parent, -1, "", size=(280,-1))
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label_str, pos=(0,0), size=(140,-1), style=wx.ALIGN_RIGHT)
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        text = self
        text.SetValue(default_str)
        text.SetHelpText(help_str)
        box.Add(text, 1, wx.EXPAND|wx.ALIGN_CENTRE, 5)
        
        self.btn = wx.Button(parent, -1, btn_str, size=(50,-1))
        box.Add(self.btn, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        
        sizer.Add(box, 0, flag, 5)
        
        
#---------------------------------------------------------------------------
class PagePathOption(wx.Panel):
    """
            Path options
    """
    def __init__(self, parent, option, option_callback):
        wx.Panel.__init__(self, parent)
        self.inited = False
        self.option = option
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        sdcc_dir = os.path.dirname(SDCC_bin_path)
        self.fbb = filebrowse.FileBrowseButton(self, -1, size=(450, -1), 
                                               buttonText= "Change",
                                               labelText= "SDCC bin:", 
                                               dialogTitle = "Choose a file",
                                               startDirectory = "",
                                               initialValue = SDCC_bin_path,
                                               changeCallback = self.fbbCallback
                                               )
        main_sizer.Add(self.fbb, 0, wx.ALL, 5)
        self.inc_path_text = PathButtonTextCtrl(self, main_sizer, "Include Search Path :", '', "", 'Change')
        self.lib_path_text = PathButtonTextCtrl(self, main_sizer, "Lib Search Path :", '', "", 'Change')

        StaticLine(self, main_sizer)

        self.SetSizer(main_sizer)
        self.Layout()
        
        # Bind event handler
                
        self.Bind(wx.EVT_BUTTON, self.OnIncPathButton, self.inc_path_text.btn)
        self.Bind(wx.EVT_BUTTON, self.OnLibPathButton, self.lib_path_text.btn)
        
        self.inited = True


    #-------------------------------------------------------------------
    def OnIncPathButton(self, event):
        # In this case we include a "New directory" button. 
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           | wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            #self.log.WriteText('You selected: %s\n' % dlg.GetPath())
            p = dlg.GetPath()
            if p.find(' ') > 0:
                p = '\"' + p + '\"'
            self.inc_path_text.write(' -I' + p)
            self.option.set_inc_pathes(self.inc_path_text.GetValue())
            self.option.dirty = True

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()    
        
    #-------------------------------------------------------------------
    def OnLibPathButton(self, event):
        # In this case we include a "New directory" button. 
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           | wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            #self.log.WriteText('You selected: %s\n' % dlg.GetPath())
            p = dlg.GetPath()
            if p.find(' ') > 0:
                p = '\"' + p + '\"'    
            self.lib_path_text.write(' -L' + p)
            self.option.set_lib_pathes(self.lib_path_text.GetValue())
            self.option.dirty = True

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
        
    #-------------------------------------------------------------------
    def fbbCallback(self, evt):
        print('FileBrowseButton: %s\n' % evt.GetString())

        
        
#---------------------------------------------------------------------------
class ToolOption():
    def __init__(self, app):
        
        self.app = app
        self.config_file = app.config_file
        self.tool_path = utils.copy_dict(app.tool_path)
        self.dirty = False
    
    
    #-------------------------------------------------------------------
    def save_config(self):
        #print("save config - sdcc.cfg")
        #self.app.save_config()
        #self.app.tool_path = utils.copy_dict(self.tool_path)
        self.dirty = False
        
    #-------------------------------------------------------------------
    def load_config(self):
        pass
    
    
        
#---------------------------------------------------------------------------
class ToolOptionDialog(Dialog):
    def __init__(self, parent, id, title):
        Dialog.__init__ ( self, parent, id, title)
        self.parent = parent
        self.log = parent.log
        self.app = parent.app
        
        self.SetInitialSize((768, 525))
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.option = ToolOption(self.app)
        opt = self.option
        opt.load_config()
        opt.dialog = self
        
        # Here we create a panel and a notebook on the panel
        nb_panel = wx.Panel(self)
        nb = wx.Notebook(nb_panel)

        nb.log = self.log
        
        self.page_list = [
            [PagePathOption,       'Tool Path Options'],
        ]
        i = 0
        for t in self.page_list:
            page_class = t[0]
            page = page_class(nb, opt, None)
            t.append(page)
            nb.AddPage(page, t[1])
            page.page_index = i
            page.parent = nb
            i += 1
            
        # Put the notebook in a sizer for the panel to manage the layout
        nb_sizer = wx.BoxSizer(wx.VERTICAL)        
        nb_sizer.Add(nb, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        nb_panel.SetSizer(nb_sizer)
        
        # Add ok and cancel button
        main_sizer.Add(nb_panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
       
        StaticLine(self, main_sizer)
        self.add_ok_cancel_button(main_sizer)
        
        self.SetSizer(main_sizer)
        self.Layout()
            
        self.Bind(wx.EVT_BUTTON, self.OnClickOK, self.btn_ok)
        self.Bind(wx.EVT_CLOSE, self.OnCloseDialog)

    #-------------------------------------------------------------------
    def OnClickOK(self, event):
        #print 'OnCloseDialog'
        opt = self.option
        opt.save_config()
        event.Skip()
                
    #-------------------------------------------------------------------
    def ask_if_save_config(self, msg):
        strs = "Tool option is modified. Do you want to save?"
        dlg = wx.MessageDialog(self, strs, msg, wx.YES_NO)
        result = dlg.ShowModal()
        dlg.Destroy()
        #log("ask_if_save return=", result, "yes=", wx.ID_YES, "no=", wx.ID_NO)
        if result == wx.ID_YES :
            opt = self.option
            opt.save_config()
        
    #-------------------------------------------------------------------
    def OnCloseDialog(self, event):
        #print 'OnCloseDialog'
        if self.option.dirty:
            self.ask_if_save_config("OnCloseDialog")
        event.Skip()


