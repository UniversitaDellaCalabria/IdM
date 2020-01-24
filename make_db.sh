export USER='thatuser'
export PASS='thatpassw'
export HOST='%'
export DB='thatdb'

mysql -u root -e "\
CREATE USER IF NOT EXISTS ${USER}@'${HOST}' IDENTIFIED BY '${PASS}';\
CREATE DATABASE  IF NOT EXISTS ${DB} CHARACTER SET utf8 COLLATE utf8_general_ci;\
GRANT ALL PRIVILEGES ON ${DB}.* TO ${USER}@'${HOST}' IDENTIFIED BY '${PASS}';"
