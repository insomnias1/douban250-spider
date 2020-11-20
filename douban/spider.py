from bs4 import BeautifulSoup  # 网页解析
import re  # 正则表达式
import urllib.request, urllib.error  # 制定url,获取网页数据
import xlwt  # 进行excel操作
import sqlite3  # 进行数据库操作


def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 1.爬取网页
    datalist = getData(baseurl)
    #savepath = ".\\豆瓣电影Top250.xls "
    dbpath = "movie.db"
    # 获取影片链接
    #saveData(datalist, savepath)
    saveData2DB(datalist, dbpath)

findLink = re.compile(r'<a href="(.*?)">')  # 创建正则表达式对象，表示规则，
# 获取图片链接
findImasrc = re.compile(r'<img.*src="(.*?)"', re.S)  # re.S忽视换行符包
# 片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
# 找到概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


def getData(baseurl):
    datalist = []
    for i in range(0, 10):  # 左闭右开，不包含10，调用函数10次，
        url = baseurl + str(i * 25)
        html = askURL(url)  # 保存获取到的网页源码，弄到一个解析一个

        # 2.逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_="item"):  # 查找符合要求的字符串，形成列表

            # print(item)  # 测试，查看电影item
            data = []  # 保存一部电影的所有信息
            item = str(item)

            # 获取影片详情的链接
            link = re.findall(findLink, item)[0]  # re库用来通过正则表达式查找特定字符串
            # 你找到的符合规则的连接可能不只一个，但是我们只要第一个，所以就用[0]
            data.append(link)
            # 获取图片
            imgSrc = re.findall(findImasrc, item)[0]
            data.append(imgSrc)
            # 获取titles
            titles = re.findall(findTitle, item)
            if len(titles) == 2:
                ctitle = titles[0]  # 添加中文名
                data.append(ctitle)
                otitle = titles[1].replace("/", " ")  # 去掉无关的符号，添加外国名
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append(' ')  # 外国名，留空
            # 获取评分
            rating = re.findall(findRating, item)[0]
            data.append(rating)
            # 获取评价人数
            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)
            # 获取概况
            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")  # 去掉句号
                data.append(inq)
            else:
                data.append(" ")  # 添加空值
            # 获取电影内容
            bd = re.findall(findBd, item)[0]
            bd = re.sub("<br(\s+)?/>(\s+)?", " ", bd)  # 去掉br
            bd = re.sub('/', " ", bd)  # 去掉/
            data.append((bd.strip()))  # 去空格
            datalist.append(data)
    return datalist


# 得到一个特定url的网页内容
def askURL(url):
    head = {  # 模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    }
    #  用户代理，表示告诉豆瓣我们是什么类型的机器，浏览器，(本质上是告诉浏览器，我们可以接受什么水平的文件)
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# 3.保存数据
def saveData(datalist, savapath):
    print("save....")
    book = xlwt.Workbook(encoding="utf-8") # 创建workbook对象
    sheet = book.add_sheet("豆瓣电影top250", cell_overwrite_ok=True)   # 创建工作区
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关内容")
    for i in range(0, 8):
        sheet.write(0, i, col[i])
    for i in range(0, 250):
        print("第%d条" % (i+1))
        data = datalist[i]
        for j in range(0, 8):
            sheet.write(i+1, j, data[j]) # 数据


    book.save("豆瓣电影Top250.xls")    #  保存数据

def  saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
                insert into movie250 (
                info_link,pic_link,cname,ename,score,rated,introduction,info)
                values(%s)''' % ",".join(data)
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()

def init_db(dbpath):
    sql = '''
    create table movie250
    (
    id integer primary key autoincrement,
    info_link text,
    pic_link text,
    cname varchar,
    ename varchar,
    score numeric,
    rated numeric,
    introduction text,
    info text
    )
    '''  #创建数据库
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()



if __name__ == "__main__":          #当程序执行时
#调用函数
    main()
    #init_db("movietest.db")
print("爬取完毕")
