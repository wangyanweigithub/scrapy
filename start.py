#!/usr/bin/env python
# -*- coding:utf-8 -*-

from scrapy import cmdline
# import sys
# output = sys.stdout
# output_file = open("3_27.log", "w")
# sys.stdout = output_file
cmdline.execute("scrapy crawl dbhouse".split())
# sys.stdout = output
