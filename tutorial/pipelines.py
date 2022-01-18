# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
import pymysql.cursors
import tutorial
from loguru import logger


def query_item(school_name, cursor):
    sql = "SELECT FROM `school_entities` where `school_name=%s`"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results) != 0:
            return True
        else:
            return False
    except:
        logger.error('cannot select {}', school_name)
        return False


class SchoolsPipeline:
    """
    存储数据
    """

    def __init__(self, host, user, password, database):
        logger.info("pipeline start")
        self.connection = None

        self.host = host
        self.user = user
        self.password = password
        self.database = database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )

    def _to_connect(self):
        return pymysql.connect(host=self.host,
                               user=self.user,
                               password=self.password,
                               database=self.database)

    def _is_connected(self):
        try:
            self.connection.ping(reconnect=True)
            logger.info("database is connecting")
        except:
            self.connection = self._to_connect()
            logger.info("database is reconnecting")

    def _process_schools(self, item):
        """
        处理学校，保存信息
        :param item:
        :return:
        """
        logger.info("process schools")
        self._is_connected()
        with self.connection:
            with self.connection.cursor() as cursor:
                if query_item(item['name'], cursor):
                    return
                sql = "INSERT INTO `school_entities`(`school_name`," \
                      "`school_url`," \
                      "`school_education_level`," \
                      "`school_region`," \
                      "`school_character`," \
                      "`school_type`," \
                      "`school_subjection`) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (
                    item['name'],
                    item['url'],
                    item['education_level'],
                    item['region'],
                    item['school_character'],
                    item['school_type'],
                    item['subjection']))
            self.connection.commit()

    def _process_party_infos(self, item):
        logger.info("process party information")
        self._is_connected()
        with self.connection:
            with self.connection.cursor() as cursor:
                # if query_item(item['school_url'], cursor):
                #     return
                sql = "INSERT INTO `party_info_entities`(" \
                      "`school_url`," \
                      "`related_url`," \
                      "`related_title`," \
                      "`brief_introduction`," \
                      "`release_time`) VALUES (%s,%s,%s,%s,%s)"
                cursor.execute(sql, (
                    item['school_url'],
                    item['related_url'],
                    item['related_title'],
                    item['brief_introduction'],
                    item['release_time'],
                ))
            self.connection.commit()

    def open_spider(self, spider):
        logger.info("open spider")
        self.connection = pymysql.connect(host=self.host,
                                          user=self.user,
                                          password=self.password,
                                          database=self.database)

    def close_spider(self, spider):
        logger.info("close spider")
        self._is_connected()
        self.connection.close()

    def process_item(self, item, spider):
        logger.info("process item")
        if type(item) == tutorial.items.SchoolsItem:
            self._process_schools(item)
        if type(item) == tutorial.items.PartyInfoItem:
            self._process_party_infos(item)

        return item
