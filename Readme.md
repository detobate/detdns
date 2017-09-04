# detdns

A basic, IPv6 capable, Python daemon to update [Dyn DNS](https://dyn.com) (or other compatible services)

## Usage
* Git clone this repository
* Change into the cloned directory and install the extra required Python packages
```
cd detdns
sudo pip3 install -r requirements.txt
```

* Create a detdns_config.py using the [example](https://github.com/detobate/detdns/raw/detdns_config.example.py) for syntax, filling in the username, password, and hostname that you'd like to update.
* Run inside a screen session with ./detdns.py or launch from systemd/etc.

## Pre-requisites
* Python3
* A [Dyn](https://dyn.com) account or another compatible provider.

## Notes:
* IPv4 address is obtained by calling [Dyn's checkip](http://checkip.dyndns.com/) service.
* IPv6 address is obtained by creating a socket to Sprint's 2600:: address. eg. Will fail without a default route.
* members.dyndns.org doesn't have an AAAA record, so requires IPv4 connectivity to update.
* Uses HTTPS unlike some other clients