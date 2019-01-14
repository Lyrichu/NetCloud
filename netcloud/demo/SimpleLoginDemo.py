#!/usr/bin/env python3
# encoding: utf-8
"""
@version: 0.1
@author: lyrichu
@license: Apache Licence 
@contact: 919987476@qq.com
@site: http://www.github.com/Lyrichu
@file: SimpleLoginDemo.py
@time: 2019/01/09 03:11
@description:
demo for NetCloudLogin
"""
from netcloud.test import NetCloudLoginTest


def run():
    login_test = NetCloudLoginTest.NetCloudLoginTest()
    login_test.test_all()

if __name__ == '__main__':
    run()