# -*- encoding: utf-8 -*-
import os,sys
import utils
from flask import Flask                                                                                                                
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')
app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

config = utils.get_config('web')

#将参数追加到app.config字典中，就可以随意调用了
app.config.update(config)



import demo,public,login
import private

