import json
import re
import urllib
import os
import requests
import inspect
from lxml import html
import scp
import paramiko

class CommonLibrary:
  def __init__(self, remoteHost=None):
    if remoteHost is not None and remoteHost != "":
      config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
      ssh_config = paramiko.SSHConfig()
      ssh_config.parse(open(config_file, 'r'))
      lkup = ssh_config.lookup(remoteHost)
      #print(lkup)
      self.ssh = paramiko.SSHClient()
      self.ssh.load_system_host_keys()
      self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy) # sftp
      self.ssh.connect(
          lkup['hostname'],
          username=lkup['user'],
          port=lkup['port'],
          key_filename=lkup['identityfile'],
      )
      self.ssh_hostname = lkup['hostname']
      self.ssh_user = lkup['user']
      self.ssh_port = lkup['port']
      self.ssh_identityfile = lkup['identityfile']

      self.scp = scp.SCPClient(self.ssh.get_transport())
      # sftp
      self.sftp = self.ssh.open_sftp()

  def scpGetFile(self, host, src, dst):
    print(host, src, dst)
    if hasattr(self, "scp"):
      try:
        paths = src.split('/')
        pathdir = ""
        for ipath in range(len(paths)):
          if ipath == len(paths) - 1:
            break
          if pathdir != "":
            pathdir = pathdir + '/'
          pathdir = pathdir + paths[ipath]
        print(paths, pathdir)
        if pathdir == '~':
          pathdir = "/home/" + self.ssh_user
        self.sftp.chdir(pathdir)
        #attrs = self.sftp.stat(paths[1])
        attrs = self.sftp.stat(paths[len(paths)-1])
        rst = attrs.st_mtime
        lst = os.stat(dst).st_mtime
        if rst > lst:
          self.scp.get(src, dst)
      except scp.SCPException as ex:
        # Assumed that No such file or directory and ignored
        print(ex)

  def scpPutFile(self, host, src, dst):
    if hasattr(self, "scp"):
      self.scp.put(src, dst)

  def __del__(self):
    if hasattr(self, "scp"):
      self.scp.close()
      self.ssh.close()

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
