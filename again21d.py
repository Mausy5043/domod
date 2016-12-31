#!/usr/bin/env python3

# again21.py measures the DS18B20 temperature.
# uses moving averages

# Wiring :
# Sensor pin       : R-Pi B+ pin
# =================:==============
# VIN   (red)      = 01  - 3v3
# Data  (yellow)   = 07  - GPIO04
# GND   (blue)     = 09  - GND

import configparser
import glob
import os
import sys
import syslog
import time
import traceback

from libdaemon import Daemon

# constants
DEBUG       = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID        = "".join(list(filter(str.isdigit, os.path.realpath(__file__).split('/')[-1])))
MYAPP       = os.path.realpath(__file__).split('/')[-2]
NODE        = os.uname()[1]

# SENSOR CALIBRATION PROCEDURE
# Given the existing gain and offset.
# 1 Determine a linear least-squares fit between the output of this program and
#   data obtained from a reference sensor
# 2 The least-squares fit will yield the gain(calc) and offset(calc)
# 3 Determine gain(new) and offset(new) as shown here:
#     gain(new)   = gain(old)   * gain(calc)
#     offset(new) = offset(old) * gain(calc) + offset(calc)
# 4 Replace the existing values for gain(old) and offset(old) with the values
#   found for gain(new) and offset(new)

# gain(old)
DS18B20_gain = 1.0
# offset(old)
DS18B20_offset = 0.0

OWdir = '/sys/bus/w1/devices/'
OWdev = glob.glob(OWdir + '28*')[0]
OWfile = OWdev + '/w1_slave'

class MyDaemon(Daemon):
  def run(self):
    iniconf         = configparser.ConfigParser()
    inisection      = MYID
    home            = os.path.expanduser('~')
    s               = iniconf.read(home + '/' + MYAPP + '/config.ini')
    syslog_trace("Config file   : {0}".format(s), False, DEBUG)
    syslog_trace("Options       : {0}".format(iniconf.items(inisection)), False, DEBUG)
    reportTime      = iniconf.getint(inisection, "reporttime")
    cycles          = iniconf.getint(inisection, "cycles")
    samplesperCycle = iniconf.getint(inisection, "samplespercycle")
    flock           = iniconf.get(inisection, "lockfile")
    fdata           = iniconf.get(inisection, "resultfile")

    samples         = samplesperCycle * cycles           # total number of samples averaged
    sampleTime      = reportTime/samplesperCycle         # time [s] between samples
    # cycleTime       = samples * sampleTime               # time [s] per cycle

    data            = []                                 # array for holding sampledata

    while True:
      try:
        startTime   = time.time()

        result      = do_work()
        syslog_trace("Result   : {0}".format(result), False, DEBUG)
        if (result is not None):
          data.append(float(result))
          if (len(data) > samples):
            data.pop(0)
          syslog_trace("Data     : {0}".format(data),   False, DEBUG)

          # report sample average
          if (startTime % reportTime < sampleTime):
            averages  = format(sum(data[:]) / len(data), '.2f')
            syslog_trace("Averages : {0}".format(averages),  False, DEBUG)
            do_report(averages, flock, fdata)
        # endif result not None

        waitTime    = sampleTime - (time.time() - startTime) - (startTime % sampleTime)
        if (waitTime > 0):
          syslog_trace("Waiting  : {0}s".format(waitTime), False, DEBUG)
          syslog_trace("................................", False, DEBUG)
          time.sleep(waitTime)
      except Exception:
        syslog_trace("Unexpected error in run()", syslog.LOG_CRIT, DEBUG)
        syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
        raise


def read_temp_raw():
  lines = "NOPE"
  if not(os.path.isfile(OWfile)):
    syslog_trace("1-wire sensor not available", syslog.LOG_ERR, DEBUG)
  else:
    with open(OWfile, 'r') as f:
      lines = f.readlines()
  return lines

def do_work():
  T = T0 = None

  # read the temperature sensor
  lines = read_temp_raw()
  if lines[0].strip()[-3:] == 'YES':
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
      temp_string = lines[1][equals_pos+2:]
      T0 = float(temp_string) / 1000.0

  # correct the temperature reading
  if T0 is not None:
    T = T0 * DS18B20_gain + DS18B20_offset
    syslog_trace("  T0 = {0:0.1f}*C        T = {1:0.1f}degC".format(T0, T), False, DEBUG)

  # validate the temperature
  if (T is not None) and (T > 45.0):
    # can't believe my sensors. Probably a glitch. Log this and return with no result
    syslog_trace("Tambient (HIGH): {0}".format(T), syslog.LOG_WARNING, DEBUG)
    T = None

  return T

def do_report(result, flock, fdata):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate  = time.strftime('%Y-%m-%dT%H:%M:%S')
  outEpoch = int(time.strftime('%s'))
  # round to current minute to ease database JOINs
  outEpoch = outEpoch - (outEpoch % 60)
  lock(flock)
  with open(fdata, 'a') as f:
    f.write('{0}, {1}, {2}\n'.format(outDate, outEpoch, result))
  unlock(flock)

def lock(fname):
  open(fname, 'a').close()

def unlock(fname):
  if os.path.isfile(fname):
    os.remove(fname)

def syslog_trace(trace, logerr, out2console):
  # Log a python stack trace to syslog
  log_lines = trace.split('\n')
  for line in log_lines:
    if line and logerr:
      syslog.syslog(logerr, line)
    if line and out2console:
      print(line)

if __name__ == "__main__":
  daemon = MyDaemon('/tmp/' + MYAPP + '/' + MYID + '.pid')
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    elif 'foreground' == sys.argv[1]:
      # assist with debugging.
      print("Debug-mode started. Use <Ctrl>+C to stop.")
      DEBUG = True
      syslog_trace("Daemon logging is ON", syslog.LOG_DEBUG, DEBUG)
      daemon.run()
    else:
      print("Unknown command")
      sys.exit(2)
    sys.exit(0)
  else:
    print("usage: {0!s} start|stop|restart|foreground".format(sys.argv[0]))
    sys.exit(2)
