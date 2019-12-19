# coding:utf-8
# 2019/12/6.22:13

import time
import wx.adv

# 启动界面
def creat_splash():
    # create a welcome screen
    screen = wx.Image("ecour/spider/images/biu.png").ConvertToBitmap()
    wx.adv.SplashScreen(screen, wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT, 1000, None, -1)
    time.sleep(1)

class TaskBarIcon(wx.adv.TaskBarIcon):
    ID_EXIT = wx.NewId()


    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name='ecour/spider/images/spider.ico', type=wx.BITMAP_TYPE_ICO), 'TaskBarIcon!')
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.Bind(wx.EVT_MENU, self.OnExit, id=self.ID_EXIT)


    # 双击托盘图标打开界面
    def OnTaskBarLeftDClick(self, event):
        # 如果当前框架最小化为图标则返回True，否则False
        if self.frame.IsIconized():
            # 若参数为True，最小化为图标，为False则恢复
            # print("从最小化图标中恢复窗口")
            self.frame.Iconize(False)
        # IsShown()：如果当前框架可见，则返回True
        if not self.frame.IsShown():
            # 若为True，则显示框架
            # print("显示框架")
            self.frame.Show(True)
        self.frame.Raise()


    def OnExit(self, event):
        # print("托盘类--》调用了OnExit")
        self.frame.Close(True)
        # self.RemoveIcon()

    # override
    def CreatePopupMenu(self):
        menu = wx.Menu()
        # menu.Append(self.ID_EXIT, 'Exit')
        # print("调用了弹出菜单")
        return menu

