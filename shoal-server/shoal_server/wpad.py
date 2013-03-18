import geoip

def generate_wpad(ip):
    squids = geoip.get_nearest_squids(ip)
    if squids:
        proxy_str = ''
        for squid in squids:
            proxy_str += "PROXY http://" + squid['public_ip'] + ';'
        return proxy_str
    else:
        return None

