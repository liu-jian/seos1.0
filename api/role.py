#!/usr/bin/env python
#coding:utf-8
from flask import  request
from . import app , jsonrpc
from auth import auth_login
import json, traceback
import utils


#这里是关于用户角色的增删改查及组对应的权限id2name

@jsonrpc.method('role.create')
@auth_login
def role_create(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in  auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        if not data.has_key('p_id'):     
            return json.dumps({'code':1,'errmsg':'must hava p_id'})
        if not app.config['db'].if_id_exist('power',data['p_id'].split(',')):     
            return json.dumps({'code':1,'errmsg':'p_id not exist'})
        app.config['db'].execute_insert_sql('role', data)
        utils.write_log('api').info("%s create role %s scucess" % (username,data['name']))
        return json.dumps({'code':0,'result':'create role %s scucess' % data['name']})
    except:
        utils.write_log('api').error("create role error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'create role fail'})

@jsonrpc.method('role.getlist')
@auth_login
def role_select(auth_info,**kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        output = ['id','name','name_cn','p_id','info']
        data = request.get_json()['params']
        fields = data.get('output', output)
          
        #查询权限表，生产id2name的字典
        result = app.config['db'].get_results('power', ['id', 'name'])
        power_name = dict([(str(x['id']), x['name']) for x in result])

        #将角色对应的p_id都转为name,最终返回的结果p_id的值都是name
        result = []
        res = app.config['db'].get_results('role', fields)
        for x in res:
            p_name = [power_name[p_id] for p_id in x['p_id'].split(',') if p_id in power_name]
            x['p_id'] = ','.join(p_name)  #将原有x['p_id']中的id转为name
            result.append(x)

        utils.write_log('api').info('%s select role list success' % username)
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        utils.write_log('api').error("select role list error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get rolelist failed'})

@jsonrpc.method('role.get')
@auth_login
def role_get(auth_info, **kwargs):
    username = auth_info['username']
    try:
        output = ['id','name','name_cn','p_id','info']
        data = request.get_json()['params']
        fields = data.get('output', output)
        where = data.get('where',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].get_one_result('role', fields, where)
        if not result :
            return json.dumps({'code':1, 'errmsg':'result is null'})
        else:
            utils.write_log('api').info("%s select role by id success" % username)
            return json.dumps({'code':0,'result':result})
    except:
        utils.write_log('api').error('select role by id error: %s'  % traceback.format_exc())
        return  json.dumps({'code':1,'errmsg ':'get role failed'})

@jsonrpc.method('role.update')
@auth_login
def role_update(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].execute_update_sql('role', data, where)
        if not result:
            return json.dumps({'code':1, 'errmsg':'result is  null'})
        utils.write_log('api').info('%s update role success!' % username)
        return json.dumps({'code':0,'result':'update role scucess'})
    except:
        utils.write_log('api').error("update error: %s"  % traceback.format_exc())
        return  json.dumps({'code':1,'errmsg':"update role failed"})

@jsonrpc.method('role.delete')
@auth_login
def role_delete(auth_info,**kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].execute_delete_sql('role', where)
        if not result :
            return json.dumps({'code':1, 'errmsg':'result is null'})
        utils.write_log('api').info('%s delete role successed' % username)
        return json.dumps({'code':0,'result':'delete role scucess'})
    except:
        utils.write_log('api').error('delete role error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete role failed'}) 

