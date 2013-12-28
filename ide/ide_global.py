import os
import os.path
import logging
import time
import wx
import wx.xrc
import wx.aui
import wx.richtext
import wx.stc as stc
import wx.html
import re
import datetime
import wx.lib.inspection
import inspect

global MyApp
MyApp = None

if wx.Platform == '__WXMSW__' :
    wxLua_path = "C:\\wx\\wxLua\\bin\\wxLua.exe"
    wxLua_Param = " --nostdout /c "
    Python_path = "C:\\Python27\\python.exe"
    
    SDCC_path = "C:\\tools\\SDCC\\"
    SDCC_bin_path = SDCC_path + "bin\\sdcc.exe"
    SDCC_inc_path = SDCC_path + "include"
    SDCC_lib_path = SDCC_path + "lib"
    
    NodeJS_path = "C:\\tools\\nw\\nw.exe"
    
    Gputil_path = "C:\\Program Files\\gputils\\"
    pic14_sdcc_lib = "C:\\Program Files\\SDCC\\lib\\pic14\\libsdcc.lib"
    pic16_sdcc_lib = "C:\\Program Files\\SDCC\\lib\\pic16\\libsdcc.lib"
    SDCC_non_free_path = "C:\\Program Files\\SDCC\\non-free\\"    
else:
    wxLua_path = "/usr/local/bin/wxLua"
    wxLua_Param = ""
    Python_path = "/usr/bin/python2"
    SDCC_bin_path = "/usr/local/bin/sdcc"
    SDCC_inc_path = "/usr/local/share/sdcc/include"
    SDCC_lib_path = "/usr/local/share/sdcc/lib"
    NodeJS_path = "/usr/local/bin/nw"
    Gputil_path = " /usr/local/share/gputils/"
    pic14_sdcc_lib = "/usr/local/share/sdcc/lib/pic14/libsdcc.lib"
    pic16_sdcc_lib = "/usr/local/share/sdcc/lib/pic16/libsdcc.lib"
    SDCC_non_free_path = "/usr/local/share/sdcc/non-free/"
    

    
ID_ANY              = wx.ID_ANY

ID_NEW_PRJ          = wx.NewId()
ID_OPEN_PRJ         = wx.NewId()
ID_CLOSE_PRJ        = wx.NewId()

ID_NEW_FILE         = wx.ID_NEW
ID_OPEN             = wx.ID_OPEN
ID_CLOSE            = wx.NewId()
ID_SAVE             = wx.ID_SAVE
ID_SAVEAS           = wx.ID_SAVEAS
ID_SAVEALL          = wx.NewId()
ID_EXIT             = wx.ID_EXIT

# Edit menu
ID_UNDO             = wx.ID_UNDO
ID_REDO             = wx.ID_REDO
ID_CUT              = wx.ID_CUT
ID_COPY             = wx.ID_COPY
ID_PASTE            = wx.ID_PASTE
ID_SELECTALL        = wx.ID_SELECTALL
ID_AUTOCOMPLETE     = wx.NewId()
ID_AUTOCOMPLETE_ENABLE = wx.NewId()
ID_COMMENT          = wx.NewId()
ID_FOLD             = wx.NewId()
ID_PY2LUA           = wx.NewId()
# Find menu
ID_FIND             = wx.ID_FIND
ID_FINDNEXT         = wx.NewId()
ID_FINDPREV         = wx.NewId()
ID_REPLACE          = wx.NewId()
ID_GOTOP            = wx.NewId()
ID_GOBOTTOM         = wx.NewId()

# Debug menu
ID_COMPILE          = wx.NewId()
ID_RUN              = wx.NewId()
ID_DBG_START        = wx.NewId()

ID_DBG_STOP         = wx.NewId()
ID_DBG_STEP         = wx.NewId()
ID_DBG_STEP_OVER    = wx.NewId()
ID_DBG_STEP_OUT     = wx.NewId()
ID_DBG_CONTINUE     = wx.NewId()
ID_DBG_BREAK        = wx.NewId()

ID_TOGGLEBREAKPOINT = wx.NewId()
ID_VIEWCALLSTACK    = wx.NewId()
ID_VIEWWATCHWINDOW  = wx.NewId()

# Help menu
ID_ABOUT            = wx.ID_ABOUT

# Watch window menu items
ID_WATCH_LISTCTRL   = wx.NewId()
ID_ADDWATCH         = wx.NewId()
ID_EDITWATCH        = wx.NewId()
ID_REMOVEWATCH      = wx.NewId()
ID_EVALUATEWATCH    = wx.NewId()

ID_CreateTree = wx.NewId()
ID_create_grid = wx.NewId()
ID_CreateText = wx.NewId()
ID_CreateNotebook = wx.NewId()

ID_CLEAR_BUTTON = wx.NewId()

#-- Markers for editor marker margin
MARKNUM_BREAK_POINT   = 1
MARKVAL_BREAK_POINT   = 1
MARKNUM_CURRENT_LINE  = 2
MARKVAL_CURRENT_LINE  = 4

id_defines = {    
    'any':wx.ID_ANY,
    'new':wx.ID_NEW,
    'open':wx.ID_OPEN,
    'close':wx.ID_CLOSE,
    'save':wx.ID_SAVE,
    'saveas':wx.ID_SAVEAS,
    'exit':wx.ID_EXIT,
    'undo':wx.ID_UNDO,
    'redo':wx.ID_REDO,
    'cut':wx.ID_CUT,
    'copy':wx.ID_COPY,
    'paste':wx.ID_PASTE,
    'selectall':wx.ID_SELECTALL,
    'find':wx.ID_FIND,
    'about':wx.ID_ABOUT,
    'help':wx.ID_HELP,
    'new prj':ID_NEW_PRJ,
    'open prj':ID_OPEN_PRJ,
    'close prj':ID_CLOSE_PRJ,
    'compile':ID_COMPILE,
    'run':ID_RUN,
    'dbg_start':ID_DBG_START,
    
    'dbg_stop':ID_DBG_STOP,
    'dbg_step':ID_DBG_STEP,
    'dbg_step_over':ID_DBG_STEP_OVER,
    'dbg_step_out':ID_DBG_STEP_OUT,
    'dbg_continue':ID_DBG_CONTINUE,
    'dbg_break':ID_DBG_BREAK,
}

def copy_to_clipboard(text):
    # Write some text to the clipboard
    if wx.TheClipboard.Open():
    
        # This data objects are held by the clipboard,
        # so do not delete them in the app.
        wx.TheClipboard.SetData(wx.TextDataObject(text))
        wx.TheClipboard.Close()    

def get_id(name):
    id = id_defines.get(name, None)
    if id == None:
        id = wx.NewId()
        id_defines[name] = id
    return id

def search_file(root_dir, search_name):
    print root_dir
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


def search_sdcc_bin():
    global SDCC_bin_path
    if os.path.exists(SDCC_bin_path):
        return SDCC_bin_path
    
    #print "search_sdcc"
    if wx.Platform == '__WXMSW__' :
        dir_lst = ['c:\\Tools\\', 'c:\\Program Files\\SDCC', 'c:\\Program Files (x86)\\SDCC', 'C:\\', 'D:\\']
        for d in dir_lst:
            path = search_file(d, 'sdcc.exe')
            if path != "":
                SDCC_bin_path = path
                #print path
                return path
        
    else:
        dir_lst = ['/usr/bin/', '/usr/local/bin/', '/usr', '/bin', '/sbin', '/']
        for d in dir_lst:
            path = search_file(d, 'sdcc')
            if path != "":
                SDCC_bin_path = path
                #print path
                return path

    return ""

def get_sdcc_bin_path():
    if file_exist(SDCC_bin_path):
        return SDCC_bin_path
    else:
        return search_sdcc_bin()
        
class Object(object):
    pass

def wxT(s):
    return s

def bit(p):
    return 1 << p  # 1-based indexing

#-- Typical call.  if hasbit(x, bit(3)) : ...
def hasbit(x, p):
    if x & (1 << p):
        return 1
    else:
        return 0

def setbit(x, p):
    return x | (1 << p)

def clearbit(x, p):
    return x & (~(1 << p))

def get_hh_mm_ss():
    now = datetime.datetime.now()
    return str(datetime.time(now.hour, now.minute, now.second))

def test_var_args(farg, *args):
    print "formal arg:", farg
    for arg in args:
        print "another arg:", arg

def trim(s):
    return s.strip(' \t\n\r')

def getchar(s, i):
    return s[i : i+1]

def get_filename(s):
    return os.path.basename(s)

def get_path(s):
    return os.path.dirname(s)

def get_filename_ext(s):
    p, ext = os.path.splitext(s)
    ext = ext.replace(".", "")
    return ext

def get_bitmap(icon):
    if icon[0:2] == "wx":
        bmp = wx.ArtProvider.GetBitmap(icon, wx.ART_TOOLBAR, wx.Size(16,16))
    else:
        bmp = wx.Bitmap(icon)
    return bmp

def isfile(s):
    return os.path.isfile(s)

def get_date_string(dt):
    return "%d-%02d-%02d %02d.%02d.%02d" % (dt.Year, dt.Month, dt.Day, dt.Hour, dt.Minute, dt.Second)

#print "last modified: %s" % time.ctime(os.path.getmtime(fn))
#print "created: %s" % time.ctime(os.path.getctime(fn))

def get_file_mod_time(file_path):
    if file_exist(file_path):
        return os.path.getmtime(file_path)
    else:
        return None

def file_exist(s):
    return os.path.exists(s)

def set_range_visible(doc, pos_start, pos_end):
    doc.set_range_visible(pos_start, pos_end)
    

def dprint(s1, s2):    
    #msg = (' '.join(map(str, args))) 
    
    if MyApp is None:
        return
    if MyApp.debug_info is None:
        return
    MyApp.debug_info.write(s1, s2)

def log(*args):
    global MyApp
    callerframerecord = inspect.stack()[1]    # 0 represents this line
                                              # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    msg = (' '.join(map(str, args))) 
    #s = get_hh_mm_ss() + " [caller: " + str(info.lineno) + " " + info.function + "]  " + msg
    s = get_hh_mm_ss() + ' ' + msg
    print("log", s)    

    MyApp.log(s + "\n")
    
def set_app(a):
    global MyApp
    MyApp = a
    
    
def MsgDlg_YesNoCancel(parent, question, caption = 'Yes or no?'):
    dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result

def MsgDlg_YesNo(parent, question, caption = 'Yes or no?'):
    dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result

def MsgDlg_Info(parent, message, caption = 'Insert program title'):
    dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    
def MsgDlg_Warn(parent, message, caption = 'Warning!'):
    dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()