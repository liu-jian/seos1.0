#!/usr/bin/env python
#coding:utf-8
from flask import request
from . import app ,jsonrpc
import time, logging, utils
from auth import auth_login
import json, traceback,hashlib

#本模块提供用户信息的增删改查，以及 用户所在组，所有权限的查询

#创建用户
@jsonrpc.method('user.create')
@auth_login
def createuser(auth_info,*arg,**kwargs):
    username = auth_info['username']
    r_id = auth_info['r_id']    #string,  eg:  '1,2,3'
    if '1' not in r_id:         #角色id = 1 为sa组，超级管理员
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params'] 
        #api端对传入端参数验证
        if 'r_id' not in data:
            return json.dumps({'code': 1, 'errmsg': "must need a role!"})
        if not app.config['db'].if_id_exist('role',data['r_id'].split(',')):
            return json.dumps({'code': 1, 'errmsg': "Role not exist!"})
        if data['password'] != data['repwd']:
            return json.dumps({'code': 1, 'errmsg': "password equal repwd!"})
        elif len(data['password']) < 6:
            return json.dumps({'code': 1, 'errmsg': 'passwd must over 6 string !'})
        else:
            data.pop('repwd')    #传入的第二次密码字段不存在，需要删除
        data['password'] = hashlib.md5(data['password']).hexdigest()
        data['join_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        app.config['db'].execute_insert_sql('user', data)
        utils.write_log('api').info("%s create_user %s" % (username,data['username']))
        return json.dumps({'code': 0, 'result': 'create user %s success' % data['username']})
    except:
        utils.write_log('api').error("Create user error: %s" % traceback.format_exc())
        return json.dumps({'code': 1, 'errmsg': 'Create user failed'})

#通过传入的条件，通常为id，查询某条用户的信息，用于管理员修改用户信息
@jsonrpc.method('user.get')
@auth_login
def userinfo(auth_info,**kwargs):
    username = auth_info['username']
    try:
        output = ['id','username','name','email','mobile','is_lock','r_id']
        data=request.get_json()['params']
        fields = data.get('output',output) # api可以指定输出字段，如果没有指定output，就按默认output输出
        where = data.get('where',None)     # 前端传来的where条件
        utils.write_log('api').info("where=%s" % where) 
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].get_one_result('user', fields, where)
        if not result :
            return json.dumps({'code':1, 'errmsg':'user  not  exist'})
        utils.write_log('api').info('%s get_one_user info' % username) 
        return json.dumps({ 'code':0,'result':result})
    except:
        utils.write_log('api').error("Get users  error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'Get user  failed'})


#获取用户具体的信息，包括基本信息，所属组，所拥有的权限，用于用户个人中心的展示和个人资料更新
@jsonrpc.method('user.getinfo')
@auth_login
def userselfinfo(auth_info,**kwargs):
    username = auth_info['username']
    fields = ['id','username','name','email','mobile','is_lock','r_id']
    try:
        user = app.config['db'].get_one_result('user', fields, where={'username': username})
        if user.get('r_id', None):
            r_id = user['r_id'].split(',')
            rids = app.config['db'].get_results('role', ['id', 'name', 'p_id'], where={'id': r_id})
        else:
            rids = {}
        pids = []
        for x in rids:    
                pids += x['p_id'].split(',')   
        pids=list(set(pids))   #去重。通过用户名查到其角色id，在通过角色id取到用户的权限id
        user['r_id'] = [x['name'] for x in rids]   #将角色id转为角色名

        if pids:   #将用户的权限id转为权限名
            mypids = app.config['db'].get_results('power', ['id', 'name', 'name_cn', 'url'], where={'id': pids})
            user['p_id'] = dict([(str(x['name']), dict([(k, x[k]) for k in ('name_cn', 'url')])) for x in mypids])     #返回格式：{'git':{'name_cn':'git','url':'http://git.com'},......}
        else:
            user['p_id'] = {}

        utils.write_log('api').info('%s get_user_info' % username)
        return  json.dumps({'code': 0, 'user': user})
    except:
        logging.getLogger('api').error("Get users list error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get userinfo failed'})

#获取用户列表
@jsonrpc.method('user.getlist')
@auth_login
def userlist(auth_info,**kwargs):
    username = auth_info['username']
    r_id = auth_info['r_id']
    users = []
    fields = ['id','username','name','email','mobile','is_lock','r_id']
    try:
        if '1' not in r_id:
            return json.dumps({'code': 1,'errmsg':'只有管理员才有此权限' })
        #获取角色的id,name并存为字典如：{'1': 'sa', '2': 'php'}
        rids = app.config['db'].get_results('role', ['id', 'name'])
        rids = dict([(str(x['id']), x['name']) for x in rids])

        result = app.config['db'].get_results('user', fields)  #[{'id:1','name':'wd','r_id':'1,2,3'},{},{}]
        for user in result: #查询user表中的r_id,与role表生成的字典对比，一致则将id替换为name,如，"sa,php"
            user['r_id'] = ','.join([rids[x] for x in user['r_id'].split(',') if x in rids])  
            users.append(user)
        utils.write_log('api').info('%s get_all_users' % username)
        return  json.dumps({'code': 0, 'users': users,'count':len(users)})
    except:
        logging.getLogger().error("Get users list error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'获取用户列表失败'})

#更新用户信息
@jsonrpc.method('user.update')
@auth_login
def userupdate(auth_info, **kwargs):
    username = auth_info['username']
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        fields = ['name','username','email','mobile']
        if not where  or not app.config['db'].if_id_exist('user',where['id']):
            return json.dumps({'code':1, 'errmsg':'User not exist'})
        if '1' in auth_info['r_id']:   #管理员更新用户信息
            result = app.config['db'].execute_update_sql('user', data, where)
        else:                          #用户更新个人信息
            result = app.config['db'].execute_update_sql('user', data,where,fields)
        utils.write_log('api').info('%s Update user success!'%username)
        return  json.dumps({'code':0,'result':'Update user success' })
    except:
        utils.write_log('api').error("update error: %s"  % traceback.format_exc())
        return json.dumps({'code':1, 'errmsg':"Update user failed"}) 


#删除用户
@jsonrpc.method('user.delete')
@auth_login
def userdelete(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code':1,'errmsg':'you not admin,no power'})
    try: 
        data = request.get_json()['params']
        where = data.get('where',None)
        if not where:
            return json.dumps({'code':1,'errmsg':'must need a condition'})
        result = app.config['db'].execute_delete_sql('user', where)
        if not result:
            return json.dumps({'code':1,'errmsg':'User not exist'})
        utils.write_log('api').info('%s Delete user successed' % username)
        return json.dumps({'code':0,'result':'Delete user success '})
    except:
        utils.write_log('api').error('Delete user error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'Delete user failed'})

#修改密码
@app.route('/api/password',methods=['POST'])
@auth_login
def passwd(auth_info):
    if auth_info['code'] == 1:  
        return json.dumps(auth_info)
    username = auth_info['username']
    uid = int(auth_info['uid'])
    r_id = auth_info['r_id']
    try:
        data = request.get_json()
        if '1' in r_id and data.has_key('user_id'):   #管理员修改用户密码，需要传入user_id,不需要输入老密码
            user_id = data['user_id']
            if not app.config['db'].if_id_exist('user',user_id): 
                return json.dumps({'code':1,'errmsg':'User not exist'})
            password = hashlib.md5(data['password']).hexdigest()
            app.config['db'].execute_update_sql('user', {'password': password}, {'id': user_id})
        else:                  #用户自己修改密码，需要输入老密码
            if not data.has_key("oldpassword") :
                return json.dumps({'code':1,'errmsg':'need oldpassword'})
            oldpassword = hashlib.md5(data['oldpassword']).hexdigest()
            res = app.config['db'].get_one_result('user', ['password'], {'username': username})
            if res['password'] != oldpassword:
                return json.dumps({'code':1,'errmsg':'oldpassword wrong'})
            password = hashlib.md5(data['password']).hexdigest()
            app.config['db'].execute_update_sql('user', {'password': password}, {'username': username})

        utils.write_log('api').info('%s update user password success' % username)
        return json.dumps({'code':0,'result':'update user passwd success'})
    except:
        utils.write_log('api ').error('update user password error : %s' % traceback.format_exc())
        return json.dumps({' code':1,'errmsg':'update user password failed'})

