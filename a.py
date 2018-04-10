import sys
import time
from scrapy.cmdline import execute

def main():
    #args：市、区
    args = sys.argv[1:]
    args_str = "scrapy crawl tencent" if not args else "scrapy crawl tencent -a"
    level = ["city", "area"]
    for i in range(len(args)):
        args_str = args_str + " " + level[i] + "=" + args[i]

    #execute(args_str.split())
    print(args_str)
    time.sleep(10)
    print ("child process successful")


if __name__ == "__main__":
    main()