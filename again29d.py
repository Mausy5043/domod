#!/usr/bin/env python3

# daemon29.py reads winddata from an external weatherstation managed by KNMI.

import configparser
import os
import sys
import syslog
import time
import traceback

from libdaemon import Daemon

from urllib.request import Request, urlopen
from lxml import etree
# from bs4 import BeautifulSoup

# constants
DEBUG       = False
IS_JOURNALD = os.path.isfile('/bin/journalctl')
MYID        = "".join(list(filter(str.isdigit, os.path.realpath(__file__).split('/')[-1])))
MYAPP       = os.path.realpath(__file__).split('/')[-2]
NODE        = os.uname()[1]

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

    # Start by getting external data.
    EXTERNAL_DATA_EXPIRY_TIME = 5 * 60  # seconds
    # This decouples the fetching of external data
    # from the reporting cycle.
    result = do_work().split(', ')
    syslog_trace("Result   : {0}".format(result), False, DEBUG)
    # data.append([float(d) for d in result])
    extern_time = time.time() + EXTERNAL_DATA_EXPIRY_TIME

    while True:
      try:
        startTime = time.time()
        da = [float(d) for d in result]
        if ((da)[0] >= 0.0) and ((da)[1] >= 0.0):
          data.append([float(d) for d in result])
          if (len(data) > samples):
            data.pop(0)
          syslog_trace("Data     : {0}".format(data),   False, DEBUG)

        # report sample average
        if (startTime % reportTime < sampleTime):   # sync reports to reportTime
          somma       = [sum(d) for d in zip(*data)]
          averages    = [float(format(sm / len(data), '.3f')) for sm in somma]
          syslog_trace("Averages : {0}".format(averages),  False, DEBUG)

          # only fetch external data if current data is
          # older than EXTERNAL_DATA_EXPIRY_TIME
          if (extern_time < time.time()):
            result = do_work().split(', ')
            syslog_trace("Result   : {0}".format(result), False, DEBUG)
            da = [float(d) for d in result]
            if ((da)[0] >= 0.0) and ((da)[1] >= 0.0):
              data.append([float(d) for d in result])
              if (len(data) > samples):
                data.pop(0)
            extern_time = time.time() + EXTERNAL_DATA_EXPIRY_TIME

          do_report(averages, flock, fdata)

          waitTime    = sampleTime - (time.time() - startTime) - (startTime % sampleTime)
          if (waitTime > 0):
            syslog_trace("Waiting  : {0}s".format(waitTime), False, DEBUG)
            syslog_trace("................................", False, DEBUG)
            time.sleep(waitTime)
      except Exception:
        syslog_trace("Unexpected error in run()", syslog.LOG_CRIT, DEBUG)
        syslog_trace(traceback.format_exc(), syslog.LOG_CRIT, DEBUG)
        raise

def do_work():
  # set defaults
  ms = -1.0
  gr = -1.0

  ardtime = time.time()
  try:
    req = Request("http://xml.buienradar.nl/")
    response = urlopen(req, timeout=25)
    for event, elem in etree.iterparse(response, tag='weerstation'):
         if elem.get('id') == '6350':
             ms = elem.find('windsnelheidMS').text
             gr = elem.find('windrichtingGR').text
             break
         # clear elements we are not interested in
         elem.clear()
         for ancestor in elem.xpath('ancestor-or-self::*'):
             while ancestor.getprevious() is not None:
                 del ancestor.getparent()[0]

#    output = response.read()
#    soup = BeautifulSoup(output, "lxml")
    souptime = time.time()-ardtime

#    MSwind = str(soup.buienradarnl.weergegevens.actueel_weer.weerstations.find(id=6350).windsnelheidms)
#    GRwind = str(soup.buienradarnl.weergegevens.actueel_weer.weerstations.find(id=6350).windrichtinggr)
    # datum = str(soup.buienradarnl.weergegevens.actueel_weer.weerstations.find(id=6350).datum)
#    ms = MSwind.replace("<", " ").replace(">", " ").split()[1]
#    gr = GRwind.replace("<", " ").replace(">", " ").split()[1]

    syslog_trace(":   [do_work]  : {0:.2f}s".format(souptime), False, DEBUG)

  except Exception as err:
    logtext = "****** Exception encountered : {0}".format(err)
    syslog_trace(logtext, syslog.LOG_DEBUG, DEBUG)
    ardtime = time.time() - ardtime
    logtext = "****** after                 {0:.2f} s".format(ardtime)
    syslog_trace(logtext, syslog.LOG_DEBUG, DEBUG)

  gilzerijen = '{0}, {1}'.format(ms, gr)
  return gilzerijen

def calc_windchill(T, W):
  # use this data to determine the windchill temperature acc. JAG/TI
  # ref.: http://knmi.nl/bibliotheek/knmipubTR/TR309.pdf
  JagTi = 13.12 + 0.6215 * T - 11.37 * (W * 3.6)**0.16 + 0.3965 * T * (W * 3.6)**0.16
  if (JagTi > T):
    JagTi = T

  return JagTi

def do_report(result, flock, fdata):
  # Get the time and date in human-readable form and UN*X-epoch...
  outDate = time.strftime('%Y-%m-%dT%H:%M:%S')
  outEpoch = int(time.strftime('%s'))
  # round to current minute to ease database JOINs
  outEpoch = outEpoch - (outEpoch % 60)
  ardtime = time.time()
  result = ', '.join(map(str, result))
  # ext_result = ', '.join(map(str, ext_result))
  # flock = '/tmp/raspdiagd/23.lock'
  lock(flock)
  with open(fdata, 'a') as f:
    f.write('{0}, {1}, {2}\n'.format(outDate, outEpoch, result))
  unlock(flock)
  ardtime = time.time() - ardtime
  syslog_trace(":  [do_report] : {0}, {1} ".format(outDate, result), False, DEBUG)
  syslog_trace(":  [do_report] : {0:.2f} s".format(ardtime), False, DEBUG)

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
