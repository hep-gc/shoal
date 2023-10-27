#!/bin/bash

set -e
BASEDIR=$(dirname "$0")/
TEMP=/tmp/

name=$(curl https://db-ip.com/db/download/ip-to-city-lite|grep mmdb\.gz|cut -d"\"" -f2)
curl "$name" | gunzip > ${TEMP}city.mmdb
echo "Database download complete"

echo "Converting mmdb to separate IPv4 and IPv6 csv files..."
${BASEDIR}mmdb_to_csv.py "${TEMP}city.mmdb"
rm ${TEMP}city.mmdb
echo "MaxMind database converted to CSV"

echo "Creating SQL database..."
mariadb -u root --password= -e "drop database if exists geoip; create database geoip;"
mariadb -u root --password= geoip < ${BASEDIR}geodata.sql
rm ${TEMP}ipv4.csv
rm ${TEMP}ipv6.csv
echo "SQL database created"

echo "Adding a shoal user..."
mariadb -u root --password= --database=geoip -e "create user 'shoal'@'localhost'; grant all privileges on geoip.* to 'shoal'@'localhost';"
mariadb -u root --password= geoip < ${BASEDIR}geodata_updates.sql
echo "Updated MySQL data entires and created shoal user"

echo "Done"
