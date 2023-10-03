#!/usr/bin/env python3
import requests
import socket
import time
from lxml import html
from collections import OrderedDict
from detdns_sh_config import cfg

v4_url = 'http://checkip.dyndns.com/'


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
        Let the OS' source address selection method do its magic
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


def update_sitehost(cfg, rr_type, ip, record_id):
    """https://docs.sitehost.nz/api/v1.1/?path=/dns/update_record&action=POST"""

    url = "https://api.sitehost.nz/1.0/dns/update_record.json"

    # We need ordered dictionary because parameters have to be in the right order.
    body = OrderedDict()

    body['apikey'] = cfg.get('api_key')
    body['client_id'] = cfg.get('client_id')
    body['domain'] = cfg.get('domain')
    body['record_id'] = record_id
    body['type'] = rr_type
    body['name'] = cfg.get('hostname')
    body['content'] = ip

    r = requests.post(url, data=body)
    if cfg.get('debug'):
        print(f"Updating {cfg.get('hostname')} {rr_type} to {ip}")
        print(r.text)


def find_record_id(cfg, rr_type):
    """ Sitehost requires the record ID when updating, so first we must find it.
        Sadly there isn't an API to call to find the specific record, so we must get the full list and iterate
        https://docs.sitehost.nz/api/v1.1/?path=/dns/list_records&action=GET """

    url = f"https://api.sitehost.nz/1.1/dns/list_records.json?apikey={cfg.get('api_key')}&" \
          f"client_id={cfg.get('client_id')}&domain={cfg.get('domain')}"
    try:
        responses = requests.get(url)
        r = responses.json()
    except requests.exceptions.ConnectionError as e:
        print(f"{now}: {e}")

    record_id = None

    for entry in r.get('return'):
        if entry.get('name') == cfg.get('hostname') and entry.get('type') == rr_type:
            if cfg.get('debug'):
                print(f"Found {rr_type} resource record ID {entry.get('id')} for {cfg.get('hostname')}")
            record_id = entry.get('id')
            break

    return record_id


def main():

    old_ipv4 = None
    old_ipv6 = None

    while True:
        now = time.asctime()
        if cfg['disable_v6']:
            ipv6 = None
        else:
            ipv6 = find_ipv6()
            ipv6_record_id = find_record_id(cfg, 'AAAA')

            if ipv6 and ipv6 != old_ipv6:
                if ipv6_record_id:
                    print(f"{now}: Updating old IPv6 {old_ipv6} with new {ipv6}")
                    update_sitehost(cfg, 'AAAA', ipv6, ipv6_record_id)
                    old_ipv6 = ipv6
                else:
                    print(f"{now}: Error: Could not find the record ID for {cfg.get('hostname')} and record type AAAA")
            elif cfg.get('debug'):
                print(f"{now}: Current IPv6 {ipv6} is the same as the previous {old_ipv6}")

        if cfg['disable_v4']:
            ipv4 = None
        else:
            ipv4 = find_ipv4()
            ipv4_record_id = find_record_id(cfg, 'A')

            if ipv4 and ipv4 != old_ipv4:
                if ipv4_record_id:
                    print(f"{now}: Updating old IPv4 {old_ipv4} with new {ipv4}")
                    update_sitehost(cfg, 'A', ipv4, ipv4_record_id)
                    old_ipv4 = ipv4
                else:
                    print(f"{now}: Error: Could not find the record ID for {cfg.get('hostname')} and record type A")
            elif cfg.get('debug'):
                print(f"{now}: Current IPv4 {ipv4} is the same as the previous {old_ipv4}")

        time.sleep(cfg.get('update_time'))


if __name__ == '__main__':
    main()
