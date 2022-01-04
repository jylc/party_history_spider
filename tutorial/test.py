# -*-coding:utf8-*-
import pymysql.cursors
from settings import MYSQL_URL, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


def main():
    num = '高校所在地：'.split('：')[1]
    print(num)
    pass


if __name__ == "__main__":
    main()
