drop table if exists ipv4;
drop table if exists ipv6;

alter database geoip character set utf8mb4 collate utf8mb4_unicode_ci;

create table ipv4 (
	start_ip int unsigned  not null, 
	end_ip int unsigned not null, 
	continent_code varchar(255), 
	continent varchar(255), 
	country_code varchar(255), 
	country varchar(255), 
	city varchar(255), 
	region varchar(255), 
	latitude double(8,5) not null, 
	longitude double(8,5) not null
)
character set 'utf8mb4'
collate 'utf8mb4_unicode_ci'
engine = MyISAM;

load data local infile '/tmp/ipv4.csv'
into table ipv4
fields terminated by ','
lines terminated by '\n'
ignore 1 rows
(start_ip, end_ip, continent_code, continent, country_code, country, city, region, latitude, longitude);

create index end4 on ipv4(end_ip);

create table ipv6 (
	start_ip decimal(39,0) not null, 
	end_ip decimal(39,0) not null, 
	continent_code varchar(255), 
	continent varchar(255), 
	country_code varchar(255), 
	country varchar(255), 
	city varchar(255), 
	region varchar(255), 
	latitude double(8,5) not null, 
	longitude double(8,5) not null
)
character set 'utf8mb4'
collate 'utf8mb4_unicode_ci'
engine = MyISAM;

load data local infile '/tmp/ipv6.csv'
into table ipv6
character set utf8mb4
fields terminated by ','
lines terminated by '\n'
ignore 1 rows
(start_ip, end_ip, continent_code, continent, country_code, country, city, region, latitude, longitude);

create index end6 on ipv6(end_ip);
