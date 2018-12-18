"""A basic modem with an IP address."""

import json
import logging
import requests
from bs4 import BeautifulSoup
from surfboard_status.modems.channel import DownstreamDocsisChannel, UpstreamDocsisChannel

logger = logging.getLogger(__name__)


class Modem(object):
    """
    A basic modem with a web interface

    Args:
        ip_address (str): The IP address of the modem's web interface
        port (int): The port number (default: 80 (http))
        ssl (bool): use ssh
        verify (bool or str): As one would pass to requests for SSL (default: True)

    """

    def __init__(self, ip_address, port=80, ssl=False, verify=True):
        if not ip_address:
            raise ValueError('An IP Address is required.')

        self.ip_address = ip_address
        self.port = int(port)
        self.ssl = ssl
        self.verify = verify

        self.scheme = 'https' if self.ssl else 'http'
        self.url = f'{self.scheme}://{self.ip_address}:{self.port}'

        self.hardware_version = None
        self.software_version = None
        self.mac_addr = None
        self.serial_number = None
        self.uptime = 0

        self.downstream_channels = []
        self.upstream_channels = []

        self._session = None

    def __repr__(self):
        return f'SurfBoard Modem v{self.hardware_version} (Software {self.software_version}, ' \
            f'Serial Number {self.serial_number}): Up {self.uptime} seconds'

    def to_json(self):
        data = {
            'downstream_channels': [c.to_json() for c in self.downstream_channels],
            'upstream_channels': [c.to_json() for c in self.upstream_channels],
            'info': {
                'hardware_version': self.hardware_version,
                'software_version': self.software_version,
                'mac_addr': self.mac_addr,
                'serial_number': self.serial_number,
                'uptime': self.uptime,
                'downstream_channel_count': self.downstream_channel_count,
                'upstream_channel_count': self.upstream_channel_count
            }
        }
        return data

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
        return self._session

    def fetch_path(self, path=''):
        """Fetch a page from the given path (or root) and return the contents

        Args:
            path (str): the path to fetch (default: the modem root page)

        Return:
            bytes: the page contents

        """
        url = f'{self.url}{path}'
        logger.debug('Fetching modem page from %s', url)
        r = self.session.get(url, verify=self.verify)
        r.raise_for_status()
        return BeautifulSoup(r.content, features='lxml')

    def load_file(self, filename):
        logger.debug('Loading modem data from %s', filename)
        with open(filename, 'rb') as f:
            b = BeautifulSoup(f, features='lxml')
        return b

    def load_all(self, test_path):
        raise RuntimeError('This method must be implemented by the child class.')

    def fetch_all(self):
        raise RuntimeError('This method must be implemented by the child class.')

    def write_cache(self, cache_file):
        logger.debug('Writing modem data to %s', cache_file)
        data = self.to_json()
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=4)

    def load_from_cache(self, cache_file):
        logger.debug('Reading modem data from %s', cache_file)
        with open(cache_file, 'r') as f:
            data = json.load(f)

        for channel_data in data['downstream_channels']:
            channel_data.pop('direction', None)
            chn = DownstreamDocsisChannel(**channel_data)
            self.downstream_channels.append(chn)
        for channel_data in data['upstream_channels']:
            channel_data.pop('direction', None)
            chn = UpstreamDocsisChannel(**channel_data)
            self.upstream_channels.append(chn)
        for k, v in data['info'].items():
            if k not in ('downstream_channel_count', 'upstream_channel_count'):
                setattr(self, k, v)

    @property
    def upstream_channel_count(self):
        return len(self.upstream_channels)

    @property
    def downstream_channel_count(self):
        return len(self.downstream_channels)
