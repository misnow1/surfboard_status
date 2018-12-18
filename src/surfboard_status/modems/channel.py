"""A DOCSIS Channel"""

from enum import Enum
from surfboard_status.modems.utils import ValueWithUnits


class DocsisChannelStatus(Enum):
    UNLOCKED = 1
    LOCKED = 2


class DocsisChannelDirection(Enum):
    DOWNSTREAM = 1
    UPSTREAM = 2


class DocsisChannel(object):
    def __init__(self, channel=None, lock_status=DocsisChannelStatus.UNLOCKED, channel_id=0, frequency=0.0, power=0.0):
        self.channel = channel
        self.lock_status = lock_status
        self.channel_id = channel_id
        self.frequency = ValueWithUnits(frequency)
        self.power = ValueWithUnits(power)
        self.direction = None

    def __repr__(self):
        return f'{self.direction} channel {self.channel_id}: {self.frequency} ({self.lock_status})'

    def to_json(self):
        return {
            'channel': self.channel,
            'lock_status': self.lock_status,
            'channel_id': self.channel_id,
            'frequency': self.frequency.to_json(),
            'power': self.power.to_json(),
            'direction': str(self.direction)
        }


class DownstreamDocsisChannel(DocsisChannel):
    def __init__(self, channel=None, lock_status=DocsisChannelStatus.UNLOCKED, channel_id=None, frequency=None, power=0.0,
                 modulation=None, snr=0.0, corrected=0, uncorrected=0):
        super(DownstreamDocsisChannel, self).__init__(channel, lock_status, channel_id, frequency, power)
        self.direction = DocsisChannelDirection.DOWNSTREAM
        self.modulation = modulation
        self.snr = ValueWithUnits(snr)
        self.corrected = corrected
        self.uncorrected = uncorrected

    def data(self):
        data = {
            'channel': self.channel,
            'lock_status': self.lock_status,
            'channel_id': self.channel_id,
            'frequency': self.frequency,
            'power': self.power,
            'direction': str(self.direction),
            'modulation': self.modulation,
            'snr': self.snr,
            'corrected': self.corrected,
            'uncorrected': self.uncorrected
        }
        return data

    def to_json(self):
        data = super(DownstreamDocsisChannel, self).to_json()
        data['modulation'] = self.modulation
        data['snr'] = self.snr.to_json()
        data['corrected'] = self.corrected
        data['uncorrected'] = self.uncorrected
        return data


class UpstreamDocsisChannel(DocsisChannel):
    def __init__(self, channel=None, lock_status=DocsisChannelStatus.UNLOCKED, modulation=None, channel_id=None,
                 frequency=None, power=0.0, channel_type=None, symbol_rate=0):
        super(UpstreamDocsisChannel, self).__init__(channel, lock_status, channel_id, frequency, power)
        self.direction = DocsisChannelDirection.UPSTREAM
        self.channel_type = channel_type
        self.symbol_rate = ValueWithUnits(symbol_rate)

    def data(self):
        data = {
            'channel': self.channel,
            'lock_status': self.lock_status,
            'channel_id': self.channel_id,
            'frequency': self.frequency,
            'power': self.power,
            'direction': str(self.direction),
            'channel_type': self.channel_type,
            'symbol_rate': self.symbol_rate
        }
        return data

    def to_json(self):
        data = super(UpstreamDocsisChannel, self).to_json()
        data['channel_type'] = self.channel_type
        data['symbol_rate'] = self.symbol_rate.to_json()
        return data
