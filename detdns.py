#!/usr/bin/env python3
import requests
import socket
import time
from lxml import html
from detdns_config import cfg, providers

v4_url = 'http://checkip.dyndns.com/'
api = providers.get(cfg['provider'])


def find_ipv4():
    """ Use a remote url to return the public IPv4 source
        address used. Because NAT """
    try:
        r = requests.get(v4_url)
        tree = html.fromstring(r.content)
        result = tree.xpath('//body/text()')
        result = result[0].split()
        ipv4 = result[len(result)-1]
    except:
        if cfg['debug']:
            print("Couldn't connect to %s" % v4_url)
            print("Check that you have a valid IPv4 default route")
        ipv4 = None

    return ipv4


def find_ipv6():
    """ Creates a socket to a public ip.
        Let the OS's source address selection method do its magic
        return the source IP it selects"""

    test_host = '2600::'  # Sprint.net
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as s:
            s.connect((test_host, 53))
            ipv6 = s.getsockname()[0]
    except:
        if cfg['debug']:
            print("Couldn't create a socket to %s" % test_host)
            print("Check that you have a valid IPv6 default route")
        ipv6 = None

    return ipv6


def main():

    oldip = None
    while True:
        ip = None
        if cfg['disable_v6']:
            ipv6 = None
        else:
            ipv6 = find_ipv6()
        if cfg['disable_v4']:
            ipv4 = None
        else:
            ipv4 = find_ipv4()

        if ipv6 and ipv4:
            ip = ipv4 + "," + ipv6
        elif ipv6 and ipv4 is None:
            ip = ipv6
        elif ipv6 is None and ipv4:
            ip = ipv4

        now = time.asctime()
        if ip != oldip:
            url = api + '?system=dyndns&hostname=%s&myip=%s' % (cfg['host'], ip)
            try:
                r = requests.get(url, auth=(cfg['user'], cfg['pass']))
            except ConnectionError:
                print("%s: Couldn't connect to %s" % (now, url))
                break
            except:
                print("%s: Error: %s - %s " % (now, r.status_code, r.text))
                break

            if r.status_code == 200:
                if "good" in r.text:
                    oldip = ip
                    print("%s: Successfully updated host: %s" % (now, cfg['host']))
                    if ipv6:
                        print("%s: AAAA set to %s" % (now, ipv6))
                    if ipv4:
                        print("%s: A set to %s" % (now, ipv4))
                elif "nochg" in r.text:
                    print("%s: No Change" % now)

            if cfg['debug']:
                print("URL Called: %s" % url)
                print("Response: %s" % r.status_code)
                print("Response: %s" % r.text)

        elif cfg['debug']:
            print("%s: No Change" % now)

        time.sleep(cfg['update_time'])


if __name__ == '__main__':
    main()
