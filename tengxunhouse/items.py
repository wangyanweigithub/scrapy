# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DetailItem(scrapy.Item):
    # define the fields for your item here like:
    city = scrapy.Field()
    area = scrapy.Field()
    building = scrapy.Field()
    link = scrapy.Field()
    basicinfo = scrapy.Field()


class PhotoItem(scrapy.Item):
    # define the fields for your item here like:
    city = scrapy.Field()
    area = scrapy.Field()
    building = scrapy.Field()
    Aimgurl = scrapy.Field()
    Aimgname = scrapy.Field()
    Dimgurl = scrapy.Field()
    Dimgname = scrapy.Field()
