import subprocess

basicpath = "/var/www/wanbuSiteNew/"

def getPath(u_path):
    x = u_path.replace('\\','/')
    path = '%s%s' % (basicpath, x)
    return path

def update_web(path):
    path = getPath(path)
    res = subprocess.Popen('svn update %s' % path,shell=True,stdout=subprocess.PIPE)
    res_in = res.stdout.read()
    print res_in
	
path = 'do'

update_web(path)
