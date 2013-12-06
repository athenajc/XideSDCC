#!/usr/bin/python

import os, sys

def test1(app):
    print("The child will write text to a pipe and ")
    print("the parent will read the text written by child...")
   
    # file descriptors r, w for reading and writing
    r, w = os.pipe() 
    
    processid = os.fork()
    if processid:
        # This is the parent process 
        # Closes file descriptor w
        os.close(w)
        r = os.fdopen(r)
        app.dprint("Parent reading")
        s = r.read()
        app.dprint("text =", s)
        #sys.exit(0)
    else:
        # This is the child process
        os.close(r)
        w = os.fdopen(w, 'w')
        print "Child writing"
        w.write("Text written by child...")
        w.close()
        print "Child closing"
        #sys.exit(0)
        
def test(app):
    import os
    import subprocess
    import sys
    
    sdcc = subprocess.Popen("/usr/bin/sdcc", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    os.close(sys.stderr.fileno())
    os.dup2(sdcc.stdin.fileno(), sys.stderr.fileno())
    #pingPopen = subprocess.Popen(args='ping -c4 www.google.cn', shell=True, stdout=subprocess.PIPE)
    print "*****", sdcc.stdout.readline() 
    
def test2():
    import os, sys
    r, w = os.pipe()
    os.close(sys.stderr.fileno())
    os.dup2(w, sys.stderr.fileno()) 
    
def read_file(path):
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content