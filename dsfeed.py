import re
from datetime import datetime
import os
import inspect
from lxml import html as lxmlhtml
import html
from lxml import etree
from urllib.parse import urlparse
import emoji 
import time
import common_library

class DsFeed:
    @staticmethod
    def getString(str, is_html_unescape=True):
        p = re.compile(r"<[^>]*?>")
        p.sub("", str)
        if is_html_unescape:
            ret = html.unescape(p.sub("", str))
        else:
            ret = p.sub("", str)
        return ''.join(c for c in ret if c not in emoji.UNICODE_EMOJI)

    @classmethod
    def getElement(cls, src, name):
        e = ""
        ret = re.search('<'+name+"(>| [^>]+>)([^<]+)<", src, re.S)
        print(name,ret)
        if ret is not None:
            ret = ret.group(2).strip()
            if ret is not None:
                e = ret
        if e == "":
            ret = re.search("<"+name+" ([^>]+)>", src, re.S)
            if ret is not None:
                ret = ret.group(1).strip()
                if ret is not None:
                    ret = re.search("href=(\"|')([^\"']+)(\"|')", ret, re.S)
                    if ret is not None:
                        ret = ret.group(2).strip()
                        if ret != "":
                            e = ret
        if e == "":
            ret = re.findall('<meta ([^>]+)>', src, re.S)
            #print(ret)
            if ret[0:1]:
                for i in range(len(ret)):
                    v = ret[i]
                    #print(v)
                    ret2 = re.search("(| )property=(\"|')([^\"']+)(\"|')", v, re.S)
                    if ret2 is not None:
                        ret2 = ret2.group(3).strip()
                        if ret2 != "":
                            property = ret2
                            if property == "og:"+name:
                                ret3 = re.search(" content=(\"|')([^\"']+)(\"|')", v, re.S)
                                if ret3 is not None:
                                    ret3 = ret3.group(2).strip()
                                    if ret3 != "":
                                        e = ret3
                                        break
        if e == "":
            ret = re.search("dc:description=('|\")([^\"']+)('|\")", src, re.S)
            if ret is not None:
                e = ret.group(2).strip()
        return cls.getString(e)

    def __del__(self):
        print("DsFeed.__del__")
        self.cmn.scpPutFile(self.shostname, self.dbpath, self.spath, ow=False)
        self.cdriver.driver.quit()
        del self.dbm
        del self.cmn

    def __init__(self, dbm, cdriver, basedir, rdbpath):
        self.dbm = dbm
        self.cdriver = cdriver
        self.driver = cdriver.driver
        self.cut = time.time()
        try:
          sim = int(os.getenv('SYNC_INTERVAL_MINUTES'))
        except Exception as ex:
          print("catch Exception to get SYNC_INTERVAL_MINUTES, set to 20 minutes default:", ex)
          sim = 20
        self.sim = sim
        print("sim:",sim)
        self.basedir = basedir
        self.dbpath =  self.basedir + "/dsfeed.db"
        self.shostname = os.getenv('SYNC_HOSTNAME')
        self.spath = os.getenv('SYNC_PATH')
        self.cmn = common_library.CommonLibrary(self.shostname)
        if rdbpath != "":
          print("overwrite db(rdbpath,syncpath):",rdbpath,self.spath)
          self.cmn.scpPutFile(self.shostname, rdbpath, self.spath)
        self.cmn.scpGetFile(self.shostname, self.spath, self.dbpath)

    def getSiteList(self, src, ui):
        curl = self.driver.current_url
        print("curl:",curl)
        domain = urlparse(curl).netloc
        #bcurl = "https://" + domain
        dhrefs = {}
        slashes = {}
        urls = {}
        hrefs = []
        ss = re.findall("href=(\"|')([^\"']+)(\"|')", src, re.S)
        for s in ss:
          hrefs.append(s[1])
        ss = re.findall("<link(|[^>]+)>([^<]+)<\/link>", src, re.S)
        for s in ss:
          hrefs.append(s[1])
        #print(hrefs)
        for href in hrefs:
          url = href
          if url in dhrefs:
            continue
          dhrefs[url] = url.split('/')
          l = len(dhrefs[url])
          bkey = ""
          for i in range(l):
            if i+1 == l:
              break
            sed = dhrefs[url][i]
            if bkey == "":
              bkey = sed
            else:
              bkey = bkey + "/" + sed
            if bkey in slashes:
              slashes[bkey] = slashes[bkey] + 1
            else:
              slashes[bkey] = 1
            if not bkey in urls:
              urls[bkey] = []
            urls[bkey].append(url)
        try:
          for k in list(slashes.keys()):
            if re.match("^(http|https):(\/|\/\/|)$", k) is not None:
            #if k == "" or re.match("^(http|https):(\/|\/\/|)$", k) is not None:
              slashes.pop(k)
            else:
              for sk in slashes.keys():
                if k == sk:
                  continue
                elif re.match("^"+k, sk) is not None:
                  if slashes[sk] > slashes[k]:
                    slashes.pop(k)
                  break
        except Exception as ex:
          print("catch Exception in for k in list(slashes.keys()):", ex)
          return []
        sslashes = sorted(slashes.items(), key=lambda x:x[1], reverse=True)
        try:
          sui = sslashes[ui]
          return urls[sui[0]]
        except IndexError:
          return []

    def saveDriver(self, fn):
        logdir = os.getenv('LOG_DIR', self.basedir+"/log")
        if not os.path.exists(logdir):
          return
        dt = datetime.now().strftime("%Y%m%d%H%M%S")
        path = logdir + "/" + fn + "___" + dt
        try:
          self.driver.save_screenshot(path + ".png")
          with open(path + ".html", "w") as f:
              f.write(self.driver.page_source)
        except Exception as ex:
          print("catch Exception in saveDriver:",ex)

    def srcScrape(self, srcurl, doc, ui=0):
        doc = html.unescape(doc)
        doc = ' '.join(doc.splitlines())
        doc = doc.replace("<![CDATA[", "").replace("]]>", "")
        # title
        title = self.getElement(doc, "title")
        print("title: "+title)
        urls = self.getSiteList(doc, ui)
        if len(urls) == 0:
          print("not found urls:ui:",ui)
          return
        curl = self.driver.current_url
        domain = urlparse(curl).netloc
        nps = 0
        for url in urls:
            ret = re.search("^(\/|\.\/)", url, re.S)
            if ret:
                url = "https://" + domain + url
            print("url:"+url)
            self.dbm.cur.execute("select count(*) from links where link = ?", (url,))
            c = self.dbm.cur.fetchone()[0]
            if c >= 1:
                continue
            try:
                self.driver.get(url)
            except Exception as e:
                self.saveDriver(common_library.CommonLibrary.getSrcLocationString())
                print(e)
                print("driver get failed and continue:"+url)
                continue
            doc = self.driver.page_source
            try:
                tree = lxmlhtml.fromstring(doc)
            except Exception as e:
                print("lxmlhtml.fromstring error:",e)
                continue
            # make out
            out = "**"+title+"**\n"
            etitle = self.getElement(doc, "title")
            self.dbm.cur.execute("select count(*) from titles where title = ?", (etitle,))
            c = self.dbm.cur.fetchone()[0]
            if c >= 1:
                continue
            edesc = self.getElement(doc, "description")
            if edesc == "":
                edesc = self.getElement(doc, "h1")
            print(etitle,edesc)
            if edesc != "" and etitle != "":
                out = out + etitle + "\n" + edesc + "\n"
                out = out + url + "\n"
                print(out)
                common_library.CommonLibrary.toDiscord(os.getenv('DISCORD_WEBHOOK_URL'), out)
                # datetime
                cd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # insert
                self.dbm.cur.execute(
                    "insert into links(source_url, link, created, updated) \
                            values (?, ?, ?, ?)",
                    (srcurl, url, cd, cd),
                )
                self.dbm.cur.execute(
                    "insert into titles(source_url, title, created, updated) \
                            values (?, ?, ?, ?)",
                    (srcurl, etitle, cd, cd),
                )
                self.dbm.conn.commit()
                nps = nps + 1
                nut = time.time()
                if nut > self.cut+self.sim*60:
                  self.cmn.scpPutFile(self.shostname, self.dbpath, self.spath, ow=False)
                  self.cut = nut
        if nps == 0:
          self.srcScrape(srcurl, doc, ui+1)

