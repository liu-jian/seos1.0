#--coding:utf-8--
from jinja2 import Template
import time
import salt.client
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#nginx负载均衡组自动配置类 locd_blance_upstream(节点名,配置列表)
class load_blance_upstream(object):
    def __init__(self, salt_name, upstream):
        self.upstream = upstream
        print self.upstream
        self.salt_name = salt_name
        self.template_path = "/srv/salt/jinja_template/nginx/"
        self.conf_path = "/srv/salt/conf/"
        self.local = salt.client.LocalClient()

    #生成nginx配置文件函数:make_conf(模板文件,生成文件)
    def make_conf(self, template_name, conf_name):
        file_template = self.template_path + template_name
        print file_template
        file_conf = self.conf_path + conf_name
        self.conf_name = conf_name
        with open(file_template) as f:
            conf_temp = Template(f.read())
            conf_content = conf_temp.render(upstream=self.upstream)
            f.close()
        with open(file_conf, 'w') as f:
            f.write(conf_content)
            f.close()

    #备份nginx配置文件函数path=(配置文件和备份文件路径)
    def bak_conf(self, client_path):
        self.client_path = client_path
        self.client_conf = self.client_path + self.conf_name
        bak_file_conf = self.client_path + 'conf_bak/' + self.conf_name + '_' + str(int(time.time()))
        x = self.local.cmd(self.salt_name,'cmd.run',['cp -R %s %s' % (self.client_conf, bak_file_conf)])
        if x[self.salt_name] == '':
            return True
        else:
            return False

    #利用salt的cp模块传输生成的nginx配置文件。
    def push_conf(self):
        x = self.local.cmd(self.salt_name,'cp.get_file',['salt://conf/%s' % self.conf_name, self.client_conf])
        if x[self.salt_name] == self.client_conf:
            return True
        else:
            return False
    
    #向nginx发出信号，使nginx重载配置文件。
    def refresh_conf(self):
        x = self.local.cmd(self.salt_name,'cmd.run',['kill -HUP `cat /usr/local/tengine/logs/nginx.pid`'])
        if x[self.salt_name] == '':
            return True
        else:
            return False
