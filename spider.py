#coding=gb2312
import pickle
import urllib2
from sgmllib import SGMLParser
import urllib
import MySQLdb
import time
import threading
import os
import Queue
import random
import re
import urlparse
from source import *
class webNode(object):
    def __init__(self,host,user,passwd,db='gxcms',prefix='gx_'):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.keyword = []
        self.db = db
        self.prefix = prefix
        self.scope = ''
        self.source = ''
class mainSpider(object):
    def __init__(self,numberOfThreads = 1):
        print "Trying to load all the web server...\n"
        try:
            fp = open("Conf/setting.ini","r+b")
        except IOError:
            print "Can't find the \"webinfo\" file ...\n"
            return
        self.webinfo = []
        line = fp.readline().strip()
        while line:
            if line.startswith("#"):
                line = fp.readline().strip()
                continue
                
            info = line.split()
            print info
            if len(info) != 3:
                print "[Error] There is an error in setting.ini\n"
                return
            SERVER = 0
            SCOPE = 1
            SOURCE = 2
            #if not self.webinfo.has_key(info[SOURCE]):
            #    self.webinfo[info[SOURCE]] = []
            try:
                fpp = open("spiderinfo/"+info[SERVER],"r+")
            except IOError:
                print "Can't find the file \"%s\"..\n" % info[SERVER]
                line = fp.readline().strip()
                continue
            
            webinfo = fpp.readline().strip().split(',')
            #address user passwd database prefix
            if len(webinfo) == 4:
                newWebNode = webNode(webinfo[0],webinfo[1],webinfo[2],webinfo[3])
            elif len(webinfo) == 5:
                newWebNode = webNode(webinfo[0],webinfo[1],webinfo[2],webinfo[3],webinfo[4])
            else:
                print "[Error] There is an error in file \"%s\" at Line 1" % info[SERVER]
            newWebNode.scope = info[SCOPE]
            newWebNode.source = info[SOURCE]
            keyword = fpp.readline().strip()
            #loading keywords if exist
            while keyword:
                keyword = keyword.decode("GB2312").encode("UTF-8")
                newWebNode.keyword.append(urllib.quote(keyword))
                keyword = fpp.readline().strip()
            self.webinfo.append(newWebNode)
            fpp.close()
            line = fp.readline().strip()
        fp.close()
        self.numberOfThreads = numberOfThreads
        self.Qout = 0
    
    def run(self):
        self.spiders = Queue.Queue()
        for web in self.webinfo:
            s = "self.spiders.put(%s(web))" % web.source
            exec(s)
        self.Pool = []
        for i in range(self.numberOfThreads):
            new_thread = threading.Thread(target = self.Mession)
            new_thread.setDaemon(True)
            self.Pool.append(new_thread)
            new_thread.start()
        while True:
            if self.Qout == self.numberOfThreads and self.Pool:
                for i in self.Pool:
                    i.join()
                del self.Pool[:]
                print "we have done all the work ,byby!\n"
                return
    def Mession(self):
        while True:
            if self.spiders.empty():
                print "One Thread got Free \n"
                self.Qout += 1
                return
            spider = self.spiders.get()
            spider.run()
            
        

            
                
                

if __name__ == "__main__":
    s = mainSpider()
    s.run()
    
