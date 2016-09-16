#!/usr/bin/python

import fcntl
import time
import unittest


class TSYS01 :
    #control constants

	# TSYS01 device address
	_TSYS01_ADDR = 0x77
	
	# TSYS01 device command
	_TSYS01_RESET_COMMAND = 0x1E
	_TSYS01_START_ADC_CONVERSION = 0x48
	_TSYS01_READ_ADC_TEMPERATURE = 0x00
	_TSYS01_CONVERSION_TIME = 0.010
	
	# TSYS01 commands read eeprom
	_PROM_ADDRESS_READ_ADDRESS_0 = 0xA0
	_PROM_ADDRESS_READ_ADDRESS_1 = 0xA2
	_PROM_ADDRESS_READ_ADDRESS_2 = 0xA4
	_PROM_ADDRESS_READ_ADDRESS_3 = 0xA6
	_PROM_ADDRESS_READ_ADDRESS_4 = 0xA8
	_PROM_ADDRESS_READ_ADDRESS_5 = 0xAA
	_PROM_ADDRESS_READ_ADDRESS_6 = 0xAC
	_PROM_ADDRESS_READ_ADDRESS_7 = 0xAE
	_PROM_ELEMENTS_NUMBER = 8
	
	_COEFF_MUL_0 = (-1.5)
	_COEFF_MUL_1 = (1)
	_COEFF_MUL_2 = (-2)
	_COEFF_MUL_3 = (4)
	_COEFF_MUL_4 = (-2)
	
	eeprom_coeff = [0,0,0,0,0,0,0,0]
	coeff_valid = False

    #From: /linux/i2c-dev.h
	I2C_SLAVE = 0x0703
	I2C_SLAVE_FORCE = 0x0706

	def __init__(self, device_number=0) :
		self.i2c = open('/dev/i2c-%s'%(device_number),'r+',0)
		fcntl.ioctl(self.i2c, self.I2C_SLAVE, self._TSYS01_ADDR)
		self.i2c.write(chr(self._TSYS01_RESET_COMMAND))
		time.sleep(0.015)

	# brief read eeprom coeff.
	# \param[in] address of coefficient in EEPROM
	# return :
	#		-> Data read 
	def read_eeprom_coeff (self, cmd) : 
		self.i2c.write(chr(cmd))
		data = self.i2c.read(2)
		return (ord(data[0]) << 8) + ord(data[1])

	#\brief Reads the ms5637 EEPROM coefficients to store them for computation.
	# return :
	#		-> All coefficients read in the EEPROM 
	def read_eeprom(self) : 
		a = 0
		coeffs = [0,0,0,0,0,0,0,0]
		
		liste = [self._PROM_ADDRESS_READ_ADDRESS_0,
		self._PROM_ADDRESS_READ_ADDRESS_1,
		self._PROM_ADDRESS_READ_ADDRESS_2,
		self._PROM_ADDRESS_READ_ADDRESS_3,
		self._PROM_ADDRESS_READ_ADDRESS_4,
		self._PROM_ADDRESS_READ_ADDRESS_5,
		self._PROM_ADDRESS_READ_ADDRESS_6,
		self._PROM_ADDRESS_READ_ADDRESS_7]
		
		for i in liste :
			coeffs[a] = self.read_eeprom_coeff(i)
			a = a+1
		if self.crc_check(coeffs) :
			self.coeff_valid = True			
			return coeffs

	# brief Triggers conversion and read ADC value
	# \param[in] : Command used for conversion (will determine Temperature vs Pressure and osr)
	# return :
	#		-> Adc value
	def convertion_read_adc(self) :
		self.i2c.write(chr(self._TSYS01_START_ADC_CONVERSION))
		time.sleep(self._TSYS01_CONVERSION_TIME)
		self.i2c.write(chr(self._TSYS01_READ_ADC_TEMPERATURE))
		data = self.i2c.read(3)
		adc = (ord(data[0]) * 0x10000) + ord(data[1]) * 0x100 + ord(data[2])
		return adc

	# brief Reads the temperature and pressure ADC value and compute the compensated values.
	# \param[in] : None
	# return :
	#		-> temperature (float) : Celsius Degree temperature value
	def read_temperature(self) :
		i = 4
		temp = 0
		coeff_mul = [self._COEFF_MUL_0,
		self._COEFF_MUL_1,
		self._COEFF_MUL_2,
		self._COEFF_MUL_3,
		self._COEFF_MUL_4]
		
		if self.coeff_valid == False :
			
			self.eeprom_coeff = self.read_eeprom()
		
		adc = self.convertion_read_adc()
		adc /= 256;
		while i > 0 :
			temp += coeff_mul[i] * self.eeprom_coeff[1+(4-i)] # eeprom_coeff[1+(4-i)] equiv. ki
			temp = temp * adc / 100000.0
			i -= 1

		temp *= 10.0
		temp += float(coeff_mul[0] * self.eeprom_coeff[5]);
		temp /= 100.0;
		return temp

	# brief CRC check
	# \param[in] : EEPROM Coefficients
	# return :
	#		-> (bool) True if the CRC is OK, else False
	def crc_check (self,n_prom) :
		sum = 0
		cnt = 0
		while cnt < self._PROM_ELEMENTS_NUMBER :
			sum += ( ( n_prom[cnt] >>8 ) + ( n_prom[cnt] & 0xFF ) )
			cnt += 1
		return  ( sum & 0xFF == 0 )

	def close(self):
		self.i2c.close()

	def __enter__(self):
		return self        

	def __exit__(self, type, value, traceback):
		self.close()

if __name__ == "__main__":
	try:
		with TSYS01(1) as tsys01:
			print "Temperature: %.1f" % tsys01.read_temperature()
	except IOError, e:
		print e
		print "Error creating connection to i2c.  This must be run as root"
