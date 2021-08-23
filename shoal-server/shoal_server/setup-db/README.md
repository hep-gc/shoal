**Installations required for sql in shoal**

MariaDB Install:
* yum install mariadb-server
* systemctl start mariadb
* systemctl enable mariadb

SQL Installation:
* pip3 install mysql-connector-python
* pip3 install pandas

Run script for database setup:
This will take a while (downloads mmdb, converts file, inserts data into mysql)
* ./setup_db.sh
