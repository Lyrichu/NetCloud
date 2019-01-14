#!/usr/bin/env python3
# encoding: utf-8
"""
@version: 0.1
@author: lyrichu
@license: Apache Licence 
@contact: 919987476@qq.com
@site: http://www.github.com/Lyrichu
@file: SimpleCrawlerDemo.py
@time: 2019/01/05 19:31
@description:
simple crawler demo of NetCloud
"""
from netcloud.test.NetCloudCrawlerTest import NetCloudCrawlerTest


def run():
    crawler_test = NetCloudCrawlerTest()
    crawler_test.test_all()


if __name__ == '__main__':
    run()


