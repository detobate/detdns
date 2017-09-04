# detdns

A basic, IPv6 capable, Python daemon to update [Dyn DNS](https://dyn.com) (or other compatible services)

## Usage
* Git clone this repository
* Create a detdns_config.py using the [example](https://github.com/detobate/detdns/raw/detdns_config.example.py) for syntax, filling in the username, password, and hostname that you'd like to update.
* Run inside a screen session with ./detdns.py or launch from systemd/etc.

## Notes:
* IPv4 address is obtained by calling [Dyn's checkip](http://checkip.dyndns.com/) service.
* IPv6 address is obtained by creating a socket to Sprint's 2600:: address. eg. Will fail without a default route.
* members.dyndns.org doesn't have an AAAA record, so requires IPv4 connectivity to update.
* Uses HTTPS unlike some other clients