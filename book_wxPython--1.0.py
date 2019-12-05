# coding:utf-8
# 2019/11/18.17:07

import _thread as thread
import wx, re, bs4, requests
from time import perf_counter
from bs4 import BeautifulSoup

# 网页爬取通用框架
def getHTMLText(url):
    try:
        headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"}
        r = requests.get(url, headers = headers, timeout = 30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as err:
        print(err)

# 图书信息处理
def fillBookList(bookInfo, html):
    soup = BeautifulSoup(html, "lxml")
    # 获取索书号  \xa0\xa0     TP311.561/Y143
    callno = soup.find_all(text=re.compile("\\xa0+\s*[A-Z]+"))
    titles = soup.find_all(text=re.compile("^\d+\."))
    total = soup.find_all(text=re.compile("馆藏复本"))
    freedom = soup.find_all(text=re.compile("可借复本"))
    # 使用标签提取作者和出版信息（因为出版信息格式存在问题）
    authors, press_info, bookid = [], [], []
    plist = soup.find_all("p", {"style": "margin-top:5px;"})
    for p in plist:
        if isinstance(p, bs4.element.Tag):
            authors.append(p.contents[2])
            press_info.append(p.contents[4].strip())

    for i in range(len(callno)):
        bookid.append(titles[i].split(".")[0])
        title = titles[i].split(".", 1)[1]
        bookNo = callno[i].strip()
        author = authors[i].strip()
        sum = total[i].strip().split("：")[1]
        free = freedom[i].strip().split("：")[1]
        bookInfo.append([bookid[i], title,bookNo, author, press_info[i], sum, free])

# 保存原始URL
def getRawUrl():
    url_list = [
        "http://172.16.73.134:8083/SMJS/tableResultDetail?",
        "&marc_ctype=0&SearchColunm=grp_02&match_flag=0&ltzt=0"
    ]
    return url_list

# 获取图书页数
def getPages(key):
    raw_url = getRawUrl()
    html = getHTMLText(raw_url[0] + "strText=" + key + raw_url[1])
    soup = BeautifulSoup(html, "lxml")
    # 获取路径深度
    depth = soup.find("div", {"class": "pagelist"})
    try:
        pageIndex = depth("b")[1].string
        return pageIndex
    except:
        pass

# 主函数调用
def main(key, page):
    bookInfo = []
    raw_url = getRawUrl()
    url = raw_url[0] + "PageIndex=" + str(page) + "&strText=" + key + raw_url[1]
    html = getHTMLText(url)                 # 调用获得文本函数
    fillBookList(bookInfo, html)            # 调用提取信息函数
    return bookInfo


# 获取简介信息url, 返回简介信息的url
def getUrl_introduction(key, page, i):
    raw_url = getRawUrl()
    url = raw_url[0] + "PageIndex=" + str(page) + "&strText=" + key + raw_url[1]
    try:
        if key != "":
            html = getHTMLText(url)
            soup = BeautifulSoup(html, "lxml")
            find_div = soup.find_all("a", {"target": "_blank"})
            code = find_div[i]["href"].split("/",2)[2]
        return code
    except:
        pass

# 移动端图书简介信息, 速度较快
def retrieve_book_introduction(code):
    # start = perf_counter()
    intro = []
    url = "http://172.16.73.134:8083/Mobile/"
    r = requests.get(url + code)
    soup = BeautifulSoup(r.text, "lxml")
    find_div = soup.find_all("div", {"class":"b_info"})
    for p in find_div:
        subject = p.contents[9].string
        type = p.contents[5].string
    tips = "提要文摘附注:"
    try:
        tips += soup.find("div", {"class" : "intro"}).string
    except:
        tips += "--暂无--"
    # print(perf_counter() - start)
    intro.append([subject, type, tips])
    return intro

# 电脑端图书简介信息
def getClient_book_introduction(code):
    # start = perf_counter()
    intro = []
    url = "http://172.16.73.134:8083/SJXQ/"
    html = getHTMLText(url + code)
    soup = BeautifulSoup(html, "lxml")
    find_div = soup.find_all("li", {"style":"display:block;"})
    type = find_div[3].contents[1].string
    subject = find_div[5].contents[1].string
    tips = find_div[7].contents[1].string
    # print(perf_counter()-start)
    intro.append([subject, type, tips])
    return intro

# BookSpider GUI
class BookFrame(wx.Frame):
    # 初始化
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, size=(980,624))
        # 创建状态栏（窗口底部）
        self.CreateStatusBar()
        # 创建菜单栏
        menuBar = wx.MenuBar()
        # 创建菜单
        filemenu = wx.Menu()
        # 将菜单添加到菜单栏中
        menuBar.Append(filemenu, "&File")
        # 添加菜单项
        menuQuit = filemenu.Append(wx.ID_EXIT, "&Quit", "退出")
        self.Bind(wx.EVT_MENU, self.OnQuit, menuQuit)
        self.SetMenuBar(menuBar)
        # 创建面板
        panel = wx.Panel(self)
        bookSizer = wx.BoxSizer(wx.HORIZONTAL)
        labelText = wx.StaticText(panel, label="Book Name:")
        # sizer.Add(组件，比例，对齐标志，边框)
        bookSizer.Add(labelText, 0, wx.ALIGN_BOTTOM)
        bookSizer.Add((10, 10))
        self.bookText = wx.TextCtrl(panel, value="", style=wx.TE_PROCESS_ENTER, size=(200,24))
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextSubmitted, self.bookText)
        bookSizer.Add(self.bookText, 0, wx.ALIGN_BOTTOM)
        bookSizer.Add((10, 10))
        btn_search = wx.Button(panel, -1, "search", size=(80, 25))
        self.Bind(wx.EVT_BUTTON, self.OnSearch, btn_search)
        bookSizer.Add(btn_search)

        self.list = wx.ListCtrl(panel, wx.NewId(), style=wx.LC_REPORT)
        self.createHeader()
        # 设置列表项默认值
        self.defaultItem()
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDoubleClick, self.list)

        # 按钮：上一页和下一页
        ctrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonLastPage = wx.Button(panel, -1, "上一页", size=(60,25))
        self.Bind(wx.EVT_BUTTON, self.OnLastPage, buttonLastPage)
        ctrlSizer.Add(buttonLastPage, 1)
        buttonNextPage = wx.Button(panel, -1, "下一页", size=(60,25))
        self.Bind(wx.EVT_BUTTON, self.OnNextPage, buttonNextPage)
        ctrlSizer.Add(buttonNextPage, 1, wx.LEFT | wx.BOTTOM)
        # 静态文本：总页数
        self.labelPages = wx.StaticText(panel, label="共{}页".format(chr(12288)))
        ctrlSizer.Add((200,0))
        ctrlSizer.Add(self.labelPages, 0, wx.ALIGN_RIGHT)
        ctrlSizer.Add((20,0))
        # 文本控件：显示当前页码
        self.pageGo =  wx.TextCtrl(panel, -1, value="", style=wx.TE_PROCESS_ENTER, size=(30,20), pos=(0,0))
        self.Bind(wx.EVT_TEXT_ENTER, self.ActionPageGo, self.pageGo)
        ctrlSizer.Add(self.pageGo, 0, 0)
        # 按钮控件，跳转页码
        buttonPageGo = wx.Button(panel, -1, "GO", size=(24,20))
        self.Bind(wx.EVT_BUTTON, self.ActionPageGo, buttonPageGo)
        ctrlSizer.Add((10,0))
        ctrlSizer.Add(buttonPageGo, 0, 0)

        # BoxSizer垂直布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(bookSizer, 0, wx.ALL, 5)
        sizer.Add(self.list, -1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(ctrlSizer, 0, wx.ALIGN_BOTTOM)
        panel.SetSizerAndFit(sizer)

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
            pos = self.list.InsertItem(pos + 1, row[0])
            self.list.SetItem(pos, 1, row[1])
            self.list.SetItem(pos, 2, row[2])
            self.list.SetItem(pos, 3, row[3])
            self.list.SetItem(pos, 4, row[4])
            self.list.SetItem(pos, 5, row[5], wx.CENTER)
            self.list.SetItem(pos, 6, row[6], wx.CENTER)
            # 设置列宽,-1表示自适应
            # self.list.SetColumnWidth(2, 100)
            # self.list.SetColumnWidth(3, -1)
            # self.list.SetColumnWidth(4, -1)
            # 设置奇数行高亮显示
            if pos % 2 == 0:
                self.list.SetItemBackgroundColour(pos, (134, 225, 249))

    # 显示总页数
    def ShowPages(self):
        try:
            key = self.process_key()
            pages = getPages(key)
            # print(type(pages))    # <class 'bs4.element.NavigableString'>
            if issubclass(type(pages), bs4.element.NavigableString):
                self.labelPages.SetLabelText("共{}页".format(pages))
            else:
                self.labelPages.SetLabelText("共{}页".format(chr(12288)))
                pages = 0
            return pages
        except:
            pass

    # 显示当前页码
    def ShowCurrentPage(self):
        self.pageGo.SetLabelText(str(page))

    # 页面跳转
    def ActionPageGo(self, event):
        try:
            global page
            pageGo = int(self.pageGo.GetValue())
            pages = int(self.ShowPages())
            # 控制台显示页数和类型
            # print(pages)
            # print(type(pages))
            if page == pageGo:
                pass
            else:
                if pageGo > 0 and pageGo <= pages:
                    page = pageGo
                    thread.start_new_thread(self.retrieve_books, (pageGo,))
                else:
                    wx.MessageBox("超出页码范围！", "警告", wx.OK | wx.ICON_INFORMATION)
        except:
            pass

    # 搜索框回车
    def OnTextSubmitted(self, event):
        # 调用OnSearch方法，默认显示第一页
        self.OnSearch(event)

    # 列表双击/回车（显示图书简介信息）
    # EVT_LIST_ITEM_ACTIVATED 表示 item 已被激活（回车）或双击
    def OnDoubleClick(self, event):
        url_code = getUrl_introduction(self.process_key(), page, event.GetIndex())
        if isinstance(url_code, str):
            intro = retrieve_book_introduction(url_code)
            wx.MessageBox("{}\r\r{}\r\r{}".format(intro[0][0], intro[0][1], intro[0][2]), "简介", wx.OK | wx.ICON_INFORMATION)

    # 爬取上一页图书信息
    def OnLastPage(self,event):
        global page
        if page > 1 :
            page -= 1
            # self.retrieve_books(page)
            self.ShowCurrentPage()
            thread.start_new_thread(self.retrieve_books, (page,))
        else:
            wx.MessageBox("已经是第一页！", "警告", wx.OK | wx.ICON_INFORMATION)

    # 爬取下一页图书信息
    def OnNextPage(self, event):
        global page
        page += 1
        key = self.process_key()
        try:
            totalPage = getPages(key)
            if page <= int(totalPage):
                self.ShowCurrentPage()
                thread.start_new_thread(self.retrieve_books, (page,))
            else:
                page = int(totalPage)
                wx.MessageBox("已经是最后一页！", "警告", wx.OK | wx.ICON_INFORMATION)
        except TypeError as err:
            print(err)

    # 退出程序
    def OnQuit(self, event):
        self.Close()
        self.Destroy()

    # 开启新线程执行retrieve_book方法
    def OnSearch(self, event):
        # 每次搜索默认显示第一页
        global page
        page = 1
        thread.start_new_thread(self.retrieve_books, ())
        pages = self.ShowPages()
        try:
            if int(pages) != 0:
                self.ShowCurrentPage()
            else:
                self.pageGo.SetLabelText("")
                self.resetView()
        except TypeError as err:
            print(err)

    # 数据获取
    def retrieve_books(self, page=1):
        key = self.process_key()
        data = main(key, page)
        if data:
            self.setData(data)
        else:
            wx.MessageBox("没有查到任何数据！", "提示", wx.OK | wx.ICON_INFORMATION)

    # 关键词处理 # -> %23
    def process_key(self):
        key = self.bookText.GetValue()
        new = re.sub("#", "%23", key)
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

# 测试方法，成功
def setData(data):
    for row in data:
        print(row[0],row[1],row[2],row[3],row[4],row[5])

if __name__ == "__main__":
    page = 1
    # False表示不将stdout和stderr重定向到一个窗口
    app = wx.App(False)
    top = BookFrame("BookSpider")
    top.Show(True)
    app.MainLoop()

    # 测试用例，成功
    # data = main()
    # if data:
    #     setData(data)
    # else:
    #     pass