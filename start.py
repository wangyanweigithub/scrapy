#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from scrapy.cmdline import execute

def main():
    #args：市、区
    args = sys.argv[1:]
    args_str = "scrapy crawl dbhouse"
    level = ["city", "area"]
    for i in range(len(args)):
        args_str = args_str + " -a " + level[i] + "=" + args[i]

    print(args_str)
    execute(args_str.split())


if __name__ == "__main__":
    main()
