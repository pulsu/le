class _Config(object):
    pass

class ConfigDomains(_Config):
    domains = {
        'ma.domain.com': {
            'type': 'web',
            'ssl_port': 443,
            'ip': '192.168.0.1',
            'port': 7521,
            'login': 'user11',
            'password': '********',
        },
        'wm.domain.com': {
            'type': 'web',
            'ssl_port': 443,
            'ip': '192.168.0.1',
            'port': 7521,
            'login': 'user11',
            'password': '********'
        },
        'imap.domain.com': {
            'type': 'imap',
            'ssl_port': 993,
            'ip': '192.168.0.1',
            'port': 7521,
            'login': 'user11',
            'password': '********'
        },
        'smtp.domain.com': {
            'type': 'smtp',
            'ssl_port': 465,
            'ip': '192.168.0.1',
            'port': 7521,
            'login': 'user11',
            'password': '********'
        },
    }


class ConfigVar(ConfigDomains):
    LocalPathDirs = {
        'le_config_path': '/etc/letsencrypt/config'
    }

    LE_config_dir = '/etc/letsencrypt'
    WebPathDirs = '/etc/ssl/web'
    ImapPathDirs = '/etc/ssl/imap'
    SmtpPathDirs = '/etc/ssl/smtp'

    CertBot = '/usr/bin/certbot'

    WebBits = 4096
    ImapBits = 2048
    SmtpBits = 2048
