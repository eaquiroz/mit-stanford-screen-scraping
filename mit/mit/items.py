# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MitItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    company = scrapy.Field()
    home_address = scrapy.Field()
    work_address = scrapy.Field()
    job_title = scrapy.Field()
    email = scrapy.Field()
