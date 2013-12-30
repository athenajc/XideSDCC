#!/usr/bin/python

from distutils.core import setup
import py2exe
from glob import glob
import sys
import os

#sys.path.append('ftpserver')

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
<assemblyIdentity
    version="0.64.1.0"
    processorArchitecture="x86"
    name="Controls"
    type="win32"
/>
<description>Xanadu - IDE for SDCC</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
"""

"""
installs manifest and icon into the .exe
but icon is still needed as we open it
for the window icon (not just the .exe)
changelog and logo are included in dist
      data_files=["yourapplication.ico"]
            "other_resources": [(24,1,manifest)]
    data_files=data_files,
"""
data_files = []
includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll']

#-------------------------------------------------------------------------------------------
def read_dir(path):
    flst = os.listdir(path)
    lst = []

    for f in flst:
        f1 = path + os.sep + f
        #print f1
        if os.path.isdir(f1):
            lst1 = read_dir(f1)
            data_pair = (f1, lst1)
            data_files.append(data_pair)
        else :
            lst.append(f1)
            
    return lst

#-------------------------------------------------------------------------------------------
def setup_data_files():
    cur_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep
    dirs = ['examples', 'ide\\images', 'ide\\sim\\images', 'ide\\sim\\pic14\\defines']
    
    for dir in dirs:
        lst = read_dir(dir)
        
        data_pair = (dir, lst)
        data_files.append(data_pair)
        
#-------------------------------------------------------------------------------------------
def do_setup():
    setup(
        windows = [
            {
                "script": "xide_sdcc.py",
                "icon_resources": [(0, "icon.ico")]     ### Icon to embed into the PE file.
            }
           ],
        data_files = data_files,
        
        options = {"py2exe": {"compressed": 2,
                             "optimize": 2,
                             "includes": includes,
                             "excludes": excludes,
                             "packages": packages,
                             "dll_excludes": dll_excludes,
                             "bundle_files": 3,
                             "dist_dir": "dist",
                             "xref": False,
                             "skip_archive": False,
                             "ascii": False,
                             "custom_boot_script": '',
                            }
                 },
    )


#-------------------------------------------------------------------------------------------
setup_data_files()
#print data_files
do_setup()
 
