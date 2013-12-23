#!/usr/bin/python2
# SDCC IDE
import wx
import ide

#--------------------------------------------------------------------------------------------------
def main():
    app = ide.IdeApp()

    if app is None:
        return False
    else:
        app.MainLoop()
        return True

main()


