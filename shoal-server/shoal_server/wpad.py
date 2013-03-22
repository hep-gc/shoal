import geoip

def generate_wpad(ip):
    squids = geoip.get_nearest_squids(ip)
    if squids:
        proxy_str = ''
        for squid in squids:
            try:
                proxy_str += "PROXY http://" + squid['hostname'] + ';'
            except TypeError as e:
                continue
        return proxy_str
    else:
        return None

