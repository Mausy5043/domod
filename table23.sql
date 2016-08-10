# MySQL script
# create table for BMP183 readings

USE domotica;

DROP TABLE IF EXISTS bmp183;

CREATE TABLE `bmp183` (
  `sample_time`   datetime,
  `sample_epoch`  bigint(11) unsigned,
  `pressure`      decimal(6,2),
  `temperature`   decimal(5,2),
  PRIMARY KEY (`sample_time`)
  ) ENGINE=InnoDB DEFAULT CHARSET=latin1 ;

# example to retrieve data:
-- mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM dht22 where (sample_time) >=NOW() - INTERVAL 6 HOUR;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql.csv
