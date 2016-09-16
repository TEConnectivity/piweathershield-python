#!/usr/bin/python
import fcntl
import time
import unittest

class HTU21D:
	#control constants	
	_I2C_ADDRESS = 0x40
	
	_SOFTRESET = 0xFE
	_TRIGGER_TEMPERATURE_NO_HOLD = 0xF3
	_TRIGGER_HUMIDITY_NO_HOLD = 0xF5

	#From: /linux/i2c-dev.h
	I2C_SLAVE = 0x0703
	I2C_SLAVE_FORCE = 0x0706

	def __init__(self, device_number=1):
		self.i2c = open('/dev/i2c-%s'%(device_number),'r+',0)
		fcntl.ioctl(self.i2c, self.I2C_SLAVE,0x40)
		self.i2c.write(chr(self._SOFTRESET))
		time.sleep(0.015)

	def read_temperature(self):
		self.i2c.write(chr(self._TRIGGER_TEMPERATURE_NO_HOLD))
		time.sleep(0.050)
		data = self.i2c.read(3)
		if self._calculate_checksum(data,2) == ord(data[2]):
			return self._get_temperature_from_buffer(data)		

	def read_humidity(self):
		self.i2c.write(chr(self._TRIGGER_HUMIDITY_NO_HOLD))
		time.sleep(0.025)
		data = self.i2c.read(3)
		if self._calculate_checksum(data,2) == ord(data[2]):
			return self._get_humidity_from_buffer(data)			

	def close(self):
		self.i2c.close()

	def __enter__(self):
		return self		

	def __exit__(self, type, value, traceback):
		self.close()

	def _calculate_checksum(self, data, nbrOfBytes):
		POLYNOMIAL = 0x131 # //P(x)=x^8+x^5+x^4+1 = 100110001
		crc = 0

		for byteCtr in range(nbrOfBytes):
			crc ^= (ord(data[byteCtr]))
			for bit in range(8,0,-1):
				if (crc & 0x80):
					crc = (crc << 1) ^ POLYNOMIAL
				else:
					crc = (crc << 1)
		return crc

	def _get_temperature_from_buffer(self, data):
		raw = (ord(data[0]) << 8) + ord(data[1])
		raw *= 175.72
		raw /= 1 << 16
		raw -= 46.85
		return raw

	def _get_humidity_from_buffer(self, data):
		raw = (ord(data[0]) << 8) + ord(data[1])
		raw *= 125.0
		raw /= 1 << 16
		raw -= 6
		return raw

if __name__ == "__main__":
	try:
		with HTU21D(1) as htu21d:
			print "Temperature: %.1f" % htu21d.read_temperature()
			print "Humidity: %.1f" % htu21d.read_humidity()
	except IOError, e:
		print e
		print "Error creating connection to i2c.  This must be run as root"
