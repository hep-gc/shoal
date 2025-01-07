#!/bin/bash

set -e
BASEDIR=$(dirname "$0")/
TEMP=/tmp/
FILETYPE=${1:-mmdb}

name=$(curl https://db-ip.com/db/download/ip-to-city-lite| grep ${FILETYPE}\.gz|sed "s/'/\"/g" |cut -d"\"" -f2)
curl "$name" | gunzip > ${TEMP}city.${FILETYPE}
echo "Database download complete"

if [ "${FILETYPE}" == "mmdb" ]
then
echo "Converting mmdb to separate IPv4 and IPv6 csv files..."
${BASEDIR}mmdb_to_csv.py "${TEMP}city.mmdb"
rm ${TEMP}city.mmdb
echo "MaxMind database converted to CSV"
fi

if [ "${FILETYPE}" == "csv" ]
then
awk '{if (match($0,"^::")) exit; print}' ${TEMP}city.csv > ${TEMP}ipv4.csv
awk '/::/' ${TEMP}city.csv > ${TEMP}ipv6.csv
fi


echo "Creating SQL database..."
mysql -u root --password= -e "drop database if exists geoip; create database geoip;"
mysql -u root --password= geoip < ${BASEDIR}geodata.sql
rm ${TEMP}ipv4.csv
rm ${TEMP}ipv6.csv
echo "SQL database created"

echo "Adding a shoal user..."
mysql -u root --password= --database=geoip -e "create user if not exists 'shoal'@'localhost'; grant all privileges on geoip.* to 'shoal'@'localhost';"
mysql -u root --password= geoip < ${BASEDIR}geodata_updates.sql
echo "Updated MySQL data entires and created shoal user"

echo "Done"
