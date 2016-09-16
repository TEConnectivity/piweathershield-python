#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys
import pprint

from htu21d import HTU21D
from ms5637 import MS5637
from tsys01 import TSYS01
from tsd305 import TSD305

class PiWeatherShield:
	htu21d = HTU21D(1)
	ms5637 = MS5637(1)
	tsys01 = TSYS01(1)
	tsd305 = TSD305(1)

if __name__ == "__main__":
	try:
		weatherShield = PiWeatherShield()

  		print "========================================" 
  		print "=== TE Connectivity Sensor Solutions ===";
  		print "===== Raspeberry Pi Weather Shield ====="; 

  		print "\n---------------- HTU21D ----------------"
		temperature = weatherShield.htu21d.read_temperature()
		humidity = weatherShield.htu21d.read_humidity()
		print "Temperature: %.1f°C" % temperature
		print "Humidity: %.1f%%" % humidity

  		print "\n---------------- MS5637 ----------------" 
		(temperature, pressure) = weatherShield.ms5637.read_temperature_and_pressure()
		print "Temperature: %.1f°C" % temperature
		print "Pressure: %.2fhPa" % pressure

  		print "\n---------------- TSYS01 ----------------" 
		temperature = weatherShield.tsys01.read_temperature()
		print "Temperature: %.1f" % temperature

  		print "\n---------------- TSD305 ----------------" 
		(temperature, object_temperature) = weatherShield.tsd305.read_temperature_and_object_temperature()
		print "Temperature: %.1f°C" % temperature
		print "Object temperature: %.1f°C" % object_temperature

  		print "\n========================================" 
	except IOError, e:
		print e
		print "Error creating connection to i2c.  This must be run as root"
