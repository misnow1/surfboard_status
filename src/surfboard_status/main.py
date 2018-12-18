
import click
import json
import logging
import os
import time
from stat import ST_MTIME
from surfboard_status.modems.surfboard import SurfboardModem
from surfboard_status.modems.utils import ValueWithUnits


def report_modem_group(modem, key_parts):
    if key_parts:
        k = key_parts[0]
        v = getattr(modem, k)
        print(v)
    else:
        keys = ('hardware_version', 'software_version', 'mac_addr', 'serial_number', 'uptime',
                'downstream_channel_count', 'upstream_channel_count')
        data = [f'modem.{k}: {getattr(modem, k)}' for k in keys]
        print(' '.join(data))


def report_channel_group(group_name, channels, key_parts):
    channel_id = None
    channel_data_key = None
    try:
        channel_id = int(key_parts.pop(0))
        channel_data_key = key_parts.pop(0)
    except IndexError:
        pass

    if channel_id is not None:
        channel_id_to_channel = {int(c.channel_id): c for c in channels}
        try:
            chn = channel_id_to_channel[channel_id]
        except KeyError:
            raise ValueError('Channel with ID %d does not exist', channel_id)
        if channel_data_key:
            print(getattr(chn, channel_data_key))
        else:
            # print all channel data
            data = [f'{group_name}.{channel_id}.{k}: {v}' for k, v in chn.data().items()]
            print(' '.join(data))
    else:
        # print all channels
        data = [f'{group_name}.{chn.channel_id}.{k}: {v}' for chn in channels for k, v in chn.data().items()]
        print(' '.join(data))


@click.command()
@click.option('-i', '--ip', '--ip-address', 'ip_address', type=str, required=True, help='The IP address of the modem to scrape')
@click.option('-k', '--key', type=str, help='Only report this key')
@click.option('-c', '--cache', type=str, help='Cache the status page in this file')
@click.option('--ttl', '--cache-ttl', 'cache_ttl', type=int, default=30,
              help='Refresh the cache data if it is more than this many seconds old')
@click.option('--units', '--display-units', is_flag=True, default=False, help='Display units when displaying data')
@click.option('-t', '--test-data', type=str, help='Load the status page from this file instead of requesting the page from the modem')
@click.option('--debug', '-d', is_flag=True, help='Output so much things')
def main(ip_address, key, cache, cache_ttl, units, test_data, debug):

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%b %d %H:%M:%S')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    modem = SurfboardModem(ip_address)

    # set up unit display
    ValueWithUnits.DISPLAY_UNITS = units

    refresh_cache = False
    if cache:
        try:
            s = os.stat(cache)
            if (int(time.time()) - s[ST_MTIME]) > cache_ttl:
                logger.debug('Cache file needs to be refreshed')
                refresh_cache = True
        except FileNotFoundError:
            logger.debug('Cache file does not exist! It will be created')
            refresh_cache = True

    if not cache or (cache and refresh_cache):
        # the cache is disabled or needs to be refreshed
        if test_data:
            modem.load_all(test_data)
        else:
            modem.fetch_all()

        # if the cache is enabled, write it out
        if cache:
            modem.write_cache(cache_file=cache)
    elif cache:
        # the cache file is just fine!
        logger.debug('Loading modem data from cache')
        modem.load_from_cache(cache_file=cache)

    if key:
        if '.' in key:
            key_parts = key.split('.')
        else:
            key_parts = [key, ]

        key_group = key_parts.pop(0)

        if key_group == 'modem':
            report_modem_group(modem, key_parts)
        elif key_group == 'downstream_channel':
            report_channel_group(key_group, modem.downstream_channels, key_parts)
        elif key_group == 'upstream_channel':
            report_channel_group(key_group, modem.upstream_channels, key_parts)
        else:
            raise ValueError('Key group %s is not supported', key_group)

    else:
        print(json.dumps(modem.to_json(), indent=4))


if __name__ == '__main__':
    main()
