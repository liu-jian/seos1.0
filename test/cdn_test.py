import hashlib
import requests

def push_cdn():
    m = hashlib.md5()
    username = 'wanbu'
    password = "wanBu1234"
    dir = "http://www.wanbu.com.cn/"
    prefix="http://ccm.chinanetcenter.com/ccm/servlet/contReceiver?"

    md5pass_str = "%s%s%s" % (username, password, dir)
    m.update(md5pass_str)

    passwd = m.hexdigest()

    result = requests.post(prefix, data={'username': username, 'passwd': passwd, 'dir': dir})
    return result.text

