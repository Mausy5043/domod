#!/bin/bash

# Pull data from MySQL server and graph them.

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
UTCOFFSET=$(($LOCALSECONDS-$UTCSECONDS))

interval="INTERVAL 50 HOUR "
host=$(hostname)

pushd $HOME/domod >/dev/null
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM ds18  where (sample_time >=NOW() - $interval);" | sed 's/\t/;/g;s/\n//g' > /tmp/sql21.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM dht22 where (sample_time >=NOW() - $interval);" | sed 's/\t/;/g;s/\n//g' > /tmp/sql22.csv
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM sysnet  where (sample_time >=NOW() - $interval) AND (host = '$host');" | sed 's/\t/;/g;s/\n//g' > /tmp/sql13.csv
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM sysmem  where (sample_time >=NOW() - $interval) AND (host = '$host');" | sed 's/\t/;/g;s/\n//g' > /tmp/sql14.csv
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM syslog  where (sample_time >=NOW() - $interval) AND (host = '$host');" | sed 's/\t/;/g;s/\n//g' > /tmp/sql15.csv

  #http://www.sitepoint.com/understanding-sql-joins-mysql-database/
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT ds18.sample_time, ds18.sample_epoch, ds18.temperature, wind.speed FROM ds18 INNER JOIN wind ON ds18.sample_epoch = wind.sample_epoch WHERE (ds18.sample_time) >=NOW() - INTERVAL 1 MINUTE;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql2c.csv

  if [ $(cat /tmp/sql21.csv |wc -l) -gt 30 ]; then
    gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph21.gp
  fi
  if [ $(cat /tmp/sql22.csv |wc -l) -gt 30 ]; then
    gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph22.gp
  fi
  #if [ $(cat /tmp/sql13.csv |wc -l) -gt 30 ]; then
  #  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph13.gp
  #fi
  #if [ $(cat /tmp/sql14.csv |wc -l) -gt 30 ]; then
  #  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph14.gp
  #fi
  #if [ $(cat /tmp/sql15.csv |wc -l) -gt 30 ]; then
  #  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph15.gp
  #fi

popd >/dev/null
