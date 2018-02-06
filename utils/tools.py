# -*- coding:utf-8 -*-
from config import *
from utils.requests import *
import json
def gsub(get, self, output):
    output = re.sub(get, self, output)
    return output
def AI(self, user, id):
    sessionData = AIAPI.getSessionData(id)
    self = re.sub(bot_username, "", self) 
    AIAPI.setBotPredicate('user', user)
    resposta = AIAPI.respond(self, id)
    return resposta
def bash(self, cmd):
  if self == '/git_':
    cmd = "git " + cmd
  comando = re.sub(self, "", cmd)
  comando = re.sub('—', '--', comando)
  shell = subprocess.check_output(comando, shell=True)
  return shell.decode('utf8')
def uptime(self):
    uptime = datetime.datetime.now().strftime(self)
    return uptime
def conversor(self):
    if self < 1000:
        return '%i' % self + 'B'
    elif 1000 <= self < 1000000:
        return '%.2f' % float(self/1000) + 'KB'
    elif 1000000 <= self < 1000000000:
        return '%.2f' % float(self/1000000) + 'MB'
    elif 1000000000 <= self < 1000000000000:
        return '%.2f' % float(self/1000000000) + 'GB'
    elif 1000000000000 <= self:
        return '%.2f' % float(self/1000000000000) + 'TB'