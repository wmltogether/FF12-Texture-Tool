#coding=utf-8
import wx
import wx._gdi
import codecs
from StringIO import StringIO
import struct
import os
from PIL import Image,ImageColor
from texture_dump import atest,btest,ctest,dtest,etest

class wxFont(wx.Frame):
    def _export_texture(self):
        print(u'读取目录为：iso')
        print(u'输出目录为：png')
        atest()
    def _import_texture(self):
        btest()
    def _import_texture_withtm2(self):
        ctest()   
    def _export_texture_tm2(self):
        dtest()
    def _import_texture_tm2(self):
        etest()
    def OnClick_eximg(self, event):
        self._export_texture()
        self.button.SetLabel(u"重新导出图片")
        dlg0=wx.MessageDialog(None,u"图片扫描完毕!",u"FF12 texture tool",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()
    def OnClick_inimg(self, event):
        self._import_texture()
        self.button2.SetLabel(u"重新导入图片")
        dlg0=wx.MessageDialog(None,u"图片导入完毕!",u"FF12 texture tool",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()
    def OnClick_withtm2(self, event):
        self._import_texture_withtm2()
        dlg0=wx.MessageDialog(None,u"图片导入完毕!",u"FF12 texture tool",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()
    def OnClick_extm2(self, event):
        self._export_texture_tm2()
        dlg0=wx.MessageDialog(None,u"图片导出完毕!",u"FF12 texture tool",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()
    def OnClick_imtm2(self, event):
        self._import_texture_tm2()
        dlg0=wx.MessageDialog(None,u"图片导入完毕!",u"FF12 texture tool",wx.OK)
        r=dlg0.ShowModal()
        dlg0.Destroy()  
    def __init__(self, parent, title = u"FF12 texture tool"):
        wx.Frame.__init__(self, parent, -1, title,pos=(150, 150), size=(500, 360))
        panel = wx.Panel(self, -1)
        self.button = wx.Button(panel, -1, u"导出EFX图片", pos=(50, 20))
        wx.StaticText(panel,-1,u"从ISO目录导出材质到PNG",(200,20))
        self.button2 = wx.Button(panel, -1, u"导入EFX图片", pos=(50, 80))
        wx.StaticText(panel,-1,u"从CNPNG目录导入材质到IMG",(200,80))
        self.button3 = wx.Button(panel, -1, u"强制根据tm2\n导入色盘和数据", pos=(50, 140))
        wx.StaticText(panel,-1,u"强制根据cntm2的数据生成EFX图片",(200,140))
        self.button4 = wx.Button(panel, -1, u"导出tim2", pos=(50, 200))
        wx.StaticText(panel,-1,u"尝试抽取tim2图片",(200,200))
        self.button5 = wx.Button(panel, -1, u"导入tim2", pos=(50, 260))
        wx.StaticText(panel,-1,u"尝试导入tim2图片",(200,260))    
        height=32
        weight=wx.NORMAL
        fontName="MS Gothic"
        font=wx.Font(height*0.75, wx.SWISS , wx.NORMAL, weight, faceName=fontName)
        self.Bind(wx.EVT_BUTTON, self.OnClick_eximg,self.button)
        self.Bind(wx.EVT_BUTTON, self.OnClick_inimg,self.button2)
        self.Bind(wx.EVT_BUTTON, self.OnClick_withtm2,self.button3)
        self.Bind(wx.EVT_BUTTON, self.OnClick_extm2,self.button4)
        self.Bind(wx.EVT_BUTTON, self.OnClick_imtm2,self.button5)
        self.button.SetDefault()
        self.button2.SetDefault()
        self.button3.SetDefault()    
        self.Show()
        #wx.Exit()

        
if __name__ == '__main__':
    app = wx.App(redirect=True)
    wxFont(None)
    app.MainLoop()
