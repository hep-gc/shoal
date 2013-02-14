import pygeoip, math
import web

def download_db():
    cmd = ['wget',DB_URL]
    ungz = ['gunzip','{0}.gz'.format(DB_PATH)]
    with open(LOG_FILE,'wb') as log:
        try:
            dl = subprocess.Popen(cmd,stdout=log,stderr=log)
            dl.wait()
            time.sleep(2)
            gz = subprocess.Popen(ungz,stdout=log,stderr=log)
            gz.wait()
        except Exception as e:
            log.write("Could not download the database. - {0}".format(e))
            sys.exit(1)

def get_geolocation(ip):
    diff = datetime.datetime.now() - datetime.timedelta(7)
    diff = time.mktime(diff.timetuple())
    # if DB doesnt exist yet
    if not os.path.isfile(DB_PATH):
        print "Database does not exist, downloading IP database"
        download_db()
    elif os.path.getmtime(DB_PATH) - diff > 2592000: # older than 30 days
        print "Database last modified: {}, trying to update.".format(datetime.fromtimestamp(os.path.getmtime(DB_PATH)))
        download_db()
    gi = pygeoip.GeoIP(DB_PATH)
    return gi.record_by_addr(ip)

def get_nearest_squid(ip):
    request = get_geolocation(ip)
    r_lat = request['latitude']
    r_long = request['longitude']
    smallest_distance = float("inf")
    nearest_squid = None
    for squid in web.shoal:
        s_lat = squid['latitude']
        s_long = squid['longitude']
        distance = get_distance_between_nodes(r_lat,r_long,s_lat,s_long)
        if distance < smallest_distance:
            smallest_distance = distance
            nearest_squid = squid
    return nearest_squid

# haversine forumla
def get_distance_between_nodes(lat1,long1,lat2,long2):
    # radius of earth
    r = 6371
    d_lat = deg_to_rad(lat2-lat1)
    d_long = deg_to_rad(long2-long1)

    a = math.sin(d_lat/2) * math.sin(d_lat/2) + \
        math.cos(deg_to_rad(lat1)) * math.cos(deg_to_rad(lat2)) * \
        math.sin(d_long/2) * math.sin(d_long/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = r * c
    return d

def deg_to_rad(deg):
    return deg * (math.pi/180)
