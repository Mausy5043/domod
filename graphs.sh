#!/bin/bash

# Pull data from MySQL server and graph them.

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
UTCOFFSET=$((LOCALSECONDS - UTCSECONDS))

pushd "$HOME/domod" >/dev/null
  if [ $(wc -l < /tmp/domod/mysql/sql21d.csv) -gt 30 ]; then
    gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph21.gp &
  fi
  if [ $(wc -l < /tmp/domod/mysql/sql22d.csv) -gt 30 ]; then
    gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph22.gp &
  fi
  if [ $(wc -l < /tmp/domod/mysql/sql23d.csv) -gt 30 ]; then
    gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph23.gp &
  fi

  wait
  
popd >/dev/null
