#!/usr/bin/env python3
# encoding: utf-8
"""
@version: 0.1
@author: lyrichu
@license: Apache Licence 
@contact: 919987476@qq.com
@site: http://www.github.com/Lyrichu
@file: NetCloudLoginTest.py
@time: 2019/01/06 21:11
@description:
test for NetCloudLogin
"""
from netcloud.login.Login import NetCloudLogin
from netcloud.login.Printer import NetCloudPrinter
from netcloud.util import Helper


class NetCloudLoginTest(object):
    def __init__(self):
        self.logger = Helper.get_logger()
        # 无参数登录
        self.login_printer = NetCloudPrinter()
        self.netcloud_login = NetCloudLogin()

    def test_login(self):
        response = self.netcloud_login.login()
        self.logger.info(response.json())

    def test_get_user_play_list(self):
        uid = 103413749
        response = self.netcloud_login.get_user_play_list(uid)
        self.logger.info(response.json())

    def test_get_self_play_list(self):
        response = self.netcloud_login.get_self_play_list()
        self.logger.info(response.json())

    def test_get_user_dj(self):
        uid = 1186346
        response = self.netcloud_login.get_user_dj(uid)
        self.logger.info(response.json())

    def test_get_self_dj(self):
        response = self.netcloud_login.get_self_dj()
        self.logger.info(response.json())

    def test_search(self):
        keyword = "周杰伦"
        type_ = 100 # 歌手
        offset = 0
        limit = 30
        response = self.netcloud_login.search(keyword=keyword, type_=type_, offset=offset, limit=limit)
        self.logger.info(response.json())

    def test_get_user_follows(self):
        uid = 103413749
        offset = 0
        limit = 50
        response = self.netcloud_login.get_user_follows(uid=uid, offset=offset, limit=limit)
        self.logger.info(response.json())

    def test_get_self_follows(self):
        response = self.netcloud_login.get_self_follows()
        self.logger.info(response.json())

    def test_get_user_fans(self):
        uid = 103413749
        response = self.netcloud_login.get_user_fans(uid=uid)
        self.logger.info(response.json())

    def test_get_self_fans(self):
        response = self.netcloud_login.get_self_fans()
        self.logger.info(response.json())

    def test_get_user_event(self):
        uid = 82133317
        response = self.netcloud_login.get_user_event(uid=uid)
        self.logger.info(response.json())

    def test_get_self_event(self):
        response = self.netcloud_login.get_self_event()
        self.logger.info(response.json())

    def test_get_user_record(self):
        uid = 82133317
        type_ = 0  # all datas
        response = self.netcloud_login.get_user_record(uid=uid, type_=type_)
        self.logger.info(response.json())

    def test_get_self_record(self):
        response = self.netcloud_login.get_self_record()
        self.logger.info(response.json())

    def test_get_friends_event(self):
        response = self.netcloud_login.get_friends_event()
        self.logger.info(response.json())

    def test_get_top_playlist_highquality(self):
        response = self.netcloud_login.get_top_playlist_highquality()
        self.logger.info(response.json())

    def test_get_play_list_detail(self):
        play_list_id = 92259156
        limit = 100
        response = self.netcloud_login.get_play_list_detail(id=play_list_id, limit=limit)
        self.logger.info(response.json())

    def test_get_music_download_url(self):
        ids = [526464293]
        response = self.netcloud_login.get_music_download_url(ids=ids)
        self.logger.info(response.json())

    def test_get_lyric(self):
        music_id = 526464293
        response = self.netcloud_login.get_lyric(id=music_id)
        self.logger.info(response.json())

    def test_get_music_comments(self):
        music_id = 526464293
        offset = 0
        limit = 100
        response = self.netcloud_login.get_music_comments(id=music_id, offset=offset, limit=limit)
        self.logger.info(response.json())

    def test_get_album_comments(self):
        album_id = 74992263
        offset = 0
        limit = 20
        response = self.netcloud_login.get_album_comments(id=album_id, offset=offset, limit=limit)
        self.logger.info(response.json())

    def test_get_songs_detail(self):
        ids = ['208902', '27747330', '529747142']
        response = self.netcloud_login.get_songs_detail(ids=ids)
        self.logger.info(response.json())

    def test_get_self_fm(self):
        response = self.netcloud_login.get_self_fm()
        self.logger.info(response.json())

    def test_pretty_print_self_info(self):
        self.login_printer.pretty_print_self_info()

    def test_pretty_print_user_play_list(self):
        uid = 103413749
        self.login_printer.pretty_print_user_play_list(uid=uid)

    def test_pretty_print_self_play_list(self):
        self.login_printer.pretty_print_self_play_list()

    def test_pretty_print_search_song(self):
        keyword = "周杰伦"
        self.login_printer.pretty_print_search_song(search_song_name=keyword, offset=0, limit=30)

    def test_pretty_print_search_singer(self):
        keyword = "陈奕迅"
        self.login_printer.pretty_print_search_singer(search_singer_name=keyword)

    def test_pretty_print_search_play_list(self):
        keyword = "周杰伦"
        self.login_printer.pretty_print_search_play_list(keyword)

    def test_pretty_print_search_user(self):
        keyword = "周杰伦"
        self.login_printer.pretty_print_search_user(keyword)

    def test_pretty_print_user_follows(self):
        uid = 48548007
        self.login_printer.pretty_print_user_follows(uid)

    def test_pretty_print_user_fans(self):
        uid = 44818930
        self.login_printer.pretty_print_user_fans(uid)

    def test_pretty_print_self_fans(self):
        self.login_printer.pretty_print_self_fans()

    def test_download_play_list_songs(self):
        play_list_id = 2353471182
        self.netcloud_login.download_play_list_songs(play_list_id)

    def test_download_play_list_songs_by_multi_threading(self):
        play_list_id = 2353471182
        self.netcloud_login.download_play_list_songs_by_multi_threading(play_list_id,threads=50)

    def test_get_download_urls_by_ids(self):
        singer_url = "http://music.163.com/artist?id=9621"
        ids_list = Helper.get_singer_hot_songs_ids(singer_url)
        self.logger.info(self.netcloud_login.get_download_urls_by_ids(ids_list))

    def test_get_songs_name_list_by_ids_list(self):
        singer_url = "http://music.163.com/artist?id=7214"
        ids_list = Helper.get_singer_hot_songs_ids(singer_url)
        self.logger.info(self.netcloud_login.get_songs_name_list_by_ids_list(ids_list))

    def test_get_singer_id_by_name(self):
        singer_name = "金海心"
        self.logger.info(self.netcloud_login.get_singer_id_by_name(singer_name))

    def test_download_singer_hot_songs_by_name(self):
        singer_name = "王力宏"
        self.netcloud_login.download_singer_hot_songs_by_name(singer_name)

    def test_download_singer_hot_songs_by_name_with_multi_threading(self):
        singer_name = "吴青峰"
        self.netcloud_login.download_singer_hot_songs_by_name_with_multi_threading(singer_name,20)

    def test_get_song_id_by_name(self):
        song_name = "吻别"
        singer_name = "张玮伽"
        self.logger.info(self.netcloud_login.get_song_id_by_name(song_name,singer_name))

    def test_get_lyrics_list_by_id(self):
        song_id = 247835
        self.logger.info(self.netcloud_login.get_lyrics_list_by_id(song_id))

    def test_get_lyrics_list_by_name(self):
        song_name = "悲伤的秋千"
        self.logger.info(self.netcloud_login.get_lyrics_list_by_name(song_name))

    def test_all(self):
        self.test_login()
        self.test_get_user_play_list()
        self.test_get_self_play_list()
        self.test_get_user_dj()
        self.test_get_self_dj()
        self.test_search()
        self.test_get_user_follows()
        self.test_get_self_follows()
        self.test_get_user_fans()
        self.test_get_self_fans()
        self.test_get_user_event()
        self.test_get_self_event()
        self.test_get_user_record()
        self.test_get_self_record()
        self.test_get_friends_event()
        self.test_get_top_playlist_highquality()
        self.test_get_play_list_detail()
        self.test_get_music_download_url()
        self.test_get_lyric()
        self.test_get_music_comments()
        self.test_get_album_comments()
        self.test_get_songs_detail()
        self.test_get_self_fm()
        self.test_pretty_print_self_info()
        self.test_pretty_print_user_play_list()
        self.test_pretty_print_self_play_list()
        self.test_pretty_print_search_song()
        self.test_pretty_print_search_singer()
        self.test_pretty_print_search_play_list()
        self.test_pretty_print_search_user()
        self.test_pretty_print_user_follows()
        self.test_pretty_print_user_fans()
        self.test_pretty_print_self_fans()
        self.test_download_play_list_songs()
        self.test_get_download_urls_by_ids()
        self.test_get_songs_name_list_by_ids_list()
        self.test_get_singer_id_by_name()
        self.test_download_singer_hot_songs_by_name()
        self.test_get_song_id_by_name()
        self.test_get_lyrics_list_by_id()
        self.test_get_lyrics_list_by_name()

if __name__ == '__main__':
    test = NetCloudLoginTest()
    test.test_all()
