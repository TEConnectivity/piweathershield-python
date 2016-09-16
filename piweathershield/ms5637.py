#!/usr/bin/python
import fcntl
import time
import unittest

class MS5637:
    #control constants
	
	# MS5637 device address
	_I2C_ADDRESS = 0x76
	
	# MS5637 device commands
	_SOFTRESET = 0x1E
	_MS5637_START_PRESSURE_ADC_CONVERSION = 0x40
	_MS5637_START_TEMPERATURE_ADC_CONVERSION = 0x50
	_MS5637_CONVERSION_OSR_MASK = 0x0F
	_ADC_READ = 0x00

	# MS5637 commands read eeprom
	_MS5637_PROM_ADDRESS_READ_ADDRESS_0 = 0xA0
	_MS5637_PROM_ADDRESS_READ_ADDRESS_1 = 0xA2
	_MS5637_PROM_ADDRESS_READ_ADDRESS_2 = 0xA4
	_MS5637_PROM_ADDRESS_READ_ADDRESS_3	= 0xA6
	_MS5637_PROM_ADDRESS_READ_ADDRESS_4	= 0xA8
	_MS5637_PROM_ADDRESS_READ_ADDRESS_5	= 0xAA
	_MS5637_PROM_ADDRESS_READ_ADDRESS_6	= 0xAC
	
	# MS5637 commands conversion time
	_MS5637_CONVERSION_TIME_OSR_256	= 0.001
	_MS5637_CONVERSION_TIME_OSR_512 = 0.002
	_MS5637_CONVERSION_TIME_OSR_1024 = 0.003
	_MS5637_CONVERSION_TIME_OSR_2048 = 0.005
	_MS5637_CONVERSION_TIME_OSR_4096 = 0.009
	_MS5637_CONVERSION_TIME_OSR_8192 = 0.017
	
	# MS5637 commands resolution 
	_RESOLUTION_OSR_256 = 0
	_RESOLUTION_OSR_512 = 1 
	_RESOLUTION_OSR_1024 = 2
	_RESOLUTION_OSR_2048 = 3
	_RESOLUTION_OSR_4096 = 4
	_RESOLUTION_OSR_8192 = 5
	
	# Coefficients indexes for temperature and pressure computation
	_MS5637_CRC_INDEX = 0
	_MS5637_PRESSURE_SENSITIVITY_INDEX = 1 
	_MS5637_PRESSURE_OFFSET_INDEX = 2
	_MS5637_TEMP_COEFF_OF_PRESSURE_SENSITIVITY_INDEX = 3
	_MS5637_TEMP_COEFF_OF_PRESSURE_OFFSET_INDEX = 4
	_MS5637_REFERENCE_TEMPERATURE_INDEX	= 5
	_MS5637_TEMP_COEFF_OF_TEMPERATURE_INDEX = 6
	
	eeprom_coeff = [0,0,0,0,0,0,0,0]
	
	coeff_valid = False

    #From: /linux/i2c-dev.h
	I2C_SLAVE = 0x0703
	I2C_SLAVE_FORCE = 0x0706

	def __init__(self, device_number=0) :
		self.i2c = open('/dev/i2c-%s'%(device_number),'r+',0)
		fcntl.ioctl(self.i2c, self.I2C_SLAVE, self._I2C_ADDRESS)
		self.i2c.write(chr(self._SOFTRESET))
		time.sleep(0.015)

	# brief Set  ADC resolution.
	# \param[in] ms5637_resolution_osr : Resolution requested
	# return :
	#		-> temperature command
	#		-> pressure command
	#		-> temperature conversion time 
	#		-> pressure conversion time 
	def set_resoltuion(self,res) :
		time = [self._MS5637_CONVERSION_TIME_OSR_256,
		self._MS5637_CONVERSION_TIME_OSR_512,
		self._MS5637_CONVERSION_TIME_OSR_1024,
		self._MS5637_CONVERSION_TIME_OSR_2048,
		self._MS5637_CONVERSION_TIME_OSR_4096,
		self._MS5637_CONVERSION_TIME_OSR_8192]
		cmd_temp = res *2;
		cmd_temp |= self._MS5637_START_TEMPERATURE_ADC_CONVERSION;
		_time_temp = time[(cmd_temp & self._MS5637_CONVERSION_OSR_MASK)/2]
		
		cmd_pressure = res *2;
		cmd_pressure |= self._MS5637_START_PRESSURE_ADC_CONVERSION;
		_time_pressure = time[(cmd_pressure & self._MS5637_CONVERSION_OSR_MASK)/2]
		return cmd_temp,cmd_pressure, _time_temp, _time_pressure

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
		crc_OK = False
		
		liste = [self._MS5637_PROM_ADDRESS_READ_ADDRESS_0,
		self._MS5637_PROM_ADDRESS_READ_ADDRESS_1,
		self._MS5637_PROM_ADDRESS_READ_ADDRESS_2,
		self._MS5637_PROM_ADDRESS_READ_ADDRESS_3,
		self._MS5637_PROM_ADDRESS_READ_ADDRESS_4,
		self._MS5637_PROM_ADDRESS_READ_ADDRESS_5,
		self._MS5637_PROM_ADDRESS_READ_ADDRESS_6,]
		
		for i in liste :
			coeffs[a] = self.read_eeprom_coeff(i)
			a = a+1
		crc_OK = self.crc_check(coeffs)
		if crc_OK != True :
			self.coeff_valid = True
			return coeffs

	# brief Triggers conversion and read ADC value
	# \param[in] : Command used for conversion (will determine Temperature vs Pressure and osr)
	# return :
	#		-> Adc value
	def convertion_read_adc(self,cmd,_time) :
		self.i2c.write(chr(cmd))
		time.sleep(_time)
		self.i2c.write(chr(self._ADC_READ))
		data = self.i2c.read(3)
		adc = (ord(data[0]) * 0x10000) + ord(data[1]) * 0x100 + ord(data[2])
		return adc

	# brief Reads the temperature and pressure ADC value and compute the compensated values.
	# \param[in] : Resolution command
	# return :
	#		-> temperature (float) : Celsius Degree temperature value
	#		-> pressure (float) : mbar pressure value
	def read_temperature_and_pressure(self,res=_RESOLUTION_OSR_8192) :
		if self.coeff_valid == False :
			self.eeprom_coeff = self.read_eeprom()
		(cmd_temp, cmd_pressure,_time_temp,_time_pressure) = self.set_resoltuion(res)
		
		adc_temperature = self.convertion_read_adc(cmd_temp,_time_temp)
		adc_pressure = self.convertion_read_adc(cmd_pressure,_time_pressure)
		 # Difference between actual and reference temperature = D2 - Tref
		dT = (adc_temperature) - (self.eeprom_coeff[self._MS5637_REFERENCE_TEMPERATURE_INDEX] * 0x100)
		 # Actual temperature = 2000 + dT * TEMPSENS
		TEMP = 2000 + (dT * self.eeprom_coeff[self._MS5637_TEMP_COEFF_OF_TEMPERATURE_INDEX] >> 23);
		 # Second order temperature compensation
		if TEMP < 2000 : 
			T2 = ( 3 * ( dT  * dT  ) ) >> 33
			OFF2 = 61 * (TEMP - 2000) * (TEMP - 2000) / 16 
			SENS2 = 29 * (TEMP - 2000) * (TEMP - 2000) / 16 
			if TEMP < -1500 :
				OFF2 += 17 * (TEMP + 1500) * (TEMP + 1500) 
				SENS2 += 9 * ((TEMP + 1500) * (TEMP + 1500))
		else :
			T2 = ( 5 * ( dT  * dT  ) ) >> 38
			OFF2 = 0 
			SENS2 = 0
			
		#  OFF = OFF_T1 + TCO * dT
		OFF = ( (self.eeprom_coeff[self._MS5637_PRESSURE_OFFSET_INDEX]) << 17 ) + ( ( (self.eeprom_coeff[self._MS5637_TEMP_COEFF_OF_PRESSURE_OFFSET_INDEX]) * dT ) >> 6 ) 
		OFF -= OFF2 ;
		
		# Sensitivity at actual temperature = SENS_T1 + TCS * dT
		SENS = ( self.eeprom_coeff[self._MS5637_PRESSURE_SENSITIVITY_INDEX] * 0x10000 ) + ( (self.eeprom_coeff[self._MS5637_TEMP_COEFF_OF_PRESSURE_SENSITIVITY_INDEX] * dT) >> 7 ) 
		SENS -= SENS2 
		
		#  Temperature compensated pressure = D1 * SENS - OFF
		P = ( ( (adc_pressure * SENS) >> 21 ) - OFF ) >> 15 
		
		temperature = ( TEMP - T2 ) / 100.0
		pressure = P / 100.0
	
		return temperature, pressure

	# brief CRC check
	# \param[in] : EEPROM Coefficients
	# return :
	#		-> (bool) True if the CRC is OK, else False
	def crc_check (self,n_prom) : 
		cnt = 0
		n_bit = 8
		n_rem = 0
		n_prom[0]=((n_prom[0]) & 0x0FFF); # CRC byte is replaced by 0
		while (cnt < 16) :
			# operation is performed on bytes
			# choose LSB or MSB
			if (cnt%2==1) :
				n_rem ^= ((n_prom[cnt/2]) & 0x00FF) 
			else :
				n_rem ^= (n_prom[cnt/2]>>8)

			while n_bit > 0 :
				n_bit -= 1
				if (n_rem & 0x8000) :
					n_rem = (n_rem << 1) ^ 0x3000

				else :
					n_rem = (n_rem << 1)

			cnt += 1
			n_bit = 8
		cnt = 0
		n_rem = ((n_rem >> 12) & 0x000F) #final 4-bit reminder is CRC code
		n_rem ^= 0x00
		return (n_rem == n_prom[0])

			
	def close(self):
		self.i2c.close()

	def __enter__(self):
		return self        

	def __exit__(self, type, value, traceback):
		self.close()

if __name__ == "__main__":
	try:
		with MS5637(1) as ms5637:
			(temperature, pressure) = ms5637.read_temperature_and_pressure(ms5637._RESOLUTION_OSR_8192)
			print "Temperature: %.1f" % temperature
			print "Pressure: %.2f" % pressure
	except IOError, e:
		print e
		print "Error creating connection to i2c.  This must be run as root"
