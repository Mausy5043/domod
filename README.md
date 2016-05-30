# domod
Platform independent domotica data gatherer.

# Installing

```
sudo su -
cd /path/to/where/you/want/store/domod
git clone https://github.com/Mausy5043/domod.git
cd domod
./install.sh
./update.sh
```

# Requirements
## Hardware:
The python scripts have been shown to work correctly on the following hardware:
 - Raspberry Pi 1B+

## Known working kernels:
The python scripts are known **not** to work on 3.8.x kernels. 
The following kernels have been tested and are considered to be working:
**Linux rbian 4.4.8+ #880 Fri Apr 22 21:27:42 BST 2016 armv6l GNU/Linux**
https://github.com/Hexxeh/rpi-firmware/commit/6d158adcc0cfa03afa17665715706e6e5f0750d2

**Linux rbagain 4.4.11+ #886 Thu May 19 15:14:34 BST 2016 armv6l GNU/Linux**
https://github.com/Hexxeh/rpi-firmware/commit/48cfa89779408ecd69db4eb793b846fb7fe40c4b

Kernels not listed above have not been tested, but may work nevertheless.

Theoretically, commits [listed here](https://github.com/Hexxeh/rpi-firmware/commits) as "kernel: bump to ..." should work.

# Attribution
The python code for the daemons is based on previous work by
- [Charles Menguy](http://stackoverflow.com/questions/10217067/implementing-a-full-python-unix-style-daemon-process)
- [Sander Marechal](http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)
