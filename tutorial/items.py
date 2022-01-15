# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class SchoolsItem(scrapy.Item):
    """学校属性

    Attributes:
        name 学校名
        url 学校网址
        school_character 学校特色['985','211','普通']
        education_level 高校性质['本科'，'专科']
        school_type 学校类别['工科',...]
        region 学校所在地区
        subjection 学校隶属
    """

    name = Field()
    url = Field()
    education_level = Field()
    region = Field()
    school_character = Field()
    school_type = Field()
    subjection = Field()


class PartyInfoItem(scrapy.Item):
    """
    相关的信息
    """
    school_url = Field()
    related_url = Field()
    related_title = Field()
    brief_introduction = Field()
    release_time = Field()


class NameAndCode:
    def __init__(self, name, code):
        self.name = name
        self.code = code
