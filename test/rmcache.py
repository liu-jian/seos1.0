import salt.client

def rmcache(pro):
    client = salt.client.LocalClient()
    wbapp = "Active template Activity Admin Api Article Blog Circle Club Group Groups HealthKnowledge Help Home Lease Manage Message Meter NewVote OutdoorAct Payment PhoneApi Prefecture Public Setting Space Subject Task User Vote Wap Weibo"
    omsPath = "oms/Runtime/*"
    basicPath = "/var/www/wanbuSiteNew/"
    if pro == 'NewWanbu':        
        ret = client.cmd('www-2-05','cmd.run', ['sh %scleanwanbucache.sh %s' % (basicPath, wbapp)])
        print 'sh %scleanwanbucache.sh %s' % (basicPath, wbapp)
    elif pro == 'oms':
        ret = client.cmd('www-2-05','cmd.run', ['rm -rf %s%s' % (basicPath, omsPath)])
        print '%s%s' % (basicPath, omsPath)
    else:
	ret = "wrong path!"
    return ret

x = 'xx'
y = rmcache(x)
print y
