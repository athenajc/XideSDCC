import wx
import random

from sim_scope import *

#----------------------------------------------------------------------------------
class TestSim():
    def __init__(self):
        self.pin_logs = {}
        
        p = self.pin_logs
        for i in range(8):
            p['RB' + str(i)] = []
        #p['RB0'] = [1,2,4,8,0x10,0x20,0x40,0x80,0xff, 0x11, 0x61]
        #p['RB1'] = [0x11, 0x22, 0x33, 0x44, 0x55]
        #p['RB2'] = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        
    #---------------------------------------------------------------
    def get_pin_log(self, pin):
        log = self.pin_logs.get(pin, [])
        return log
    
    #---------------------------------------------------------------
    def step(self):
        p = self.pin_logs
        for name, lst in self.pin_logs.items():
            lst.append(random.randint(0,256))
    
#----------------------------------------------------------------------------------
class TestFrame(wx.Frame):
    def __init__(self, parent, title):
        sz = wx.GetDisplaySize() 
        w = sz.GetWidth() * 3 / 4
        h = sz.GetHeight() / 2
        x = (sz.GetWidth() - w) / 2
        y = (sz.GetHeight() - h) / 2
        wx.Frame.__init__(self, parent, title=title, size=(w, h), pos=(x, 80),
                          style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetMinSize(wx.Size(300,100))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.frame = self
        self.sim = TestSim()
        self.scope = p = TestPanel(self, self.sim)
        self.sizer.Add(p, 1, wx.EXPAND)    
        
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        
        self.timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer1Timer, self.timer1)
        self.timer1.Start(100)
        
    #-------------------------------------------------------------------
    def OnTimer1Timer(self, event):  
        self.sim.step()
        self.scope.update(self.sim)
            
#----------------------------------------------------------------------------------
class TestApp(wx.App):
    def OnInit(self):
        frame = TestFrame(None, 'Test Frame')
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

    def OnClose(self):
        print 'TestApp onclose'
        return true
        
def t(v): 
    for bit in bin(v)[2:]: 
        print bit
        
#----------------------------------------------------------------------------------
if __name__ == '__main__':
    app = TestApp(0)
    app.MainLoop()