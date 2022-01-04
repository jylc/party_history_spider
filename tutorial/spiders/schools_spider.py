# -*-coding:utf8-*-
import os.path
import sys

from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
import re
from tutorial.items import SchoolsItem
from loguru import logger
from tutorial.items import NameAndCode


class SchoolsSpider(CrawlSpider):
    """
    从网站中寻找高校
    """
    name = "tutorial"
    allow_domains = ['www.gaokao.com']
    start_urls = ['http://college.gaokao.com/schlist']

    # 基础url
    base_url = 'http://college.gaokao.com/schlist'

    def __init__(self, *args, **kwargs):
        super(SchoolsSpider, self).__init__(*args, **kwargs)
        self.xsrf = ''

    def start_requests(self):
        return [Request(self.base_url, callback=self.prepare_school_url, errback=self.parse_error)]

    def prepare_school_url(self, response):
        """
        解析高校所在区域
        :param response:
        :return:
        """
        selector = Selector(response)
        # 第一个p包含地区信息，提取
        test1 = selector.xpath('//div[@class="menufix"]/p[contains(.,"高校所在地：")]').extract_first()
        logger.info('test1')
        regions_info_urls = selector.xpath('//div[@class="menufix"]/p[contains(.,"高校所在地：")]//a/@href').extract()
        logger.info('regions_info_urls')
        regions_info_names = selector.xpath('//div[@class="menufix"]/p[contains(.,"高校所在地：")]//a/text()').extract()
        logger.info('regions_info_names')
        school_type_urls = selector.xpath('//div[@class="menufix"]/p[contains(.,"高校类型：")]//a/@href').extract()
        logger.info('school_type_urls')
        school_type_names = selector.xpath('//div[@class="menufix"]/p[contains(.,"高校类型：")]//a/text()').extract()
        logger.info('school_type_names')
        school_level_urls = selector.xpath('//div[@class="menufix"]/p[contains(.,"高校特色：")]//a/@href').extract()
        logger.info('school_level_urls')
        school_level_names = selector.xpath('//div[@class="menufix"]/p[contains(.,"高校特色：")]//a/text()').extract()
        logger.info('school_level_names')
        education_level_urls = selector.xpath('//div[@class="menufix"]/p[contains(.,"学历层次：")]//a/@href').extract()
        logger.info('education_level_urls')
        education_level_names = selector.xpath(
            '//div[@class="menufix"]/p[contains(.,"学历层次：")]//a/text()').extract()
        logger.info('education_level_names')

        regionNameAndCodeArr = []
        if len(regions_info_names) == len(regions_info_urls):
            for i in range(1, len(regions_info_urls)):
                url = regions_info_urls[i]
                name = regions_info_names[i]
                # <a class="on" href="http://college.gaokao.com/schlist/">全部</a>
                # <a href="http://college.gaokao.com/schlist/a1/">北京</a>
                if 'class' in str(url):
                    continue
                code = str(url).rsplit('schlist/')[1].split('/')[0]
                regionNameAndCodeArr.append(NameAndCode(name=name, code=code))

        typeNameAndCodeArr = []
        if len(school_type_urls) == len(school_type_names):
            for i in range(1, len(school_type_urls)):
                url = school_type_urls[i]
                name = school_type_names[i]
                if 'class' in str(url):
                    continue
                # <a href="http://college.gaokao.com/schlist/c1/">综合</a>
                code = str(url).rsplit('schlist/')[1].split('/')[0]
                typeNameAndCodeArr.append(NameAndCode(name=name, code=code))

        levelNameAndCodeArr = []
        if len(school_level_urls) == len(school_level_names):
            for i in range(1, len(school_level_urls)):
                url = school_level_urls[i]
                name = school_level_names[i]
                if 'class' in str(url):
                    continue
                code = str(url).rsplit('schlist/')[1].split('/')[0]
                levelNameAndCodeArr.append(NameAndCode(name=name, code=code))

        educationNameAndCodeArr = []
        if len(education_level_urls) == len(education_level_names):
            for i in range(1, len(education_level_urls)):
                url = education_level_urls[i]
                name = education_level_names[i]
                if 'class' in str(url):
                    continue
                # <a href="http://college.gaokao.com/schlist/c1/">综合</a>
                code = str(url).rsplit('schlist/')[1].split('/')[0]
                educationNameAndCodeArr.append(NameAndCode(name=name, code=code))

        # 暂时只查北京的学校
        regionCodes = []
        for regionObj in regionNameAndCodeArr:
            if regionObj.name == '北京':
                regionCodes.append(regionObj.code)

        for regionCode in regionCodes:
            request_url = '{}/{}/{}'.format(self.base_url, regionCode, 's1')
            yield Request(request_url, self.parse_school_info, errback=self.parse_error)

    def parse_school_info(self, response):
        selector = Selector(response)
        # 分析页码数
        total_pages_xpath = selector.xpath('//ul[@class="fany"]/li[@id="qx"]').extract_first()
        total_pages = re.findall(r'\d+', str(total_pages_xpath))[1]  # '1/3页 第'
        logger.info(total_pages)
        current_base_url = str(response.url).rsplit('/', 1)[0]
        logger.info(current_base_url)
        for page in range(1, int(total_pages) + 1):
            yield Request('{}/{}'.format(current_base_url, 'p' + str(page)), self.get_school_info,
                          errback=self.parse_error)

    def get_school_info(self, response):
        selector = Selector(response)
        schools_url_dls = selector.xpath('//div[@class="scores_List"]//dl')
        for schools_url_dl in schools_url_dls:
            try:
                logger.info(schools_url_dl)
                school_name = schools_url_dl.xpath('./dt/strong/@title').extract_first()
                logger.info(school_name)
                li_texts = schools_url_dl.xpath('./dd/ul//li/text()').extract()
                logger.info(li_texts)

                school_region = str(li_texts[0]).split('：')[1]
                school_character = str(li_texts[1]).split('：')[1]
                school_type = str(li_texts[2]).split('：')[1]
                school_subjection = str(li_texts[3]).split('：')[1]
                school_education_level = str(li_texts[4]).split('：')[1]
                school_url = str(li_texts[5]).split('：')[1]
                yield SchoolsItem(
                    name=school_name,
                    url=school_url,
                    education_level=school_education_level,
                    region=school_region,
                    school_character=school_character,
                    school_type=school_type,
                    subjection=school_subjection,
                )
            except Exception:
                logger.error("error")
                exit(-1)

    def parse_error(self, response):
        logger.error('craw {} failed', response.url)
        pass
