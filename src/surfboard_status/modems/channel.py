"""A DOCSIS Channel"""

from enum import Enum


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
        self.frequency = frequency
        self.power = power
        self.direction = None

    def __repr__(self):
        return f'{self.direction} channel {self.channel_id}: {self.frequency} ({self.lock_status})'

    def to_json(self):
        return {
            'channel': self.channel,
            'lock_status': self.lock_status,
            'channel_id': self.channel_id,
            'frequency': self.frequency,
            'power': self.power,
            'direction': self.direction
        }


class DownstreamDocsisChannel(DocsisChannel):
    def __init__(self, channel=None, lock_status=DocsisChannelStatus.UNLOCKED, channel_id=None, frequency=None, power=0.0,
                 modulation=None, snr=0.0, corrected=0, uncorrected=0):
        super(DownstreamDocsisChannel, self).__init__(channel, lock_status, channel_id, frequency, power)
        self.direction = DocsisChannelDirection.DOWNSTREAM
        self.modulation = modulation
        self.snr = snr
        self.corrected = corrected
        self.uncorrected = uncorrected

    def to_json(self):
        data = super(DownstreamDocsisChannel, self).to_json()
        data['modulation'] = self.modulation
        data['snr'] = self.snr
        data['corrected'] = self.corrected
        data['uncorrected'] = self.uncorrected
        return data


class UpstreamDocsisChannel(DocsisChannel):
    def __init__(self, channel=None, lock_status=DocsisChannelStatus.UNLOCKED, modulation=None, channel_id=None,
                 frequency=None, power=0.0, channel_type=None, symbol_rate=0):
        super(UpstreamDocsisChannel, self).__init__(channel, lock_status, channel_id, frequency, power)
        self.direction = DocsisChannelDirection.UPSTREAM
        self.channel_type = channel_type
        self.symbol_rate = symbol_rate

    def to_json(self):
        data = super(UpstreamDocsisChannel, self).to_json()
        data['channel_type'] = self.channel_type
        data['symbol_rate'] = self.symbol_rate
        return data
