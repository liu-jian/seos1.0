#coding:utf-8
from flask import  request
from . import app , jsonrpc
from auth import auth_login
import json, traceback
import utils
import time
    
@jsonrpc.method('upgrade.svn')
@auth_login
def svn(auth_info,**kwargs):
    username = auth_info['username']
    if '29' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        path = data.get('path',None)
        where = data.get('where',None)
        utils.write_log('api').info('test svn %s' % data)
        result = utils.update_web(path)
        utils.write_log('api').info('%s svn update SRC:%s result:%s' % (username,path,result))
        res_html = result.replace('\n','<br>')
        data = {'result':res_html}
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result=app.config['db'].execute_update_sql('project_temp', data, where)
        if not result:
            return json.dumps({'code':1, 'errmsg':'data not exist'})
        utils.write_log('api').info("%s svn result into    DB successed" % username )
        return json.dumps({'code':0,'result':'update SRC success'})
    except:
        utils.write_log('api').error("svn update error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'svn update failed'})

@jsonrpc.method('upgrade.rsync')
@auth_login
def rsync(auth_info,**kwargs):
    username = auth_info['username']
    if '29' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        result = utils.push_rsync()
        utils.write_log('api').info('%s svn update SRC result:%s' % (username,result))
        return json.dumps({'code':0,'result':'push SRC success'})
    except:
        utils.write_log('api').error("rsync push error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'push rsync failed'})


@jsonrpc.method('upgrade.rmcache')
@auth_login
def rmcache(auth_info,**kwargs):
    username = auth_info['username']
    if '29' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not sa,no power' })
    try:
        data = request.get_json()['params']
        path = data.get('path',None)
        result = utils.rm_cache(path)
        utils.write_log('api').info('%s rm web cache:%s result:%s' % (username,path,result))
        return json.dumps({'code':0,'result':'rm cache success!'})
    except:
        utils.write_log('api').error("svn update error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'rm cache failed'})

@jsonrpc.method('upgrade.cdn')
@auth_login
def cdn(auth_info,**kwargs):
    username = auth_info['username']
    if '29' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not sa,no power' })
    try:
        data = request.get_json()['params']
        result = utils.push_cdn()
        utils.write_log('api').info('%s push cdn success result:%s' % (username,result))
        return json.dumps({'code':0,'result':'push cdn success'})
    except:
        utils.write_log('api').error("cdn push error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'push cdn failed'})



@jsonrpc.method('upgrade.create')
@auth_login
def upgrade_create(auth_info, **kwargs):
    username = auth_info['username']
    if '29' not in  auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        data['create_date'] = int(time.time())
        app.config['db'].execute_insert_sql('project_temp', data)
        utils.write_log('api').info("%s create project_temp %s scucess" % (username,data['name']))
        return json.dumps({'code':0,'result':'create project_temp %s scucess' % data['name']})
    except:
        utils.write_log('api').error("create project_temp error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'create project_temp fail'})

@jsonrpc.method('upgrade.getlist')
@auth_login
def upgrade_select(auth_info,**kwargs):
    username = auth_info['username']
    if '29' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not sa,no power' })
    try:
        output = ['id','name','path','create_date','comment']
        data = request.get_json()['params']
        fields = data.get('output', output)
        result = app.config['db'].get_results('project_temp', fields)
        for i in result:
            if i.has_key('create_date'):
                i['create_date'] = str(utils.get_time(int(i['create_date'])))
        utils.write_log('api').info('%s select project_temp list success' % username)
        return json.dumps({'code':0,'result':result,'count':len(result)})
    except:
        utils.write_log('api').error("select project_temp list error: %s"  %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get rolelist failed'})
        
@jsonrpc.method('upgrade.get')
@auth_login
def getbyid(auth_info,**kwargs):
    username = auth_info['username']                                                                                             
    try:
        output = ['id','name','path','create_date','comment','status','result']
        data = request.get_json()['params']
        fields = data.get('output', output)
        where = data.get('where',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result = app.config['db'].get_one_result('project_temp', fields, where)
        if not result:
            return json.dumps({'code':1, 'errmsg':'data not exist'})
        utils.write_log('api').info('%s select project_temp by id successed!' % username)
        return json.dumps({'code':0, 'result':result})
    except:
        utils.write_log('api').error("select project_temp by id error: %s" %  traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'get project_temp failed'})


@jsonrpc.method('upgrade.update')
@auth_login
def update(auth_info, **kwargs):
    username = auth_info['username']
    if '29' not in auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not admin,no power' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        data = data.get('data',None)
        if not where:
            return json.dumps({'code':1, 'errmsg':'must need a condition'})
        result=app.config['db'].execute_update_sql('project_temp', data, where)
        if not result: 
            return json.dumps({'code':1, 'errmsg':'data not exist'})
        utils.write_log('api').info("%s update project_temp successed" % username )
        return json.dumps({'code':0,'result':'update project_temp success'})
    except:
        utils.write_log('api').error("update error: %s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg':'update project_temp failed'})
    
        
        
@jsonrpc.method('upgrade.delete')
@auth_login
def delete(auth_info,**kwargs):
    username = auth_info['username']
    if '29' not in  auth_info['r_id']:
        return json.dumps({'code': 1,'errmsg':'you not sa,no power' })
    try:
        data = request.get_json()['params']
        where = data.get('where',None)
        if not where:
            return json.dumps({'code':1,'errmsg':'must need a condition'})
        result = app.config['db'].get_one_result('project_temp', ['name'], where)
        if not result:
            return json.dumps({'code':1,'errmsg':'data not exist'})
        app.config['db'].execute_delete_sql('project_temp', where)
        utils.write_log('api').info("%s delete project_temp  success" % username)
        return json.dumps({'code':0,'result':'delete project_temp success'})
    except:
        utils.write_log('api').error("delete project_temp error:%s" % traceback.format_exc())
        return json.dumps({'code':1,'errmsg': 'delete project_temp failed'})
