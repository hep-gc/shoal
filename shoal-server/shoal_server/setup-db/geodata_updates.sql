-- Updates to existing geoip sql database

UPDATE ipv4
SET city = REPLACE(city, "Arching", "Garching bei München")
WHERE city LIKE "Arching%";

UPDATE ipv6
SET city = REPLACE(city, "Arching", "Garching bei München")
WHERE city LIKE "Arching%";
