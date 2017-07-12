import os
from fabric.api import sudo, execute,env
from helpers import DeployEnv, mkdir_ifnot_exist, create_config_tmpl, save_le_config, make_le_cert, web_copy_cert, change_nginx_host, imap_copy_cert, change_imap_host, smtp_copy_cert, change_smtp_host, GetRecordExpired
from config import ConfigVar

class CreateNewCert():
    def __init__(self, **kwargs):
        self.host = host = kwargs.get('host')
        self.type = type = kwargs.get('type')
        self.ip = ip = kwargs.get('ip')
        self.port = port = kwargs.get('port')
        self.login = login = kwargs.get('login')
        self.password = password = kwargs.get('password')

        if host and login and password:
            for p in ConfigVar.LocalPathDirs.itervalues():
                mkdir_ifnot_exist(p)

            if type == 'web':
                self.make_web_cert(**kwargs)
            elif type == 'imap':
                self.make_imap_cert(**kwargs)
            elif type == 'smtp':
                self.make_smtp_cert(**kwargs)

    def make_web_cert(self, **kwargs):
        kwargs['bits'] = ConfigVar.WebBits
        config_body = create_config_tmpl(**kwargs)
        config_path = "".join([os.path.join(ConfigVar.LocalPathDirs.get('le_config_path'), kwargs.get('host')), '.conf'])
        save_le_config(config_path, config_body, **kwargs)
        make_le_cert(ConfigVar.CertBot, config_path, **kwargs)
        web_copy_cert(ConfigVar.LE_config_dir, ConfigVar.WebPathDirs, **kwargs)

#        if kwargs.get('nginx') and (kwargs.get('dur') == 'ma' or kwargs.get('dur') == 'wm'):
#            change_nginx_host(**kwargs)

    def make_imap_cert(self, **kwargs):
        kwargs['bits'] = ConfigVar.ImapBits
        config_body = create_config_tmpl(**kwargs)
        config_path = "".join([os.path.join(ConfigVar.LocalPathDirs.get('le_config_path'), kwargs.get('host')), '.conf'])
        save_le_config(config_path, config_body, **kwargs)
        make_le_cert(ConfigVar.CertBot, config_path, **kwargs)
        imap_copy_cert(ConfigVar.LE_config_dir, ConfigVar.ImapPathDirs, **kwargs)
#        change_imap_host(**kwargs)

    def make_smtp_cert(self, **kwargs):
        kwargs['bits'] = ConfigVar.SmtpBits
        config_body = create_config_tmpl(**kwargs)
        config_path = "".join([os.path.join(ConfigVar.LocalPathDirs.get('le_config_path'), kwargs.get('host')), '.conf'])
        save_le_config(config_path, config_body, **kwargs)
        make_le_cert(ConfigVar.CertBot, config_path, **kwargs)
        smtp_copy_cert(ConfigVar.LE_config_dir, ConfigVar.SmtpPathDirs, **kwargs)
#        change_smtp_host(**kwargs)


class ReNewCert():
    def __init__(self):
        for h in ConfigVar.domains:
            config_path = "".join([os.path.join(ConfigVar.LocalPathDirs.get('le_config_path'), h), '.conf'])
            kwargs = ConfigVar.domains.get(h)
            kwargs['host'] = h
            type = ConfigVar.domains.get(h).get('type')
            ssl_port = ConfigVar.domains.get(h).get('ssl_port')
            host_expire = GetRecordExpired(h, ssl_port)
            if host_expire == 14:
                make_le_cert(ConfigVar.CertBot, config_path, **kwargs)
            elif host_expire == 5:
                if type == 'web':
                    web_copy_cert(ConfigVar.LE_config_dir, ConfigVar.WebPathDirs, **kwargs)
                    execute(self.restart_service, name='nginx', kwargs=kwargs, hosts=[kwargs.get('ip')])
                elif type == 'imap':
                    imap_copy_cert(ConfigVar.LE_config_dir, ConfigVar.ImapPathDirs, **kwargs)
                    execute(self.restart_service, name='dovecot', kwargs=kwargs, hosts=[kwargs.get('ip')])
                elif type == 'smtp':
                    smtp_copy_cert(ConfigVar.LE_config_dir, ConfigVar.SmtpPathDirs, **kwargs)
                    execute(self.restart_service, name='exim4', kwargs=kwargs, hosts=[kwargs.get('ip')])

    def restart_service(self, name, kwargs):
        DeployEnv(**kwargs)
        sudo('/etc/init.d/%s restart' % name)
