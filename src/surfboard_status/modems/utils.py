

import re

VALUE_RE = re.compile(r'(?P<value>[0-9.]+)\s*(?P<unit>[a-zA-Z/]+)')

PREFIXES = {
    'k': 1000,
    'M': 1000000,
}


class ValueWithUnits(object):
    DISPLAY_UNITS = True

    def __init__(self, value_with_units):
        if isinstance(value_with_units, dict):
            # the value will be a dict when reloading from the cache file
            self.value = value_with_units['value']
            self.unit = value_with_units['unit']
        else:
            m = VALUE_RE.match(value_with_units)
            if m:
                self.value = float(m.group('value'))
                self.unit = m.group('unit')
            else:
                self.value = value_with_units
                self.unit = None

    def __repr__(self):
        if self.unit and ValueWithUnits.DISPLAY_UNITS:
            return f'{self.value} {self.unit}'
        else:
            return str(self.value)

    def to_json(self):
        return {
            'value': self.value,
            'unit': self.unit
        }
