#coding=utf8
import urllib2
from sgmllib import SGMLParser
import urllib
import time
import threading
import Queue
import re
import random
import urlparse
import codecs
import json
import string
from xml.etree import ElementTree
import MySQLdb
url = "http://pub.alimama.com/pubauc/searchAuctionList.json?q=%s&user_type=1&toPage=%d"
coder = codecs.getreader('utf8')
class webNode(object):
    def __init__(self,file,host,user,passwd,db):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db  or ""
        print self.host
        print self.user
        print self.passwd
        print self.db
        #获取所有关键词
        try:
            filename = "Conf/%s" % file 
            fp = open(filename,"r+b")
        except IOError:
            self.status = 0
            print "Can't find the \"Conf\%s\" file" % file    
            return
        self.status = 1
        self.keywords = []
        self.filename = file
        line = fp.readline().strip()
        while line:
            line = urllib2.quote(line)
            self.keywords.append(line)
            line = fp.readline().strip()
        #获取所有关键词可能的题目
        self.othernames = {}
        soku = "http://www.sogou.com/web?query=%s&_asf=www.sogou.com&_ast=&w=01019900&p=40040100&ie=utf8&sut=2953&sst0=1430749044567"
        for keyword in self.keywords:
            url = soku % keyword
            
            try:
                context = urllib2.urlopen(url,timeout = 20)
                content = context.read()
            except:
                print "can't read from %s" % url
                continue
            othername = KEYWORDTITLE()
            othername.feed(content)
            #获得所有可能的别名
            self.othernames[keyword] = othername.result

    def run(self):
        opener = urllib2.build_opener()
        cookie = "cookie2=%s" % s.cookie
        opener.addheaders.append(("Cookie",cookie))
        pages = 1
        totalpages = 1
        rstr = {"data":{}}
        rstr["data"]["pagelist"] = [] 
        re_h=re.compile('</?\w+[^>]*>')
        
        #数据库链接句柄
        try:

             self.conn = MySQLdb.connect(host = self.host,
                                         user = self.user,
                                         passwd = self.passwd,
                                         db = self.db,
                                         charset="utf8",
                                         connect_timeout=20)  
             self.cursor = self.conn.cursor()                       
        except Exception as err:
             print "%s Can't connect to Server %s\n" % (self.host,self.host)
             print err
             return
             
        # 获取数据库所有得目录id
        sql  = "select `cid` from `tw_category` where 1"
        self.cursor.execute(sql)
        category = self.cursor.fetchall()
        category_len = len(category)
        for keyword in self.othernames: 
            keyword_len = len(self.othernames[keyword])
            while pages <= totalpages:
                 f = opener.open(url % (keyword,pages))
                 result = f.read()
                 result = result.decode("utf8").encode("utf8")
                 fjson = json.loads(result)
                 totalpages = int(fjson["data"]["paginator"]["pages"])
                 pages += 1
                 #print "total pages is %d and we are in %d" % (totalpages,pages) 
                 for li in fjson["data"]["pagelist"]:
                     li["title"] = re_h.sub('',li["title"])
                     temp = "{"
                     starta = 1
                     for key in li:
                         try:
                             if key in ["title","zkPrice","reservePrice","biz30day","pictUrl","auctionId","userNumberId"]:
                                 if starta != 1:
                                     temp = temp +","
                                 
                                 temp = temp + "\""+key+"\""+":\""+str(li[key]).encode("utf8")+"\""
                                 starta = starta + 1
                         except UnicodeEncodeError:
                             if key in ["title","zkPrice","reservePrice","biz30day","pictUrl","auctionId","userNumberId"]:
                                 temp = temp + "\""+key+"\""+":\""+li[key]+"\""
                                 starta = starta + 1
                     temp = temp +"}"
                     temp =temp.encode("utf8")
                     time1 = int(time.time())
                     #插入 
                     #随机获取一个目录id
                     cate = str(category[random.randint(0,category_len)-1][0])
                     
                     #组成名字
                     title = urllib.unquote(keyword) + ","+self.othernames[keyword][random.randint(0,keyword_len-1)]
                     print title
                     #用户id
                     source= li["userNumberId"].encode("utf8")

                     #生成别名
               
                     alias=string.join(random.sample(['a','b','c','d','e','f','g','h','i','g','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9'],15)).replace(' ','')
                     sql = "insert into `tw_cms_article` (`cid`,`title`,`alias`,`tags`,`uid`,`author`,`source`,`dateline`,`lasttime`,`ip`) Values ("+cate+",'"+title+"','"+alias+"',\"{}\",1,'admin','"+source+"','"+str(time1)+"','"+str(time1)+"','"+str(time1)+"')"

                     print sql
                     try:
                         self.cursor.execute(sql)
                         lastid = self.cursor.lastrowid
                         temp =  MySQLdb.escape_string(temp)
                         sql = "insert into `tw_cms_article_data` (`id`,`content`) values(" + str(lastid)+",'"+temp+"')"
                         self.cursor.execute(sql)
                         #插入浏览表
                         sql ="insert into `tw_cms_article_views` (`id`,`cid`,`views`) values("+str(lastid)+",'"+cate+"',0)"
                         self.cursor.execute(sql)
                     except:
                          pass
                     
            pages = 1
      
        
class Application(object):
    def __init__(self):
        print "Trying to load all the web server...\n"
        xml = open("config.xml").read()
        root = ElementTree.fromstring(xml)
        self.numberofThreads = int(root.find("numberofThreads").text.strip())
        self.Qout = 0
        #获取cookie
        self.cookie = root.find('cookie').text.strip()
        #获取搜索属性来组装url
        config = root.find("config")
        self.startCommrate = config.find("startCommrate").text.strip()
        self.startTotalnum = config.find("startTotalnum").text.strip()
        self.endTotalnum   = config.find("endTotalnum").text.strip()
        self.startPrice    = config.find("startPrice").text.strip()
        self.endPrice      = config.find("endPrice").text.strip()
        global url
        if self.startCommrate:
            url = url + "&startCommrate="+self.startCommrate
        if self.startTotalnum:
            url = url + "&startTotalnum="+self.startTotalnum
        if self.endTotalnum:
            url = url + "&endTotalnum="+self.endTotalnum
        if self.startPrice:
            url = url + "&startPrice ="+self.startPrice
        if self.endPrice:
            url = url + "&endPrice="+self.endPrice
        print url
        self.webnodes = []
        webnode = root.findall("webnode")
        for w in webnode:
            host = w.find("webinfo").find("server").text.strip()
            user = w.find("webinfo").find("user").text.strip()
            passwd = w.find("webinfo").find("passwd").text.strip()
            dbq = w.find("webinfo").find("db").text.strip()
            file = w.find("keyword").text.strip()
            new_w = webNode(file,host,user,passwd,dbq)
            if new_w.status:
                 self.webnodes.append(new_w)
                 
                 
    def run(self):
        self.spiders = Queue.Queue()
        for web in self.webnodes:
            self.spiders.put(web)
        for web in self.webnodes:
            pass
        self.Pool = [] 
        for i in range(self.numberofThreads):
             new_thread = threading.Thread(target = self.Mession)
             new_thread.setDaemon(True)
             self.Pool.append(new_thread)
             new_thread.start()
        while True:
             if self.Qout == self.numberofThreads and self.Pool:
                 for i in self.Pool: 
                     i.join()
                 del self.Pool[:]
                 print "we have done all the work,byby!\n"
                 return
    def Mession(self):
        while True:
            if self.spiders.empty():
                self.Qout += 1 
                return
            spider = self.spiders.get()
            spider.run()

class KEYWORDTITLE(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.startflag = 0
        self.starttext = 0
        self.result =[]
    def start_table(self,attrs):
        for k,v in attrs:
            if k == "id" and v=="hint_container":
                self.startflag = 1
    def start_a(self,attrs):
        if self.startflag==1:
            self.starttext = 1
    def handle_data(self,text):
        if self.starttext==1:
            self.result.append(text)
            self.starttext = 0
    def start_script(self, attr): 
         self.literal = 1 
    def end_a(self):
        if self.starttext == 1:
            self.starttext =0 
    def end_table(self):
        if self.startflag:
            self.startflag = 0



if __name__ == '__main__':
    s = Application()
    s.run() 
