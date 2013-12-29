import os
import sys
import wx
import wx.grid
import wx.lib.filebrowsebutton as filebrowse
import xml.etree.ElementTree as ET
import subprocess


from ide_global import *
import utils
from sim import SimFrame, DebugFrame


#----------------------------------------------------------------------------------------------
class Project():
    def __init__(self, app, tree, file_path):
        self.app = app
        self.tree = tree
        self.frame = app.frame
        self.dirty = False
        
        self.file_list = []
        self.file_path = file_path
        self.app.prj = self
        self.dirname = os.path.dirname(file_path) + os.sep
        self.config_file = file_path.replace('sdprj', 'sdcfg')
        self.file_list = []
        self.app.proj_history.add_proj_history(file_path)

        self.xml2prj(file_path)
 
    #-------------------------------------------------------------------
    def select_file(self, path):
        if os.path.exists(path):
            self.app.open_file(path)
        
    #-------------------------------------------------------------------
    def remove_file(self, path):
        if path in self.file_list:
            self.dirty = True
            self.file_list.remove(path)
            self.gen_prj_tree()
        
    #-------------------------------------------------------------------
    def run_compile_cmd(self, cmd, file_path):
        proc = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc is None:
            return False
        warn_count = 0
        err_count = 0    
        for line in proc.stdout.readlines():
            if line == "\n":
                dprint("", line)
            elif line.find("warning") >= 0:
                log("find warning", line.find("warning"))
                warn_count += 1
                dprint("Warning", line)
            else:
                dprint("Info", line)
    
        for line in proc.stderr.readlines():
            if line == "\n":
                dprint("", line)
            else:
                err_count += 1
                dprint("Error", line)
    
        dprint("Done", file_path + " compilation done.")
        if err_count == 0 :
            r = "Pass"
        else:
            r = "Fail"
    
        dprint(r, "Error:" + str(err_count) + ", Warning:" + str(warn_count))
        
        if err_count > 0:
            return False
        else:
            return True    
        
    #-------------------------------------------------------------------
    def compile_file(self, file_path):
        dprint("Compile", file_path)
        #-- do the compilation
        # --model-small --code-loc 0x2000 --data-loc 0x30 --stack-after-data --xram
        #flag = " --debug --peep-asm " 
        rel_file = file_path.replace('.c', '.rel')
        #flag = " --disable-warning 59 -c "
        flag = " " + self.app.cflags + " -c " 
        cmd = SDCC_bin_path + flag + file_path + ' -o ' + rel_file

        dprint("Cmd", cmd)
        #os.chdir(os.path.dirname(file_path))
        result = self.run_compile_cmd(cmd, file_path)

        return result # return True if it compiled ok
    
    #-------------------------------------------------------------------
    def compile_main_and_link(self, file_path, lst):
        dprint("Compile", file_path)
        rel_files = ''
        for f in lst:
            f = f.replace('.c', '.rel')
            rel_files += ' ' + f
        #-- do the compilation
        # --model-small --code-loc 0x2000 --data-loc 0x30 --stack-after-data --xram
        #flag = " --debug --peep-asm " 
        #flag = " --disable-warning 59 "        
        flag = " " + self.app.cflags + " " + self.app.ldflags + " "
        cmd = SDCC_bin_path + flag + file_path + rel_files

        dprint("Cmd", cmd)
        #os.chdir(os.path.dirname(file_path))
        result = self.run_compile_cmd(cmd, file_path)

        return result # return True if it compiled ok
    
    #-------------------------------------------------------------------
    def get_project_main_file(self):
        lst = []
        self.main_file = None
        
        for f in self.file_list:
            if f.find('.c') > 0:
                f = self.dirname + f
                if utils.check_if_with_main(f):
                    self.main_file = f
                else:
                    lst.append(f)
        
        self.other_c_file_list = lst
        
    #-------------------------------------------------------------------
    def compile_project(self):
        self.app.clear_debug()
        
        self.get_project_main_file()
        lst = self.other_c_file_list
        # TODO: check if file opened, need save or not
                
        if self.main_file == None:
            dprint('Error', 'Can\'t find function main.')
        else:
            os.chdir(os.path.dirname(self.main_file))
            for f in lst:
                self.compile_file(f)
            self.compile_main_and_link(self.main_file, lst)
               
        self.app.show_debug()
               
    #-------------------------------------------------------------------
    def run_project(self):
        log("PrjMgr.run_project")
        self.app.running = True
        self.app.clear_debug()
            
        dprint("Run", self.file_path)
        self.get_project_main_file()
        lst = self.other_c_file_list
                    
        lst.insert(0, self.main_file)
        # set cwd to main file path
        os.chdir(os.path.dirname(self.main_file))

        #self.cmd_queue = Queue.Queue()
        self.sim_frame = SimFrame(self.app, self.tree, 
                                  lst, 
                                  self.config_file)
        
        self.app.SetTopWindow(self.sim_frame)
        self.sim_frame.Show(True)
    
    #-------------------------------------------------------------------
    def debug_project(self):
        log("PrjMgr.debug_project")
        self.app.running = True
        self.app.clear_debug()
            
        dprint("Debug", self.file_path)
        self.get_project_main_file()
        lst = self.other_c_file_list
                    
        lst.insert(0, self.main_file)
        # set cwd to main file path
        os.chdir(os.path.dirname(self.main_file))

        #self.cmd_queue = Queue.Queue()
        self.sim_frame = DebugFrame(self.app, self.tree, 
                                  lst, 
                                  self.config_file)
        
        self.app.SetTopWindow(self.sim_frame)
        self.sim_frame.Show(True)    
        
        
    #-------------------------------------------------------------------
    def _scan_xml_node_(self, xml_node, lst):
        for child in xml_node:
            if child.tag == 'file':
                for k in child.attrib:
                    if k == 'path':
                        lst.append(child.attrib[k])
            self._scan_xml_node_(child, lst)
            
    #-------------------------------------------------------------------
    def strip_prj_file_list(self):
        path = self.dirname 
        
        i = 0
        for f in self.file_list:
            if f.find(os.sep) < 0:
                f = path + f
            p = os.path.relpath(f, path)
            self.file_list[i] = p #f.replace(path, '')
            i += 1
        
    #-------------------------------------------------------------------
    def xml2prj(self, filename):
        xml_tree = ET.parse(filename)
        if not xml_tree:
            return False
        
        # start processing the XML file
        xml_root = xml_tree.getroot()
        lst = []
       
        for child in xml_root:
            tag = child.tag
            if tag == 'project':
                for k in child.attrib:
                    if k == 'filename':
                        self.file_path = child.attrib['filename']
                    elif k == 'path':
                        self.dirname = child.attrib['path']
            else:
                self._scan_xml_node_(child, lst)

        self.file_list = lst
        self.strip_prj_file_list()
        
        self.gen_prj_tree()
        
    #-------------------------------------------------------------------
    def gen_prj_xml(self, filename):
        # create root element of xml
        xml_root = ET.Element('sdcc_project')
        prj_node = ET.SubElement(xml_root, 'project', {'filename':self.file_path, 'path':self.dirname})
        
        inc_node = ET.SubElement(xml_root, 'include_files')
        src_node = ET.SubElement(xml_root, 'source_files')
        other_node = ET.SubElement(xml_root, 'other_files')
        for f in self.file_list:
            d = {'path':f}
            if f.find('.h') > 0:
                ET.SubElement(inc_node, 'file', d)
            elif f.find('.c') > 0:
                ET.SubElement(src_node, 'file', d)
            else:
                ET.SubElement(other_node, 'file', d)
        
        xml_tree = ET.ElementTree(xml_root)
        xml_tree.write(filename, 'utf-8', None, None, 'xml')
        
        self.xml_pretty_rewrite(filename)
        
    #-------------------------------------------------------------------
    def xml_pretty_rewrite(self, fn):
        f = open(fn, 'r')
        s = f.read()
        f.close()
        s = s.replace('>', '>\n')
        indents = []
        indent = ''
        for i in range(6):
            indents.append(indent)
            indent += '    '
            
        s1 = ''
        depth = 0
        for t in s.split('\n'):
            add_depth = 0
            if t[0:2] == '</':
                depth -= 1
                #print t[0:2], depth
            else:
                if t.find('/>') > 0:
                    pass
                else:
                    add_depth = 1
                
            if depth < 6:
                indent = indents[depth]
            else:
                indent = indents[6]
                
            s1 = s1 + indent + t + '\n'
            depth += add_depth
            
        output = open(fn, 'w+')
        output.write(s1)
        output.close()
    
    #-------------------------------------------------------------------
    # move to tree
    def gen_prj_tree(self):
        self.tree.gen_prj_tree(self.file_path, self.file_list)
        
    #-------------------------------------------------------------------
    def close_project(self):
        """Close current Project file."""
        if self.file_path == None:
            return 
       
        self.file_path = None
        self.app.prj = None
        self.dirty = False
        self.dirname = None
        self.file_list = []
    
    #-------------------------------------------------------------------
    def save_project(self):
        print 'save paroject ' + self.file_path
        self.gen_prj_xml(self.file_path)
        self.dirty = False

    #-------------------------------------------------------------------
    def add_file(self, file_path):
        if file_path in self.file_list :
            return False
        self.file_list.append(file_path)
        self.dirty = True
        return True
        
        
        
#-----------------------------------------------------------------------
class PrjTreeMenu(wx.Menu):
    def __init__(self, parent, menu_lst=[]):
        wx.Menu.__init__(self)
        menu = self
        for m in menu_lst:
            if m == []:
                menu.AppendSeparator()
            else:
                #print m
                id_name = m[0]
                id = get_id(id_name)
                setattr(parent, id_name, id)
                obj = menu.Append(id, m[1], m[2])
                parent.Bind(wx.EVT_MENU, m[3], id=id)
                
    
#----------------------------------------------------------------------------------------------
class PrjTree(wx.TreeCtrl):
    def __init__(self, app, frame, notebook):
        wx.TreeCtrl.__init__(self, frame, ID_ANY,
                             wx.DefaultPosition, wx.DefaultSize,
                             wx.TR_DEFAULT_STYLE + wx.NO_BORDER)
        self.app = app
        self.frame = frame
        self.parent = notebook
        self.prj = None
        
        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(get_bitmap(wx.ART_FOLDER))
        imglist.Add(get_bitmap(wx.ART_NORMAL_FILE))
        self.AssignImageList(imglist)

        self.root = self.AddRoot(wxT("Project"), 0)
        self.Expand(self.root)
        init_menu_lst = [
            ["ID_OPEN", "Open Project",  "Select and Open prject", self.OnOpenPrj],
            ["ID_NEW",  "Create New Project",  "Create Open prject", self.OnNewPrj],
        ]

        full_menu_lst = [
            #["Build Option",     "Configure current project compile/build option", self.OnBuildOption],
            ["ID_CMPILE", "Compile Project",  "Compile current project", self.OnCompilePrj],
            ["ID_RUN",    "Run Project",  "Run the program", self.OnRunPrj],
            ["ID_DEBUG",  "Debug Project",  "Debug the program", self.OnDebugPrj],
            [],
            ["ID_ADD_FILES", "Add Files",  "Add files to the project", self.OnAddFiles],
            #["Add Directory",  "Add directory to the project", self.OnAddFiles],
            ["ID_REMOVE_FILE", "Remove File",  "Remove file from the project", self.OnRemoveFile],
            [],            
            ["ID_NEW",  "Create New Project",  "Create Open prject", self.OnNewPrj],
            ["ID_OPEN",  "Open Project",  "Select and Open prject", self.OnOpenPrj],
            ["ID_SAVE",  "Save Project",  "Save the project", self.OnSavePrj],
            ["ID_CLOSE", "Close Project", "Close current project", self.OnClosePrj],
        ]
        
        self.init_menu = PrjTreeMenu(self, init_menu_lst)
        self.full_menu = PrjTreeMenu(self, full_menu_lst)
        self.pop_menu = self.init_menu

        # bind popup menu events
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelectFile)
        
    #-------------------------------------------------------------------
    def OnRightDown(self, event):
        if self.prj:
            item = self.GetSelection()
            path = self.GetItemText(item)
            log(item, path)
            if path in self.prj.file_list:
                self.full_menu.Enable(self.ID_REMOVE_FILE, True)
                self.full_menu.SetLabel(self.ID_REMOVE_FILE, "Remove " + path)
            else:
                log('disable remove file')
                self.full_menu.Enable(self.ID_REMOVE_FILE, False)
                self.full_menu.SetLabel(self.ID_REMOVE_FILE, "Remove File")
            self.PopupMenu(self.full_menu, event.GetPosition())
        else:
            self.PopupMenu(self.init_menu, event.GetPosition())
            
    #-------------------------------------------------------------------
    def add_prj_file(self, filename):
        f = filename
        if self.prj:
            path = self.prj.dirname
            if f.startswith(path):
                f = f.replace(path, '')
        if f.find('.h') > 0:
            self.AppendItem(self.inc_file_node, f)
        elif f.find('.c') > 0:
            self.AppendItem(self.src_file_node, f)
        else:
            self.AppendItem(self.other_file_node, f)
    
    #-------------------------------------------------------------------
    def gen_prj_tree(self, prj_file_name, prj_file_lst):
        self.DeleteAllItems()
        name = os.path.basename(prj_file_name)
        tree_root = self.AddRoot(name)
        self.src_file_node = self.AppendItem(tree_root, 'Source file')
        self.inc_file_node = self.AppendItem(tree_root, 'Include file')
        self.other_file_node = self.AppendItem(tree_root, 'Other file')
        
        for f in prj_file_lst:
            self.add_prj_file(f)
            
        self.ExpandAll()       
        
    #-------------------------------------------------------------------
    def check_prj_dirty(self):
        """Were the current project changed? If so, save it before."""
        if self.prj:
            if self.prj.dirty:
                # save the current project file first.
                result = MsgDlg_YesNoCancel(self.frame, 'The project has been changed.  Save?')
                if result == wx.ID_YES:
                    self.prj.save_project()
                if result == wx.ID_CANCEL:
                    return False

        return True
    
    #-------------------------------------------------------------------
    def close_prj(self):
        if not self.prj:
            return True
        
        if self.check_prj_dirty():
            self.prj.close_project()
            del self.prj
            self.prj = None
            self.DeleteAllItems()
            self.pop_menu = self.init_menu
    
    #-------------------------------------------------------------------
    def open_project(self, path):    
        if os.path.exists(path):
            if self.prj:
                self.close_prj()
            self.prj = Project(self.app, self, path)
            self.ExpandAll()
            self.pop_menu = self.full_menu
            self.parent.SetSelection(self.page_index)
            
    #-------------------------------------------------------------------
    def open_prj(self):
        open_it = self.check_prj_dirty()
        if open_it:
            dlg = wx.FileDialog(self.frame, 'Choose a project to open', '.', '', '*.sdprj', wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                #self.app.open_project(dlg.GetPath())
                path = dlg.GetPath()
                self.open_project(path)
                
            dlg.Destroy()

    #-------------------------------------------------------------------
    def new_prj(self):
        if self.prj:
            open_it = self.check_prj_dirty()
            if not open_it:
                return
            else:
                self.prj.dirty = False
            
        dlg = wx.TextEntryDialog(self.frame, 'Name for new project:', 'New Project',
                                 'project.sdprj', wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            new_proj = dlg.GetValue()
            dlg.Destroy()
            dlg = wx.FileDialog(self.frame, 'Place to store new project.', '', new_proj, '*.sdprj', wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    # save the project file.
                    file_path = dlg.GetPath()
                    print file_path
                    proj = open(file_path, 'w')
                    proj.write('<sdcc_project><project filename=\"' + file_path + '\" /></sdcc_project>')
                    proj.close()
                    self.open_project(file_path)
                except IOError:
                    MsgDlg_Warn(self, 'There was an error saving the new project file.', 'Error!')
        dlg.Destroy()
        
    #-------------------------------------------------------------------
    def add_files(self):
        if not self.prj:
            return

        dlg = wx.FileDialog(self.frame,
                                   "Select files add to project",
                                   self.prj.dirname,
                                   "",
                                   "C files(*.c,*.h)|*.c;*.h|Python files(*.py)|*.py|Lua files(*.lua)|*.lua|All files(*)|*",
                                   wx.FD_OPEN | wx.FILE_MUST_EXIST | wx.MULTIPLE)
        result = False
        if dlg.ShowModal() == wx.ID_OK :
            path = os.path.dirname(dlg.GetPath())
            log('Add files', path, dlg.GetFilenames())

            for fn in dlg.GetFilenames():
                file_path = path + os.sep + fn
                print 'add file ', file_path, 'to project'
                if self.app.prj.add_file(file_path):
                    self.add_prj_file(file_path)

        dlg.Destroy()
        return result
    
    #-------------------------------------------------------------------
    def OnNewPrj(self, event):
        self.new_prj()

    #-------------------------------------------------------------------
    def OnOpenPrj(self, event):
        self.open_prj()
        
    #-------------------------------------------------------------------
    def OnSavePrj(self, event):
        """Save a SDCC project file."""
        self.prj.save_project()   
        
    #-------------------------------------------------------------------
    def OnClosePrj(self, event):
        self.close_prj()
        
    #-------------------------------------------------------------------
    def OnSelectFile(self, event):
        if not self.prj:
            return
        item = event.GetItem()
        path = self.prj.dirname + self.GetItemText(item)
        log('select', path)
        if os.path.exists(path):
            self.app.open_file(path)
        
    #-------------------------------------------------------------------
    def OnRemoveFile(self, event):
        if not self.prj:
            return
        item = self.GetSelection()
        path = self.GetItemText(item)
        log('remove', item, path)
        self.prj.remove_file(path)
        self.gen_prj_tree(self.prj.file_path, self.prj.file_list)
        
    #-------------------------------------------------------------------
    def OnAddFiles(self, event):
        if self.prj:
            self.add_files()
                
    #-------------------------------------------------------------------
    def OnCompilePrj(self, event):
        if self.prj:
            log("PrjMgr.OnCompile")
            self.prj.compile_project()
        
    #-------------------------------------------------------------------
    def OnRunPrj(self, event):
        if self.prj:
            log("PrjMgr.OnRun")
            self.prj.run_project()
            
    #-------------------------------------------------------------------
    def OnDebugPrj(self, event):
        if self.prj:
            log("PrjMgr.OnDebug")
            self.prj.debug_project()


#---------------------------------------------------------------------------------------------------
class SearchBox(wx.ComboBox):
    def __init__(self, panel, tree):
        wx.ComboBox.__init__(self, panel, wx.ID_ANY, "",
                    wx.DefaultPosition, wx.DefaultSize,
                    [],
                    wx.TE_PROCESS_ENTER) # generates event when enter is pressed
        self.tree = tree
        self.func_lst = []
        self.full_func_lst = []
        self.event_from_item_selected = False
        self.search_string = ""

        self.Bind(wx.EVT_COMBOBOX, self.OnSelectItem)
        self.Bind(wx.EVT_TEXT, self.OnKeyUpdate)
    #-------------------------------------------------------------------
    def set_items(self, lst):
        self.Clear()
        if (lst == None or len(lst) == 0) :
            return
        lst1 = []
        for t in lst :
            if (type(t) is not list) :
                lst1.append(t)

        lst1.sort()

        for t in lst1 :
            self.Append(t)

    #-------------------------------------------------------------------
    def add_func_lst(self, lst):
        if (lst == None or len(lst) == 0) :
            return

        for t in lst:
            if (type(t) is list) :
                self.add_func_lst(t)
            else:
                table.insert(self.func_lst, t)

    #-------------------------------------------------------------------
    def set_func_lst(self, lst):
        self.set_items(lst)
        self.full_func_lst = lst
        self.func_lst = []
        self.add_func_lst(lst)

    #-------------------------------------------------------------------
    def update_search_text(self, s):
        n = len(s)

        if (n == 0) :
            self.tree.set_list(self.full_func_lst)
            return

        lst = []
        n1 = 0
        for f in self.func_lst :
            p0 = f.find(s)
            if (p0 == 0) :
                #print(p0, f)
                lst.append(f)
                n1 = n1 + 1

        if (n > 1 or n1 == 0) :
            for f in self.func_lst :
                p0 = f.find(s)
                if (p0 >= 0) :
                    #print(p0, f)
                    lst.append(f)

        self.tree.set_list(lst)

    #-------------------------------------------------------------------
    def clear_text(self):
        self.SetValue("")
        self.update_search_text("")
        self.search_string = ""
        
    #-------------------------------------------------------------------
    def OnSelectItem(self, event):
        self.event_from_item_selected = True
        #print("OnSelectItem", event.GetString(), event.GetId(), event.GetEventType(), event.GetEventObject())
        if (self.search_string != "") :
            self.update_search_text("")
            self.search_string = ""

        self.tree.select_item(event.GetString())

    #-------------------------------------------------------------------
    def OnKeyUpdate(self, event):
        if (self.event_from_item_selected == False) :
            #print("OnKeyUpdate", event.GetString(), event.GetId(), event.GetEventType(), event.GetEventObject())
            self.update_search_text(event.GetString())
            self.search_string = event.GetString()

        self.event_from_item_selected = False


#----------------------------------------------------------------------------------------------
class DirTree(wx.GenericDirCtrl):
    def __init__(self, app, frame, notebook):
        wx.GenericDirCtrl.__init__(self, frame, wx.ID_ANY, wx.DirDialogDefaultFolderStr,
                             wx.DefaultPosition, wx.DefaultSize, style=wx.DIRCTRL_SHOW_FILTERS,
                             filter="Source files (*.c;*.h;*.lua;*.py;*.asm;*.lst;*.rst)|*.c;*.h;*.lua;*.py;*.asm;*.lst;*.rst")
        self.app = app
        self.notebook = notebook
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelectFile)
        self.SetPath(app.work_dir)
        
    #-------------------------------------------------------------------
    def OnSelectFile(self, event):
        path = self.GetPath()
        if (isfile(path)) :
            self.app.open_file(path)
        else:
            self.ExpandPath(path)
            
            
#----------------------------------------------------------------------------------------------
class FunctionTree(wx.TreeCtrl):
    def __init__(self, app, frame, notebook):
        wx.TreeCtrl.__init__(self, frame, wx.NewId(),
                             wx.DefaultPosition, wx.DefaultSize,
                             wx.TR_DEFAULT_STYLE)
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.SetImageList(il)
        self.il = il

        self.root = self.AddRoot("The Root Item")
        self.SetPyData(self.root, None)
        self.SetItemImage(self.root, fldridx, wx.TreeItemIcon_Normal)
        self.SetItemImage(self.root, fldropenidx, wx.TreeItemIcon_Expanded)
        
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelectFunction)
        self.app = app
        
    #-------------------------------------------------------------------
    def add_list(self, root, lst, depth):
        if (depth > 4):
            log("depth > 4", depth)
        for t in lst:
            if (type(t) is list) :
                node = self.GetLastChild(root)
                self.add_list(node, t, depth+1)
            else:
                self.AppendItem(root, str(t), 4)

    #-------------------------------------------------------------------
    def set_list(self, lst):
        #print "set_list", lst
        #-- remove all items
        self.DeleteAllItems()

        #-- add root
        root_id = self.AddRoot( "Root", 2, -1 )
        self.add_list(root_id, lst, 0)

        self.Expand(root_id)

    #-------------------------------------------------------------------
    def OnSelectFunction(self, event):
        doc = self.app.get_doc()
        item_id = event.GetItem()
        s = self.GetItemText(item_id)+ "\n"
        #--log(s)
        #--print(doc, doc.file_name)
        doc.find_func_pos(s)

    #-------------------------------------------------------------------
    def get_root_child(self):
        tree = self
        lst = []
        root = tree.GetRootItem()
        #-- GetChildrenCount, GetFirstChild, GetNextChild

        child_id, cookie = tree.GetFirstChild(root)
        while (child_id.IsOk()) :
            text = tree.GetItemText(child_id)
            #--print(tree.GetItemText(child_id))
            lst.append(text)
            child_id, cookie = tree.GetNextChild(child_id, cookie)

        lst.sort()
        return lst

    #-------------------------------------------------------------------
    def select_item(self, s):
        tree = FunctionTree
        root = tree.GetRootItem()

        child_id, cookie = tree.GetFirstChild(root)
        while (child_id.IsOk()) :
            if (s == tree.GetItemText(child_id)) :
                tree.SelectItem(child_id, True)
                tree.Expand(child_id)
                #--tree.ScrollTo(child_id)
                return child_id

            child_id, cookie = tree.GetNextChild(child_id, cookie)

        return None

#---------------------------------------------------------------------------------------------------
class PrjMgr(wx.aui.AuiNotebook):
    def __init__(self, app, frame):
        wx.aui.AuiNotebook.__init__(self, frame, wx.ID_ANY,
                                    wx.DefaultPosition,
                                    wx.Size(250, 200),
                                    wx.aui.AUI_NB_TOP |
                                    wx.aui.AUI_NB_TAB_SPLIT |
                                    wx.aui.AUI_NB_TAB_MOVE |
                                    wx.aui.AUI_NB_TAB_EXTERNAL_MOVE |
                                    wx.aui.AUI_NB_SCROLL_BUTTONS |
                                    wx.aui.AUI_NB_WINDOWLIST_BUTTON |
                                    wx.NO_BORDER)
        self.SetMinSize(wx.Size(200, 200))

        notebook = self
        self.dir_tree = DirTree(app, frame, notebook)
        self.prj_tree = PrjTree(app, frame, notebook)

        notebook.AddPage( self.dir_tree, wxT("Dir") )
        self.prj_tree.page_index = notebook.AddPage( self.prj_tree, wxT("Project"))
        
        self.func_tree = self.add_func_tree(app)

        app.dir_tree = self.dir_tree
        app.prj_tree = self.prj_tree
        app.functree = self.func_tree

    #-------------------------------------------------------------------
    def OnClearSearchBox(self, event):
        self.search_box.clear_text()
        
    #-------------------------------------------------------------------
    def add_func_tree(self, app):
        notebook = self
        panel = wx.Panel(notebook, wx.ID_ANY)

        sizer = wx.FlexGridSizer(2, 0, 0, 0)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(1)

        #-- create our treectrl
        tree = FunctionTree(app, panel, notebook)

        self.search_box = SearchBox(panel, tree)

        sizer2 = wx.FlexGridSizer(0, 2, 0, 0)
        sizer2.AddGrowableCol(1)
        sizer2.AddGrowableRow(0)

        b1 = wx.Button(panel, wx.ID_ANY, "<", wx.DefaultPosition, wx.Size(28, 28))
        b1.Bind(wx.EVT_BUTTON, self.OnClearSearchBox)

        sizer2.Add(b1, 0, wx.ALIGN_CENTER_VERTICAL+wx.ALL, 0)
        sizer2.Add(self.search_box, 0, wx.GROW+wx.ALIGN_LEFT+wx.ALL, 1)

        sizer.Add( sizer2, 0, wx.GROW+wx.ALIGN_CENTER_VERTICAL, 0 )
        sizer.Add( tree, 0, wx.GROW+wx.ALIGN_CENTER_VERTICAL, 0 )

        panel.SetSizer(sizer)
        sizer.SetSizeHints(panel)
        panel.Layout() # help sizing the windows before being shown
        notebook.AddPage( panel, wxT("Function") ) #, False, get_bitmap(wx.ART_LIST_VIEW) )
        if app.last_file_count > 0:
            notebook.SetSelection(notebook.GetPageIndex(panel))
        
        return tree
    
    #-------------------------------------------------------------------
    def add_file(self, file_path):
        if self.prj_tree.prj:
            self.prj_tree.prj.add_file(file_path)
        
    #-------------------------------------------------------------------
    def compile_project(self):
        if self.prj_tree.prj:
            self.prj_tree.prj.compile_project()
        
    #-------------------------------------------------------------------
    def run_project(self):
        if self.prj_tree.prj:
            self.prj_tree.prj.run_project()
        
    #-------------------------------------------------------------------
    def set_func_lst(self, lst):
        self.func_tree.set_list(lst)
        self.search_box.set_func_lst(lst)
        


