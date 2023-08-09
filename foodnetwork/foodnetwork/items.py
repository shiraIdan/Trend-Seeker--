import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


class FoodnetworkItem(scrapy.Item):
    link = scrapy.Field()
    author = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    title = scrapy.Field()
    description = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    ingredients = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    special_equipment = scrapy.Field()
    directions = scrapy.Field(input_processor=MapCompose(
        str.strip), output_processor=TakeFirst())
    rating = scrapy.Field()
    reviews = scrapy.Field()
    pass
