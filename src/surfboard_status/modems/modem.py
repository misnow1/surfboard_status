"""A basic modem with an IP address."""

import requests
from bs4 import BeautifulSoup


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

        self.downstream_channels = []
        self.upstream_channels = []

        self._session = None

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
        return self._session

    def fetch_status(self, path=None, write_page=None):
        """Fetches the status page and returns the contents as a BeautifulSoup object

        Args:
            path (str): The path to the status page

        """

        if path:
            url = f'{self.url}{path}'
        else:
            url = self.url
        r = self.session.get(url, verify=self.verify)
        r.raise_for_status()

        if write_page:
            with open(write_page, 'wb') as f:
                f.write(r.content)

        b = BeautifulSoup(r.content, features='lxml')

        self._parse_status(b)

    def load_status(self, filename):
        """Load the status page from a file on disk

        Args:
            filename (str): The filename from which to load the status page

        """
        with open(filename, 'rb') as f:
            b = BeautifulSoup(f, features='lxml')

        self._parse_status(b)

    @property
    def upstream_channel_count(self):
        return len(self.upstream_channels)

    @property
    def downstream_channel_count(self):
        return len(self.downstream_channels)
