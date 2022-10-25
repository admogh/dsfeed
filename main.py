from argparse import ArgumentParser
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

usage = 'Usage: python {} [--url <url>] [--rdb <rdb>] [--help]'\
        .format(__file__)
argparser = ArgumentParser(usage=usage)
argparser.add_argument('-u', '--url', type=str,
                       dest='url',
                       help='source url')
argparser.add_argument('-r', '--rdb', type=str,
                       dest='rdb',
                       help='restore: overwrite remote db')
args = argparser.parse_args()

srcurl = ""
if args.url:
  print("url set:" + args.url)
  srcurl = args.url

rdbpath = ""
if args.rdb:
  if os.path.exists(args.rdb):
    rdbpath = args.rdb

basedir = os.path.dirname(os.path.abspath(__file__))
dbpath =  basedir + "/dsfeed.db"
dbm = sqlitemodel.SqliteModel(dbpath)
cdriver = chromedriver.ChromeDriver()
cdsfeed = dsfeed.DsFeed(dbm, cdriver, basedir, rdbpath)
dbmcur = dbm.cur
stsp =  basedir + "/sql/tables" # should be env
fns = os.listdir(stsp)
for fn in fns:
  f = open(stsp + "/" + fn, 'r')
  data = f.read()
  dbmcur.execute(data)
  f.close()

def getSrc(url):
    if re.match("^(http|https):(\/|\/\/|)", url) is None:
      url = "https://" + url
    print("getSrc: " + url)
    doc = cdriver.get_doc(url)
    if doc == "":
      cdsfeed.saveDriver(common_library.CommonLibrary.getSrcLocationString())
    else:
      cdsfeed.srcScrape(url, doc)

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

del cdsfeed
