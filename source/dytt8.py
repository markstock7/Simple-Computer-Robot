#coding=gb2312
import urllib2
from sgmllib import SGMLParser
import urllib
import MySQLdb
import time
import os
import random
import re
import urlparse
class dytt8(object):
    def __init__(self,web):
        self.web = web
        self.urls = ["http://www.ygdy8.net/html/gndy/china/list_4_%s.html",
                    "http://www.ygdy8.net/html/gndy/oumei/list_7_%s.html",
                    "http://www.ygdy8.net/html/gndy/rihan/list_6_%s.html",
                    "http://www.ygdy8.net/html/gndy/jddy/list_63_%s.html",
                    "http://www.ygdy8.com/html/gndy/dyzz/list_23_%s.html"]
                    
    def run(self):
        try:
            self.conn = MySQLdb.connect(host = self.web.host,
                                        user = self.web.user,
                                        passwd = self.web.passwd,
                                        db = self.web.db,charset="utf8",connect_timeout=5)
            print "connect to %s " % self.web.db
            self.sql = "insert into gx_video(`cid`,`intro`,`title`,`picurl`,`playurl`,`score`,`scoreer`,\
`keywords`,`color`,`actor`,`director`,`content`,`area`,`language`,`year`,`serial`,`addtime`,`hits`,\
`monthhits`,`weekhits`,`dayhits`,`hitstime`,`stars`,`status`,`up`,`down`,`downurl`,`inputer`,`reurl`,\
`letter`,`genuine`) values (%d,'',\'%s\',\'%s\',\'%s\',%d,%d,'','','','',\'%s\','','',0,0,%d,0,0,0,0,0,0,1,0,0,'','','','',0)"
            #(index,clist["title"], clist["pic"],clist["link"],score,scoreer,posturl)
        except:
            print "%s Can't connect to Server %s\n" % (self.web.db,self.web.host)
            return
        try:
           if os.path.isfile("temp/dytt8"):
               print "loading from temp file ... /n" 
               temf = open("temp/dytt8","r+")
               line = temf.readline()
               ttitle = ''
               tdetail = ''
               tdownurl = ''
               tpurl = ''
               END = False
               while line:
                   if line.startswith("title=>"):
                       ttitle = line[7:]
                   elif line.startswith("downurl=>"):
                       tdownurl = line[9:]
                   elif line.startswith("purl=>"):
                       tpurl = line[6:]
                   elif line.startswith("detail=>"):
                       tdetail += line[7:]
                   elif line.startswith("[END]"):
                       index = random.randint(1,21)
                       atime = int(time.time())
                       score = round(random.random(),2)*10
                       scorrer = random.randint(10,100)
                       sql = self.sql % (index,ttitle,tpurl,'',score,scorrer,tdetail,atime)
                       try:
                           e = False
                           try:
                               self.conn.ping()
                           except:
                               try:
                                   self.conn = MySQLdb.connect(host = self.web.host,
                                        user = self.web.user,
                                        passwd = self.web.passwd,
                                        db = self.web.db,charset="utf8",connect_timeout=5)
                                   print "Reconnect to %s" % self.web.host
                               except:
                                   e = True
                                   print "Reconnect to %s failed" % self.web.host
                           if not e:
                               self.conn.query(sql)
                               tdetail = ''
                       except Exception,e:
                           print e
                   else:
                       tdetail += line
                  
                   line = temf.readline()
               print "i am return"
               temf.close()
               return 
        except Exception,e:
            print e
            return
        
        dytt8sgml = dytt8SGML()
        tfile = open('temp/dytt8','w+')
        totalresult = 0
        for urlp in self.urls:
            page = 1
            url = urlp % page
            netloc ="http://"+ urlparse.urlparse(url).netloc
            try:
                context = urllib2.urlopen(url,timeout = 20)
                content = context.read()
            except:
                print "can't read from %s" % url
                continue
            dytt8sgml.feed(content)
            totalpages = dytt8sgml.totalpages
            print "total pages %s " % totalpages
            while totalpages>page:
                url = urlp % page
                try:
                    context = urllib2.urlopen(url)
                    content = context.read()
                    page += 1
                except:
                    print "can't read from %s "% url
                    page += 1
                    continue
                dytt8sgml.feed(content)
                
                for r in dytt8sgml.result:
                    childUrl = netloc+r
                    try:
                        context = urllib2.urlopen(childUrl,timeout = 3)
                        content = context.read()
                    except:
                        print "can't read from %s \n"% childUrl
                        continue
                    dytt8sgmlchild = dytt8SGML()
                    dytt8sgmlchild.feed(content)
                    #print "---------------------------------------------"
                    #print " name  => %s \n" % dytt8sgmlchild.newr["name"]
                    #print " year  => %s \n" % dytt8sgmlchild.newr["year"]
                    #print " detail => %s \n" % dytt8sgmlchild.newr["detail"]
                    #print " downurl => %s \n" % dytt8sgmlchild.newr["downurl"]
                    #print " startflag => %d \n" % dytt8sgmlchild.startflag
                    #print " picurl => %s | %s " % (dytt8sgmlchild.newr["pic"][0],dytt8sgmlchild.newr["pic"][1])
                    if dytt8sgmlchild.newr["name"] == "error" or dytt8sgmlchild.newr["name"] =='':continue
                    print "i am here"
                    index = page % 21 + 1
                    atime = int(time.time())
                    score = round(random.random(),2)*10
                    scorrer = random.randint(10,100)
                    fname = MySQLdb.escape_string(dytt8sgmlchild.newr["name"])
                    fdetail = MySQLdb.escape_string(dytt8sgmlchild.newr["detail"].strip('\''))
                    fpurl = MySQLdb.escape_string(dytt8sgmlchild.newr["pic"][0].strip('\''))
                    sql = self.sql % (index,fname,fpurl,'',score,scorrer,fdetail,atime)
                    print "loading from %s " % childUrl
                    try:
                        e = False
                        try:
                            self.conn.ping()
                        except:
                            try:
                                self.conn = MySQLdb.connect(host = self.web.host,
                                        user = self.web.user,
                                        passwd = self.web.passwd,
                                        db = self.web.db,charset="utf8",connect_timeout=5)
                                print "Reconnect to %s" % self.web.host
                            except:e = True
                        if not e:
                            tfile.writelines("title=>" + fname+"\n")
                            tfile.writelines("downurl=>"+fpurl+"\n")
                            tfile.writelines("purl=>"+fpurl+"\n")
                            tfile.writelines("detail=>"+fdetail+"\n")
                            tfile.writelines("[END]"+"\n")
 #                           self.conn.query(sql)
                            totalresult += 1
                            print "Done %s" % totalresult
                    except Exception,e:print e
        tfile.close() 
class dytt8SGML(SGMLParser):
    def __init__(self,getNum = False,totalpages = -1):
        SGMLParser.__init__(self)
        self.totalpages = totalpages
        self.getNum = getNum
        self.geturl =False
        self.pagepattern = re.compile("%20%B9%B2([0-9]+)%D2%B3")
        self.result = []
        self.newr = {"name":'',"year":'','detail':'',"downurl":'',"pic":[]}
        self.startflag = 0
        self.getDetail = False
        self.detail_br = False
        self.startname = "◎译　　名"
        self.startyear = "◎年　　代"
        self.startname1 = "◎片　　名"
    def start_div(self,attrs):
        if self.startflag > 0:
            self.startflag += 1
        for k,v in attrs:
            if k == "class" and v == "x" and self.totalpages == -1: #get the number of all the items
                self.getNum = True
            if k == "id" and v.strip() == "Zoom":
                self.startflag = 1
    def handle_data(self,text):
        
        if self.startflag>0:
            try:
                if text.startswith(self.startname): 
                    self.newr["name"] = text[len(self.startname):].strip().decode("GB2312").encode("UTF-8")
                elif text.startswith(self.startname1) and self.newr["name"] =='':
                    self.newr["name"] = text[len(self.startname1):].strip().decode("GB2312").encode("UTF-8")
                elif text.startswith("片名:") and self.newr["name"] =='':
                    self.newr["name"] = text[len('片名:'):].strip().decode("GB2312").encode("UTF-8")
                elif text.startswith("◎又　　名") and self.newr["name"] =='':
                    self.newr["name"] = text[len('◎又　　名'):].strip().decode("GB2312").encode("UTF-8")                        
                elif text.startswith(self.startyear):
                    self.newr["year"] = text[len(self.startyear):].strip().decode("GB2312").encode("UTF-8")
                elif text.startswith("◎简　　介"):
                    self.getDetail = True
                elif self.getDetail:
                    if not self.detail_br:
                        self.newr["detail"] += "\'"+text.decode("GB2312").encode("utf-8")
                        self.detail_br = False
                    else:
                        self.newr["detail"] += text.decode("GB2312").encode("utf-8")+"\n\n"
            except:self.newr["name"]="error"
        if self.getNum:
            if not text.strip():return
            text = urllib.quote(text)
            r = self.pagepattern.findall(text)
            if r:
                self.totalpages = int(r[0])
                print self.totalpages
                self.getNum = False
            
    def start_table(self,attrs):
        for k,v in attrs:
            if k == "class" and v =="tbspan":
                self.geturl = True
                break
    def start_a(self,attrs):
        attrs = dict(attrs)
        for k in attrs:
            if k == "class" and attrs[k] == "ulink":
                if not attrs["href"].endswith("index.html"):
                    self.result.append(attrs["href"].strip())

            if k == "href" and self.startflag>0 and attrs[k].startswith("ftp"):
               self.newr["downurl"] = attrs[k]
  
                    
    def start_img(self,attrs):
        if self.startflag > 0:
            attrs = dict(attrs)
            if not self.newr.has_key("pic"):
                self.newr["pic"] = []
            self.newr["pic"].append(attrs["src"])
        if self.getDetail:
            self.getDetail = False
    def end_div(self):
        if self.startflag > 0:
            self.startflag -= 1
            if self.getDetail:
                self.getDetail = False
    def end_p(self):
        if self.getDetail:
            self.getDetail = False
    def end_span(self):
        if self.getDetail:
            self.getDetail = False
    def end_br(self):
        self.detail_br = True
