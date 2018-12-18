"""A surfboard modem."""

from surfboard_status.constants import UPTIME_KEYS
from surfboard_status.modems.modem import Modem
from surfboard_status.modems.channel import DownstreamDocsisChannel, UpstreamDocsisChannel
import logging
import os

logger = logging.getLogger(__name__)


class SurfboardModem(Modem):
    """A Motorola(R) SurfBoard(TM) Modem

    Args:
        ip_address (str): the modem's IP address

    """
    TABLE_SKIP_ROWS = 2
    DOWNSTREAM_COLUMN_KEYS = [
        'channel',
        'lock_status',
        'modulation',
        'channel_id',
        'frequency',
        'power',
        'snr',
        'corrected',
        'uncorrected'
    ]

    UPSTREAM_COLUMN_KEYS = [
        'channel',
        'lock_status',
        'channel_type',
        'channel_id',
        'symbol_rate',
        'frequency',
        'power'
    ]

    STATUS_TITLE_TO_KEY = {
        'Hardware Version': 'hardware_version',
        'Software Version': 'software_version',
        'Cable Modem MAC Address': 'mac_addr',
        'Serial Number': 'serial_number'
    }

    def __init__(self, ip_address):
        # blindly assume we don't support SSL and just pass the ip address
        super(SurfboardModem, self).__init__(ip_address)

    def fetch_status(self):
        return self.fetch_path(path='/cgi-bin/status')

    def fetch_product_info(self):
        return self.fetch_path(path='/cgi-bin/swinfo')

    def fetch_all(self):
        b = self.fetch_status()
        self._parse_status(b)

    def load_all(self, test_path):
        """Load the status page from a file on disk

        Args:
            filename (str): The filename from which to load the status page

        """
        b = self.load_file(os.path.join(test_path, 'status.html'))
        self._parse_status(b)
        b = self.load_file(os.path.join(test_path, 'swinfo.html'))
        self._parse_swinfo(b)

    def _parse_status(self, b):
        tables = b.find_all('table', 'simpleTable')
        for bt in tables:
            heading = bt.find('th').string
            if 'Downstream' in heading:
                self._parse_channel_table(bt, SurfboardModem.DOWNSTREAM_COLUMN_KEYS, DownstreamDocsisChannel, self.downstream_channels)
            elif 'Upstream' in heading:
                self._parse_channel_table(bt, SurfboardModem.UPSTREAM_COLUMN_KEYS, UpstreamDocsisChannel, self.upstream_channels)

    def _parse_channel_table(self, table, col_keys, channel_cls, channel_list):
        rows = table.find_all('tr')
        skip = SurfboardModem.TABLE_SKIP_ROWS
        for row in rows:
            if skip > 0:
                skip -= 1
                continue

            channel_args = {}
            cols = row.find_all('td')
            for i in range(len(cols)):
                key = col_keys[i]
                val = cols[i].string.strip()
                channel_args[key] = val
            channel = channel_cls(**channel_args)
            channel_list.append(channel)

    def _parse_swinfo(self, b):
        tables = b.find_all('table', 'simpleTable')
        for table in tables:
            heading = table.find('th').string
            if heading == 'Information':
                self._parse_information_table(table)
            elif heading == 'Status':
                self._parse_status_table(table)

    def _parse_information_table(self, table):
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if not cols:
                continue

            title = cols[0].string
            value = cols[1].string
            if title not in SurfboardModem.STATUS_TITLE_TO_KEY:
                logger.debug('Skipping title %s: title not in key map', title)
                continue
            key = SurfboardModem.STATUS_TITLE_TO_KEY[title]
            setattr(self, key, value)

    def _parse_status_table(self, table):
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if not cols:
                continue

            title = cols[0].string
            value = cols[1].string
            if title == 'Up Time':
                self.uptime = 0
                logger.debug('Parsing %s: %s', title, value)
                uptime_parts = map(str.strip, value.split(':'))
                for p in uptime_parts:
                    v, k = p.split()
                    v = int(v)
                    k = k.strip()
                    if k in UPTIME_KEYS:
                        self.uptime += v * UPTIME_KEYS[k]
                    else:
                        logger.warning('Unknown key %s in uptime %s', k, value)
                logger.debug('Calculated modem uptime: %ds', self.uptime)
                break
