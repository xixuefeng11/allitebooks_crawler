# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AllitebooksItem(scrapy.Item):
    # define the fields for your item here like:
    title           = scrapy.Field()
    author          = scrapy.Field()
    isbn10          = scrapy.Field()
    year            = scrapy.Field()
    pages           = scrapy.Field()
    language        = scrapy.Field()
    filesize        = scrapy.Field()
    fileformat      = scrapy.Field()
    category        = scrapy.Field()
    description     = scrapy.Field()
    image_url       = scrapy.Field()
    download_links  = scrapy.Field()
    url             = scrapy.Field()
