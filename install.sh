#!/bin/bash

# this repo gets installed either manually by the user or automatically by
# a `*boot` repo.

ME=$(whoami)

echo -n "Started installing DOMOD on "; date
minit=$(echo $RANDOM/555 |bc)
echo "MINIT = $minit"

install_package()
{
  # See if packages are installed and install them.
  package=$1
  status=$(dpkg-query -W -f='${Status} ${Version}\n' $package 2>/dev/null | wc -l)
  if [ "$status" -eq 0 ]; then
    sudo apt-get -yuV install $package
  fi
}

sudo apt-get update

# install_package "git"  # already installed by `mod-rasbian-netinst`

# Python 2 package
# install_package "python"
# Python 3 package and associates
install_package "python3"
install_package "build-essential"
install_package "python3-dev"
install_package "python3-pip"
install_package "python3-numpy"
install_package "python-libxml2"
install_package "python-libxslt1"
install_package "python3-lxml"

# MySQL support
install_package "mysql-client"
install_package "libmysqlclient-dev"
# install_package "python-mysqldb"  # only required by python 2
sudo pip3 install mysqlclient     # only required by python 3


pushd "$HOME/domod"
  # To suppress git detecting changes by chmod:
  git config core.fileMode false
  # set the branch
  if [ ! -e "$HOME/.domod.branch" ]; then
    echo "python3" > "$HOME/.domod.branch"
  fi

  # Create the /etc/cron.d directory if it doesn't exist
  sudo mkdir -p /etc/cron.d
  # Set up some cronjobs
  echo "# m h dom mon dow user  command" | sudo tee /etc/cron.d/domod
  echo "$minit  * *   *   *   $ME    $HOME/domod/update.sh 2>&1 | logger -p info -t domod" | sudo tee --append /etc/cron.d/domod
  # @reboot we allow for 120s for the WiFi to come up:
  echo "@reboot               $ME    sleep 120; $HOME/domod/update.sh 2>&1 | logger -p info -t domod" | sudo tee --append /etc/cron.d/domod
  # ref: http://abyz.co.uk/rpi/pigpio/examples.html#pdif2_DHTXXD
  pushd DHTXXD
    gcc -Wall -pthread -o DHTXXD test_DHTXXD.c DHTXXD.c -lpigpiod_if2
    # sudo pigpiod
    mv DHTXXD "$HOME/bin/DHTXXD"
    DHTXXD -g18
  popd
popd

echo -n "Finished installation of DOMOD on "; date
