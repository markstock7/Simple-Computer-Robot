#coding=utf-8
import urllib2
from sgmllib import SGMLParser
import urllib
import MySQLdb
import time
import os
import random
import re
import urlparse

url = "http://www.soku.com/search_video/q_%s_orderby_2_page_%s"
class youku(object):
    def __init__(self,web):
        self.web = web
        self.result = 0
        self.id = -1
        self.rfinally = 0
    def run(self):
        try:
            self.conn = MySQLdb.connect(host=self.web.host,user=self.web.user,passwd = self.web.passwd,db=self.web.db,charset="utf8",connect_timeout=5)
            print "connet to %s ,%s\n" % (self.web.host,self.web.db)
        except:
            print "can't connet to %s ,%s\n" % (self.web.host,self.web.db)
            return
        i = 0
        try:  
            # python UCS-4 build的处理方式  
            highpoints = re.compile('[\\x00-\\xFF]{2,4}')  
        except re.error:  
            # python UCS-2 build的处理方式  
            highpoints = re.compile('[\uD800-\uDBFF][\uDC00-\uDFFF]')  
        for index,keyword in enumerate(self.web.keyword):
            index = index + 1
            #组合成所需要的url
            for i in range(1,2):#默认扫描十页
                myurl = url % (keyword , i)
                #获取所有最新的视频
                food = youkuSGML(self.web.scope)
                #获取当前页的所有结果
                try:
                    context = urllib2.urlopen(myurl,timeout=5)
                    content = context.read()
                except:
                    print "can't read from %s " % myurl
                    continue

                food.feed(content)
                self.result += len(food.result)
        #将结果输入进数据库
                for clist in food.result:
                    score = round(random.random(),2)*10
                    scoreer = random.randint(10,100)
                    atime = int(time.time())
                    e = False
                    if clist["title"] == '':
                        continue
                    clist["title"] = MySQLdb.escape_string(clist["title"])
                    sql = "insert into gx_video(`cid`,`intro`,`title`,`picurl`,`playurl`,`score`,`scoreer`,`keywords`,`color`,`actor`,`director`,`content`,`area`,`language`,`year`,`serial`,`addtime`,`hits`,`monthhits`,`weekhits`,`dayhits`,`hitstime`,`stars`,`status`,`up`,`down`,`downurl`,`inputer`,`reurl`,`letter`,`genuine`) values (%d,'',\'%s\',\'%s\',\'%s\',%d,%d,'','','','','','','',0,0,%d,0,0,0,0,0,0,1,0,0,'','','','',0)" % (index,clist["title"],clist["pic"],clist["link"],score,scoreer,atime)
                    print sql
                    try:
                        try:
                            self.conn.ping()
                        except Exception,e:
                            try:
                               self.conn = MySQLdb.connect(host=self.web.host,user=self.web.user,passwd = self.web.passwd,db=self.web.db,charset="utf8",connect_timeout=5)
                               print "Reconnet to %s ,%s\n" % (self.web.host,self.web.db)
                            except:
                               print "can't Reconnet to %s ,%s\n" % (self.web.host,self.web.db)
                               e = True
                        if not e:
                            self.conn.query(sql)
                            self.rfinally += 1
                    except:print sql+"/n"
        print "%s get %d results\n and %s insert successfully" % (self.web.db,self.result,self.rfinally)
        self.conn.close()
class youkuSGML(SGMLParser):
    def __init__(self,scope):
        SGMLParser.__init__(self)
        self.startflag = 0
        self.result =[]
        self.scope = scope
        print self.scope
        self.newr = {}
        self.getpic = False
        self.getlink = False
        self.gettime = False
    def start_div(self,attrs):
        if self.startflag > 0:
           self.startflag += 1
        for k,v in attrs:
           if k == "class" and v.strip() == "sk-vlist clearfix":
               self.startflag = 1
               return 
           if self.startflag > 0 :
               if k == "class" and v == "v-thumb":
                   self.getpic = True
               if k == "class" and v == "v-link":
                   self.getlink = True
    def start_img(self,attrs):
        if self.getpic and self.startflag:
            for k,v in attrs:
                if k == "src":
                    self.newr["pic"] = v
                if k == "alt":
                    self.newr["title"] = v
            self.gitpic = False
    def start_a(self,attrs):
        if self.getlink and self.startflag:
            for k,v in attrs:
                if k == "href":
                    self.newr["link"] = v
                    self.result.append(self.newr)
                    self.newr = dict()
                    break
            self.getlink = False
    def start_span(self,attrs):
        if self.startflag:
            for k,v in attrs:
                if k == "class" and v == "pub":
                    self.gettime = True
    def handle_data(self,text):
        if self.gettime and self.scope != 'ALL':
            #check the uplaod time
            if text.strip("0123456789") != '\xe5\xb0\x8f\xe6\x97\xb6\xe5\x89\x8d':
                self.startflag = 0
                self.gettime = False
            else:
               self.gettime = False
    def end_div(self):
        if self.startflag> 0:
            self.startflag -= 1
