cfg = {
    'user': 'nobody',
    'pass': 'hunter2',
    'host': 'example.dyndns.org',
    'update_time': 300,
    'debug': False,
    'disable_v4': True,
    'disable_v6': False,
    'provider': 'no-ip'
}

providers = {
    'dyn': 'https://members.dyndns.org/nic/update',
    'no-ip': 'https://dynupdate.no-ip.com/nic/update'
}
