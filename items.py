# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MonsterItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    companyname = scrapy.Field()
    companyurl = scrapy.Field()
    jobLocationRegion = scrapy.Field()
    jobLocationCity = scrapy.Field()
    jobdescription = scrapy.Field()
    #salary = scrapy.Field()


    # description_raw = scrapy.Field()
    # job_id = scrapy.Field()

