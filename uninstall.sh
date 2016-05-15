#!/bin/bash

# this repo gets installed either manually by the user or automatically by
# a `*boot` repo.

# The hostname is in /etc/hostname prior to running `install.sh` here!
HOSTNAME=$(cat /etc/hostname)

echo -n "Started UNinstalling DOMOD on "; date

pushd "$HOME/domod"
 source ./includes

  sudo rm /etc/cron.d/domod

  echo "  Stopping all diagnostic daemons"
  for daemon in $againlist; do
    echo "Stopping "$daemon
    eval "./again"$daemon"d.py stop"
  done
  echo "  Stopping all service daemons"
  for daemon in $srvclist; do
    echo "Stopping "$daemon
    eval "./again"$daemon"d.py stop"
  done
popd

echo -n "Finished UNinstallation of DOMOD on "; date
