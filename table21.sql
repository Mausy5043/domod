# MySQL script
# create table for DS18B20 readings

USE domotica;

DROP TABLE IF EXISTS ds18;

CREATE TABLE `ds18` (
  `sample_time`   datetime,
  `sample_epoch`  bigint(20) unsigned,
  `temperature`   decimal(5,2),
  PRIMARY KEY (`sample_time`),
  INDEX (`sample_epoch`)
  ) ENGINE=InnoDB DEFAULT CHARSET=latin1 ;

# example to retrieve data:
-- mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM bmp183 where (sample_time) >=NOW() - INTERVAL 6 HOUR;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql.csv
