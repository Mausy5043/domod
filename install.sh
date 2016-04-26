#!/bin/bash

# this repo gets installed either manually by the user or automatically by
# a `*boot` repo.

ME=$(whoami)

echo -n "Started installing DOMOD on "; date
minit=$(echo $RANDOM/555 |bc)
echo "MINIT = "$minit
pushd "$HOME/domod"
  # To suppress git detecting changes by chmod:
  git config core.fileMode false
  # set the branch
  if [ ! -e "$HOME/.domod.branch" ]; then
    echo "v0" > "$HOME/.domod.branch"
  fi

  # Create the /etc/cron.d directory if it doesn't exist
  sudo mkdir -p /etc/cron.d
  # Set up some cronjobs
  echo "# m h dom mon dow user  command" | sudo tee /etc/cron.d/domod
  echo "$MINIT  * *   *   *   $ME    $HOME/domod/update.sh 2>&1 | logger -p info -t domod" | sudo tee --append /etc/cron.d/domod
  # @reboot we allow for 120s for the WiFi to come up:
  echo "@reboot               $ME    sleep 120; $HOME/domod/update.sh 2>&1 | logger -p info -t domod" | sudo tee --append /etc/cron.d/domod
  # ref: http://abyz.co.uk/rpi/pigpio/examples.html#pdif2_DHTXXD
  pushd DHTXXD
    gcc -Wall -pthread -o DHTXXD test_DHTXXD.c DHTXXD.c -lpigpiod_if2

    sudo pigpiod
    ./DHTXXD -g18
  popd
popd

echo -n "Finished installation of DOMOD on "; date
