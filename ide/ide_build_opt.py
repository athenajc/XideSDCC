import os
import sys
import wx
import wx.combo
import wx.lib.scrolledpanel as scrolled
import wx.lib.filebrowsebutton as filebrowse

from ide_global import *
import utils

"""
General options:
  -V                        Execute verbosely. Show sub commands as they are run
  -d                        
  -D                        Define macro as in -Dmacro
  -A                        
  -U                        
  -M                        Preprocessor option
  -W                        Pass through options to the pre-processor (p), assembler (a) or linker (l)
  -S                        Compile only; do not assemble or link
  -c  --compile-only        Compile and assemble, but do not link
  -E  --preprocessonly      Preprocess only, do not compile
      --c1mode              Act in c1 mode.  The standard input is preprocessed code, the output is assembly code.
  -m                        Set the port to use e.g. -mz80.
  -p                        Select port specific processor e.g. -mpic14 -p16f84
"""


#---------------------------------------------------------------------------
class StaticLine(wx.StaticLine):
    def __init__(self, parent, sizer):
        wx.StaticLine.__init__(self, parent, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(self, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        
        
#---------------------------------------------------------------------------
class StaticTextCtrl(wx.TextCtrl):
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL):
        wx.TextCtrl.__init__(self, parent, -1, "", size=(180,-1), style=wx.TE_READONLY)
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label_str, pos=(0,0), size=(75,-1), style=wx.ALIGN_RIGHT)
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        text = self
        text.SetValue(default_str)
        text.SetHelpText(help_str)
        text.SetBackgroundColour((185,185,185))
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.RIGHT, 5)

        sizer.Add(box, 0, flag, 5)


#---------------------------------------------------------------------------
class LabelTextCtrl(wx.TextCtrl):
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL):
        wx.TextCtrl.__init__(self, parent, -1, "", size=(180,-1))
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label_str, pos=(0,0), size=(140,-1), style=wx.ALIGN_RIGHT)
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        
        text = self
        text.SetValue(default_str)
        text.SetHelpText(help_str)
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.RIGHT, 5)

        sizer.Add(box, 0, flag, 5)


#---------------------------------------------------------------------------
class LabelButtonTextCtrl(wx.TextCtrl):
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
class CheckBox(wx.CheckBox):
    def __init__(self, parent, sizer, id, label):
        wx.CheckBox.__init__(self, parent, id, label)
        
        sizer.Add(self, 0, wx.EXPAND, 5)
            
        
#---------------------------------------------------------------------------
class RadioButton(wx.RadioButton):
    def __init__(self, parent, sizer, id, label):
        wx.RadioButton.__init__(self, parent, id, label)        
        sizer.Add(self, 1, wx.EXPAND, 5)
        
        
#---------------------------------------------------------------------------
class ComboBox(wx.ComboBox):
    """ usage : cbox = ComboBox(parent, sizer, "label", ['item a', 'bbb', 'c'] """
    def __init__(self, parent, sizer, label, lst, flag = wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL):
        wx.ComboBox.__init__(self, parent, pos=(150, 90), size=(95, -1), choices=lst, style=wx.CB_DROPDOWN)
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label)
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        box.Add(self, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        
        if sizer:
            sizer.Add(box, 0, flag, 5)
            
#---------------------------------------------------------------------------
class ListBox(wx.ListBox):
    def __init__(self, parent, sizer, label, lst, flag = wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL):
        wx.ListBox.__init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=lst)

        sizer.Add(self, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        
        self.Bind(wx.EVT_LISTBOX, self.OnSelect, id=26)
        
        def OnSelect(self, event):
            index = event.GetSelection()
            #time_zone = self.time_zones.GetString(index)
            #self.diff = self.time_diff[time_zone]
            #self.text.SetValue(self.full_list[time_zone])
            
#---------------------------------------------------------------------------
class CheckBoxWithHelp():
    def __init__(self, parent, sizer, label, help_text, checkbox_click, te=None):
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.checkbox_click = checkbox_click

        self.id = wx.NewId()
        self.label = label
        
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.SetMinSize(wx.Size(200, -1))
        
        # if option need input
        if te :
            # add checkbox at first
            self.cbox = wx.CheckBox(parent, self.id, label, wx.DefaultPosition, wx.Size(-1, -1), 0)
            box1.Add(self.cbox, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
            
            text = wx.TextCtrl(parent, -1, "", size=(80,-1))
            box1.Add(text, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
            self.text_entry = text
        else:
            self.cbox = wx.CheckBox(parent, self.id, label, wx.DefaultPosition, wx.Size(180, -1), 0)
            box1.Add(self.cbox, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)
            self.text_entry = None
                
        box.Add(box1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        stext = wx.StaticText(parent, wx.ID_ANY, help_text)
        stext.Wrap(-1)
        box.Add(stext, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        
        sizer.Add(box, 0, wx.EXPAND, 5)    
        self.cbox.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.cbox)
    
    #-------------------------------------------------------------------
    def OnCheckBox(self, evt):
        #print 'OnCheckBox', evt.GetId(), self.label, evt.IsChecked()
        
        if self.text_entry is not None:
            # if user didn't input value, give warning and return
            if evt.IsChecked() and self.text_entry.GetValue() == '':
                fc = self.cbox.GetForegroundColour()
                self.cbox.SetForegroundColour(wx.RED)                
                wx.MessageBox('Please enter value of   \"' + self.label + '\"   before select it.', 'Error', 
                            wx.OK | wx.ICON_INFORMATION) 
                self.cbox.SetForegroundColour(fc)
                self.cbox.SetValue(False)
                return
            
            text = self.label
            value = self.text_entry.GetValue().strip()
            if text.find('=') < 0 :
                value = ' ' + value.strip()
            self.checkbox_click(text, evt.IsChecked(), value)
        else:
            text = self.label
            self.checkbox_click(text, evt.IsChecked())
        

#---------------------------------------------------------------------------
class CheckBoxList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer, title, lst, checkbox_click):
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.HORIZONTAL)
        box_sizer = self
        
        # add listbox for device list pic14/pic16
        if lst[0][0] == 'combo':
            sizer1a = wx.BoxSizer(wx.VERTICAL)
            t = lst.pop(0)
            devices = t[1]
            b = wx.ListBox(parent, 26, wx.DefaultPosition, (-1, 30), devices, wx.LB_SINGLE)
            sizer1a.Add(b, 1, wx.EXPAND|wx.ALL, 5)
            box_sizer.Add(sizer1a, 0, wx.EXPAND|wx.ALL, 5)
            self.device_listbox = b
        else:
            self.device_listbox = None
            
        if len(lst) < 10:
            panel1 = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        else:
            panel1 = wx.ScrolledWindow( parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER )
            panel1.SetScrollRate(10, 20)
            panel1.EnableScrolling(True,True)
            
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        
        self.cboxes = []
        h = 0
        for t in lst:
            if len(t) == 2:
                c = CheckBoxWithHelp(panel1, sizer1, t[0], t[1], checkbox_click)
            else:
                c = CheckBoxWithHelp(panel1, sizer1, t[0], t[1], checkbox_click, t[2])
            h = c.cbox.GetSize().GetHeight() + 5
            self.cboxes.append([c, t[0], t[1]])
        
        panel1.SetInitialSize((-1, h))
            
        panel1.SetSizer(sizer1)
        panel1.Layout()
         
        box_sizer.Add(panel1, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        parent_sizer.Add(box_sizer, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
    
#---------------------------------------------------------------------------
class Dialog(wx.Dialog):
    
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        pass
    
    #-------------------------------------------------------------------
    def add_ok_cancel_button(self, sizer):
        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        self.btn_cancel = btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        
        self.btn_ok = btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)
        
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        #self.Bind(wx.EVT_SIZE, self.OnResize)
        
    #def OnResize(self, event):
        #print "Resizing dialog"
        #event.Skip()
        
    #-------------------------------------------------------------------
    def __del__( self ):
        pass


#---------------------------------------------------------------------------
class OptionPanel(wx.Panel):
    """  OptionPanel Tamplate """
    def __init__(self, parent, option, option_callback):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.option = option
        self.option_callback = option_callback
        self.SetSizer(self.sizer)
        self.Layout()
        
    #-------------------------------------------------------------------
    def set_check_list(self, title, lst):
        """ 
            Create one staticbox with title string, 
            Create one checkbox list with lst contents 
        """
        self.title = title
        self.lst = lst
        self.cbox_list = CheckBoxList(self, self.sizer, self.title, self.lst, self.checkbox_click)
        
    #-------------------------------------------------------------------
    def checkbox_click(self, label, checked, value=None):
        #print label, value
        self.option.dirty = True
        if self.option_callback:
            self.option_callback(self.title, label, checked, value)
            
    #-------------------------------------------------------------------
    def option_callback(self, title, label, checked, value):
        #print title, label, value       
        if checked == True:
            self.option.add_cflag(label, value)
        else:            
            self.option.remove_cflag(label, value)
            
        self.option.update_cflags()
        
    #-------------------------------------------------------------------
    def update_flags(self):
        for t in self.cbox_list.cboxes:
            cb = t[0]
            key = t[1]
            value = self.option.flag_dict.get(key, None)
            #print key, value
            if value:
                key += value
                print key
            if key in self.option.cflag_lst:
                cb.cbox.SetValue(True)
                if value:
                    cb.text_entry.SetValue(value.strip())
            else:
                cb.cbox.SetValue(False)

#---------------------------------------------------------------------------
class PageGeneralOption(OptionPanel):
    """
            General options:
    """
    def __init__(self, parent, option, option_callback):
        OptionPanel.__init__(self, parent, option, self.option_callback)
            
        title = 'General options:'
        lst = [        
            ['--debug',               'Enable debugging symbol output'],
            ['--Werror',              'Treat the warnings as errors'],
            ['--verbose',             'Trace calls to the preprocessor, assembler, and linker'],
            ['--print-search-dirs',   'display the directories in the compiler\'s search path'],
            ['--cyclomatic',          'Display complexity of compiled functions'],            
            ['--vc',                  'messages are compatible with Micro$oft visual studio'],
            ['--use-stdout',          'send errors to stdout instead of stderr'],
            ['--nostdlib',            'Do not include the standard library directory in the search path'],
            ['--nostdinc',            'Do not include the standard include directory in the search path'],
            ['--less-pedantic',       'Disable some of the more pedantic warnings'],
            ['--disable-warning',     '<nnnn> Disable specific warning', 'num'],
            ['--fdollars-in-identifiers',  'Permit \'$\' as an identifier character'],
            ['--funsigned-char',      'Make "char" unsigned by default'],
            
            ]
        
        self.set_check_list(title, lst)
        self.update_flags()
                
                
#---------------------------------------------------------------------------
class PageCodeGenOption(OptionPanel):
    """
            Code generation options:
    """
    def __init__(self, parent, option, option_callback):
        OptionPanel.__init__(self, parent, option, self.option_callback)
            
        title = "Code generation options:"
        lst = [
            ['--stack-auto',       'Stack automatic variables'],
            ['--xstack',           'Use external stack'],
            ['--int-long-reent',   'Use reentrant calls on the int and long support functions'],
            ['--float-reent',      'Use reentrant calls on the float support functions'],
            ['--xram-movc',        'Use movc instead of movx to read xram (xdata)'],
            ['--callee-saves',     '<func[,func,...]> Cause the called function to save registers instead of the caller', 'func'],
            ['--profile',          'On supported ports, generate extra profiling information'],
            ['--fomit-frame-pointer', 'Leave out the frame pointer.'],
            ['--all-callee-saves', 'callee will always save registers used'],
            ['--stack-probe',      'insert call to function __stack_probe at each function prologue'],
            ['--no-xinit-opt',     'don\'t memcpy initialized xram from code'],
            ['--no-c-code-in-asm', 'don\'t include c-code as comments in the asm file'],
            ['--no-peep-comments', 'don\'t include peephole optimizer comments'],
            ['--short-is-8bits',   'Make short 8 bits (for old times sake)'],
            ['--codeseg',          '<name> use this name for the code segment', 'name'],
            ['--constseg',         '<name> use this name for the const segment', 'name'],
        ]
        self.set_check_list(title, lst)
        self.update_flags()
        
        
#---------------------------------------------------------------------------
class PageDebugOption(OptionPanel):
    """
            Internal debugging options:
    """
    def __init__(self, parent, option, option_callback):
        OptionPanel.__init__(self, parent, option, self.option_callback)
            
        title = "Internal debugging options:"
        lst = [
            ['--dump-ast',      'Dump front-end AST before generating i-code'],
            ['--dump-i-code',   'Dump the i-code structure at all stages'],
            ['--dump-graphs',   'Dump graphs (control-flow, conflict, etc)'],
            ['--i-code-in-asm', 'Include i-code as comments in the asm file'],
            ['--fverbose-asm',  'Include code generator comments in the asm output'],
        ]
        self.set_check_list(title, lst)
        self.update_flags()
        
        
#---------------------------------------------------------------------------
class PageModelOption(OptionPanel):
    """ Data Space Model: """
    def __init__(self, parent, option, option_callback):
        OptionPanel.__init__(self, parent, option, None)
        self.options = [
                '--model-small',
                '--model-medium',
                '--model-large',
                '--model-huge',
            ]    
        options_text = [
            '--model-small         internal data space is used (default)',
            '--model-medium        external paged data space is used',
            '--model-large         external data space is used',
            '--model-huge          functions are banked, data in external space',
        ]
        
        self.rb = wx.RadioBox(self, wx.ID_ANY, u"Data Space Model", wx.DefaultPosition, wx.DefaultSize, options_text, 1, wx.RA_SPECIFY_COLS)
        self.update_flags()
        
        self.sizer.Add(self.rb, 0, wx.ALL, 5)
        
        self.SetSizer(self.sizer)
        self.Layout()
        
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, self.rb)
        
    #-------------------------------------------------------------------
    def update_flags(self):
        i = 0
        for s in self.options:
            if s in self.option.cflag_lst:
                self.rb.SetSelection(i)
                return
            i += 1
        # if can't find --std, show default selection --std-sdcc89
        self.rb.SetSelection(0)
        
    #-------------------------------------------------------------------
    def EvtRadioBox(self, event):
        #print('EvtRadioBox: %d' % event.GetInt())
    
        label = self.options[event.GetInt()]
        #print label
        self.option.model_option_flag = label
        self.option.add_cflag(label)
        self.option.update_flags()
        self.option.dirty = True

#---------------------------------------------------------------------------
class PageCOption(OptionPanel):
    """ C Standard: """
    def __init__(self, parent, option, option_callback):
        OptionPanel.__init__(self, parent, option, None)        
        self.options = [
            '--std-c89',
            '--std-sdcc89',
            '--std-c99',
            '--std-sdcc99',
            '--std-c11',
        ]        
        options_text = [
            '--std-c89             Use C89 standard (slightly incomplete)',
            '--std-sdcc89          Use C89 standard with SDCC extensions (default)',
            '--std-c99             Use C99 standard (incomplete)',
            '--std-sdcc99          Use C99 standard with SDCC extensions',
            '--std-c11             Use C11 standard (very incomplete)',
        ]
        
        self.rb = wx.RadioBox(self, wx.ID_ANY, u"C standard", wx.DefaultPosition, wx.DefaultSize, options_text, 1, wx.RA_SPECIFY_COLS)
        self.update_flags()
            
        self.sizer.Add(self.rb, 0, wx.ALL, 5)
        
        self.SetSizer(self.sizer)
        self.Layout()
        
        self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, self.rb)
    
    #-------------------------------------------------------------------
    def update_flags(self):
        i = 0
        for s in self.options:
            if s in self.option.cflag_lst:
                self.rb.SetSelection(i)
                return
            i += 1
        # if can't find --std, show default selection --std-sdcc89
        self.rb.SetSelection(1)

    #-------------------------------------------------------------------
    def EvtRadioBox(self, event):
        #print('EvtRadioBox: %d' % event.GetInt())
        label = self.options[event.GetInt()]
        #print label
        self.option.dirty = True
        self.option.add_cflag(label)
        self.option.update_flags()
        
        
#---------------------------------------------------------------------------
class PageOptimizeOption(OptionPanel):
    """
            Optimization options:
    """
    def __init__(self, parent, option, option_callback):
        OptionPanel.__init__(self, parent, option, self.option_callback)

        title = 'Optimization options:'
        lst = [        
            ['--nooverlay',           'Disable overlaying leaf function auto variables'],
            ['--nogcse',              'Disable the GCSE optimisation'],
            ['--nolabelopt',          'Disable label optimisation'],
            ['--noinvariant',         'Disable optimisation of invariants'],
            ['--noinduction',         'Disable loop variable induction'],
            ['--nojtbound',           'Don\'t generate boundary check for jump tables'],
            ['--noloopreverse',       'Disable the loop reverse optimisation'],
            ['--no-peep',             'Disable the peephole assembly file optimisation'],
            ['--no-reg-params',       'On some ports, disable passing some parameters in registers'],
            ['--peep-asm',            'Enable peephole optimization on inline assembly'],
            ['--peep-return',         'Enable peephole optimization for return instructions'],
            ['--no-peep-return',      'Disable peephole optimization for return instructions'],
            ['--peep-file',           '<file> use this extra peephole file', 'file'],
            ['--opt-code-speed',      'Optimize for code speed rather than size'],
            ['--opt-code-size',       'Optimize for code size rather than speed'],
            ['--max-allocs-per-node', 'Maximum number of register assignments considered at each node of the tree decomposition'],
            ['--nolospre',            'Disable lospre'],
            ['--lospre-unsafe-read',  'Allow unsafe reads in lospre'],
            ]
        self.set_check_list(title, lst)
        self.update_flags()
        
        
#---------------------------------------------------------------------------
class PageLinkerOption(OptionPanel):
    """ Linker options: """
    def __init__(self, parent, option, option_callback):
        OptionPanel.__init__(self, parent, option, self.option_callback)
        #-l                        Include the given library in the link
        #-L                        Add the next field to the library search path        
        
        #LabelTextCtrl(self, self.sizer, '--xram-loc', help_str='<nnnn> External Ram start location', default_str='')
        #LabelTextCtrl(self, self.sizer, '--xram-size', help_str='<nnnn> External Ram size', default_str='')
        
        title = 'Linker options:'
        lst = [        
            ['--out-fmt-ihx',         'Output in Intel hex format'],
            ['--out-fmt-s19',         'Output in S19 hex format'],
            ['--xram-loc',            '<nnnn> External Ram start location', 'hex'],
            ['--xram-size',           '<nnnn> External Ram size', 'hex'],
            ['--iram-size',           '<nnnn> Internal Ram size', 'hex'],
            ['--xstack-loc',          '<nnnn> External Stack start location', 'hex'],
            ['--code-loc',            '<nnnn> Code Segment Location', 'hex'],
            ['--code-size',           '<nnnn> Code Segment size', 'hex'],
            ['--stack-loc',           '<nnnn> Stack pointer initial value', 'hex'],
            ['--data-loc',            '<nnnn> Direct data start location', 'hex'],
            ['--idata-loc',           '<nnnn>', 'hex'],
            ['--no-optsdcc-in-asm',   'Do not emit .optsdcc in asm'],
        ]
        self.set_check_list(title, lst)
        self.update_flags()
                
    #-------------------------------------------------------------------
    def update_flags(self):
        for t in self.cbox_list.cboxes:
            cb = t[0]
            key = t[1]
            value = self.option.flag_dict.get(key, None)
            #print key, value
            if value:
                key += value
            if key in self.option.ldflag_lst:
                cb.cbox.SetValue(True)
                if value:
                    cb.text_entry.SetValue(value.strip())
            else:
                cb.cbox.SetValue(False)
                
    #-------------------------------------------------------------------
    def option_callback(self, title, label, checked, value):
        print title, label, checked, value
        if checked == True:
            self.option.add_ldflag(label, value)
        else:            
            self.option.remove_ldflag(label, value)
            
        self.option.update_ldflags()
        
        
#---------------------------------------------------------------------------
class Mcu():
    def __init__(self, mcu_name, option):
        self.option = option
        self.mcu_name = mcu_name
        self.mcu_flag = '-m' + mcu_name
        self.default_cflags = ''
        self.default_ldflags = ''
        self.devices = None
        
#---------------------------------------------------------------------------
class McuMCS51(Mcu):
    def __init__(self, mcu_name, option):
        Mcu.__init__(self, mcu_name, option)
        self.default_ldflag =  '--no-std-crt0 --code-loc 0x8080 --data-loc 0x7000'
        self.title = 'Special options for the mcs51 port:'
        self.lst = [              
            ['--stack-size',          'Tells the linker to allocate this space for stack'],
            ['--parms-in-bank1',      'use Bank1 for parameter passing'],
            ['--pack-iram',           'Tells the linker to pack variables in internal ram (default)'],
            ['--no-pack-iram',        'Deprecated: Tells the linker not to pack variables in internal ram'],
            ['--acall-ajmp',          'Use acall/ajmp instead of lcall/ljmp'],
            ['--no-ret-without-call', 'Do not use ret independent of acall/lcall'],
            ]
        self.devices = ['8051', '8052', 'ADuC84x', 'AT89C513xA', 'C8051F000', 
                        'C8051F018', 'C8051F020', 'C8051F040', 'C8051F060', 
                        'C8051F120', 'C8051F200', 'C8051F300', 'C8051F310', 
                        'C8051F320', 'C8051F326', 'C8051F330', 'C8051F336', 
                        'C8051F340', 'C8051F350', 'C8051F360', 'C8051F410', 
                        'C8051F520', 'C8051F920', 'C8051T600', 'C8051T610', 'C8051T630', 
                        'P89LPC901', 'P89LPC922', 'P89LPC925', 'P89LPC932', 'P89c51RD2',
                        'SST89x5xRDx', 'XC866', 'at89S8252', 'at89Sx051', 'at89c51ed2', 
                        'at89c51snd1c', 'at89c55', 'at89s53', 'at89s8253', 'at89x051', 
                        'at89x51', 'at89x52', 'cc1110', 'cc2430', 'cc2510fx', 'cc2530', 
                        'msc1210', 'msm8xc154s', 'p89c66x', 'p89lpc9321', 'p89lpc9331', 
                        'p89lpc933_4', 'p89lpc9351', 'p89lpc935_6', 'p89lpc938', 'p89v51rd2', 
                        'p89v66x', 'reg51', 'reg764', 'regc515c', 'sab80515', 
                        'stc12', 'uPSD32xx', 'uPSD33xx', 'w7100']

#---------------------------------------------------------------------------
class McuZ80(Mcu):
    def __init__(self, mcu_name, option):
        Mcu.__init__(self, mcu_name, option)
        self.default_ldflags =  '--no-std-crt0 --code-loc 0x8080 --data-loc 0x7000'
        self.title = 'Special options for the ' + mcu_name + ' port:'
        self.lst = [
              ['--callee-saves-bc',     'Force a called function to always save BC'],
              ['--portmode=',           'Determine PORT I/O mode (z80/z180)', ['z80', 'z180']],
              ['--asm=',                'Define assembler name (rgbds/asxxxx/isas/z80asm)', ['rgbds', 'asxxxx', 'isas', 'z80asm']],
              ['--codeseg',             '<name> use this name for the code segment', 'name'],
              ['--constseg',            '<name> use this name for the const segment', 'name'],
              ['--no-std-crt0',         'For the z80/gbz80 do not link default crt0.rel'],
              ['--reserve-regs-iy',     'Do not use IY (incompatible with --fomit-frame-pointer)'],
              ['--oldralloc',           'Use old register allocator'],
              ['--fno-omit-frame-pointer',  'Do not omit frame pointer'],
              ]
        self.devices = None

#-------------------------------------------------------------------
class McuGBZ80(Mcu):
    def __init__(self, mcu_name, option):
        Mcu.__init__(self, mcu_name, option)
        self.title = 'Special options for the gbz80 port:'
        
        self.lst = [              
              ['-bo',                   '<num> use code bank <num>', 'num'],
              ['-ba',                   '<num> use data bank <num>', 'num'],
              ['--callee-saves-bc',     'Force a called function to always save BC'],
              ['--codeseg',             '<name> use this name for the code segment', 'name'],
              ['--constseg',            '<name> use this name for the const segment', 'name'],
              ['--no-std-crt0',         'For the z80/gbz80 do not link default crt0.rel'],
              ]
        self.devices = None
        
#-------------------------------------------------------------------
class McuPIC16(Mcu):
    def __init__(self, mcu_name, option):
        Mcu.__init__(self, mcu_name, option)
        self.title = 'Special options for the pic16 port:'
        self.default_cflags = '--use-non-free'
        self.lst = [
              ['--use-non-free',        'Search / include non-free licensed libraries and header files'],
              ['--pstack-model=',       'use stack model \'small\' (default) or \'large\'', ['small', 'large']],
              ['--extended',            'enable Extended Instruction Set/Literal Offset Addressing mode'],
              ['--pno-banksel',         'do not generate BANKSEL assembler directives'],
              ['--obanksel=',           'set banksel optimization level (default=0 no)', 'num'],
              ['--denable-peeps',       'explicit enable of peepholes'],
              ['--no-optimize-goto',    'do NOT use (conditional) BRA instead of GOTO'],
              ['--optimize-cmp',        'try to optimize some compares'],
              ['--optimize-df',         'thoroughly analyze data flow (memory and time intensive!)'],
              ['--asm=',                'Use alternative assembler', 'name'],
              ['--mplab-comp',          'enable compatibility mode for MPLAB utilities (MPASM/MPLINK)'],
              ['--link=',               'Use alternative linker', 'name'],
              ['--preplace-udata-with=',  'Place udata variables at another section: udata_acs, udata_ovr, udata_shr'],
              ['--ivt-loc=',            'Set address of interrupt vector table.', 'num'],
              ['--nodefaultlibs',       'do not link default libraries when linking'],
              ['--use-crt=',            'use <crt-o> run-time initialization module', 'name'],
              ['--no-crt',              'do not link any default run-time initialization module'],
              ['--debug-xtra',          'show more debug info in assembly output'],
              ['--debug-ralloc',        'dump register allocator debug file *.d'],
              ['--pcode-verbose',       'dump pcode related info'],
              ['--calltree',            'dump call tree in .calltree file'],
              ['--gstack',              'trace stack pointer push/pop to overflow'],
              ]
        self.devices = ['18f1220', '18f1230', '18f1320', '18f1330', '18f13k22', 
                        '18f13k50', '18f14k22', '18f14k50', '18f2220', '18f2221', 
                        '18f2320', '18f2321', '18f2331', '18f23k20', '18f23k22',
                        '18f2410', '18f242', '18f2420', '18f2423', '18f2431',
                        '18f2439', '18f2450', '18f2455', '18f2458', '18f248', 
                        '18f2480', '18f24j10', '18f24j11', '18f24j50', '18f24k20', 
                        '18f24k22', '18f24k50', '18f2510', '18f2515', '18f252', 
                        '18f2520', '18f2523', '18f2525', '18f2539', '18f2550', 
                        '18f2553', '18f258', '18f2580', '18f2585', '18f25j10', 
                        '18f25j11', '18f25j50', '18f25k20', '18f25k22', '18f25k50', 
                        '18f25k80', '18f2610', '18f2620', '18f2680', '18f2682', 
                        '18f2685', '18f26j11', '18f26j13', '18f26j50', '18f26j53', 
                        '18f26k20', '18f26k22', '18f26k80', '18f27j13', '18f27j53', 
                        '18f4220', '18f4221', '18f4320', '18f4321', '18f4331', 
                        '18f43k20', '18f43k22', '18f4410', '18f442', '18f4420', 
                        '18f4423', '18f4431', '18f4439', '18f4450', '18f4455', 
                        '18f4458', '18f448', '18f4480', '18f44j10', '18f44j11', 
                        '18f44j50', '18f44k20', '18f44k22', '18f4510', '18f4515', 
                        '18f452', '18f4520', '18f4523', '18f4525', '18f4539', 
                        '18f4550', '18f4553', '18f458', '18f4580', '18f4585', 
                        '18f45j10', '18f45j11', '18f45j50', '18f45k20', '18f45k22', 
                        '18f45k50', '18f45k80', '18f4610', '18f4620', '18f4680', 
                        '18f4682', '18f4685', '18f46j11', '18f46j13', '18f46j50', 
                        '18f46j53', '18f46k20', '18f46k22', '18f46k80', '18f47j13', 
                        '18f47j53', '18f6310', '18f6390', '18f6393', '18f63j11', 
                        '18f63j90', '18f6410', '18f6490', '18f6493', '18f64j11', 
                        '18f64j90', '18f6520', '18f6525', '18f6527', '18f6585', 
                        '18f65j10', '18f65j11', '18f65j15', '18f65j50', '18f65j90', 
                        '18f65j94', '18f65k22', '18f65k80', '18f65k90', '18f6620', 
                        '18f6621', '18f6622', '18f6627', '18f6628', '18f6680', 
                        '18f66j10', '18f66j11', '18f66j15', '18f66j16', '18f66j50', 
                        '18f66j55', '18f66j60', '18f66j65', '18f66j90', '18f66j93', 
                        '18f66j94', '18f66j99', '18f66k22', '18f66k80', '18f66k90', 
                        '18f6720', '18f6722', '18f6723', '18f67j10', '18f67j11', 
                        '18f67j50', '18f67j60', '18f67j90', '18f67j93', '18f67j94', 
                        '18f67k22', '18f67k90', '18f8310', '18f8390', '18f8393', 
                        '18f83j11', '18f83j90', '18f8410', '18f8490', '18f8493', 
                        '18f84j11', '18f84j90', '18f8520', '18f8525', '18f8527', 
                        '18f8585', '18f85j10', '18f85j11', '18f85j15', '18f85j50', 
                        '18f85j90', '18f85j94', '18f85k22', '18f85k90', '18f8620', 
                        '18f8621', '18f8622', '18f8627', '18f8628', '18f8680', 
                        '18f86j10', '18f86j11', '18f86j15', '18f86j16', '18f86j50', 
                        '18f86j55', '18f86j60', '18f86j65', '18f86j72', '18f86j90', 
                        '18f86j93', '18f86j94', '18f86j99', '18f86k22', '18f86k90', 
                        '18f8720', '18f8722', '18f8723', '18f87j10', '18f87j11', 
                        '18f87j50', '18f87j60', '18f87j72', '18f87j90', '18f87j93', 
                        '18f87j94', '18f87k22', '18f87k90', '18f95j94', '18f96j60', 
                        '18f96j65', '18f96j94', '18f96j99', '18f97j60', '18f97j94', 
                        '18fam']
        self.lst.insert(0, ['combo', self.devices])
    
#-------------------------------------------------------------------
class McuPIC14(Mcu):
    def __init__(self, mcu_name, option):
        Mcu.__init__(self, mcu_name, option)
        self.title = 'Special options for the pic14 port:'
        self.default_cflags = '--use-non-free'
        self.lst = [
              ['--use-non-free',        'Search / include non-free licensed libraries and header files'],
              ['--debug-xtra',          'show more debug info in assembly output'],
              ['--no-pcode-opt',        'disable (slightly faulty) optimization on pCode'],
              ['--stack-size',          'sets the size if the argument passing stack (default: 16, minimum: 4)'],
              ['--no-extended-instructions',  'forbid use of the extended instruction set (e.g., ADDFSR)'],
              ]
        self.devices = ['10f320', '10f322', '12f1501', '12f1822', '12f1840', 
                        '12f609', '12f615', '12f617', '12f629',  '12f635', 
                        '12f675', '12f683', '12f752', '12lf1552', '14regs', 
                        '16c432', '16c433', '16c554', '16c557', '16c558', 
                        '16c62', '16c620', '16c620a', '16c621', '16c621a', 
                        '16c622', '16c622a', '16c63a', '16c65b', '16c71', 
                        '16c710', '16c711', '16c715', '16c717', '16c72', 
                        '16c73b', '16c745', '16c74b', '16c765', '16c770', 
                        '16c771', '16c773', '16c774', '16c781', '16c782', 
                        '16c925', '16c926', '16f1454', '16f1455', '16f1458', 
                        '16f1459', '16f1503', '16f1507', '16f1508', '16f1509', 
                        '16f1512', '16f1513', '16f1516', '16f1517', '16f1518', 
                        '16f1519', '16f1526', '16f1527', '16f1704', '16f1708', 
                        '16f1782', '16f1783', '16f1784', '16f1786', '16f1787', 
                        '16f1788', '16f1789', '16f1823', '16f1824', '16f1825', 
                        '16f1826', '16f1827', '16f1828', '16f1829', '16f1847', 
                        '16f1933', '16f1934', '16f1936', '16f1937', '16f1938', 
                        '16f1939', '16f1946', '16f1947', '16f610', '16f616', 
                        '16f627', '16f627a', '16f628', '16f628a', '16f630', 
                        '16f631', '16f636', '16f639', '16f648a', '16f676', 
                        '16f677', '16f684', '16f685', '16f687', '16f688', 
                        '16f689', '16f690', '16f707', '16f716', '16f72', 
                        '16f720', '16f721', '16f722', '16f722a', '16f723', 
                        '16f723a', '16f724', '16f726', '16f727', '16f73', 
                        '16f737', '16f74', '16f747', '16f753', '16f76', 
                        '16f767', '16f77', '16f777', '16f785', '16f818', 
                        '16f819', '16f84', '16f84a', '16f87', '16f870', 
                        '16f871', '16f872', '16f873', '16f873a', '16f874', 
                        '16f874a', '16f876', '16f876a', '16f877', '16f877a', 
                        '16f88', '16f882', '16f883', '16f884', '16f886', 
                        '16f887', '16f913', '16f914', '16f916', '16f917', 
                        '16f946', '16fam', '16hv616', '16hv753', '16lf1704', 
                        '16lf1708', '16lf1902', '16lf1903', '16lf1904', '16lf1906', '16lf1907']
        self.lst.insert(0, ['combo', self.devices])
    
#-------------------------------------------------------------------
class McuDS390(Mcu):
    def __init__(self, mcu_name, option):
        Mcu.__init__(self, mcu_name, option)
        self.default_cflags = '--model-large'
        self.default_ldflags = '--xram-loc 0x100080 --code-loc 0x10000 -Wl-r'
        self.title = 'Special options for the TININative port:'
        self.lst = [
              ['--model-flat24',        'use the flat24 model for the ds390 (default)'],
              ['--stack-8bit',          'use the 8bit stack for the ds390 (not supported yet)'],
              ['--stack-size',          'Tells the linker to allocate this space for stack'],
              ['--pack-iram',           'Tells the linker to pack variables in internal ram (default)'],
              ['--no-pack-iram',        'Deprecated: Tells the linker not to pack variables in internal ram'],
              ['--stack-10bit',         'use the 10bit stack for ds390 (default)'],
              ['--use-accelerator',     'generate code for ds390 arithmetic accelerator'],
              ['--protect-sp-update',   'will disable interrupts during ESP:SP updates'],
              ['--parms-in-bank1',      'use Bank1 for parameter passing'],
              ['--tini-libid',          '<nnnn> LibraryID used in -mTININative', 'num'],
              ]
        self.devices = None
    
 #-------------------------------------------------------------------
class McuDS400(Mcu):
    def __init__(self, mcu_name, option):
        Mcu.__init__(self, mcu_name, option)
        self.default_cflags = '--model-large'
        self.default_ldflags = '--xram-loc 0x10000 --code-loc 0x400000 -Wl-r'
        self.title = 'Special options for the ds400 port:'
        self.lst = [
              ['--model-flat24',        'use the flat24 model for the ds400 (default)'],
              ['--stack-8bit',          'use the 8bit stack for the ds400 (not supported yet)'],
              ['--stack-size',          'Tells the linker to allocate this space for stack'],
              ['--pack-iram',           'Tells the linker to pack variables in internal ram (default)'],
              ['--no-pack-iram',        'Deprecated: Tells the linker not to pack variables in internal ram'],
              ['--stack-10bit',         'use the 10bit stack for ds400 (default)'],
              ['--use-accelerator',     'generate code for ds400 arithmetic accelerator'],
              ['--protect-sp-update',   'will disable interrupts during ESP:SP updates'],
              ['--parms-in-bank1',      'use Bank1 for parameter passing'],
              ]
        self.devices = None
        
#-------------------------------------------------------------------
class McuHC08(Mcu):
    def __init__(self, mcu_name, option):
        Mcu.__init__(self, mcu_name, option)
        self.title = 'Special options for the ' + mcu_name + ' port:'
        self.lst = [
              ['--out-fmt-elf',         'Output executable in ELF format'],
              ['--oldralloc',           'Use old register allocator'],
              ]
        self.devices = ['mc68hc908apxx', 'mc68hc908gp32', 'mc68hc908jb8', 'mc68hc908jkjl', 'mc68hc908qy']
    
    
#---------------------------------------------------------------------------
class PageMcuOptions(OptionPanel):
    def __init__(self, parent, option, option_callback):
        OptionPanel.__init__(self, parent, option, self.option_callback)
        #self.SetInitialSize((800, 600))
        
        self.log = parent.log
        self.option = option
        self.cbox_list = None
        self.title = 'Mcu Options'
        self.select_mcu(option.mcu_name)
        
        self.SetSizer( self.sizer )
        self.Layout()
                
    #-------------------------------------------------------------------
    def select_mcu(self, mcu_name):
        """ select new mcu and create new panel """        
        
        #if self.option.mcu:
        option = self.option
        mcu = option.get_mcu_class(mcu_name)
        
        if self.cbox_list is not None:
            self.sizer.Hide(self.cbox_list)
            self.sizer.Remove(self.cbox_list)
            del self.cbox_list
            self.cbox_list = None
        
        option.mcu = mcu
        self.cbox_list = CheckBoxList(self, self.sizer, mcu.title, mcu.lst, self.checkbox_click)
        
        if mcu.devices and self.cbox_list.device_listbox is not None:
            if option.mcu_device != "":
                self.cbox_list.device_listbox.SetStringSelection(option.mcu_device, True)
            self.Bind(wx.EVT_LISTBOX, self.OnSelect, self.cbox_list.device_listbox)
            
            #ComboBox(self, self.sizer, 'devices', mcu.devices)
        self.update_flags()
        self.sizer.Show(self.cbox_list)
            
        self.SetSizer( self.sizer )
        self.Layout()
        
    #-------------------------------------------------------------------
    def OnSelect(self, event):
        index = event.GetSelection()
        s = self.option.mcu.devices[index]
        self.option.select_mcu_device(s)
        
#---------------------------------------------------------------------------
class PageMajorOption(wx.Panel):
    """
            Major options, sdcc bin, lib, include, cflagss, ldflags
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
        
        mcu_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mcu_cbox = ComboBox(self, mcu_sizer, "Select MCU", option.mcu_lst)
        if option.mcu_name == '':
            option.mcu_name = 'mcs51'
            
        self.mcu_cbox.SetValue(option.mcu_name)
        
        main_sizer.Add(mcu_sizer, 0, wx.ALL, 5)
        
        self.inc_path_text = LabelButtonTextCtrl(self, main_sizer, "Include Search Path :", '', option.inc_pathes, '+')
        self.lib_path_text = LabelButtonTextCtrl(self, main_sizer, "Lib Search Path :", '', option.lib_pathes, '+')
        
        StaticLine(self, main_sizer)
        self.cb_ignore = CheckBox(self, main_sizer, -1, 'Ignore other cflags and ldflags')        
        
        option.custom_cflags_text = LabelButtonTextCtrl(self, main_sizer, "Add CFLAGS :", "", option.custom_cflags, 'Enter')
        option.custom_ldflags_text = LabelButtonTextCtrl(self, main_sizer, "Add LDFLAGS :", "", option.custom_ldflags, 'Enter')

        self.update_flags()
        self.SetSizer(main_sizer)
        self.Layout()
        
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectMcuItem, self.mcu_cbox)
        self.Bind(wx.EVT_BUTTON, self.OnCflagButton, option.custom_cflags_text.btn)
        self.Bind(wx.EVT_CHECKBOX, self.OnIgnoreFlagCheckBox, self.cb_ignore)
                
        self.Bind(wx.EVT_BUTTON, self.OnIncPathButton, self.inc_path_text.btn)
        self.Bind(wx.EVT_BUTTON, self.OnLibPathButton, self.lib_path_text.btn)
            
        self.inited = True

        
    #-------------------------------------------------------------------
    def update_flags(self):
        opt = self.option
        if self.inited:
            opt.custom_cflags_text.SetValue(opt.custom_cflags)
            opt.custom_ldflags_text.SetValue(opt.custom_ldflags)
            
        if opt.custom_flag_only:
            self.cb_ignore.SetValue(True)
        else:
            self.cb_ignore.SetValue(False)
        
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
            self.inc_path_text.write(' -I' + dlg.GetPath())
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
            self.lib_path_text.write(' -L' + dlg.GetPath())
            self.option.set_lib_pathes(self.lib_path_text.GetValue())
            self.option.dirty = True

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
        
    #-------------------------------------------------------------------
    def OnIgnoreFlagCheckBox(self, event):
        self.option.set_custom_flag_only(event.IsChecked())
        self.option.dirty = True
        
    #-------------------------------------------------------------------
    def OnCflagButton(self, event):
        self.option.set_custom_cflag(self.option.custom_cflags_text.GetValue())
        self.option.dirty = True
        
    #-------------------------------------------------------------------
    def OnLdflagButton(self, event):
        self.option.set_custom_ldflag(self.option.custom_ldflags_text.GetValue())
        self.option.dirty = True
        
    #-------------------------------------------------------------------
    def fbbCallback(self, evt):
        print('FileBrowseButton: %s\n' % evt.GetString())

    #-------------------------------------------------------------------
    def OnSelectMcuItem(self, event):
        #print("OnSelectItem", event.GetString(), event.GetId(), event.GetEventType(), event.GetEventObject())
        mcu_name = event.GetString()
        self.option.select_mcu(mcu_name)
        self.option.dirty = True
        
        
#---------------------------------------------------------------------------
class BuildOption():
    def __init__(self, file_path):
        self.dialog = None
        self.dirty = False
        
        self.target_file_path = file_path
        if file_path == '':
            self.target_type = ''
            self.config_file = 'sdcc.cfg'
        elif file_path.find('.sdprj') >= 0:
            self.target_type = 'prj'
            self.config_file = file_path.replace('.sdprj', '.sdcfg')
        elif file_path.find('.c') >= 0:
            self.target_type = 'c'
            self.config_file = file_path.replace('.c', '.sdcfg')
        else:
            p, ext = os.path.splitext(file_path)
            self.target_type = ext.replace('.', '')
            self.config_file = file_path.replace(ext, '.sdcfg')
        print self.config_file
        self.mcu = None
        self.mcu_page = None
        self.mcu_name = 'mcs51'
        self.mcu_device = ""
        self.mcu_lst = [
                      'mcs51',
                      'pic16',
                      'pic14',
                      'ds390',
                      'ds400',
                      'hc08',
                      's08',
                      'z80',
                      'z180',
                      'r2k',
                      'r3ka',
                      'gbz80',
                      'tlcs90',
                      ]
        self.cflag_lst = []
        self.ldflag_lst = []
        self.flag_dict = {}
        
        self.cflags = ''
        self.ldflags = ''
        self.custom_cflags = ''
        self.custom_ldflags = ''
        self.custom_flag_only = False
        
        self.cflags_text = None
        self.ldflags_text = None
        
        self.set_inc_pathes('-I. -I' + SDCC_inc_path)
        self.set_lib_pathes('-L. -L' + SDCC_lib_path)
        
        self.select_mcu(self.mcu_name)
                
                
    #-------------------------------------------------------------------
    def clear_cflags(self):
        self.cflag_lst = []
        
    #-------------------------------------------------------------------
    def clear_ldflags(self):
        self.ldflag_lst = []
        
    #-------------------------------------------------------------------
    def clear_flags(self):
        self.clear_cflags()
        self.clear_ldflags()
        
    #-------------------------------------------------------------------
    def get_mcu_class(self, mcu_name):
        z80_lst = ['z80', 'z180', 'r2k', 'r3ka', 'tlcs90']
        option = self
        if mcu_name == 'mcs51':
            mcu = McuMCS51(mcu_name, option)
        elif mcu_name == 'gbz80':
            mcu = McuGBZ80(mcu_name, option)
        elif mcu_name == 'pic16':
            mcu = McuPIC16(mcu_name, option)
        elif mcu_name == 'pic14':
            mcu = McuPIC14(mcu_name, option)
        elif mcu_name == 'ds390':
            mcu = McuDS390(mcu_name, option)
        elif mcu_name == 'ds400':
            mcu = McuDS400(mcu_name, option)
        elif mcu_name == 'hc08' or mcu_name == 's08':
            mcu = McuHC08(mcu_name, option)
        elif mcu_name in z80_lst:
            mcu = McuZ80(mcu_name, option)
        else:
            mcu = McuMCS51(mcu_name, option)
            
        return mcu
        
    #-------------------------------------------------------------------
    def select_mcu(self, mcu_name):

        if mcu_name != self.mcu_name:
            self.clear_flags()
            
        option = self
        mcu = self.get_mcu_class(mcu_name)

        self.mcu = mcu
        self.mcu_name = mcu_name
        self.mcu_flag = '-m' + mcu_name
        if self.mcu_page:
            page = self.mcu_page
            page.parent.SetPageText(page.page_index, mcu_name + ' Options')
            page.select_mcu(mcu_name)
            
        if self.dialog:
            self.dialog.update_flags()
            
        self.update_flags()
        
    #-------------------------------------------------------------------
    def select_mcu_device(self, dev_name):
        self.mcu_device = dev_name
        self.update_flags()
        
    #-------------------------------------------------------------------
    def set_custom_flag_only(self, flag):
        self.custom_flag_only = flag
        self.update_flags()
        
    #-------------------------------------------------------------------
    def set_custom_cflag(self, flag):
        self.custom_cflags = flag
        self.update_flags()
        
    #-------------------------------------------------------------------
    def set_custom_ldflag(self, flag):
        self.custom_ldflags = flag
        self.update_flags()
        
    #-------------------------------------------------------------------
    def set_inc_pathes(self, p):
        self.inc_pathes = p
        lst = self.inc_pathes.split('-I')
        lst.remove('')
        self.inc_path_lst = lst
        
    #-------------------------------------------------------------------
    def set_lib_pathes(self, p):
        self.lib_pathes = p
        lst = self.lib_pathes.split('-L')
        lst.remove('')
        self.lib_path_lst = lst
            
    #-------------------------------------------------------------------
    def update_flags(self):
        self.update_cflags()
        self.update_ldflags()
        
    #-------------------------------------------------------------------
    def update_cflags(self):
        if self.custom_flag_only:
            self.cflags = self.custom_cflags 
        else:
            mcu_flag = '-m' + self.mcu_name + ' '
            if self.mcu_device:
                mcu_flag += '-p' + self.mcu_device + ' '
                
            self.cflags = mcu_flag + self.custom_cflags + ' ' + ' '.join(self.cflag_lst)
            
        if self.cflags_text:
            self.cflags_text.SetValue(self.cflags)
            
    #-------------------------------------------------------------------
    def update_ldflags(self):
        if self.custom_flag_only:
            self.ldflags = self.custom_ldflags
        else:
            self.ldflags = self.custom_ldflags + ' ' + ' '.join(self.ldflag_lst)
        
        if self.ldflags_text:
            self.ldflags_text.SetValue(self.ldflags)
            
    #-------------------------------------------------------------------
    def remove_cflag(self, key, value=None):
        #print 'remove_cflag', key
        if key in self.cflag_lst:
            self.cflag_lst.remove(key)
            
        value = self.flag_dict.get(key, "")
        if value == "":
            return
        
        self.flag_dict.pop(key, None)
        #print key, value
        key += value
        if key in self.cflag_lst:
            self.cflag_lst.remove(key)
            
    #-------------------------------------------------------------------
    def remove_ldflag(self, key, value=None):
        #print 'remove_ldflag', key
        if key in self.ldflag_lst:
            self.ldflag_lst.remove(key)
            
        value = self.flag_dict.get(key, "")
        if value == "":
            return
        
        self.flag_dict.pop(key, None)
        #print key, value
        key += value
        if key in self.ldflag_lst:
            self.ldflag_lst.remove(key)
            
    #-------------------------------------------------------------------
    def remove_cflag_type(self, t):
        for key in self.cflag_lst:
            if key.find(t) >= 0:
                self.cflag_lst.remove(key)
                self.flag_dict[key] = ''
                break
            
    #-------------------------------------------------------------------
    def add_cflag(self, key, value=None):
        #print 'add_cflag ', key
        if key.find('--std-') >= 0:
            self.remove_cflag_type('--std-')
                
        if key.find('--model-') >= 0:
            self.remove_cflag_type('--model-')
            self.add_ldflag(key)
            self.update_ldflags()
            
        self.remove_cflag(key)
        if value:
            self.flag_dict[key] = value
            self.cflag_lst.append(key + value)
        else:
            if key == '--std-sdcc89' or key == '--model-small' :
                pass
            else:            
                self.cflag_lst.append(key)
            
    #-------------------------------------------------------------------
    def remove_ldflag_type(self, t):
        for key in self.ldflag_lst:
            if key.find(t) >= 0:
                self.ldflag_lst.remove(key)
                self.flag_dict[key] = ''
                break
            
    #-------------------------------------------------------------------
    def add_ldflag(self, key, value=None):
        #print 'add_ldflag ', key

        if key.find('--model-') >= 0:
            self.remove_ldflag_type('--model-')
            
        self.remove_ldflag(key)
        if value:
            self.flag_dict[key] = value
            self.ldflag_lst.append(key + value)
        else:
            if key == '--std-sdcc89' or key == '--model-small' :
                pass
            else:
                self.ldflag_lst.append(key)
            
    #-------------------------------------------------------------------
    def load_ldflags(self, s):
        """ clear and add all flag in string """
        self.clear_ldflags()
        
        for key in s.split(','):
            if not key in self.ldflag_lst:
                if key == '--std-sdcc89' or key == '--model-small' :
                    pass
                else:                            
                    self.ldflag_lst.append(key)
                
            if key.find(' ') > 0:
                k, v = key.split(' ')
                self.flag_dict[k] = ' ' + v
                
            if key.find('=') > 0:
                k, v = key.split('=')
                self.flag_dict[k] = v
        
    #-------------------------------------------------------------------
    def load_cflags(self, s):
        self.clear_cflags()

        for key in s.split(','):
            key = key.strip()
            if not key in self.cflag_lst:
                if key == '--std-sdcc89' or key == '--model-small' :
                    pass
                else:                            
                    self.cflag_lst.append(key)
                
            if key.find(' ') > 0:
                k, v = key.split(' ')
                self.flag_dict[k] = ' ' + v
                
            if key.find('=') > 0:
                k, v = key.split('=')
                self.flag_dict[k] = v
                
    #-------------------------------------------------------------------
    def save_config(self):
        #print("save config - sdcc.cfg")
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)
        
        config.Write("mcu_name", self.mcu_name)
        config.Write("mcu_device", self.mcu_device)
                
        config.Write("custom_flag_only", str(self.custom_flag_only))
        config.Write("custom_cflags", self.custom_cflags)
        config.Write("custom_ldflags", self.custom_ldflags)
        
        config.Write("inc_pathes", self.inc_pathes)
        config.Write("lib_pathes", self.lib_pathes)
        
        config.Write("cflag_lst",  ",".join(self.cflag_lst))
        config.Write("ldflag_lst", ",".join(self.ldflag_lst))
        
        config.Write("cflags",  self.cflags + ' ' + self.inc_pathes)
        config.Write("ldflags", self.ldflags + ' ' + self.lib_pathes)
        
        del config
        
        if self.config_file != 'sdcc.cfg':
            utils.copy_file(self.config_file, 'sdcc.cfg')
            
        self.dirty = False
        
    #-------------------------------------------------------------------
    def load_config(self):
        #print("load config - sdcc.cfg")
        config = wx.FileConfig("", "", self.config_file, "", wx.CONFIG_USE_LOCAL_FILE)

        if config.Exists("mcu_name"):
            
            self.mcu_name = config.Read("mcu_name", "mcs51") 
            self.mcu_device = config.Read("mcu_device", "") 
            
            flag_str = config.Read("custom_flag_only", "False")
            if flag_str == "True":
                self.custom_flag_only = True
            else:
                self.custom_flag_only = False
            self.custom_cflags = config.Read("custom_cflags", "")
            self.custom_ldflags = config.Read("custom_ldflags", "")
            
            self.inc_pathes = config.Read("inc_pathes", "")
            self.lib_pathes = config.Read("lib_pathes", "")
            
            s = config.Read("cflag_lst", "")
            self.load_cflags(s)
            
            s = config.Read("ldflag_lst", "")
            self.load_ldflags(s)
        else:
            self.clear_flags()
            self.select_mcu("mcs51")
            
        del config
        
        
#---------------------------------------------------------------------------
class BuildOptionDialog(Dialog):
    def __init__(self, parent, id, title, file_path):
        #Dialog.__init__ ( self, parent, id, title + ' [' + os.path.basename(file_path) + ']')
        Dialog.__init__ ( self, parent, id, title)
        self.parent = parent
        self.log = parent.log
        
        self.cflags = None
        self.ldflags = None
        
        self.SetInitialSize((768, 525))
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.option = BuildOption(file_path)
        opt = self.option
        opt.load_config()
        opt.dialog = self
        
        # Here we create a panel and a notebook on the panel
        nb_panel = wx.Panel(self)
        nb = wx.Notebook(nb_panel)

        nb.log = self.log
        
        self.page_list = [
            [PageMajorOption,       'Major Options'],
            [PageMcuOptions,        opt.mcu_name + ' Options'],
            [PageGeneralOption,     'General'],
            [PageCOption,           'C Options'],
            [PageOptimizeOption,    'Optimization'],
            [PageLinkerOption,      'Linker'],
            [PageModelOption,       'Data Model'],
            [PageCodeGenOption,     'Code Gen'],
            [PageDebugOption,       'Debugging'],
        ]
        i = 0
        for t in self.page_list:
            page_class = t[0]
            page = page_class(nb, opt, None)
            t.append(page)
            nb.AddPage(page, t[1])
            page.page_index = i
            page.parent = nb
            if page_class == PageMcuOptions:
                opt.mcu_page = page
            i += 1
            #print t[1], page.GetSize(), page.GetPosition()
                
        # Put the notebook in a sizer for the panel to manage the layout
        nb_sizer = wx.BoxSizer(wx.VERTICAL)        
        nb_sizer.Add(nb, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        nb_panel.SetSizer(nb_sizer)
        
        # Add ok and cancel button
        main_sizer.Add(nb_panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        StaticLine(self, main_sizer)
        
        opt.cflags_text = StaticTextCtrl(self, main_sizer, "CFLAGS :", "", '')
        opt.ldflags_text = StaticTextCtrl(self, main_sizer, "LDFLAGS :", "", '')
        
        opt.update_flags()
        
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
        self.cflags = opt.cflags + ' ' + opt.inc_pathes + ' ' + opt.custom_cflags
        self.ldflags = opt.ldflags + ' ' + opt.lib_pathes + ' ' + opt.custom_ldflags

        event.Skip()
                
    #-------------------------------------------------------------------
    def ask_if_save_config(self, msg):
        strs = "Build option is modified. Do you want to save?"
        dlg = wx.MessageDialog(self, strs, msg, wx.YES_NO)
        result = dlg.ShowModal()
        dlg.Destroy()
        #log("ask_if_save return=", result, "yes=", wx.ID_YES, "no=", wx.ID_NO)
        if result == wx.ID_YES :
            opt = self.option
            opt.save_config()
            self.cflags = opt.cflags + ' ' + opt.inc_pathes + ' ' + opt.custom_cflags
            self.ldflags = opt.ldflags + ' ' + opt.lib_pathes + ' ' + opt.custom_ldflags
        
    #-------------------------------------------------------------------
    def OnCloseDialog(self, event):
        #print 'OnCloseDialog'
        if self.option.dirty:
            self.ask_if_save_config("OnCloseDialog")
        event.Skip()
        
    #-------------------------------------------------------------------
    def update_flags(self):
        for t in self.page_list:
            page = t[2]
            page.update_flags()


#-------------------------------------------------------------------
def get_mcu_from_config(file_path):
    file_path = file_path.replace('.c', '.sdcfg')
    
    #print("load config - sdcc.cfg")
    config = wx.FileConfig("", "", file_path, "", wx.CONFIG_USE_LOCAL_FILE)

    if config.Exists("mcu_name"):
        mcu_name = config.Read("mcu_name", "mcs51") 
        mcu_device = config.Read("mcu_device", "") 
    
    return mcu_name
            
#---------------------------------------------------------------------------
def show_build_option_dialog(parent):
    #p = "/home/athena/src/8051/BlinkLEDs/main.c"
    p = "/home/athena/src/pic/test1/test.c"
    dlg = BuildOptionDialog(parent, -1, "SDCC Build Options", p)
    dlg.CenterOnScreen()

    # this does not return until the dialog is closed.
    val = dlg.ShowModal()

    if val == wx.ID_OK:
        print("You pressed OK\n")
    else:
        print("You pressed Cancel\n")

    dlg.Destroy()
    
    
#---- for testing -------------------------------------------------------------
class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)
        
    #-------------------------------------------------------------------
    def show_dialog(self):
        #dlg = ProjectSettingDialog(self, -1, "Project Settings", size=(800, 600))
        dlg = BuildOptionDialog(self, -1, "SDCC Build Options",  "/home/athena/src/8051/BlinkLEDs/main.c")
        dlg.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()
    
        if val == wx.ID_OK:
            print("You pressed OK\n")
        else:
            print("You pressed Cancel\n")

        dlg.Destroy()
        
        
#---- for testing -------------------------------------------------------------
def test_app():
    app = wx.PySimpleApp()
    frame = wx.Frame(None, pos=wx.Point(400, 400))

    sizer = wx.BoxSizer(wx.VERTICAL)
    
    log = wx.TextCtrl(frame, size=wx.Size(300, 200), style = wx.TE_MULTILINE)
    test_panel = TestPanel(frame,  log)
    
    sizer.Add(test_panel, 0, wx.EXPAND, 5)
    sizer.Add(log, 0, wx.ALL, 5)
    
    frame.SetSizer(sizer)
    sizer.Fit(frame)
    
    app.SetTopWindow(frame)
    frame.Show(True)
    
    test_panel.show_dialog()
    
    app.MainLoop()


#---- for testing -------------------------------------------------------------
if __name__ == '__main__':
    #utils.proc_file('/home/athena/myproject/py_ide/sdcc.help')
    test_app()


