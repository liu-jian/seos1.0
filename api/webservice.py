#!/usr/bin/env python
#coding:utf-8
from flask import  request
from . import app , jsonrpc
from auth import auth_login
import json, traceback
import utils,utils_two

output = ['id','server_id','weight','status_id']

#配置列表upstream生成函数
def get_upstream():
    output_service = ['server_id','weight','status_id']
    output_server = ['inner_ip']
    res = app.config['db'].get_results('service_upstream', output_service)
    upstream = []
    for x in res:
        if x['status_id'] == '1':
            where = {}
            where['id'] = int(x['server_id'])
            res_server = app.config['db'].get_one_result('cmdb_server', output_server, where)
            x['host'] = res_server['inner_ip'] + ":80"
            x['status'] = ""
            x['weight'] = str(x['weight'])
            x.pop('server_id')
            x.pop('status_id')
            upstream.append(x)
        else:
            continue
    return upstream

#nginx配置生成，备份，传输，重载生效接口
@jsonrpc.method('webservice.change_conf')
@auth_login
def change_conf(auth_info,**kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        #生成upstream配置列表函数
        upstream = get_upstream()
        utils.write_log('api').info(upstream)
        if len(upstream) == 0:
            return json.dumps({'code':1,'errmsg':'At least change one live web server status!'})
        else:
            go_conf = utils_two.load_blance_upstream('lb_www_14',upstream)
            go_conf.make_conf('nginx_tempalte.conf', 'nginx.conf')
            utils.write_log('api').info("make nginx conf success!")
            if go_conf.bak_conf('/usr/local/tengine/conf/') is True:
                if go_conf.push_conf() is True:
                    if go_conf.refresh_conf() is True:
                        utils.write_log('api').info('%s change nginx conf success' % username)
                        return json.dumps({'code':0,'result':'change conf success!'})
                    else:
                        utils.write_log('api').info('%s reload nginx conf faild' % username)
                        return json.dumps({'code':1,'errmsg':'reload nginx conf faild!'})
                else:
                    utils.write_log('api').info('%s push nginx conf faild' % username)
                    return json.dumps({'code':1,'errmsg':'push nginx conf faild!'})
            else:
                utils.write_log('api').info('%s bak nginx conf faild' % username)
                return json.dumps({'code':1,'errmsg':'bak nginx conf faild!'})
    except:
        utils.write_log('api').error("rsync push error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'push rsync failed'})


#网站负载控制：创建接口
@jsonrpc.method('webservice.create')
@auth_login
def server_create(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in  auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        utils.write_log('api').info(data)
        app.config['db'].execute_insert_sql('service_upstream', data)
        utils.write_log('api').info("%s create webservice scucess" % username)
        return json.dumps({'code':0,'result':'create webservice scucess'})
    except:
        utils.write_log('api').error("create webservice error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'create webservice fail'})

#webservice列表展示查询api
@jsonrpc.method('webservice.getlist')
@auth_login
def webservice_getlist(auth_info,**kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        fields = data.get('output', output)
        #将角色对应的p_id都转为name,最终返回的结果p_id的值都是name
        result = app.config['db'].get_results('cmdb_status', ['id', 'name'])
        status_name = dict([(str(x['id']), x['name']) for x in result])
        result = []
        #select查询结果以字典组合列表的方式返回[{},{}],并且status_id转换为name
        res = app.config['db'].get_results('service_upstream', fields)
        for x in res:
            #status_id转换为name
            s_name = [status_name[status_id] for status_id in str(x['status_id']).split(',') if status_id in status_name]
            x['status_id'] = ','.join(s_name)
            where = {}
            where['id'] = int(x['server_id'])
            fields = ['inner_ip','saltname']
            res_server = app.config['db'].get_one_result('cmdb_server', fields, where)
            x['ip'] = res_server['inner_ip']
            x['saltname'] = res_server['saltname']
            result.append(x)

        utils.write_log('api').info('%s select webservice list success' % username)
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        utils.write_log('api').error("select webservice list error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get webservice list failed'})


#获取单条数据，用于详情展示和更新列表生成
@jsonrpc.method('webservice.get')    
@auth_login
def webservice_select(auth_info,**kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        fields = data.get('output', output)
        where = data.get('where', None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].get_one_result('service_upstream', fields, where)
        if not result :
            return json.dumps({'code':1, 'errmsg':'result is null'})
        else:
            utils.write_log('api').info("%s select service_upstream by id success" % username)
            return json.dumps({'code':0,'result':result})
    except:
        utils.write_log('api').error('select service_upstream by id error: %s'  % traceback.format_exc())
        return  json.dumps({'code':1,'errmsg ':'get service_upstream failed'})

#用于更新数据表
@jsonrpc.method('webservice.update')
@auth_login
def webservice_update(auth_info, **kwargs):
    username = auth_info['username']
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].execute_update_sql('service_upstream', data, where)
        if not result:
            return json.dumps({'code':1, 'errmsg':'result is  null'})
        utils.write_log('api').info('%s update service_upstream success!' % username)
        return json.dumps({'code':0,'result':'update service_upstream scucess'})
    except:
        utils.write_log('api').error("update error: %s"  % traceback.format_exc())
        return  json.dumps({'code':1,'errmsg':"update service_upstream failed"})

#标准删除接口。
@jsonrpc.method('webservice.delete')
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
        result = app.config['db'].execute_delete_sql('service_upstream', where)
        if not result :
            return json.dumps({'code':1, 'errmsg':'result is null'})
        utils.write_log('api').info('%s delete service_upstream successed' % username)
        return json.dumps({'code':0,'result':'delete service_upstream scucess'})
    except:
        utils.write_log('api').error('delete service_upstream error: %s' %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'delete service_upstream failed'}) 