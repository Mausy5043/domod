#!/usr/bin/env python

import pigpio
import time
import numpy

# BMP pin : RPi pin
# ========:====================
# VIN     : 17  (3v3)
# 3vo     : N/C
# GND     : 25  (GND)
# SCLK    : 23  (GPIO11)
# SDO     : 21  (GPIO09; MISO)
# SDI     : 19  (GPIO10; MOSI)
# CS      : 24  (GPIO08; CE0)

class bmp183():
  """
  For use on Raspberry Pi
  Class for Bosch BMP183 pressure and temperature sensor with SPI interface as sold by Adafruit
  Does not require sudo.
  """
  # BMP183 registers
  BMP183_REG = {
    # @ Calibration data
    'CAL_AC1':            0xAA,
    'CAL_AC2':            0xAC,
    'CAL_AC3':            0xAE,
    'CAL_AC4':            0xB0,
    'CAL_AC5':            0xB2,
    'CAL_AC6':            0xB4,
    'CAL_B1':             0xB6,
    'CAL_B2':             0xB8,
    'CAL_MB':             0xBA,
    'CAL_MC':             0xBC,
    'CAL_MD':             0xBE,

    # @ Chip ID. Value fixed to 0x55. Useful to check if communication works
    'ID':                 0xD0,

    # @ VER Undocumented
    'VER':                0xD1,

    # @ SOFT_RESET Write only. If set to 0xB6, will perform the same sequence as power on reset.
    'SOFT_RESET':         0xE0,

    # @ CTRL_MEAS Controls measurements
    # In order to *WRITE* to address 0xF4 you need to clear bit 8 in the SPI commands
    'CTRL_MEAS':          0x74,

    # @ DATA
    # In order to *READ* from address 0xF6 no adjustment is needed (bit 8 = 1)
    'DATA':               0xF6,
  }

  # BMP183 commands
  BMP183_CMD = {
    # @ Chip ID Value fixed to 0x55. Useful to check if communication works
    'ID_VALUE':           0x55,

    # Read TEMPERATURE, Wait time 4.5 ms
    'TEMP':               0x2E,
    'TEMP_WAIT':          0.0045,

    # Read PRESSURE
    'PRESS':              0x34,  # 001

    # PRESSURE reading modes
    # Example usage: (PRESS || (OVERSAMPLE_2 << 4)
    'OVERSAMPLE_0':       0x0,  # ultra low power, no oversampling, wait time 4.5 ms
    'OVERSAMPLE_0_WAIT':  0.0045,
    'OVERSAMPLE_1':       0x1,  # standard, 2 internal samples, wait time 7.5 ms
    'OVERSAMPLE_1_WAIT':  0.0075,
    'OVERSAMPLE_2':       0x2,  # high resolution, 4 internal samples, wait time 13.5 ms
    'OVERSAMPLE_2_WAIT':  0.0135,
    'OVERSAMPLE_3':       0x3,  # ultra high resolution, 8 internal samples, Wait time 25.5 ms
    'OVERSAMPLE_3_WAIT':  0.0255,
  }

  def __init__(self):
    self.temperature = 0
    self.pressure    = 0
    # Setup Raspberry Pi **pinnumbers**, as numbered on BOARD
    self.SCK         = 23  # pin for SCLK
    self.SDO         = 21  # pin for MISO
    self.SDI         = 19  # pin for MOSI
    self.CS          = 24  # pin for CE0

    self.set_up_pigpio()

    # Check communication / read ID
    ret = self.read_byte(self.BMP183_REG['ID'])
    if ret != self.BMP183_CMD['ID_VALUE']:
      print ("BMP183 returned ", ret, " instead of 0x55. Communication failed, expect problems.")

    self.read_calibration_data()
    # Proceed with initial pressure/temperature measurement
    self.measure_pressure()

  def __del__(self):
    self.cleanup_pigpio()

  def set_up_pigpio(self):
    # GPIO initialisation
    self.pi = pigpio.pi()

  def cleanup_pigpio(self):
    self.pi.stop()

  def read_byte(self, addr):
    # Read byte from SPI interface from address "addr"
    ret_value = -1
    if self.pi.connected:
      hndl = self.pi.spi_open(0, 34000, 3)
      (cnt, rxd) = self.pi.spi_xfer(hndl, [addr, 0])
      self.pi.spi_close(hndl)
      # Evaluate result
      if cnt == 2:
        ret_value = rxd[1]
    #   else:
    #     print("Unexpected return length: {0}".format(cnt))
    # else:
    #   print("Unexpected error: not connected to pigpio while trying to read byte {0}".format(addr))
    return ret_value

  def read_word(self, addr):
    # Read word from SPI interface from address "addr"
    ret_value = -1
    if self.pi.connected:
      hndl = self.pi.spi_open(0, 34000, 3)
      (cnt, rxd) = self.pi.spi_xfer(hndl, [addr, 0, 0])
      self.pi.spi_close(hndl)
      # Evaluate result
      if cnt == 3:
        ret_value = (rxd[1] << 8) + rxd[2]
    #   else:
    #     print("Unexpected return length: {0}".format(cnt))
    # else:
    #   print("Unexpected error: not connected to pigpio while trying to read word {0}".format(addr))
    return ret_value

  def read_calibration_data(self):
    # Read calibration data
    self.AC1 = numpy.int16(self.read_word(self.BMP183_REG['CAL_AC1']))
    self.AC2 = numpy.int16(self.read_word(self.BMP183_REG['CAL_AC2']))
    self.AC3 = numpy.int16(self.read_word(self.BMP183_REG['CAL_AC3']))
    self.AC4 = numpy.uint16(self.read_word(self.BMP183_REG['CAL_AC4']))
    self.AC5 = numpy.uint16(self.read_word(self.BMP183_REG['CAL_AC5']))
    self.AC6 = numpy.uint16(self.read_word(self.BMP183_REG['CAL_AC6']))
    self.B1  = numpy.int16(self.read_word(self.BMP183_REG['CAL_B1']))
    self.B2  = numpy.int16(self.read_word(self.BMP183_REG['CAL_B2']))
    self.MB  = numpy.int16(self.read_word(self.BMP183_REG['CAL_MB']))
    self.MC  = numpy.int16(self.read_word(self.BMP183_REG['CAL_MC']))
    self.MD  = numpy.int16(self.read_word(self.BMP183_REG['CAL_MD']))
    self.ID  = numpy.int16(self.read_byte(self.BMP183_REG['ID']))
    self.VER = numpy.int16(self.read_word(self.BMP183_REG['VER']))

  def measure_temperature(self):
    # Start temperature measurement
    F6 = 26400
    if self.pi.connected:
      hndl = self.pi.spi_open(0, 34000, 3)
      self.pi.spi_write(hndl, [self.BMP183_REG['CTRL_MEAS'], self.BMP183_CMD['TEMP'], 0])
      # Wait
      time.sleep(self.BMP183_CMD['TEMP_WAIT'])
      # Read uncompensated temperature
      (cnt, rxd) = self.pi.spi_xfer(hndl, [self.BMP183_REG['DATA'], 0, 0])
      # Evaluate result
      if cnt > 0:
        F6 = (rxd[1] << 8) + rxd[2]
        # print(">>T> Value stored at 0xF6 : {0}".format(F6))
        self.UT = numpy.int32(F6)
      # else:
      #   print("Unexpected return length: {0}".format(cnt))
      # close SPI
      self.pi.spi_close(hndl)
    # else:
    #   print("Unexpected error: not connected to pigpio while trying to read temperature")
    # Store uncompensated temperature
    self.UT = numpy.int32(F6)
    self.calculate_temperature()

  def measure_pressure(self):
    # Measure temperature - required for calculations
    self.measure_temperature()
    # Read 3 samples of uncompensated pressure
    UP = {}
    F6 = 26400
    if self.pi.connected:
      hndl = self.pi.spi_open(0, 34000, 3)
      for i in range(3):
        self.pi.spi_write(hndl, [self.BMP183_REG['CTRL_MEAS'], self.BMP183_CMD['PRESS'], 0]) + (self.BMP183_CMD['OVERSAMPLE_3'] << 6)
        # Wait
        time.sleep(self.BMP183_CMD['OVERSAMPLE_3_WAIT'])
        (cnt, rxd) = self.pi.spi_xfer(hndl, [self.BMP183_REG['DATA'], 0, 0, 0])
        # Evaluate result
        if cnt > 0:
          F6 = ((rxd[1] << 16) + (rxd[2] << 8) + rxd[3]) >> (8 - self.BMP183_CMD['OVERSAMPLE_3'])
          # print(">>P> Value stored at 0xF6 : {0}".format(F6))
          UP[i] = numpy.int32(F6)
        # else:
        #  print("Unexpected return length: {0}".format(cnt))
      # close SPI
      self.pi.spi_close(hndl)
    # else:
    #   print("Unexpected error: not connected to pigpio while trying to read temperature")
    # Store average uncompensated pressure
    self.UP = (UP[0] + UP[1] + UP[2]) / 3
    self.calculate_pressure()

  def calculate_pressure(self):
    # Calculate atmospheric pressure in [Pa]
    self.B6 = self.B5 - 4000
    X1 = (self.B2 * (self.B6 * self.B6 / 2 ** 12)) / 2 ** 11
    X2 = self.AC2 * self.B6 / 2 ** 11
    X3 = X1 + X2
    self.B3 = (((numpy.uint32(self.AC1 * 4 + X3)) << self.BMP183_CMD['OVERSAMPLE_3']) + 2) / 4
    X1 = self.AC3 * self.B6 / 2 ** 13
    X2 = (self.B1 * (self.B6 * self.B6 / 2 ** 12)) / 2 ** 16
    X3 = ((X1 + X2) + 2) / 2 ** 2
    self.B4 = numpy.uint32(self.AC4 * (X3 + 32768) / 2 ** 15)
    self.B7 = (numpy.uint32(self.UP) - self.B3) * (50000 >> self.BMP183_CMD['OVERSAMPLE_3'])
    p = numpy.uint32((self.B7 * 2) / self.B4)
    X1 = (p / 2 ** 8) * (p / 2 ** 8)
    X1 = int(X1 * 3038) / 2 ** 16
    X2 = int(-7357 * p) / 2 ** 16
    self.pressure = p + (X1 + X2 + 3791) / 2 ** 4

  def calculate_temperature(self):
    # Calculate temperature in [degC]
    X1 = (self.UT - self.AC6) * self.AC5 / 2 ** 15
    X2 = self.MC * 2 ** 11 / (X1 + self.MD)
    self.B5 = X1 + X2
    self.T = (self.B5 + 8) / 2 ** 4
    self.temperature = self.T / 10.0
