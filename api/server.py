#!/usr/bin/env python
#coding:utf-8
from flask import  request
from . import app , jsonrpc
from auth import auth_login
import json, traceback
import utils


#这里是关于CMDB服务器的增删改查及对应的属性id2name

@jsonrpc.method('server.create')
@auth_login
def server_create(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in  auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        app.config['db'].execute_insert_sql('cmdb_server', data)
        utils.write_log('api').info("%s create server %s scucess" % (username,data['saltname']))
        return json.dumps({'code':0,'result':'create server %s scucess' % data['saltname']})
    except:
        utils.write_log('api').error("create server error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'create server fail'})


#转换字典
change_dict = {'idc_id','cabinet_id','product_id','service_id','status_id','servertype_id'}

#转换函数
def id_name(x,y):
    table = "cmdb_" + y.replace('_id','')
    result_t = app.config['db'].get_results(table, ['id','name'])
    name_dict = dict([(str(z['id']), z['name']) for z in result_t])
    name_t = [name_dict[i] for i in str(x[y]).split(',') if i in name_dict]
    res = ','.join(name_t)
    return res

@jsonrpc.method('server.getlist')
@auth_login
def server_select(auth_info,**kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        output = ['id','servertype_id','sn','assets_no','idc_id','cabinet_id','up_time','hostname','saltname','inner_ip','mac_address','server_disk','server_cpu','server_mem','raid','status_id','product_id','service_id','last_check_time']
        data = request.get_json()['params']
        fields = data.get('output', output)

        #将角色对应的p_id都转为name,最终返回的结果p_id的值都是name
        result = []
        res = app.config['db'].get_results('cmdb_server', fields)
        for x in res:
            utils.write_log('api').info('x is ::%s' % x)
            for y in change_dict:
                temp = x[y]
                utils.write_log('api').info('x[y] is ::%s' % temp)
                x[y] = id_name(x,y)
            result.append(x)

        utils.write_log('api').info('%s select server list success' % username)
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        utils.write_log('api').error("select server list error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get serverlist failed'})



@jsonrpc.method('server.delete')
@auth_login
def server_delete(auth_info,**kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].execute_delete_sql('server', where)
        if not result :
            return json.dumps({'code':1, 'errmsg':'result is null'})
        utils.write_log('api').info('%s delete server successed' % username)
        return json.dumps({'code':0,'result':'delete server scucess'})
    except:
        utils.write_log('api').error('delete server error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete server failed'}) 

