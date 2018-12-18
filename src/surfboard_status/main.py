
import click
import logging
from surfboard_status.modems.surfboard import SurfboardModem


@click.command()
@click.option('-i', '--ip', '--ip-address', 'ip_address', type=str, required=True, help='The IP address of the modem to scrape')
@click.option('-c', '--cache', type=str, help='Cache the status page in this file.')
@click.option('--debug', '-d', is_flag=True, help='Output so much things')
def main(ip_address, cache, debug):

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%b %d %H:%M:%S')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    modem = SurfboardModem(ip_address)
    # modem.fetch_status(write_page=cache)
    modem.load_status(cache)

    for c in modem.downstream_channels:
        print(c)

    for c in modem.upstream_channels:
        print(c)


if __name__ == '__main__':
    main()
