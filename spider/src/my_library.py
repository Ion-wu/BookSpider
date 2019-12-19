# coding:utf-8
# 2019/12/3.9:40

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
        pageIndex = int(depth("b")[1].string)
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
    find_div = soup.find_all("div", {"class": "b_info"})
    for p in find_div:
        subject = str(p.contents[9].string)
        type = str(p.contents[5].string)
        intro.append(subject)
        intro.append(type)
    tips = "提要文摘附注:"
    try:
        tips += soup.find("div", {"class": "intro"}).string
    except:
        tips += "--暂无--"
    # print(perf_counter() - start)
    intro.append(tips)
    # intro = processIntro(intro)
    return processIntro(intro)


# 简介信息处理
def processIntro(list):
    for i, str in enumerate(list):
        list[i] = str.split(":")[-1]
    return list


# 电脑端图书简介信息
def getClient_book_introduction(code):
    # start = perf_counter()
    intro = []
    url = "http://172.16.73.134:8083/SJXQ/"
    html = getHTMLText(url + code)
    soup = BeautifulSoup(html, "lxml")
    find_div = soup.find_all("li", {"style": "display:block;"})
    type = find_div[3].contents[1].string
    subject = find_div[5].contents[1].string
    tips = find_div[7].contents[1].string
    # print(perf_counter()-start)
    intro.append([subject, type, tips])
    return intro

