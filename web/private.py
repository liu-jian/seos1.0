#coding:utf-8
from __future__ import unicode_literals
from flask import Flask, render_template,session,redirect,request
from  . import app  
import requests,json 
import utils,urllib

headers = {"Content-Type": "application/json"}
data = {
        "jsonrpc": "2.0",
        "id":1,
}

def get_url():
    return "http://%s/api" % app.config['api_host']
	
@app.route('/upgradeapi', methods=['GET','POST'])
def upgradeapi():
    headers['authorization'] = session['author']
    formdata = dict((k,','.join(v)) for k,v in dict(request.form).items())
    if not formdata.has_key('id'):
        formdata['id'] = '0'
    method = formdata['method']
    data['method'] = "upgrade."+method
    formdata.pop('method')
    data['params']=formdata
    data['params']['where'] = {
        "id":int(formdata['id'])
        }
    utils.write_log('web').info(data)
    r = requests.post(get_url(),headers=headers,json=data)
    return r.text

@app.route('/confapi', methods=['GET','POST'])
def confapi():
    headers['authorization'] = session['author']
    formdata = dict((k,','.join(v)) for k,v in dict(request.form).items())
    if not formdata.has_key('id'):
        formdata['id'] = '0'
    method = formdata['method']
    data['method'] = "webservice."+method
    formdata.pop('method')
    data['params']=formdata
    data['params']['where'] = {
        "id":int(formdata['id'])
        }
    utils.write_log('web').info(data)
    r = requests.post(get_url(),headers=headers,json=data)
    return r.text

