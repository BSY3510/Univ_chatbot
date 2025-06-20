# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class NoticeItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    content = Field()
    date = Field()
    department = Field()
    url = Field()
    files = Field()
