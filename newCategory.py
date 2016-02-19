import string
import random
import MySQLdb
from xml.etree import ElementTree
print "Tring to load all the web server ...\n"

xml = open('config.xml').read()

root = ElementTree.fromstring(xml)
webnodes = root.findall('webnode')

for w in webnodes:
    categorypath = w.find('category').text.strip()
     
    try:
        fp = open("Category/"+categorypath,"r+b")
    except IOError:
        print "Can't find the \"Category\/ %s\" file" % categorypath
    
    host = w.find("webinfo").find("server").text.strip()
    user = w.find("webinfo").find("user").text.strip()
    passwd = w.find("webinfo").find("passwd").text.strip()
    dbq = w.find("webinfo").find("db").text.strip()
   
    try:
        conn = MySQLdb.connect(host = host,
                               user = user, 
   			       passwd = passwd,
                               db = dbq,
                               charset = "utf8",
                               connect_timeout = 20)
        cursor = conn.cursor()
    except Exception as err:
        print "%s Can't connect to server %s\n" % (host,host)
        print err
        continue
   
    cate = fp.readline().strip()
    
    while cate:
        sql = "select `cid` from `tw_category` where `name` = '"+cate+"'"
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) == 0:
            alias=string.join(random.sample(['a','b','c','d','e','f','g','h','i','g','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9'],15)).replace(' ','')
            sql = "insert into `tw_category` (`mid`,`name`,`alias`,`cate_tpl`,`show_tpl`) values (2,'"+cate+"','"+alias+"','article_list.htm','article_show.htm')"
            cursor.execute(sql)
        cate = fp.readline().strip()
    print "we have done!!!!!!"
