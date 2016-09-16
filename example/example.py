#!/usr/bin/python
# -*- coding: utf-8 -*-

from piweathershield import PiWeatherShield

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

