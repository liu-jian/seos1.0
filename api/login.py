#!/usr/bin/env python
#coding:utf-8
from flask import Flask, request
from . import app
import  utils
import json,time,traceback,hashlib

#用户登录验证，并生成token
@app.route('/api/login', methods=['GET'])
def login():
        try:
            username = request.args.get('username', None)
            passwd = request.args.get('passwd', None)
            passwd = hashlib.md5(passwd).hexdigest()
            if not (username and passwd):
                return json.dumps({'code': 1, 'errmsg': "need username or passwd"})
            result = app.config['db'].get_one_result('user', ['id', 'username', 'password', 'r_id', 'is_lock'], {'username': username})
            if not result:
                return json.dumps({'code': 1, 'errmsg': "user is not exist"})
            if result['is_lock'] == 1:
                return json.dumps({'code': 1, 'errmsg': "user is lock"})
            if passwd == result['password']:
                data = {'last_login': time.strftime('%Y-%m-%d %H:%M:%S')}
                app.config['db'].execute_update_sql('user', data, {'username': username})
                token = utils.get_validate(result['username'], result['id'], result['r_id'], app.config['passport_key'])
                utils.write_log('api').info("%s login sucess" % username)
                return json.dumps({'code': 0, 'authorization': token})
            else:
                return json.dumps({'code': 1, 'errmsg': "passwd is wrong"})
        except:
            utils.write_log('api').error("login error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': "login fail"})


