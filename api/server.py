#!/usr/bin/env python
#coding:utf-8
from flask import  request
from . import app , jsonrpc
from auth import auth_login
import json, traceback
import utils
import salt.client

output = ['id','serialnumber','assets_no','ethno','idc_id','cabinet_id','up_time','host','saltname','inner_ip','disk_usage','disk_total','num_cpus','mem_total','status_id','product_id','service_id','last_check_time','info']

#根据saltname和网卡信息查询服务器相关信息，并自动填充
def get_server_info(saltname, netcard):
    local = salt.client.LocalClient()
    info_basic = local.cmd(saltname, 'grains.item', ['host','ip4_interfaces'])
    info_disk = local.cmd(saltname, 'disk.usage')
    disk_usage = info_disk[saltname]['/']['capacity']
    res = {}
    res['inner_ip'] = info_basic[saltname]['ip4_interfaces'][netcard][0]
    res['hostname'] = info_basic[saltname]['host']
    res['disk_usage'] = disk_usage
    return res

#CMDB初始化函数
def cmdb_init():
    local = salt.client.LocalClient()
    #获取minion列表
    temp = local.cmd('*','cmd.run',['test.ping'])
    client_all = [k for k in temp.iterkeys()]
    #获取已有的minion列表
    res = app.config['db'].get_results('cmdb_server', ['saltname'])
    client_has = [i['saltname'] for i in res]   
    #需要判断获取列表长度
    client_get = list(set(client_all) - set(client_has))    
    #获取grains数据
    res = local.cmd(client_get,'grains.item',['mem_total','num_cpus','os','osrelease','serialnumber','host','id'],expr_form='list')
    info_disk = local.cmd(client_get, 'disk.usage', expr_form='list')
    #将数据插入数据库
    for v in res.itervalues():
        minion = v['id']
        v['disk_total'] = str(int(info_disk[minion]['/']['1K-blocks'])/1024/1024) + 'G'
        v['disk_usage'] = info_disk[minion]['/']['capacity']
        v['mem_total'] = str(int(v['mem_total'])/1000) + 'G'
        v['saltname'] = v['id']
        del v['id']
        data = v
        app.config['db'].execute_insert_sql('cmdb_server', data)
    
    if len(client_get) > 0:
        return True
    else:
        return False 

#CMDB初始化api
@jsonrpc.method('server.cmdbinit')
@auth_login
def server_create(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in  auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        res = cmdb_init()
        if res is False:            
            utils.write_log('api').info("%s init cmdb failed, no minion need insert" % username)
            return json.dumps({'code':1,'errmsg':'create server fail'})
        return json.dumps({'code':0,'result':'create server  scucess'})
    except:
        utils.write_log('api').error("create server error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'create server fail'})
    

#这里是关于CMDB服务器的增删改查及对应的属性id2name
@jsonrpc.method('server.create')
@auth_login
def server_create(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in  auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        if data.has_key('saltname') and data.has_key('ethno'):
            server_info = get_server_info(data['saltname'], data['ethno'])
            data.update(server_info)
        else:
            utils.write_log('api').info("%s create server fail,saltname or ethno is not found!" % username)
            return json.dumps({'code':1,'errmsg':'create server fail'})
        app.config['db'].execute_insert_sql('cmdb_server', data)
        utils.write_log('api').info("%s create server %s scucess" % (username,data['saltname']))
        return json.dumps({'code':0,'result':'create server %s scucess' % data['saltname']})
    except:
        utils.write_log('api').error("create server error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'create server fail'})


#转换字典
change_dict = {'idc_id','cabinet_id','product_id','service_id','status_id'}

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
        data = request.get_json()['params']
        fields = data.get('output', output)

        #将角色对应的p_id都转为name,最终返回的结果p_id的值都是name
        result = []
        #select查询结果以字典组合列表的方式返回[{},{}]
        res = app.config['db'].get_results('cmdb_server', fields)
        for x in res:
            for y in change_dict:
                temp = x[y]
                x[y] = id_name(x,y)
            result.append(x)

        utils.write_log('api').info('%s select server list success' % username)
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        utils.write_log('api').error("select server list error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get serverlist failed'})


@jsonrpc.method('server.get')    
@auth_login
def server_select(auth_info,**kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        fields = data.get('output', output)
        where = data.get('where', None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        #将角色对应的p_id都转为name,最终返回的结果p_id的值都是name
        res = app.config['db'].get_results('cmdb_server', fields, where)
        result = []
        for x in res:
            for y in change_dict:
                temp = x[y]
                x[y] = id_name(x,y)
            result.append(x)
        utils.write_log('api').info('%s get server data success' % username)
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        utils.write_log('api').error("select server list error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get serverlist failed'})    


@jsonrpc.method('server.update')
@auth_login
def role_update(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        if data.has_key('saltname') and data.has_key('ethno'):
            res = get_server_info(data['saltname'],data['ethno'])
            data['inner_ip'] = res['inner_ip']
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].execute_update_sql('cmdb_server', data, where)
        if not result:
            return json.dumps({'code':1, 'errmsg':'result is  null'})
        utils.write_log('api').info('%s update role success!' % username)
        return json.dumps({'code':0,'result':'update role scucess'})
    except:
        utils.write_log('api').error("update error: %s"  % traceback.format_exc())
        return  json.dumps({'code':1,'errmsg':"update role failed"})
        
    

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

