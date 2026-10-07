# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class FightmatrixItem(scrapy.Item):
    # Campos de FightMatrix
    fighter = scrapy.Field()
    birthd = scrapy.Field()
    prorecord = scrapy.Field()
    ufcdebut = scrapy.Field()
    ufcrecord = scrapy.Field()
    oct_time = scrapy.Field()
    longest_ws = scrapy.Field()
    last_ufc_fight = scrapy.Field()
    last_5 = scrapy.Field()
    association = scrapy.Field()
    pro_d_date = scrapy.Field()
    
    # Campos de Sherdog
    sherdog_age = scrapy.Field()
    sherdog_birthdate = scrapy.Field()
    sherdog_division = scrapy.Field()
    sherdog_height_cm = scrapy.Field()
    sherdog_recent_fights = scrapy.Field()