#! /usr/bin/python
# coding: utf-8

import sys
import os
import shutil

import caengineconf

f = open('/opt/JionLab/caengine/etc/svr~import.m', 'w')
f.write('import')
f.close

cfg = caengineconf.config('', __name__ == "__main__")

if cfg.APTFlag: # use APT
	shutil.move('/opt/JionLab/caengine/etc/svr~import.m','/home/DATA/PUT/PUB0/svr~import.m')
else:
	shutil.move('/opt/JionLab/caengine/etc/svr~import.m','/home/DATA/PUT/PUB/svr~import.m')
