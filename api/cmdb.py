#coding:utf-8
from flask import request
from . import app , jsonrpc
from auth import auth_login
import json, traceback
import utils

output={
'cmdb_idc':['id','name','name_cn','user_interface','phone','address','email'],
'cmdb_cabinet':['id','name','idc_id','power'],
'cmdb_server':['id','sn','assets_no','idc_id','cabinet_id','up_time','hostname','saltname','inner_ip','disk_total','num_cpus','mem_total','raid','status_id','product_id','service_id','last_check_time'],
'cmdb_status':['id','name'],
'cmdb_product':['id','name','name_cn','dev_interface','pm_interface','op_interface'],
'cmdb_servertype':['id','name'],
'cmdb_service':['id','name','name_cn'],
}



#CMDB的增删改查(单查、列表)

@jsonrpc.method('cmdb.create')    
@auth_login
def create(auth_info, **kwargs):
    username = auth_info['username']
    #判断是否具有相关权限
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        table = request.get_json()['table']
        app.config['db'].execute_insert_sql(table, data)
        utils.write_log('api').info("%s create cmdb %s %s success"  % (username,table,data['name']))
        return json.dumps({'code':0,'result':'create %s %s success' %  (table,data['name'])})
    except:
        utils.write_log('api').error('create power error:%s' % traceback.format_exc())
        return json.dumps({'code':1,'errmsg': 'create cmdb %s failed' % table})

@jsonrpc.method('cmdb.getlist')    
@auth_login
def create(auth_info, **kwargs):
    username = auth_info['username']
    #判断是否具有相关权限
    if '1' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        table = data.get('table',None)
        fields = data.get('output',output[table])
        result = app.config['db'].get_results(table, fields)
        utils.write_log('api').info('%s select %s list success' % (username,table))
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        utils.write_log('api').error("get list permission error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get %s list failed' % table})
	
	
	
	
	
	
