#coding:utf-8
from flask import request
from . import app 
import json,traceback
import utils


def auth_login(func):
    def wrapper(*arg, **kwargs):
        try:
            authorization = request.headers.get('authorization', 'None')
            res = utils.validate(authorization, app.config['passport_key'])
            res = json.loads(res)
            if int(res['code']) == 1:
                utils.write_log('api').warning("Request forbiden:%s" % res['errmsg'])
                return json.dumps({'code': 1, 'errmsg': '%s' % res['errmsg']})                                                         
        except:
            utils.write_log('api').warning("Validate error: %s" % traceback.format_exc())
            return json.dumps({'code': 1, 'errmsg': '验证异常'})
        return func(res, *arg, **kwargs)
    wrapper.__name__ = '%s_wrapper' % func.__name__
    return wrapper
