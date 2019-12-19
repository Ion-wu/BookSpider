# coding:utf-8
# 2019/12/12.18:07

import wx, jieba
import wordcloud
import matplotlib.pyplot as plt

# 简介信息界面类，使用FlexiGridSizer布局
class IntroFrame(wx.Frame):
    def __init__(self, parent, title, intro):
        super(IntroFrame, self).__init__(parent, title=title, size=(460, 300))
        # 添加窗口图标
        ico = wx.Icon(name="ecour/spider/images/spider.ico", type=wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.initUI(intro)
        self.Centre()               # 设置居中显示
        self.SetTransparent(255)    # 透明度设置
        self.SetMinSize((460, 300))
        self.SetMaxSize((560, 360))
        self.Show()

    def initUI(self, intro):
        # 创建菜单条和菜单
        self.CreateStatusBar()
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        menuBar.Append(fileMenu, "&File")
        # 词语菜单项
        # menuCloud = fileMenu.Append(100, "wordCloud", "生成词云") # 无法添加图标，改成下面形式
        cloudmenu = wx.MenuItem(fileMenu, 100, text="&词云\tCtrl+W", helpString="生成词云，最低要求【提要文摘附注】100字或以上", kind=wx.ITEM_NORMAL)
        cloudmenu.SetBitmap(wx.Bitmap("ecour/spider/images/cloud.png"))
        fileMenu.Append(cloudmenu)
        # 使用lambda表达式传递参数，解决event的问题
        self.Bind(wx.EVT_MENU, lambda e, info = intro : self.showCloud(e, info))
        # self.Bind(wx.EVT_MENU, self.showCloud, menuCloud)     # 这样子无法传参数
        # 退出菜单项
        exitmenu = wx.MenuItem(fileMenu, 101, text="&退出\tCtrl+Q", helpString="退出简介信息界面", kind=wx.ITEM_NORMAL)
        exitmenu.SetBitmap(wx.Bitmap("ecour/spider/images/exit.png"))
        self.Bind(wx.EVT_MENU, self.onQuit, exitmenu)
        fileMenu.Append(exitmenu)
        self.SetMenuBar(menuBar)
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour((255, 255, 255))
        # 设置背景图片
        self.panel.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBack)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        # Wx.FlexiGridSizer(rows, cols, vgap, hgap)
        fgs = wx.FlexGridSizer(4, 2, 10, 10)
        name = wx.StaticText(self.panel, label="题名：")
        title = wx.StaticText(self.panel, label="学科主题:")
        type = wx.StaticText(self.panel, label="载体形态项:")
        tips = wx.StaticText(self.panel, label="提要文摘附注:")
        # 设置StaticText的背景色
        # name.SetBackgroundColour((134, 255, 249))
        # title.SetBackgroundColour((134, 255, 249))
        # type.SetBackgroundColour((134, 255, 249))
        # tips.SetBackgroundColour((134, 255, 249))
        # 设为只读状态
        tc0 = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        tc1 = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        tc2 = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        tc3 = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        # 设置文本值
        tc0.SetLabelText(intro[3])
        tc1.SetLabelText(intro[0])
        tc2.SetLabelText(intro[1])
        tc3.SetLabelText(intro[2])
        # 设置背景
        tc0.SetBackgroundColour((255, 225, 249))
        tc1.SetBackgroundColour((255, 225, 249))
        tc2.SetBackgroundColour((255, 225, 249))
        tc3.SetBackgroundColour((255, 225, 249))
        fgs.AddMany([(name), (tc0, 1, wx.EXPAND),
                     (title), (tc1, 1, wx.EXPAND),
                     (type), (tc2, 1, wx.EXPAND),
                     (tips), (tc3, 1, wx.EXPAND)])
        # 指定索引的行增长，为第四行
        fgs.AddGrowableRow(3, 1)
        # 指定索引的列增长，为第二列
        fgs.AddGrowableCol(1, 1)
        hbox.Add(fgs, proportion=2, flag=wx.ALL | wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)

    # 生成词云显示
    def showCloud(self, event, info):
        if len(info[2]) > 100:
            ls = jieba.lcut(info[2])
            txt = " ".join(ls)
            w = wordcloud.WordCloud(margin=2, scale=4, font_path="msyh.ttf", height=400, width=800, background_color="white")
            cloud = w.generate(txt)
            # 展示词云图
            plt.figure("词云")
            plt.title("{}--简介\n".format(info[3]))
            plt.imshow(cloud)
            plt.axis("off")
            plt.show()
        else:
            wx.MessageBox("内容过于简短，无法生成词云！", "Tips", wx.OK | wx.ICON_EXCLAMATION)

    # 设置背景图片
    def onEraseBack(self, event):
        dc = event.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("ecour/spider/images/grid.png")
        dc.DrawBitmap(bmp, 0, 0)

    def onQuit(self, event):
        self.Close()

