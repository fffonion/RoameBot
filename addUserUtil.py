#!/usr/bin/env python
# -*- coding:utf-8 -*-
# A ajax POSTer for roame.net
# Contributor:
#      fffonion        <fffonion@gmail.com>

__version__ = '1.00'

import urllib2
import os,ConfigParser,time,sys,re
def print_c(str):
    '''
    UTF-8 print module
    '''
    print(normstr(str.decode('utf-8')))

def normstr(str,errors='ignore'):
    return str.encode('cp936',errors)
def read_config(sec,key):
    '''
    Read config from file
    '''
    cf=ConfigParser.ConfigParser()
    cf.read(os.getcwdu()+os.path.sep+'config.ini')
    if cf.has_option(sec, key):
        val=cf.get(sec, key)
        if sys.platform=='win32':val=val.decode('gbk').encode('utf-8')
    else:
        val=''
    if val=='':return ''
    else:return val

def write_config(sec,key,val):
    '''
    Write config to file
    '''
    cf=ConfigParser.ConfigParser()
    cf.read(os.getcwdu()+os.path.sep+'config.ini')
    cf.set(sec, key,val)
    cf.write(open(os.getcwdu()+os.path.sep+'config.ini', "w"))
    
def del_option(sec,key):
    '''
    Delete an option
    '''
    cf=ConfigParser.ConfigParser()
    cf.read(os.getcwdu()+os.path.sep+'config.ini')
    cf.remove_option(sec, key)
    cf.write(open(os.getcwdu()+os.path.sep+'config.ini', "w"))

def mklogin():
    #ajax提交，返回均为json，直接用，分割算了
    name=raw_input(normstr('请输入用户名：'))
    if sys.platform=='win32':name=name.decode('gbk').encode('utf-8')
    pw=raw_input(normstr('请输入密码：'))
    data='m='+name+'&p='+pw
    req = urllib2.Request('http://www.roame.net/ajax.php?a=4098&_nc='+str(int(time.time())))
    resp=urllib2.urlopen(req,data)
    coo=resp.info().getheader('Set-Cookie')
    result=resp.read()[1:-1].split(',')
    if result[1]=='0':
        print_c('登录成功！已保存Cookie~')
        coo=re.findall('uid=(.+); exp.+upw=(.+); exp.+cmd=(.+); exp',str(coo))[0]
        coo='uid='+coo[0]+';upw='+coo[1]+';cmd='+coo[2]
        print_c('正在获取用户状态……'+'\b'*40),
        req = urllib2.Request('http://www.roame.net/ajax.php?a=769&_nc='+str(int(time.time())))
        req.add_header('Cookie',coo)
        resp=urllib2.urlopen(req,'i=1').read()
        resp=resp.replace('"','').decode('unicode-escape').split(',')
        print_c('获取成功！')
        #共88组:1,0状态码，3-49界面标签，50 [fffonion@163.com 51 fffonoon 52 成员级 53 2012-07-09
        #54 http:\/\/www.roame.net\/space\ 57 139107] 59 路人 66 [1993 67 7 68 9] 69 19
        #71 [2 (2) 72 60 (60) 73 20.6MB 74 2]
        #85 [701 86 0 87 0]]
        uname=resp[51]
        print_c('['+uname+'] - '+resp[57][:-1]+'\n用户标识：'+resp[50][1:]+'\n隶属组  ：'+resp[52]+\
            ' - '+resp[59]+'\n结算信息：'+resp[85][1:]+'积分, '+resp[86]+'LYB, '+resp[87][:-2]+'YLB')
        write_config('cookie','uname',uname)
        write_config('cookie',uname,coo)
        print_c('添加了'+uname)
    else:
        print_c('登陆失败'+(len(result)>2 and '：'+result[2][1:-1].decode('unicode-escape') or ''))
    print('-'*50)  
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    while True:
        mklogin()