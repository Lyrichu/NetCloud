#!/usr/bin/env python3
# encoding: utf-8
"""
@version: 0.1
@author: lyrichu
@license: Apache Licence 
@contact: 919987476@qq.com
@site: http://www.github.com/Lyrichu
@file: NetCloudAnalyseTest.py
@time: 2019/01/06 19:38
@description:
test for NetCloudAnalyse
"""
from netcloud.analyse.Analyse import NetCloudAnalyse
from netcloud.util import Helper


class NetCloudAnalyseTest:
    def __init__(self):
        self.logger = Helper.get_logger()
        song_name = "梦醒时分"
        singer_name = "李翊君"
        self.netcloud_analyse = NetCloudAnalyse(song_name = song_name,singer_name = singer_name)


    def test_load_users_url(self):
        users_url = self.netcloud_analyse.load_all_users_url()
        self.logger.debug("There are %d users ulr." % len(users_url))
        num = 10
        self.logger.debug("Top %d users ulr are:" % num)
        for i in range(num):
            self.logger.debug("{index}:{url}".format(index=i + 1, url=users_url[i]))

    def test_save_users_info_to_file(self):
        self.netcloud_analyse.save_all_users_info_to_file()


    def test_core_visual_analyse(self):
        self.netcloud_analyse.core_visual_analyse()

    def test_save_all_users_info_to_file_by_multi_threading(self, threads=10):
        self.netcloud_analyse.save_all_users_info_to_file_by_multi_threading(threads)

    def test_generate_all_analyse_files(self):
        self.netcloud_analyse.generate_all_analyse_files()

    def test_all(self):
        # self.test_load_users_url()
        # self.test_save_users_info_to_file()
        # self.test_core_visual_analyse()
        # self.test_save_all_users_info_to_file_by_multi_threading()
        self.test_generate_all_analyse_files()


if __name__ == '__main__':
    test = NetCloudAnalyseTest()
    test.test_all()




