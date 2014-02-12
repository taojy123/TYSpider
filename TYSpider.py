# -*- coding: cp936 -*-

import cookielib
import urllib2, urllib
import time
import re
import traceback
import time
import shutil

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'),
                     ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'), 
                     ('Accept-Language', 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'), 
                     ('Connection', 'keep-alive')
                     ]
opener.addheaders.append( ('Accept-encoding', 'identity') )
opener.addheaders.append( ('Referer', 'http://www.taobao.com/') )


def get_page(url, data=None):
    resp = None
    n = 0
    while n < 5:
        n = n + 1
        try:
            resp = opener.open(url, data, timeout=30)
            page = resp.read()
            return page
        except:
            #traceback.print_exc()
            print "Will try after 2 seconds ..."
            time.sleep(2)
            continue
        break
    return "Null"


def add_data(filename, name, url, nowtime, data):
    try:
        s = open(filename,).read()
    except:
        s = ""
    if not s:
        if "taobao" in filename:
            s = "名称,网址,时间,浏览量,售出,交易成功\n"
        elif "youku" in filename:
            s = "名称,网址,时间,播放数,评论数,顶,踩\n"
        else:
            s = "\n"

    if name and s.rfind(name) > -1:
        i = s.rfind(name)
    elif s.rfind(url) > -1:
        i = s.rfind(url)
    else:
        i = -1
        
    j = s.find("\n", i) + 1

    r = "%s,%s,%s,%s\n"%(name, url, nowtime, data)
    s = s[:j] + r + s[j:]

    open(filename, "w").write(s)


print "================ 优酷淘宝 爬虫助手 ================="

print "确认已将要获取的网址数据写入 data.txt 文件中"

interval = input("请输入每次采集间隔时间(分钟):")

print

while True:

    try:
        nowtime = time.strftime('%Y-%m-%d %H:%M')
        print "开始采集", nowtime
        
        lines = open("data.txt").readlines()
        for line in lines:
            time.sleep(3)
            
            url = line.strip() + ","
            print url
            
            name = url.split(",")[1]
            url = url.split(",")[0]
            
            if "taobao" in url[:20]:
                p = get_page(url)
                
                link = re.findall(r'"apiItemViews": "(.*?)",', p)[0]
                p2 = get_page(link)
                viewcount = int(re.findall(r':(.*?)}', p2)[0])

                link = re.findall(r'"apiItemInfo":"(.*?)",', p)[0]
                p3 = get_page(link)
                quanity = int(re.findall(r'quanity:(.*?),', p3)[0])
                confirm = int(re.findall(r'confirmGoods:(.*?),', p3)[0])
                
                print name, nowtime, viewcount, quanity, confirm

                data = "%s,%s,%s"%(viewcount, quanity, confirm)
                add_data("taobao.csv", name, url, nowtime, data)

                
            if "youku" in url[:20]:
                p = get_page(url)
                
                ding = re.findall(r'"upVideoTimes">(.*?)</em>', p)[0]
                cai = re.findall(r'"downVideoTimes">(.*?)</em>', p)[0]
                
                vid = re.findall(r"var videoId = '(.*?)';", p)[0]
                link = "http://v.youku.com/QVideo/~ajax/getVideoPlayInfo?id=%s&type=vv"%vid
                p2 = get_page(link)
                viewcount = re.findall(r'"vv":(.*?),', p2)[0]

                link = 'http://comments.youku.com/comments/~ajax/getStatus.html?__ap={"videoid":"%s"}'%vid
                p3 = get_page(link)
                total = re.findall(r'"total":"(.*?)",', p3)[0]

                print name, nowtime, viewcount, total, ding, cai

                data = "%s,%s,%s,%s"%(viewcount, total, ding, cai)
                add_data("youku.csv", name, url, nowtime, data)

        print
        print "等待 %d 分钟后 再次采集..."%interval
        time.sleep(interval*60)
        
        shutil.copyfile("taobao.csv", "taobao_bak.csv")    
        shutil.copyfile("youku.csv", "youku_bak.csv")

    except:
        traceback.print_exc()
        open("error.txt", "w").write(traceback.format_exc())
    





