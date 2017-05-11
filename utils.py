#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

def random_color():
	r = lambda: random.randint(0,255)
	color = '#%02X%02X%02X' % (r(),r(),r()) 
	return color