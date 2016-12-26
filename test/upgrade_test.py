#!/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json
import requests

url = "http://127.0.0.1:3000/api"
#登录并获取token
def login(username,password):
        rep_url = "%s/login?username=%s&passwd=%s" % (url,username,password)
        r = requests.get(rep_url)      
        result = json.loads(r.content)
        if result['code'] == 0:
            token = result["authorization"]
            return json.dumps({'code':0,'token':token})
        else: 
            return json.dumps({'code':1,'errmsg':result['errmsg']})

def rpc():
        res=login('admin','123456')
        result = json.loads(res)
        if int(result['code']) ==0:
            token=result['token']
            headers = {'content-type': 'application/json','authorization':token}
            print token
        else:
            print  result
            return result
        #create请求
	'''
        data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.svn',      
                'id':'1',
                'params':{
                  'path':'do',
                  'id':'19',
                  'data':{'result':'xxxxx'},
                  'where':{'id':'19'}
                 }
            }
	'''
	'''
        data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.rsync',
                'id':'1',
                'params':{
                 }
            }
        '''
        '''
        data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.rmcache',
                'id':'1',
                'params':{
                  'path':'oms',
                 }
            }

	'''
        '''
        data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.create',
                'id':'1',
                'params':{
                  'name':'haoyou',
                  'path':'do',
                  'comment':'upgrade'
                 }
            }
        '''
	'''
        data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.getlist',
                'id':'1',
                'params':{
                  'output':['id','name','path','comment']
                 }
            }

	'''
	'''
        #getbyid请求
        data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.get',      
                'id':'1',
                'params':{
#                    'output':['id','name','path','result'],
                    'where':{'id':'17'}
                 }
        }
	'''
	'''
        data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.cdn',
                'id':'29',
                'params':{
                 }
            }
	'''
        #update project请求
        data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.update',
                'id':'1',
                'params':{
                    'data':{'name':'test update'},
                    'where':{'id':'25'}
                 }
        }

	'''
	data = {
                'jsonrpc':'2.0',
                'method': 'upgrade.delete',
                'id':'29',
                'params':{
                      'id':'20'
                 }
            }
	'''

        r = requests.post(url, headers=headers,json=data)

        print r.status_code
        print r.text 


rpc()
