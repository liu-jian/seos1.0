# -*- encoding: utf-8 -*-
from flask import Flask                                                                        
from flask_jsonrpc import JSONRPC
import sys 
import utils
import db

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api')

# 导入自定义的各种配置参数，最终参数以字典形式返回
config = utils.get_config('api')

# 将自定义的配置文件全部加载到全局的大字典app.config中，可以在任意地方调用
app.config.update(config)

#实例化数据库类，并将实例化的对象导入配置
app.config['db'] = db.Cursor(config)

import login
import power
import role
import select
import user
import upgrade
