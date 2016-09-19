#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(  name='pi-weather-shield',
    version='0.0.2',
    author='William Markezana',
    author_email='william.markezana@te.com',
    url='https://github.com/TEConnectivity/piweathershield-python',
    packages=find_packages(),
    license=open('LICENSE').read(),
    description="Python module to control the TE Connectivity Raspberry Pi Weather Shield",
    classifiers=[
      "Development Status :: 5 - Production/Stable",
      "Programming Language :: Python :: 2",
      "Programming Language :: Python :: 3",
      "Topic :: Education",
      "Topic :: Scientific/Engineering",
      "Topic :: Software Development",
      "Intended Audience :: Developers",
      "Intended Audience :: Education",
      "Intended Audience :: Science/Research",
      "License :: OSI Approved :: MIT License",
    ],
  )
