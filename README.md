# Raspberry Pi Weather Shield Python

Python library for the TE Connectivity Raspberry Pi Weather Shield 
![piweathershield](https://cloud.githubusercontent.com/assets/20226823/18578539/e20da908-7bf0-11e6-86df-abaaf46f6a36.jpg)

This library provides easy access to all the sensors featured by the TE Connectivity Weather Shield :
* [HTU21D](http://www.te.com/usa-en/product-CAT-HSC0004.html) (Temperature and Humidity)
* [MS5637](http://www.te.com/usa-en/product-CAT-BLPS0037.html) (Temperature and Pressure)
* [TSYS01](http://www.te.com/usa-en/product-G-NICO-018.html) (Temperature)
* [TSD305](http://www.te.com/usa-en/product-G-TPMO-101.html) (Temperature and Contactless Temperature)


Installation
============

To install the Weather Shield library software, you can use [pip](https://pypi.python.org/pypi/pip):

    pip install pi-weather-shield
    
or checkout this repository and run:

    python setup.py install
    
Usage
=====

Import the piweathershield module and instantiate a PiWeatherShield object:

    from piweathershield import PiWeatherShield

    weatherShield = PiWeatherShield()
