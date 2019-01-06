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
from test.NetCloudLoginTest import NetCloudLoginTest
from test.NetCloudCrawlerTest import NetCloudCrawlerTest
from test.NetCloudAnalyseTest import NetCloudAnalyseTest


def run():
    crawler_test = NetCloudCrawlerTest()
    # analyse_test = NetCloudAnalyseTest()
    # crawler_test.test_all()
    # analyse_test.test_all()
    crawler_test.crawler.save_lyrics_to_file()
    # login_test = NetCloudLoginTest()
    # login_test.test_all()



if __name__ == '__main__':
    run()


