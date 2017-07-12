import argparse
import socket
import ssl

from fabric.api import env, sudo, execute, local
import os
from datetime import datetime, date

from templates import template_config, dhparam_4096_body, dhparam_2048_body


def date_duration(date1):
    if date.today() < date1.date():
        return abs((date1.date() - date.today()).days)
    else:
        return -1


def DeployEnv(**kwargs):
    env.hosts = kwargs['ip']
    env.port = kwargs['port']
    env.user = kwargs['login']
    env.password = kwargs['password']


def params_main():
    m = argparse.ArgumentParser(description='Make New LetsEncrypt Certificate', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    m.add_argument('--host', type=str, default=None, help='name od DNS A record to generate new certificate')
    m.add_argument('--type', type=str, default='web', help='type for new certificate (TYPE: web, imap, smtp)')
    m.add_argument('--ip', type=str, default='127.0.0.1', help='ip address of server')
    m.add_argument('--port', type=int, default=22, help='ssh port of server')
    m.add_argument('--login', type=str, default=None, help='ssh login of server')
    m.add_argument('--password', type=str, default=None, help='ssh password of server')
    m.add_argument('--nginx', type=int, default=0, help='modify nginx config (0 - False, 1 - True)')
    m.add_argument('--dur', type=str, default=None, help='web host appointment (ma or wm)')
    options = m.parse_args()

    options =  vars(options)
    options['nginx'] = bool(options.get('nginx'))
    return options


def mkdir_ifnot_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)


def mkdir_ifnot_exist_remote(path, **kwargs):
    DeployEnv(**kwargs)
    def create_dir():
        sudo('mkdir -p %s' % path)
    execute(create_dir, hosts=[kwargs.get('ip')])

def create_config_tmpl(**kwargs):
    DeployEnv(**kwargs)
    config_le_body = template_config % {
            'host': kwargs.get('host'),
            'bits': kwargs.get('bits'),
        }
    return config_le_body

def save_le_config(config_path, config_body, **kwargs):
    def executing():
        sudo('cat <<EOF > %s\n%s\nEOF' % (config_path, config_body))
    execute(executing, hosts=[kwargs.get('ip')])

def make_le_cert(cerbot, path, **kwargs):
    DeployEnv(**kwargs)
    def create_cert():
        sudo('%s --config %s certonly' % (cerbot, path))
    execute(create_cert, hosts=[kwargs.get('ip')])

def web_copy_cert(le_dir, web_ssl_path, **kwargs):
    host_cert_path = "".join([os.path.join(web_ssl_path, kwargs.get('host')), '.crt'])
    host_key_path = "".join([os.path.join(web_ssl_path, kwargs.get('host')), '.key'])
    DeployEnv(**kwargs)
    def copy_cert_key():
        sudo('mkdir -p %s' % (web_ssl_path))
        sudo('cat <<EOF > %s/dhparam.pem\n%s\nEOF' % (web_ssl_path, dhparam_4096_body))
        sudo('cp %s/live/%s/fullchain.pem %s' % (le_dir, kwargs.get('host'), host_cert_path))
        sudo('cp %s/live/%s/privkey.pem %s' % (le_dir, kwargs.get('host'), host_key_path))
    execute(copy_cert_key, hosts=[kwargs.get('ip')])


def imap_copy_cert(le_dir, imap_ssl_path, **kwargs):
    mkdir_ifnot_exist_remote(imap_ssl_path, **kwargs)

    # COPY CERT
    host_ca_path = "".join([os.path.join(imap_ssl_path, kwargs.get('host')), '.pem'])
    host_cert_path = "".join([os.path.join(imap_ssl_path, kwargs.get('host')), '.crt'])
    host_key_path = "".join([os.path.join(imap_ssl_path, kwargs.get('host')), '.key'])
    DeployEnv(**kwargs)
    def copy_cert_key():
        sudo('cp %s/live/%s/chain.pem %s' % (le_dir, kwargs.get('host'), host_ca_path))
        sudo('cp %s/live/%s/fullchain.pem %s' % (le_dir, kwargs.get('host'), host_cert_path))
        sudo('cp %s/live/%s/privkey.pem %s' % (le_dir, kwargs.get('host'), host_key_path))
    execute(copy_cert_key, hosts=[kwargs.get('ip')])

def smtp_copy_cert(le_dir, smtp_ssl_path, **kwargs):
    mkdir_ifnot_exist_remote(smtp_ssl_path, **kwargs)

    # COPY CERT
    host_ca_path = "".join([os.path.join(smtp_ssl_path, kwargs.get('host')), '.pem'])
    host_cert_path = "".join([os.path.join(smtp_ssl_path, kwargs.get('host')), '.crt'])
    host_key_path = "".join([os.path.join(smtp_ssl_path, kwargs.get('host')), '.key'])
    DeployEnv(**kwargs)
    def copy_cert_key():
        sudo('cat <<EOF > %s/dhparam_2048.pem\n%s\nEOF' % (smtp_ssl_path, dhparam_2048_body))
        sudo('cp %s/live/%s/chain.pem %s' % (le_dir, kwargs.get('host'), host_ca_path))
        sudo('cp %s/live/%s/fullchain.pem %s' % (le_dir, kwargs.get('host'), host_cert_path))
        sudo('cp %s/live/%s/privkey.pem %s' % (le_dir, kwargs.get('host'), host_key_path))
    execute(copy_cert_key, hosts=[kwargs.get('ip')])

def change_nginx_host(**kwargs):
    dur = kwargs.get('dur')
    host = kwargs.get('host')
    nginx_conf_path = '/etc/nginx'

    def change_config():
        sudo("perl -i -pe 's/%s.example.com/%s/g' %s/sites-available/%s.conf" % (dur, host, nginx_conf_path, dur))
        sudo("mv %s/sites-available/%s.conf %s/sites-available/%s.conf" % (nginx_conf_path, dur, nginx_conf_path, host))
        sudo("ln -s %s/sites-available/%s.conf %s/sites-enabled/%s.conf" % (nginx_conf_path, host, nginx_conf_path, host))
        sudo("/etc/init.d/nginx restart")

    execute(change_config, hosts=[kwargs.get('ip')])

def change_imap_host(**kwargs):
    host = kwargs.get('host')
    imap_conf_path = '/etc/dovecot/conf.d'

    def change_config():
        sudo("perl -i -pe 's/example.com/%s/g' %s/10-ssl.conf.backup" % (host, imap_conf_path))
        sudo("mv %s/10-ssl.conf.backup %s/10-ssl.conf" % (imap_conf_path, imap_conf_path))
        sudo("/etc/init.d/dovecot restart")

    execute(change_config, hosts=[kwargs.get('ip')])


def change_smtp_host(**kwargs):
    host = kwargs.get('host')
    smtp_conf_path = '/etc/exim4/conf.d'

    def change_config():
        sudo("perl -i -pe 's/example.com/%s/g' %s.bkp/main/03_exim4-config_tlsoptions" % (host, smtp_conf_path))
        sudo("mv %s.bkp/main/03_exim4-config_tlsoptions %s/main/03_exim4-config_tlsoptions" % (smtp_conf_path, smtp_conf_path))
        sudo("/etc/init.d/exim4 restart")

    execute(change_config, hosts=[kwargs.get('ip')])


def GetRecordCert(record=None, ssl_port=443):
    if record:
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(socket.socket(), server_hostname=record)
        # s.connect((record, 443))
        s.connect((record, ssl_port))
        return s.getpeercert()



def GetRecordExpired(record=None, ssl_port=443):
    if record:
        status_kwargs = {
                'record': record,
        }

        cert = GetRecordCert(record=record, ssl_port=ssl_port)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        status_kwargs['check_date'] = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        status_kwargs['notBefore'] = datetime.strptime(cert.get('notBefore'), '%b %d %H:%M:%S %Y %Z')
        status_kwargs['notAfter'] = datetime.strptime(cert.get('notAfter'), '%b %d %H:%M:%S %Y %Z')
        status_kwargs['date_durations'] = date_duration(status_kwargs['notAfter'])
        status_kwargs['organization'] = cert.get('issuer')[1][0][1]

        # return datetime.strptime(cert.get('notAfter'), '%b %d %H:%M:%S %Y %Z'), cert.get('issuer')[1][0][1]
        return date_duration(datetime.strptime(cert.get('notAfter'), '%b %d %H:%M:%S %Y %Z'))