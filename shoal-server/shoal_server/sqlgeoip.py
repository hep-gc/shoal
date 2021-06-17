import mysql.connector
import ipaddress

class Reader:

    def __init__(self, db_name):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database=db_name
        )

        self._db = mydb
        self._cursor = mydb.cursor(dictionary=True)

    def __enter__(self):
        return self
    
    def __exit__(self):
        self._cursor.close()

    def city(self, ip):
        address = ipaddress.ip_address(ip)
        ip_int = int(address)
        if address.version == 4:
            table = 'ipv4'
        else:
            table = 'ipv6'

        cursor = self._cursor
        cursor.execute("SELECT * FROM %s WHERE end_ip >= %d ORDER BY end_ip \
                        ASC LIMIT 1" % (table, ip_int))

        row = cursor.fetchone()
        if row is None or int(row['start_ip']) > ip_int:
            return None
        else:
            return Geodata(row)

class Geodata:
    """
        data - dictionary of geographic info
    """
    def __init__(self, data):
        self.city = City(data['city'])
        self.country = Country(data['country'], data['country_code'])
        self.continent = Continent(data['continent'], data['continent_code'])
        self.location = Location(data['latitude'], data['longitude'])
        self.subdivisions = Subdivisions(data['region'])
        self.postal = Postal()

class City:
    def __init__(self, name):
        self.name = name

class Country:
    def __init__(self, name, code):
        self.name = name
        self.iso_code = code

class Continent:
    def __init__(self, name, code):
        self.name = name
        self.code = code

class Location:
    def __init__(self, lat, long, time_zone=None, metro_code=None):
        self.latitude = lat
        self.longitude = long
        self.time_zone = time_zone
        self.metro_code = metro_code

class Subdivisions:
    def __init__(self, sub):
        self.most_specific = Subdivision(sub)

class Subdivision:
    def __init__(self, name, code=None):
        self.name = name
        self.iso_code = code

class Postal:
    def __init__(self, code=None):
        self.code = code
