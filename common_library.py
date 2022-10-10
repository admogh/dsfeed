import json
import re
import urllib
import os
import requests
import inspect
from lxml import html

class CommonLibrary:
    @staticmethod
    def getSrcLocationString():
        frame = inspect.currentframe().f_back
        s = os.path.basename(frame.f_code.co_filename).replace('.', '_')
        s = s + "__" + frame.f_code.co_name
        s = s + "__" + str(frame.f_lineno)
        return s
    @staticmethod
    def toDiscord(whurl, msg):
        mc = {
            "content": msg
        }
        requests.post(whurl, mc)
        return
        rh = {'Content-Type': 'application/json'} #;charset=utf-8'}
        rd = json.dumps({"content": msg}).encode("utf-8")
        req = urllib.request.Request(
                whurl, rd, 
                {"User-Agent": "curl/7.64.1", "Content-Type" : "application/json"},
                method='POST', headers=rh)
        try:
            with urllib.request.urlopen(req) as response:
                body = json.loads(response.read())
                headers = response.getheaders()
                status = response.getcode()
                print(headers)
                print(status)
                print(body)
        except urllib.error.URLError as e:
             print(e.reason)
