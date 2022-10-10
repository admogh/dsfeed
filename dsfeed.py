import re
import os
import inspect
from lxml import html as lxmlhtml
import html
from lxml import etree
from urllib.parse import urlparse
import emoji 

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

    def __init__(self, cdriver):
        self.cdriver = cdriver
        self.driver = cdriver.driver

    #@classmethod
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
        print(hrefs)
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
        sslashes = sorted(slashes.items(), key=lambda x:x[1], reverse=True)
        print(sslashes)
        try:
          sui = sslashes[ui]
          return urls[sui[0]]
        except IndexError:
          return []
