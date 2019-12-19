# coding:utf-8
# 2019/12/3.9:40

import os
from MyQR import myqr
from PIL import Image
from random import uniform
import numpy as np
import pandas as pd
# 导入图书处理相关函数以其它类
from src.my_library import *
from src.hide_to_tray import *
from src.transparent_text import *
from src.intro_wxpython import *

# BookSpider GUI 主界面类
class BookFrame(wx.Frame):
    # 初始化
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, size=(990, 600),
                          # 禁止最大化 （wx.DEFAULT_FRAME_STYLE - wx.MAXIMIZE_BOX）
                          # style = wx.MINIMIZE_BOX| wx.RESIZE_BORDER| wx.SYSTEM_MENU| wx.CAPTION| wx.CLOSE_BOX| wx.CLIP_CHILDREN
                          )
        # 最小化托盘实例
        self.taskBarIcon = TaskBarIcon(self)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_ICONIZE, self.onHide)

        # 添加窗口小图标
        icon = wx.Icon(name="ecour/spider/images/spider.ico", type=wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        # 创建状态栏（窗口底部）
        self.CreateStatusBar()
        # 创建菜单栏
        menuBar = wx.MenuBar()
        # 创建菜单
        filemenu = wx.Menu()
        # 将菜单添加到菜单栏中
        menuBar.Append(filemenu, "File")
        # 发现只有MenuItem项SetBitmap才有效，helpString为状态栏显示帮助信息
        menuRefresh = wx.MenuItem(filemenu, 99, text="&Flush\tF5", helpString="刷新", kind=wx.ITEM_NORMAL)
        menuRefresh.SetBitmap(wx.Bitmap("ecour/spider/images/flush.png"))
        self.Bind(wx.EVT_MENU, self.refresh, menuRefresh)
        filemenu.Append(menuRefresh)
        # 添加数据图菜单
        plotMenu = wx.Menu()
        lineItem = wx.MenuItem(plotMenu, 100, text="&折线图\tF1", helpString="生成折线图，要求至少存在两条数据", kind=wx.ITEM_NORMAL)
        barItem = wx.MenuItem(plotMenu, 101, text="&柱状图\tF2", helpString="生成柱状图，要求至少存在两条数据", kind=wx.ITEM_NORMAL)
        pieItem = wx.MenuItem(plotMenu, 102, text="&饼状图\tF3", helpString="生成饼状图，要求至少存在两条数据", kind=wx.ITEM_NORMAL)
        levelItem = wx.MenuItem(plotMenu, 103, text="&水平图\tF4", helpString="生成水平柱状图，要求至少存在两条数据", kind=wx.ITEM_NORMAL)
        # 设置小图标
        lineItem.SetBitmap(wx.Bitmap("ecour/spider/images/line.png"))
        barItem.SetBitmap(wx.Bitmap("ecour/spider/images/bar.png"))
        pieItem.SetBitmap(wx.Bitmap("ecour/spider/images/pie.png"))
        levelItem.SetBitmap(wx.Bitmap("ecour/spider/images/barh.png"))
        plotMenu.Append(lineItem)
        plotMenu.Append(barItem)
        plotMenu.Append(pieItem)
        plotMenu.Append(levelItem)
        self.Bind(wx.EVT_MENU, self.show_lineChart, lineItem)
        self.Bind(wx.EVT_MENU, self.show_barChart, barItem)
        self.Bind(wx.EVT_MENU, self.show_pieChart, pieItem)
        self.Bind(wx.EVT_MENU, self.show_barhChart, levelItem)
        filemenu.Append(wx.ID_ANY, "Plot", plotMenu)
        # 添加分割线
        filemenu.AppendSeparator()
        # 添加背景样式菜单
        styleMenu = wx.Menu()
        # 使用循环添加菜单的方式，并且结合lambda传递参数
        styleList = ["背景一", "背景二", "背景三", "背景四"]
        for i, str in enumerate(styleList):
            styleItem = wx.MenuItem(styleMenu, 200 + i, text="&{}\tCtrl+{}".format(str, i + 1), kind=wx.ITEM_NORMAL)
            styleItem.SetBitmap(wx.Bitmap("ecour/spider/images/style{}.png".format(i)))
            self.Bind(wx.EVT_MENU, lambda e, mark = i : self.chooseBG(e, mark), styleItem)
            styleMenu.Append(styleItem)
        # 普通方式添加菜单，不能传参数
        # oneStyle = wx.MenuItem(styleMenu, 200, text="背景一", kind=wx.ITEM_NORMAL)
        # twoStyle = wx.MenuItem(styleMenu, 201, text="背景二", kind=wx.ITEM_NORMAL)
        # threeStyle = wx.MenuItem(styleMenu, 202, text="背景三", kind=wx.ITEM_NORMAL)
        # fourStyle = wx.MenuItem(styleMenu, 203, text="背景四", kind=wx.ITEM_NORMAL)
        # self.Bind(wx.EVT_MENU, self.chooseBG, oneStyle)
        # self.Bind(wx.EVT_MENU, self.chooseBG, twoStyle)
        # self.Bind(wx.EVT_MENU, self.chooseBG, threeStyle)
        # self.Bind(wx.EVT_MENU, self.chooseBG, fourStyle)
        # styleMenu.Append(oneStyle)
        # styleMenu.Append(twoStyle)
        # styleMenu.Append(threeStyle)
        # styleMenu.Append(fourStyle)
        filemenu.Append(wx.ID_ANY, "Style", styleMenu)
        filemenu.AppendSeparator()
        # 添加菜单项 & 表示热键
        menuQuit = wx.MenuItem(filemenu, 300, text="&Quit\tCtrl+Q", helpString="退出", kind=wx.ITEM_NORMAL)
        menuQuit.SetBitmap(wx.Bitmap("ecour/spider/images/exit.png"))
        self.Bind(wx.EVT_MENU, self.onQuit, menuQuit)
        filemenu.Append(menuQuit)
        # 添加帮助 help 菜单
        menuHelp = wx.Menu()
        menuBar.Append(menuHelp, "&Help")
        helpItem = wx.MenuItem(menuHelp, 301, text="Help", helpString="帮助手册", kind=wx.ITEM_NORMAL)
        helpItem.SetBitmap(wx.Bitmap("ecour/spider/images/help.png"))
        menuHelp.Append(helpItem)
        menuHelp.AppendSeparator()
        downItem = wx.MenuItem(menuHelp, 302, text="Down", helpString="扫码下载", kind=wx.ITEM_NORMAL)
        downItem.SetBitmap(wx.Bitmap("ecour/spider/images/down.png"))
        menuHelp.Append(downItem)
        menuHelp.AppendSeparator()
        # aboutItem = menuHelp.Append(wx.ID_ANY, "About", "关于")
        aboutItem = wx.MenuItem(menuHelp, 303, text="About", helpString="关于我", kind=wx.ITEM_NORMAL)
        aboutItem.SetBitmap(wx.Bitmap("ecour/spider/images/about.png"))
        menuHelp.Append(aboutItem)
        # 为help子菜单绑定事件
        self.Bind(wx.EVT_MENU, self.askForHelp, helpItem)
        self.Bind(wx.EVT_MENU, self.toDownload, downItem)
        self.Bind(wx.EVT_MENU, self.inRegardTo, aboutItem)
        self.SetMenuBar(menuBar)
        # 创建面板
        self.panel = wx.Panel(self)
        # 设置背景图片
        # self.panel.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBack())
        # 设置透明度
        self.SetTransparent(255)
        bookSizer = wx.BoxSizer(wx.HORIZONTAL)
        labelText = TransparentText(self.panel, label="书名:")
        # sizer.Add(组件，比例，对齐标志，边框)
        bookSizer.Add(labelText, 0, wx.ALIGN_BOTTOM)
        bookSizer.Add((10, 10))
        self.bookText = wx.TextCtrl(self.panel, value="", style=wx.TE_PROCESS_ENTER, size=(200,24))
        self.Bind(wx.EVT_TEXT_ENTER, self.onTextSubmitted, self.bookText)
        bookSizer.Add(self.bookText, 0, wx.ALIGN_BOTTOM)
        bookSizer.Add((10, 10))
        btn_search = wx.Button(self.panel, -1, "查找", size=(60, 25))
        self.Bind(wx.EVT_BUTTON, self.onSearch, btn_search)
        bookSizer.Add(btn_search)

        self.list = wx.ListCtrl(self.panel, wx.NewId(), style=wx.LC_REPORT)
        self.createHeader()
        # 设置列表项默认值
        self.defaultItem()
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick, self.list)

        # 按钮：上一页和下一页
        ctrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonLastPage = wx.Button(self.panel, -1, "上一页", size=(60, 25))
        self.Bind(wx.EVT_BUTTON, self.onLastPage, buttonLastPage)
        ctrlSizer.Add(buttonLastPage, 1)
        buttonNextPage = wx.Button(self.panel, -1, "下一页", size=(60, 25))
        self.Bind(wx.EVT_BUTTON, self.onNextPage, buttonNextPage)
        ctrlSizer.Add(buttonNextPage, 1, wx.LEFT | wx.BOTTOM)
        # 静态文本：总页数
        self.labelPages = TransparentText(self.panel, label="共{}页".format(chr(12288)))
        ctrlSizer.Add((200, 0))
        ctrlSizer.Add(self.labelPages, 0, wx.ALIGN_RIGHT)
        ctrlSizer.Add((20, 0))
        # 文本控件：显示当前页码
        self.pageGo =  wx.TextCtrl(self.panel, -1, value="", style=wx.TE_PROCESS_ENTER, size=(30,20), pos=(0,0))
        self.Bind(wx.EVT_TEXT_ENTER, self.actionPageGo, self.pageGo)
        ctrlSizer.Add(self.pageGo, 0, 0)
        # 按钮控件，跳转页码
        buttonPageGo = wx.Button(self.panel, -1, "GO", size=(24, 20))
        self.Bind(wx.EVT_BUTTON, self.actionPageGo, buttonPageGo)
        ctrlSizer.Add((10, 0))
        ctrlSizer.Add(buttonPageGo, 0, 0)

        # BoxSizer垂直布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(bookSizer, 0, wx.ALL, 5)
        sizer.Add(self.list, -1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(ctrlSizer, 0, wx.ALIGN_BOTTOM)
        self.panel.SetSizerAndFit(sizer)
        self.panel.Bind(wx.EVT_ERASE_BACKGROUND, lambda e, style = "ecour/spider/images/1.jpg" : self.onEraseBack(e, style))

    # 创建表头
    def createHeader(self):
        self.list.InsertColumn(0, "序号", width=40)
        self.list.InsertColumn(1, "书名", width=200)
        self.list.InsertColumn(2, "索书号", width=100)
        self.list.InsertColumn(3, "作者", width=262)
        self.list.InsertColumn(4, "出版信息", width=198)
        self.list.InsertColumn(5, "馆藏复本", width=wx.LIST_AUTOSIZE, format=wx.LIST_FORMAT_CENTER)
        self.list.InsertColumn(6, "可借复本", width=wx.LIST_AUTOSIZE, format=wx.LIST_FORMAT_CENTER)

    # 生成列表
    def setData(self, data):
        self.list.ClearAll()
        self.createHeader()
        pos = 0
        for row in data:
            # 插入一个item，参数一为位置，参数二位内容，默认只有一列，后续通过SetItem继续添加列
            pos = self.list.InsertItem(pos + 1, row[0])    # 序号
            self.list.SetItem(pos, 1, row[1])              # 书名
            self.list.SetItem(pos, 2, row[2])              # 书号
            self.list.SetItem(pos, 3, row[3])              # 作者
            self.list.SetItem(pos, 4, row[4])              # 出版信息
            self.list.SetItem(pos, 5, row[5], wx.CENTER)   # 馆藏复本
            self.list.SetItem(pos, 6, row[6], wx.CENTER)   # 可借复本
            # 设置列宽,-1表示自适应
            # self.list.SetColumnWidth(2, 100)
            # self.list.SetColumnWidth(3, -1)
            # self.list.SetColumnWidth(4, -1)
            # 设置奇数行高亮显示
            if pos % 2 == 0:
                self.list.SetItemBackgroundColour(pos, (134, 225, 249))

    # 帮助信息
    def askForHelp(self, event):
        title = "*:ஐ٩(๑´ᵕ`)۶ஐ:* 学习使我进步(✪ω✪)\n\n"
        ps = "☆本程序使用的API支持模糊查询，按书名、作者查询☆\n\n"
        search = "查找功能：输入书名或作者，按下回车键或点击查找按钮\n\n"
        plot = "绘图功能：搜索后，点击File菜单--》Plot--》选择生成数据图\n\n"
        cloud = "词云显示：搜索后，双击列表某一行弹出图书简介界面，点击File--》生成词云\n\n"
        style = "更换背景：点击File菜单--》Style--》选择背景图片，双击任务栏中本程序即可显示\n\n"
        tips = "补充说明：绘图功能默认显示列表中至少存在两条数据，词云显示要求图书简介至少100字\n\n"
        str = title + ps + search + plot + cloud + style + tips
        wx.MessageDialog(None, str, "Help", wx.OK | wx.ICON_EXCLAMATION).ShowModal()

    # 下载地址
    def toDownload(self, event):
        # 判断是否存在二维码背景图，不存在则设为空
        picture = os.getcwd() + "/ecour/spider/images/raw.jpg"
        print(picture)
        if not os.path.exists("ecour/spider/images/raw.jpg"):
            picture = ""
        # 如果该二维码不存在则重新生成
        if not os.path.exists("ecour/spider/images/qrcode.png"):
            if not os.path.exists(os.getcwd() + "/ecour/spider/images"):
                os.makedirs(os.getcwd() + "/ecour/spider/images")
            myqr.run(words="https://github.com/Ion-wu/BookSpider",
                    version=10,                 # 版本控制边长，1-40，正比
                    level='H',                  # 纠错等级，低到高：L、M、Q、H
                    picture=picture,            # 文件放在同目录下（源文件）
                    colorized=True,             # True 为彩色
                    contrast=1.0,               # 对比度
                    brightness=1.0,             # 亮度
                    save_name="qrcode.png",     # 存储文件命名，格式可以是JPG、PNG、BMP、GIF
                    save_dir=os.getcwd() + "/ecour/spider/images")  # 存储路径
        img = Image.open("ecour/spider/images/qrcode.png")
        plt.figure("Down")
        plt.title("github")
        plt.axis(False)
        plt.imshow(img)
        plt.show()

    # About信息
    def inRegardTo(self, event):
        title = "（づ￣3￣）づ╭❤～好好学习天天向上ლ(╹ε╹ლ)\n\n"
        name = "Name：Bookworm\n\n"
        version = "Version：2.4\n\n"
        description = "Mission：Access all the book information in the school library!\n\n"
        copyright = "Time：© 2019.12\n\n"
        author = "Author：Wuzengyu\n\n"
        website = "Download：https://github.com/Ion-wu/BookSpider\n\n"
        str = title + name + version + copyright + author + website + description
        wx.MessageDialog(None, str, "About", wx.OK | wx.ICON_EXCLAMATION).ShowModal()

    # 按F5进入坦克
    def refresh(self, event):
        self.onSearch(event)

    # 清空DataFrame
    def clearDF(self):
        global df
        if not df.empty:
            df.drop(df.index, inplace=True)

    # 处理绘制图形所需的数据
    def plotData(self):
        global df
        # 获取指定每一行的指定列数据
        count = self.list.GetItemCount()
        if count > 1:
            for row in range(count):
                item = self.list.GetItemText(row, col=0)
                total = self.list.GetItemText(row, col=5)
                vacant = self.list.GetItemText(row, col=6)
                df = df.append(pd.DataFrame({"序号": [item], "馆藏复本": [total], "可借复本": [vacant]}))
            itemArr = np.array(df["序号"])
            totalArr = np.array(df["馆藏复本"])
            vacantArr = np.array(df["可借复本"])
            xdata = itemArr.tolist()
            ydata1 = totalArr.tolist()
            ydata2 = vacantArr.tolist()
            return xdata, ydata1, ydata2

    # 生成折线图
    def show_lineChart(self, event):
        # 声明全局变量，并清空数据以便复用
        global df
        self.clearDF()
        count = self.list.GetItemCount()
        if count > 1:
            xdata, ydata1, ydata2 = self.plotData()
            # 指定折线颜色， 线宽和样式
            plt.figure("折线图")
            plt.plot(xdata, ydata1, label="馆藏复本")
            plt.plot(xdata, ydata2, label="可借复本")
            plt.legend(loc="best")
            plt.xlabel("序号")
            plt.ylabel("数量")
            plt.title("馆藏复本与可借复本对比")
            plt.grid(True)
            plt.show()
            df.drop(df.index, inplace=True)

    # 显示条状图
    def show_barChart(self, event):
        global df
        self.clearDF()
        count = self.list.GetItemCount()
        if count > 1:
            xdata, ydata1, ydata2 = self.plotData()
            bar_width = 0.1
            plt.figure("柱状图")
            plt.grid(True)
            plt.bar(x=range(len(xdata)), height=ydata1, label="馆藏复本", alpha=0.8, width=bar_width)
            plt.bar(x=np.arange(len(xdata)) + bar_width + 0.05, height=ydata2, label="可借复本", alpha=0.8, width=bar_width)
            # 在柱状图上显示具体的值
            # for x, y in enumerate(ydata1):
            #     plt.text(int(x), int(y), "%s" % y, ha="center", va="bottom")
            # for x, y in enumerate(ydata2):
            #     plt.text(int(x) + bar_width, int(y), "%s" % y, ha="center", va="top")
            plt.xlabel("序号")
            plt.ylabel("数量")
            plt.legend(loc="best")
            plt.title("馆藏复本与可借复本对比")
            plt.show()
            df.drop(df.index, inplace=True)

    # 生成饼状图
    def show_pieChart(self, event):
        global df
        self.clearDF()
        count = self.list.GetItemCount()
        if count > 1:
            labels, ydata1, ydata2 = self.plotData()
            data = np.divide(list(map(int, ydata2)), list(map(int, ydata1)))
            # 凸显一部分数据
            explode = []
            # 随机生成0-1之间的小数且长度等于当前列表长度
            for row in range(count):
                explode.append(uniform(0.0, 0.3))
            # 使用自定义颜色
            colors = ["cornflowerblue", "orange", "limegreen", "gold", "teal", "lightcoral", "sandybrown"]
            plt.figure("饼图")
            # 将横、纵坐标轴标准化处理,保证饼图是一个圆,否则为椭圆
            plt.axes(aspect="equal")
            # 控制X轴和Y轴的范围(用于控制饼图的圆心、半径)
            plt.xlim(0, 8)
            plt.ylim(0, 8)
            # 绘制饼图
            plt.pie(x=data,  # 绘图数据
                    labels=labels,  # 添加编程语言标签
                    explode=explode,  # 突出显示Python
                    colors=colors,  # 设置饼图的自定义填充色
                    autopct="%.3f%%",  # 设置百分比的格式,此处保留3位小数
                    pctdistance=0.8,  # 设置百分比标签与圆心的距离
                    labeldistance=1.15,  # 设置标签与圆心的距离
                    startangle=180,  # 设置饼图的初始角度
                    center=(4, 4),  # 设置饼图的圆心(相当于X轴和Y轴的范围)
                    radius=3.8,  # 设置饼图的半径(相当于X轴和Y轴的范围)
                    counterclock=False,  # 是否为逆时针方向,设置为顺时针
                    wedgeprops={"linewidth": 1},  # 设置饼图内外边界的属性值
                    shadow=True,
                    textprops={"fontsize": 12, "color": "w"},  # 设置文本属性
                    frame=1)  # 是否显示饼图的圆圈, 设置为显示
            # 不显示X轴和Y轴的刻度值
            plt.xticks(())
            plt.yticks(())
            """
                显示图例
            """
            plt.legend(loc=[1, 0], prop={"size": 8}, shadow=True)

            """
                去掉四周的边框
            """
            ax = plt.gca()
            ax.spines["top"].set_color("none")
            ax.spines["right"].set_color("none")
            ax.spines["bottom"].set_color("none")
            ax.spines["left"].set_color("none")

            """
                修改X轴和Y轴的位置
            """
            # ax.spines["bottom"].set_position(("data", 4))
            # ax.spines["left"].set_position(("data", 0))

            # 添加饼图标题
            plt.title("可借复本与馆藏复本的对比")
            # 显示图形
            plt.show()

    # 生成水平柱状图
    def show_barhChart(self, event):
        global df
        self.clearDF()
        count = self.list.GetItemCount()
        if count > 1:
            xdata, ydata1, ydata2 = self.plotData()
            bar_width = 0.3
            plt.figure("水平柱状图")
            plt.grid(True)
            # Y轴数据使用range(len(x_data)), 就是0,1,2
            plt.barh(y=range(len(xdata)), width=ydata1, label="馆藏复本",
                     color="steelblue", alpha=0.8, height=bar_width)
            # Y轴数据使用np.arange(len(x_data))+bar_width
            # 就是bar_width, 1+bar_width, 2+bar_width...,这样就和第一个柱状图并列了
            plt.barh(y=np.arange(len(xdata)) + bar_width + 0.05, width=ydata2,
                     label="可借复本", color="indianred", alpha=0.8, height=bar_width)

            # 在柱状图上显示具体的数值, ha参数控制水平格式对齐方式, va参数控制垂直对齐方式
            # for y, x in enumerate(ydata1):
            #     plt.text(int(x) + 5000, y - bar_width / 2, "%s" % x, ha="center", va="bottom")
            # for y, x in enumerate(ydata2):
            #     plt.text(int(x) + 5000, y + bar_width / 2, "%s" % x, ha="center", va="bottom")
            # 为Y轴设置刻度值
            plt.yticks(np.arange(len(xdata)) + bar_width / 2, xdata)
            # 设置标题
            plt.title("馆藏复本与可借复本对比")
            # 为两个坐标轴设置名称
            plt.xlabel("数量")
            plt.ylabel("序号")
            # 显示图例
            plt.legend()
            plt.show()

    # 选择背景图片
    def chooseBG(self, event, mark):
        style = ""
        if mark == 0:
            style = "ecour/spider/images/1.jpg"
        elif mark == 1:
            style = "ecour/spider/images/3.jpg"
        elif mark == 2:
            style = "ecour/spider/images/5.jpg"
        elif mark == 3:
            style = "ecour/spider/images/6.jpg"
        self.setBG(style)

    # 定义背景图片
    def setBG(self, mark):
        self.panel.Bind(wx.EVT_ERASE_BACKGROUND, lambda e, style = mark : self.onEraseBack(e, style))

    # 显示总页数
    def showPages(self):
        try:
            key = self.process_key()
            pages = getPages(key)
            # if issubclass(type(pages), bs4.element.NavigableString):
            if issubclass(type(pages), int):
                # 显示总页数时清空原内容，否则叠加导致背景不透明
                self.labelPages.SetLabel("")
                self.labelPages.SetLabelText("共{}页".format(pages))
            else:
                self.labelPages.SetLabel("")
                self.labelPages.SetLabelText("共{}页".format(chr(12288)))
                pages = 0
            global totalPages
            totalPages = pages
            return pages
        except:
            pass

    # 显示当前页码
    def showCurrentPage(self):
        self.pageGo.SetLabelText(str(page))

    # 页面跳转
    def actionPageGo(self, event):
        try:
            global page
            pageGo = int(self.pageGo.GetValue())
            pages = totalPages
            # print("调用了跳转函数：pages={}，类型为：{}".format(pages, type(pages)))
            if page == pageGo:
                pass
            else:
                if pageGo > 0 and pageGo <= pages:
                    page = pageGo
                    thread.start_new_thread(self.retrieve_books, (pageGo,))
                else:
                    wx.MessageBox("超出页码范围！", "警告", wx.OK | wx.ICON_EXCLAMATION)
        except:
            print(pageGo)
            print(type(pageGo))
            print("页面跳转异常")

    # 搜索框回车
    def onTextSubmitted(self, event):
        # 调用onSearch方法，默认显示第一页
        self.onSearch(event)

    # 列表双击/回车（显示图书简介信息）
    # EVT_LIST_ITEM_ACTIVATED 表示 item 已被激活（回车）或双击
    def onDoubleClick(self, event):
        url_code = getUrl_introduction(self.process_key(), page, event.GetIndex())
        # 获取指定列数指定行数的Item内容(GetIndex获取行数，第二个参数获取列数，下标均从0开始)
        name = self.list.GetItemText(event.GetIndex(), 1)
        if isinstance(url_code, str):
            intro = retrieve_book_introduction(url_code)
            intro.append(name)
            # 方式一：使用消息框弹出（界面不好看）
            # wx.MessageBox("{}\r\r{}\r\r{}".format(intro[0], intro[1], intro[2]), "简介", wx.OK | wx.ICON_INFORMATION)
            # 方式二：弹出新窗口
            IntroFrame(None, title="图书简介", intro=intro)

    # 爬取上一页图书信息
    def onLastPage(self, event):
        global page
        if page > 1:
            page -= 1
            # self.retrieve_books(page)
            self.showCurrentPage()
            thread.start_new_thread(self.retrieve_books, (page,))
        else:
            wx.MessageBox("已经是第一页！", "信息", wx.OK | wx.ICON_EXCLAMATION)

    # 爬取下一页图书信息
    def onNextPage(self, event):
        global page
        page += 1
        key = self.process_key()
        try:
            totalPage = getPages(key)
            if page <= int(totalPage):
                self.showCurrentPage()
                thread.start_new_thread(self.retrieve_books, (page,))
            else:
                page = int(totalPage)
                wx.MessageBox("已经是最后一页！", "信息", wx.OK | wx.ICON_EXCLAMATION)
        except TypeError as err:
            print(err)

    # 最小化时隐藏任务栏图标
    def onHide(self, event):
        self.Hide()
        event.Skip()

    # 单击框架退出按钮时
    def onClose(self, event):
        # 只有为 wx.EVT_CLOSE绑定了事件才需要Destroy()方法，其它情况用Close()，此处必须使用Destroy()
        # print("退出按钮--》调用了：self.taskBarIcon.Destroy()  self.Destroy()")
        self.taskBarIcon.Destroy()
        self.Destroy()

    # Ctrl+Q 退出程序
    def onQuit(self, event):
        self.Close()

    # 开启新线程执行retrieve_book方法
    def onSearch(self, event):
        # 每次搜索默认显示第一页
        global page
        page = 1
        thread.start_new_thread(self.retrieve_books, ())
        pages = self.showPages()
        try:
            if int(pages) != 0:
                self.showCurrentPage()
            else:
                self.pageGo.SetLabelText("")
                self.resetView()
        except TypeError as err:
            print("错误信息：", err)
            print("总页数：{}，当前：{}".format(pages, page))

    # 数据获取
    def retrieve_books(self, page=1):
        key = self.process_key()
        # 关键词不为空才执行查询，为空则弹出信息框
        if key != "":
            data = main(key, page)
            if data:
                self.setData(data)
            else:
                wx.MessageBox("没有查到任何数据！", "提示", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("请输入需要查询的关键词！", "信息", wx.OK | wx.ICON_EXCLAMATION)

    # 关键词处理 # -> %23(C#)
    def process_key(self):
        key = self.bookText.GetValue()
        for i in key:
            if i == "#":
                new = re.sub("#", "%23", key)
            elif i == "+":
                new = re.sub("\+", "%2B", key)
            else:
                new = key
        return new

    # 搜索为空时重置列表
    def resetView(self):
        self.list.ClearAll()
        self.createHeader()
        self.defaultItem()

    # 默认加载项
    def defaultItem(self):
        pos = self.list.InsertItem(0, "--")
        self.list.SetItem(pos, 1, "loading...")
        self.list.SetItem(pos, 2, "--")

    # 设置背景图片
    def onEraseBack(self, event, style):
        dc = event.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap(style)
        dc.DrawBitmap(bmp, 0, 0)


if __name__ == "__main__":
    page = 1         # 控制变量
    totalPages = 0   # 总页数控制变量
    # 用于存放绘图数据
    df = pd.DataFrame(columns= ["序号", "馆藏复本", "可借复本"])
    # False表示不将stdout和stderr重定向到一个窗口
    app = wx.App(False)
    creat_splash()
    top = BookFrame("Bookworm")
    top.SetMaxSize((990, 600))
    top.SetMinSize((990, 600))
    top.Centre()
    top.Show(True)
    app.MainLoop()