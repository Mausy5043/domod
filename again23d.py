#!/usr/bin/env python3

# daemon23.py measures the BMP183 pressure and temperature.
# uses moving averages

# Wiring:
# BMP pin : RPi pin
# ========:====================
# VIN     : 17  (3v3)
# 3vo     : N/C
# GND     : 25  (GND)
# SCLK    : 23  (GPIO11)
# SDO     : 21  (GPIO09; MISO)
# SDI     : 19  (GPIO10; MOSI)
# CS      : 24  (GPIO08; CE0)

import configparser
import os
import sys
import syslog
import time
import traceback

from libdaemon import Daemon
from pigbmp183 import bmp183

bmp = bmp183()

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
BMP183T_gain = 1.0
BMP183P_gain = 1.0
# offset(old)
BMP183T_offset = -0.2
BMP183P_offset = 0.0

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

        state, result      = do_work(home)
        syslog_trace("Result   : {0}".format(result), False, DEBUG)
        if (state == 85):
          result = result.split(',')
          data.append([float(d) for d in result])
          if (len(data) > samples):
            data.pop(0)
          syslog_trace("Data     : {0}".format(data),   False, DEBUG)

          # report sample average
          if (startTime % reportTime < sampleTime):
            somma       = [sum(d) for d in zip(*data)]
            # not all entries should be float
            # 0.37, 0.18, 0.17, 4, 143, 32147, 3, 4, 93, 0, 0
            averages    = [float(format(sm / len(data), '.2f')) for sm in somma]
            # averages = map(float, averages)
            # averages  = format(sum(data[:]) / len(data), '.3f')
            syslog_trace("Averages : {0}".format(averages),  False, DEBUG)
            do_report(averages, flock, fdata)
        # endif result not None
        time.sleep(3.5)  # at least wait 3 seconds between meaurements
        waitTime    = sampleTime - (time.time() - startTime) - (startTime % sampleTime)
        if (waitTime > 0):
          syslog_trace("Waiting  : {0}s".format(waitTime), False, DEBUG)
          syslog_trace("................................", False, DEBUG)
          time.sleep(waitTime)
      except Exception:
        syslog_trace("Unexpected error in run()", syslog.LOG_CRIT, DEBUG)
        syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
        raise

def do_work(homedir):
  P0 = T0 = P = T = 0.11
  bmp.measure_pressure()
  P0 = bmp.pressure / 100.0  # hPa := mbar
  T0 = bmp.temperature
  state = bmp.ID

  P = P0 * BMP183P_gain + BMP183P_offset
  T = T0 * BMP183T_gain + BMP183T_offset
  syslog_trace("  T0 = {0:0.1f}*C        T = {1:0.1f}degC".format(T0, T), False, DEBUG)
  syslog_trace("  P0 = {0:0.1f}*mbar     P = {1:0.1f}mbar".format(P0, P), False, DEBUG)

  return state, '{0}, {1}'.format(P, T)

def do_report(result, flock, fdata):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate  = time.strftime('%Y-%m-%dT%H:%M:%S')
  outEpoch = int(time.strftime('%s'))
  # round to current minute to ease database JOINs
  outEpoch = outEpoch - (outEpoch % 60)
  result   = ', '.join(map(str, result))
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
