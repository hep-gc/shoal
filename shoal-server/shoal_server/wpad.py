import geoip

def generate_wpad(ip):
    squids = geoip.get_nearest_squids(ip)
    if squids:
        proxy_str = ''
        for squid in squids:
            try:
                proxy_str += "PROXY http://{0}:{1};".format(squid['hostname'],squid['squid_port'])
            except TypeError as e:
                continue
        return proxy_str
    else:
        return None

