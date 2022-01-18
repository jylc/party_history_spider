# -*-coding:utf8-*-
import os.path
import sys

from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
import requests
import re

from scrapy_splash import SplashRequest

from tutorial.items import SchoolsItem, PartyInfoItem
from loguru import logger
from tutorial.items import NameAndCode
from settings import PROXIES


def parse_error(response):
    logger.error('craw {} failed'.format(response))
    pass


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
        # return [Request(self.base_url, callback=self.prepare_school_url, errback=parse_error)]
        return [Request(self.base_url, callback=self.prepare_school_url, errback=parse_error)]

    def prepare_school_url(self, response):
        """
        解析高校所在区域
        :param response:
        :return:
        """
        selector = Selector(response)
        # 第一个p包含地区信息，提取
        test1 = selector.xpath('//div[@class="menufix"]/p[contains(.,"高校所在地：")]').extract_first()
        logger.info('test1={}'.format(test1))
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
                code = str(url).rsplit('schlist/')[1].split('/')[0]
                educationNameAndCodeArr.append(NameAndCode(name=name, code=code))

        # 暂时只查北京的学校
        regionCodes = []
        for regionObj in regionNameAndCodeArr:
            if regionObj.name == '北京':
                regionCodes.append(regionObj.code)

        for regionCode in regionCodes:
            request_url = '{}/{}/{}'.format(self.base_url, regionCode, 's1')
            yield Request(request_url, self.parse_school_info_page_nums, errback=parse_error)

    def parse_school_info_page_nums(self, response):
        selector = Selector(response)
        # 分析页码数
        total_pages_xpath = selector.xpath('//ul[@class="fany"]/li[@id="qx"]').extract_first()
        total_pages = re.findall(r'\d+', str(total_pages_xpath))[1]  # '1/3页 第'
        logger.info(total_pages)
        current_base_url = str(response.url).rsplit('/', 1)[0]
        logger.info(current_base_url)
        # for page in range(1, int(total_pages) + 1):
        #     yield Request('{}/{}'.format(current_base_url, 'p' + str(page)), self.get_school_info,
        #                   errback=parse_error)
        # FIXME 只分析一个
        for page in range(1, 2):
            yield Request('{}/{}'.format(current_base_url, 'p' + str(page)), self.get_school_info,
                          errback=parse_error)

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

                if 'http://' in str(school_url):
                    school_url = str(school_url).split('http://')[1]
                if 'www.' in str(school_url):
                    school_url = str(school_url).split('www.')[1]

                school_item = SchoolsItem(
                    name=school_name,
                    url=school_url,
                    education_level=school_education_level,
                    region=school_region,
                    school_character=school_character,
                    school_type=school_type,
                    subjection=school_subjection,
                )
                yield school_item

                # 根据高校网址，通过谷歌去搜寻包含关键字的网页
                if school_url != '——':
                    logger.info('school url:{}'.format(school_url))
                    try:
                        status = requests.get(url='http://www.{}/'.format(school_url), timeout=5).status_code
                        if status != 200:
                            school_url = '——'
                    except Exception as err:
                        logger.error('school url has error:{}!'.format(err))
                        school_url = '——'

                    if school_url != '——':
                        google_url = 'https://google.com/search?q=site:{} {}'.format(school_url, '党史')
                        logger.info(google_url)
                        splash_args = {'wait': '0.5', 'proxy': 'http://192.168.219.1:8181', 'school_url': school_url, }
                        yield SplashRequest(google_url, self.parse_google_page_nums, endpoint='render.html',
                                            args=splash_args)
            except Exception:
                logger.error('error')
                exit(-1)
            break

    # 从谷歌中查询并分析
    def parse_google_page_nums(self, response):
        logger.info('start parse goolge page nums')
        logger.info('google page num url={}'.format(response.url))
        selector = Selector(response)
        next_page_url = selector.xpath('//a[@id="pnnext"]/@href').extract_first()

        query_results_entities = selector.xpath('//div[@class="g tF2Cxc"]')
        if len(query_results_entities) == 0:
            query_results_entities = selector.xpath('//div[@class="tF2Cxc"]')
        logger.info('query_results_entities size:{}', len(query_results_entities))
        school_url = response.meta['splash']['args']['school_url']

        # 解析当前页上的条目
        for entity in query_results_entities:
            related_url = entity.xpath('.//div[@class="yuRUbf"]/a/@href').extract_first()
            related_title = entity.xpath('.//div[@class="yuRUbf"]/a/h3/text()').extract_first()
            content = entity.xpath(
                './/div[@class="VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf"]')
            # TODO 发布时间(release time)提取
            brief_introduction = None
            release_time = 'None'
            if len(content) == 1:
                if not content.xpath('.//span//text()').extract():
                    brief_introduction = content.xpath('.//text()').extract_first()
                else:
                    brief_introduction = ''.join(content.xpath('.//span//text()').extract())
            elif len(content) == 2:
                brief_introduction = ''.join(content[0].xpath('.//span//text()').extract())
                release_time = content.xpath('.//span[@class="MUxGbd wuQ4Ob WZ8Tjf"]').extract_first()

            # party的相关信息
            party_info_entity = PartyInfoItem(
                school_url=school_url,
                related_url=related_url,
                related_title=related_title,
                brief_introduction=brief_introduction,
                release_time=release_time,
            )
            logger.info(party_info_entity)
            yield party_info_entity

        # 迭代翻页
        if next_page_url is not None:
            # 迭代页面
            google_url = 'https://google.com{}'.format(next_page_url)
            splash_args = {'wait': '0.5', 'proxy': 'http://192.168.219.1:8181',
                           'school_url': response.meta['splash']['args']['school_url'], }
            yield SplashRequest(google_url, self.parse_google_page_nums, endpoint='render.html',
                                args=splash_args)
