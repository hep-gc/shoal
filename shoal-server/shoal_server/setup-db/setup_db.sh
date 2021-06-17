#!/bin/bash

set -e
SETUP=/opt/shoal/shoal-server/shoal_server/setup-db/

curl "https://download.db-ip.com/free/dbip-city-lite-2021-06.mmdb.gz" | gunzip > ${SETUP}city.mmdb
echo "Database download complete"

echo "Converting mmdb to separate IPv4 and IPv6 csv files..."
${SETUP}mmdb_to_csv.py "${SETUP}city.mmdb"
rm ${SETUP}city.mmdb
echo "MaxMind database converted to CSV"

echo "Creating SQL database..."
mysql -u root --password= -e "drop database if exists geoip; create database geoip;"
mysql -u root --password= geoip < ${SETUP}geodata.sql
rm ${SETUP}ipv4.csv
rm ${SETUP}ipv6.csv
echo "SQL database created"

mysql -u root --password= geoip < ${SETUP}geodata_updates.sql
echo "Updated MySQL data entires"

echo "Done"
