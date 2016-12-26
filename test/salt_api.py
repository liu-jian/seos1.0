import salt.client
client = salt.client.LocalClient()
exc_conf = "/etc/rsync/excluded.conf"
path = "/var/www/wanbuSiteNew/"
ret = client.cmd('www*','cmd.run', ['rsync -aP --progress --exclude-from="%s"  root@192.168.1.249:%s %s' % (exc_conf,path,path)])

print ret
