"""A surfboard modem."""

from surfboard_status.modems.modem import Modem
from surfboard_status.modems.channel import DownstreamDocsisChannel, UpstreamDocsisChannel
import logging

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

    def __init__(self, ip_address):
        # blindly assume we don't support SSL and just pass the ip address
        super(SurfboardModem, self).__init__(ip_address)

    def fetch_status(self, write_page=None):
        return super(SurfboardModem, self).fetch_status(path='/cgi-bin/status', write_page=write_page)

    def _parse_status(self, b):
        tables = b.find_all('table', 'simpleTable')
        for bt in tables:
            heading = bt.find('th').string
            if 'Downstream' in heading:
                self._parse_downstream_table(bt)
            elif 'Upstream' in heading:
                self._parse_upstream_table(bt)

    def _parse_downstream_table(self, table):
        rows = table.find_all('tr')
        skip = SurfboardModem.TABLE_SKIP_ROWS
        for row in rows:
            if skip > 0:
                skip -= 1
                continue

            channel_args = {}
            cols = row.find_all('td')
            for i in range(len(cols)):
                key = SurfboardModem.DOWNSTREAM_COLUMN_KEYS[i]
                val = cols[i].string.strip()
                channel_args[key] = val
            channel = DownstreamDocsisChannel(**channel_args)
            self.upstream_channels.append(channel)

    def _parse_upstream_table(self, table):
        rows = table.find_all('tr')
        skip = SurfboardModem.TABLE_SKIP_ROWS
        for row in rows:
            if skip > 0:
                skip -= 1
                continue

            channel_args = {}
            cols = row.find_all('td')
            for i in range(len(cols)):
                key = SurfboardModem.UPSTREAM_COLUMN_KEYS[i]
                val = cols[i].string.strip()
                channel_args[key] = val
            channel = UpstreamDocsisChannel(**channel_args)
            self.upstream_channels.append(channel)
