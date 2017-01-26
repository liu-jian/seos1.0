#!/bin/env python
# -*- encoding: utf-8 -*-
import os, os.path
import time,json         
import base64
import subprocess
import salt.client
import hashlib
import traceback
import ConfigParser
import logging,logging.config
import requests

work_dir = os.path.dirname(os.path.realpath(__file__))
def get_config(section=''):
    config = ConfigParser.ConfigParser()
    service_conf= os.path.join(work_dir, 'conf/service.conf')
    config.read(service_conf)
    conf_items = dict(config.items('common')) if config.has_section('common') else {}
    # print conf_items  #dict
    if section and config.has_section(section):
       conf_items.update(config.items(section))
    return conf_items

def write_log(loggername):
    log_conf= os.path.join(work_dir, 'conf/logger.conf')
    logging.config.fileConfig(log_conf)
    logger = logging.getLogger(loggername)
    return logger


def get_validate(username, uid, role, fix_pwd):
    t = int(time.time())
    return base64.b64encode('%s|%s|%s|%s|%s' % (username, t, uid, role, fix_pwd)).strip()

def validate(key, fix_pwd):
    t = int(time.time())
    key = base64.b64decode(key)
    x = key.split('|')
    if len(x) != 5:
        write_log('api').warning("token参数数量不足")
        return json.dumps({'code':1,'errmsg':'token参数不足'})
    if t > int(x[1]) + 2*60*60:
        write_log('api').warning("登录已经过期")
        return json.dumps({'code':1,'errmsg':'登录已过期'})
    if fix_pwd == x[4]:
        write_log('api').info("api认证通过")
        return json.dumps({'code':0,'username':x[0],'uid':x[2],'r_id':x[3]})
    else:
        write_log('api').warning("密码不正确")
        return json.dumps({'code':1,'errmsg':'密码不正确'})


def update_web(path):
    basicpath = "/var/www/wanbuSiteNew/"
    x = path.replace('\\','/')
    path = '%s%s' % (basicpath, x)
    res = subprocess.Popen('svn update %s' % path,shell=True,stdout=subprocess.PIPE)
    res_in = res.stdout.read()
    return res_in


def push_rsync():
    client = salt.client.LocalClient()
    exc_conf = "/etc/rsync/excluded.conf"
    path = "/var/www/wanbuSiteNew/"
    ret = client.cmd('www*','cmd.run', ['rsync -aP --progress --exclude-from="%s"  root@192.168.1.249:%s %s' % (exc_conf,path,path)])
    return ret

def get_time(int_time):
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(int_time)
    dt = time.strftime(format, value)
    return dt


def rm_cache(pro):
    client = salt.client.LocalClient()
    wbapp = "Active template Activity Admin Api Article Blog Circle Club Group Groups HealthKnowledge Help Home Lease Manage Message Meter NewVote OutdoorAct Payment PhoneApi Prefecture Public Setting Space Subject Task User Vote Wap Weibo"
    omsPath = "oms/Runtime/*"
    basicPath = "/var/www/wanbuSiteNew/"
    if pro == 'NewWanbu':
        ret = client.cmd('www*','cmd.run', ['sh %scleanwanbucache.sh %s' % (basicPath, wbapp)])
    elif pro == 'oms':
        ret = client.cmd('www*','cmd.run', ['rm -rf %s%s' % (basicPath, omsPath)])
    else:
        ret = "wrong path!"
    return ret


def push_cdn():
    m = hashlib.md5()
    username = 'wanbu'
    password = "wanBu1234"
    dir = "http://www.wanbu.com.cn/"
    prefix="http://ccm.chinanetcenter.com/ccm/servlet/contReceiver?"

    md5pass_str = "%s%s%s" % (username, password, dir)
    m.update(md5pass_str)

    passwd = m.hexdigest()

    result = requests.post(prefix, data={'username': username, 'passwd': passwd, 'dir': dir})
    return result.text


