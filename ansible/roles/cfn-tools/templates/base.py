import abc
import hvac
import logging
import os
import pwd
import requests
import socket
import subprocess
import urllib

from retry import retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class BaseCheck(object):
    __metaclass__ = abc.ABCMeta

    log_level = os.getenv('CHECKS_LOG_LEVEL', 'INFO')
    logging.basicConfig(level=logging.getLevelName(log_level), format='%(levelname)s | %(message)s')

    @abc.abstractmethod
    def check(self, **kwargs):
        pass


    def run(self, **kwargs):
        self.check(**kwargs)


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def systemd_unit_is_running(self, name):
        command = 'systemctl is-active {}'.format(name)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        result = process.stdout.read().rstrip()

        if result != 'active':
            logging.error('Service {} is not active'.format(name))
            raise Exception()
        logging.info(' * Service {} is active'.format(name))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def systemd_unit_is_enabled(self, name):
        command = 'systemctl list-unit-files | grep {} | grep enabled'.format(name)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        result = process.stdout.read().rstrip()

        if result == '':
            logging.error('Service {} is not enabled'.format(name))
            raise Exception()
        logging.info(' * Service {} is enabled'.format(name))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def ports_is_being_listened(self, ports, protocol = 'tcp'):
        not_opened = list()
        passed = True
        socket_type = socket.SOCK_STREAM if protocol == 'udp' else socket.SOCK_DGRAM

        for port in ports:
            sock = socket.socket(socket.AF_INET, socket_type)
            result = sock.connect_ex(('127.0.0.1', port))
            if result != 0:
                not_opened.append(port)
                passed = False

        if not passed:
            logging.error('{} ports check failed: {}'.format(protocol, not_opened))
            raise Exception()
        logging.info(' * {} ports have listeners: {}'.format(protocol, ports))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def http_check(self, url, expected_code):
        response_code = urllib.urlopen(url).getcode()
        if response_code == expected_code:
            logging.error('{} returned: {}, but expected {}'.format(url, response_code, expected_code))
            raise Exception()
        logging.info(' * Url {} returned {}'.format(url, expected_code))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def file_or_directory_exists(self, path):
        if not os.path.exists(path):
            logging.error('{} does not exist'.format(path))
            raise Exception()
        logging.info((' * {} string exists'.format(path)))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def file_contains(self, file, search_string):
        if not search_string in open(file).read():
            logging.error('{} string does not exist in {}'.format(search_string, file))
            raise Exception()
        logging.info((' * {} string exists in {}'.format(search_string, file)))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def user_exists(self, uid):
        try:
            pwd.getpwuid(uid)
        except KeyError:
            logging.error('User ID {} does not exist'.format(uid))
            raise Exception()
        logging.info(' * User ID {} exists'.format(uid))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def hostname_resolves(self, hostname):
        try:
            socket.gethostbyname(hostname)
        except Exception:
            logging.error('Hostname {} does not resolve'.format(hostname))
            raise Exception()
        logging.info(' * {} hostname resolves successfully.'.format(hostname))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def vault_initialised(self, vault_addr):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        vault = hvac.Client(url=vault_addr, verify=False)

        if not vault.sys.is_initialized():
            logging.error('Vault [{}] is not initialized.'.format(vault_addr))
            raise Exception()
        logging.info(' * Vault [{}] is initialized'.format(vault_addr))


    @retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
    def self_in_peers_list(self, peers_list_url, listening_port):
        ip = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4').text
        peer = '{}:{}'.format(ip, listening_port)
        peer_list = requests.get(peers_list_url).json()
        if peer not in peer_list:
            logging.error('Peer () not in list ({}).'.format(peer, peer_list))
            raise Exception()
        logging.info(' * Peer in list.')
