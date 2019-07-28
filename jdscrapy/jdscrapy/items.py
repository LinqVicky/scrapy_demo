# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection = 'tryskus'
    sku_id = scrapy.Field()
    activity_id = scrapy.Field()
    img = scrapy.Field()
    name = scrapy.Field()
    supply = scrapy.Field()
    apply_count = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
