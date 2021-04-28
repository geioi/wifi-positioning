#!/bin/bash
sudo apt install -y mysql-server
sudo service mysql restart

# If /root/.my.cnf exists then it won't ask for root password
if [ -f /root/.my.cnf ]; then
	for db_name in wifi_positioning_delta wifi_positioning_test1 wifi_positioning_test2 wifi_positioning_test3
	do
		echo "Creating database: $db_name"
		mysql -e "CREATE DATABASE IF NOT EXISTS $db_name /*\!40100 DEFAULT CHARACTER SET latin1 */;"
		echo "Database successfully created!"
	done
	echo "Showing existing databases..."
	mysql -e "show databases;"
	echo ""
	echo "Please enter the NAME of the new MySQL database user! (example: user1)"
	read username
	echo "Please enter the PASSWORD for the new MySQL database user!"
	echo "Note: password will be hidden when typing"
	read -s userpass
	echo "Creating new user..."
	mysql -e "CREATE USER ${username}@localhost IDENTIFIED WITH mysql_native_password BY '${userpass}';"
	echo "User successfully created!"
	echo ""
	echo "Granting ALL privileges to ${username}!"
	mysql -e "GRANT ALL PRIVILEGES ON *.* TO '${username}'@'localhost';"
	mysql -e "FLUSH PRIVILEGES;"
	
	echo "importing databases..."
	mysql -u ${username} -p${userpass} wifi_positioning_delta < wifi_positioning_delta.sql
	for db_dump in wifi_positioning_test1 wifi_positioning_test2 wifi_positioning_test3
	do
		mysql -u${username} -p${userpass} $db_dump < wifi_positioning_empty_dump.sql
	done
	
	echo "You're good now :)"
	exit
	
# If /root/.my.cnf doesn't exist then it'll ask for root password	
else
	for db_name in wifi_positioning_delta wifi_positioning_test1 wifi_positioning_test2 wifi_positioning_test3
	do
		echo "Creating database: $db_name"
		sudo mysql -e "CREATE DATABASE IF NOT EXISTS $db_name /*\!40100 DEFAULT CHARACTER SET latin1 */;"
		echo "Database successfully created!"
	done
	echo "Showing existing databases..."
	sudo mysql -e "show databases;"
	echo ""
	echo "Please enter the NAME of the new MySQL database user! (example: user1)"
	read username
	echo "Please enter the PASSWORD for the new MySQL database user!"
	echo "Note: password will be hidden when typing"
	read -s userpass
	echo "Creating new user..."
	sudo mysql -e "CREATE USER ${username}@localhost IDENTIFIED WITH mysql_native_password BY '${userpass}';"
	echo "User successfully created!"
	echo ""
	echo "Granting ALL privileges to ${username}!"
	sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO '${username}'@'localhost';"
	sudo mysql -e "FLUSH PRIVILEGES;"
	
	echo "importing databases..."
	mysql -u ${username} -p${userpass} wifi_positioning_delta < wifi_positioning_delta.sql
	for db_dump in wifi_positioning_test1 wifi_positioning_test2 wifi_positioning_test3
	do
		mysql -u${username} -p${userpass} $db_dump < wifi_positioning_empty_dump.sql
	done
	
	echo "You're good now :)"
	exit
fi
