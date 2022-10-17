from datetime import datetime
import os
import re
import json
import time
import urllib.request
import requests
import sys
from lxml import html as lxmlhtml
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import lxml.etree as etree
from urllib.parse import urlparse
import dsfeed
import common_library
import sqlitemodel
import chromedriver
import html
from dotenv import load_dotenv
load_dotenv()

srcurl = ""
if sys.argv[1:2]:
    srcurl = sys.argv[1]

dbpath =  os.path.dirname(os.path.abspath(__file__)) + "/dsfeed.db"
shostname = os.getenv('SYNC_HOSTNAME')
spath = os.getenv('SYNC_PATH')
cmn = common_library.CommonLibrary(shostname)
cmn.scpGetFile(shostname, spath, dbpath)

dbm = sqlitemodel.SqliteModel(dbpath)
dbmconn = dbm.conn
dbmcur = dbm.cur
stsp =  os.path.dirname(os.path.abspath(__file__)) + "/sql/tables" # should be env
fns = os.listdir(stsp)
for fn in fns:
  f = open(stsp + "/" + fn, 'r')
  data = f.read()
  dbmcur.execute(data)
  f.close()

cdriver = chromedriver.ChromeDriver()
driver = cdriver.driver
cdsfeed = dsfeed.DsFeed(cdriver)

def saveDriver(fn):
    dt = datetime.now().strftime("%Y%m%d%H%M%S")
    path = os.path.dirname(os.path.abspath(__file__)) + "/logs/" + fn + "___" + dt
    driver.save_screenshot(path + ".png")
    with open(path + ".html", "w") as f:
        f.write(driver.page_source)

def srcScrape(doc, ui=0):
    doc = html.unescape(doc)
    doc = ' '.join(doc.splitlines())
    doc = doc.replace("<![CDATA[", "").replace("]]>", "")
    # title
    title = dsfeed.DsFeed.getElement(doc, "title")
    print("title: "+title)
    urls = cdsfeed.getSiteList(doc, ui)
    if len(urls) == 0:
      print("not found urls:ui:",ui)
      return
    curl = driver.current_url
    domain = urlparse(curl).netloc
    nps = 0
    for url in urls:
        ret = re.search("^(\/|\.\/)", url, re.S)
        if ret:
            url = "https://" + domain + url
        print("url:"+url)
        dbmcur.execute("select count(*) from links where link = ?", (url,))
        c = dbmcur.fetchone()[0]
        if c >= 1:
            continue
        try:
            driver.get(url)
        except Exception as e:
            saveDriver(common_library.CommonLibrary.getSrcLocationString())
            print(e)
            print("driver get failed and continue:"+url)
            continue
        doc = driver.page_source
        tree = lxmlhtml.fromstring(doc)
        # make out
        out = "**"+title+"**\n"
        etitle = dsfeed.DsFeed.getElement(doc, "title")
        dbmcur.execute("select count(*) from titles where title = ?", (etitle,))
        #dbmcur.statement
        c = dbmcur.fetchone()[0]
        if c >= 1:
            continue
        edesc = dsfeed.DsFeed.getElement(doc, "description")
        if edesc == "":
            edesc = dsfeed.DsFeed.getElement(doc, "h1")
        print(etitle,edesc)
        if edesc != "" and etitle != "":
            out = out + etitle + "\n" + edesc + "\n"
            out = out + url + "\n"
            print(out)
            common_library.CommonLibrary.toDiscord(os.getenv('DISCORD_WEBHOOK_URL'), out)
            # datetime
            cd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # insert
            dbmcur.execute(
                "insert into links(source_url, link, created, updated) \
                        values (?, ?, ?, ?)",
                (srcurl, url, cd, cd),
            )
            dbmcur.execute(
                "insert into titles(source_url, title, created, updated) \
                        values (?, ?, ?, ?)",
                (srcurl, etitle, cd, cd),
            )
            dbmconn.commit()
            nps = nps + 1
    if nps == 0:
      srcScrape(doc, ui+1)

def getSrc(url):
    if re.match("^(http|https):(\/|\/\/|)", url) is None:
      url = "https://" + url
    print("getSrc: " + url)
    doc = cdriver.get_doc(url)
    try:
        srcScrape(doc)
    except Exception as e:
        saveDriver(common_library.CommonLibrary.getSrcLocationString())
        print(e)
        print("catch exception in getSrc and retry get")
        doc = cdriver.get_doc(url,4)
        srcScrape(doc)

try:
  if srcurl == "":
      # from db
      dbmcur.execute("select id, url from sources")
      rs = dbmcur.fetchall()
      for r in rs:
          id = r[0]
          url = r[1]
          print(id,url)
          srcurl = url
          getSrc(srcurl)
  else:
      getSrc(srcurl)
except KeyboardInterrupt:
  pass

cmn.scpPutFile(shostname, dbpath, spath)

cdriver.driver.quit()
del dbm
del cmn
