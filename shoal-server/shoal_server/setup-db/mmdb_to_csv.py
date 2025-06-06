#!/usr/bin/env python3
"""
Convert a mmdb file into two csv files: ipv4.csv and ipv6.csv
"""

"""
File currently not working needs fix in relation to _start_node attribute of reader from mmdb no longer existing
"""

import maxminddb
import copy
import pandas as pd
import sys

from ipaddress import IPv4Network, IPv6Network

"""Input the file and path names"""
path = '/tmp/'
input_file = sys.argv[1]
out_ipv4 = path + 'ipv4.csv'
out_ipv6 = path + 'ipv6.csv'

def combine_rows(rows):
  """ Iterate through sorted list of row dicts, compare side-by-side entries, combine when possible """
  rows.sort(key=lambda k: k['start_ip'])
  length = len(rows)
  i = 0
  while i < length-1:
    if rows[i]['hash'] == rows[i+1]['hash']:
      if rows[i]['end_ip']+1 == rows[i+1]['start_ip']:
        rows[i]['end_ip'] = rows[i+1]['end_ip']
        rows.remove(rows[i+1])
        length = len(rows)
      elif rows[i]['start_ip']-1 == rows[i+1]['end_ip']:
        rows[i]['start_ip'] = rows[i+1]['start_ip']
        rows.remove(rows[i+1])
        length = len(rows)
      else:
        i = i + 1
    else:
      i = i + 1
  for row in rows:
    del row['hash']

counter=0
write_header = True

# Change: removed 'range', 'region_code', 'location_accuracy_radius', and added 'start_ip', 'end_ip'
row_format = {
  'start_ip': None,
  'end_ip': None,
  'continent_code': "",
  'continent': "",
  'country_code': "",
  'country': "",
  'city': "",
  'region': "",
  'latitude': None,
  'longitude': None,
  'hash': "",
}

with maxminddb.open_database(input_file) as reader:

  ipv4_rows = []
  ipv6_rows = []
  count = 0

  for node in reader:
    #if count >= 20:
      #break
    #count += 1

    row = copy.deepcopy(row_format)
    
    row['start_ip'] = int(node[0][0])
    row['end_ip'] = int(node[0][-1])

    d = node[1]

    if 'continent' in d:
      if 'code' in d['continent']:
        row['continent_code'] = d['continent']['code']

      if 'names' in d['continent']:
        if 'en' in d['continent']['names']:
            row['continent'] = d['continent']['names']['en']
    
    # Change: 'registered_country' to 'country'
    if 'country' in d:
      if 'iso_code' in d['country']:
          row['country_code'] = d['country']['iso_code']

      if 'names' in d['country']:
        if 'en' in d['country']['names']:
            row['country'] = d['country']['names']['en']
    
    if 'city' in d:
      if 'names' in d['city']:
          if 'en' in d['city']['names']:
            row['city'] = d['city']['names']['en']
    
    if 'subdivisions' in d:
      if 'names' in d['subdivisions'][0]:
          if 'en' in d['subdivisions'][0]['names']:
            row['region'] = d['subdivisions'][0]['names']['en']

    if 'location' in d:
      if 'latitude' in d['location']:
        lat = d['location']['latitude']
        row['latitude'] = round(lat, 5)

      if 'longitude' in d['location']:
        lon = d['location']['longitude']
        row['longitude'] = round(lon, 5)

    row['hash'] = hash(row['city']+str(row['latitude'])+str(row['longitude']))

    counter += 1
    if row['start_ip'] < 2**32:
      ipv4_rows.append(row)
    else:
      ipv6_rows.append(row)
    
    if counter % 10000 == 0:
      combine_rows(ipv4_rows)
      combine_rows(ipv6_rows)

      pd.DataFrame(ipv4_rows).to_csv(out_ipv4, mode='a', header=write_header, index=False)
      pd.DataFrame(ipv6_rows).to_csv(out_ipv6, mode='a', header=write_header, index=False)
      write_header = False
      ipv4_rows = []
      ipv6_rows = []
      print('.',end='')
    
    if counter % 1000000 == 0:
      print('.')
    
# Ouput final list of rows
combine_rows(ipv4_rows)
combine_rows(ipv6_rows)

pd.DataFrame(ipv4_rows).to_csv(out_ipv4, mode='a', header=False, index=False)
pd.DataFrame(ipv6_rows).to_csv(out_ipv6, mode='a', header=False, index=False)
