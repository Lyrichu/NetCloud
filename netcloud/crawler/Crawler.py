#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# @Time   : 2018/1/26
# @Author : Lyrichu
# @Email  : 919987476@qq.com
# @File   : NetCloudCrawler
'''
@Description:
网易云音乐评论抓取
reference:@平胸小仙女's article(address:https://www.zhihu.com/question/36081767)
post encryption part can be found in the following articles:
author：平胸小仙女
link：https://www.zhihu.com/question/36081767/answer/140287795
source：知乎
'''

import requests
import json
import time
import os
import re
from threading import Thread,Lock

from netcloud.login.Login import NetCloudLogin
from netcloud.util import Constants, Helper


class NetCloudCrawler(object):
    '''
    the main crawler class
    '''
    def __init__(self,song_name,singer_name,song_id = None,singer_id = None):
        self.logger = Helper.get_logger()
        # 如果id缺失,则尝试登录以从name获取id
        if song_id is None or singer_id is None:
            # 从用户机器配置文件加载登录信息
            config_dict = Helper._parse_config_xml()
            phone = config_dict['phone']
            password = config_dict['password']
            email = config_dict['email']
            rememberLogin = config_dict['rememberLogin']
            try:
                netcloud_login = NetCloudLogin(phone,password,email,rememberLogin)
                if song_id is None:
                    song_id = netcloud_login.get_song_id_by_name(song_name)
                    self.logger.info("Login to get %s's song_id(=%s) succeed!"
                                     %(song_name,song_id))
                if singer_id is None:
                    singer_id = netcloud_login.get_singer_id_by_name(singer_name)
                    self.logger.info("Login to get %s's singer_id(=%s) succeed!"
                                     %(singer_name,singer_id))
            except Exception as e:
                self.logger.error("NetCloud login failed:%s" % e)
                self.logger.error("Please fullfill singer_id and song_id parameter"
                                 " or check your login info in %s!" % Constants.USER_CONFIG_FILE_PATH)
                return
        self.song_name = song_name
        self.song_id = song_id
        self.singer_name = singer_name
        self.singer_id = singer_id
        self.comments_url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_{song_id}/?csrf_token=".format(song_id = song_id)
        self.singer_url = 'http://music.163.com/artist?id={singer_id}'.format(singer_id = singer_id)
        # 保存下载文件(歌曲,评论等)的地址
        self.singer_root_dir = Constants.SINGER_SAVE_DIR
        Helper.mkdir(self.singer_root_dir)
        # 同一个歌手的相关文件保存在同一文件夹下
        self.singer_path = os.path.join(self.singer_root_dir,self.singer_name)
        Helper.mkdir(self.singer_path)
        # 同一首歌的相关文件保存在同一文件夹下
        self.song_path = os.path.join(self.singer_path,self.song_name)
        Helper.mkdir(self.song_path)
        # 评论文件保存地址
        self.comments_file_path = os.path.join(self.song_path,self.song_name+"_all_comments.json")
        # 用户信息保存地址
        self.users_info_file_path = os.path.join(self.song_path,Constants.USER_INFO_FILENAME)
        # 歌手全部热门歌曲文件保存地址
        self.singer_all_hot_comments_file_path = os.path.join(self.singer_path,Constants.SINGER_ALL_HOT_COMMENTS_FILENAME)
        # 计数器
        self.no_counter = 0
        # 多线程锁,防止文件写入冲突以及计数冲突
        self.lock = Lock()


    def no_counter_init(self):
        '''
        计数器初始化
        :return:
        '''
        self.no_counter = 0


    def get_page_comments_format_raw_json(self,url,page):
        '''
        获取原生服务器返回的json格式的指定page评论结果
        :param url: 请求url
        :param page: 当前页数
        :return: raw json format comments
        '''
        params = Helper.get_params(page)
        json_text = Helper.get_json(url,params)
        if isinstance(json_text, bytes):
            json_text = json_text.decode("utf-8")  # convert json_text from bytes to str
        return json_text

    def get_page_comments_format_dict(self,url,page):
        json_text = self.get_page_comments_format_raw_json(url,page)
        return json.loads(json_text)

    def get_hot_comments_format_raw_json(self,url):
        '''
        获取原生服务器返回的json格式的热门评论结果,
        热门评论都在首页
        :param url: 请求url
        :return: raw json format hot comments
        '''
        return self.get_page_comments_format_raw_json(url,1)


    def get_hot_comments_format_dict(self,url):
        '''
        服务器原生json格式转换成dict
        :param url: 请求url
        :return: dict format hot comments
        '''
        json_text = self.get_hot_comments_format_raw_json(url)
        # 字符串转python内置dict
        json_dict = json.loads(json_text)
        return json_dict

    def get_hot_comments(self,url):
        '''
        获取热门评论,返回结果是list(dict)形式
        :param url:请求url
        :return:the hot comments list
        '''
        json_dict = self.get_hot_comments_format_dict(url)
        return list(json_dict[Constants.HOT_COMMENTS_KEY])

    def get_song_total_comments_num_and_page_num(self):
        '''
        获取歌曲评论总数以及评论总页数
        :return:(评论总数,页数)
        '''
        json_dict = self.get_hot_comments_format_dict(self.comments_url)
        total_comments_num = int(json_dict[Constants.TOTAL_COMMENTS_NUM])  # 评论总数
        # 获取总页数
        if total_comments_num % Constants.COMMENTS_NUM_PER_PAGE == 0:
            page = total_comments_num // 20
        else:
            page = int(total_comments_num / 20) + 1
        return total_comments_num,page

    def extract_comment_info_as_json_str(self,raw_comment):
        '''
        将原始的评论json dict(嵌套) 转化为 自定义形式的简单json str
        :param raw_comment: 原始评论json dict
        :return: converted json str
        '''
        comment_dict = {}
        # 评论内容
        comment_dict[Constants.COMMENT_CONTENT_KEY] = raw_comment[Constants.COMMENT_CONTENT_KEY]
        # 赞同数量
        comment_dict[Constants.LIKED_COUNT_KEY] = raw_comment[Constants.LIKED_COUNT_KEY]
        # 评论创建时间戳
        comment_dict[Constants.CREATE_TIME_STAMP_KEY] = raw_comment[Constants.CREATE_TIME_STAMP_KEY]
        # 用户id
        comment_dict[Constants.USER_ID_KEY] = raw_comment[Constants.USER_KEY][Constants.USER_ID_KEY]
        # 用户昵称
        comment_dict[Constants.NICK_NAME_KEY] = raw_comment[Constants.USER_KEY][Constants.NICK_NAME_KEY]
        # 用户头像地址
        comment_dict[Constants.AVATAR_URL_KEY] = raw_comment[Constants.USER_KEY][Constants.AVATAR_URL_KEY]
        # dict to str
        return json.dumps(comment_dict,ensure_ascii=False)

    
    def get_all_comments(self):
        '''
        返回一首歌的全部评论,如果评论数过多,获取速度可能会较慢,
        此时可以考虑调用多线程方法,但是此时不保证评论的顺序与原始一致
        '''
        all_comments_list = [] # 保存全部评论
        total_comments_num,page = self.get_song_total_comments_num_and_page_num()
        self.logger.info("Song name:{song_name}".format(song_name = self.song_name))
        self.logger.info("There are %d pages of comments!" % page)
        self.logger.info("There are total %d comments!" % total_comments_num)
        # 逐页按照顺序抓取全部评论
        for i in range(page):
            json_dict = self.get_page_comments_format_dict(self.comments_url,i+1)
            try:
                all_comments_list.extend(json_dict[Constants.COMMENTS_KEY])
            except KeyError as key_error:
                self.logger.info("Fail to get page {page}.".format(page = i+1))
                self.logger.info("Server parse error:{error}".format(error = key_error))
            except Exception as e:
                self.logger.info("Fail to get page {page}.".format(page = i+1))
                self.logger.info(e)
            else:
                self.logger.info("Successfully to get page {page}.".format(page = i+1))
        return all_comments_list


    def save_all_comments_to_file_by_multi_threading(self,threads = 10):
        '''
        使用多线程保存全部评论文件到磁盘
        :param threads:线程数
        '''
        self.no_counter_init()
        # 检查文件是否已经存在
        Helper.check_file_exits_and_overwrite(self.comments_file_path)
        start_time = time.time()
        total_comments_num,page = self.get_song_total_comments_num_and_page_num()
        self.logger.info("Song name:{song_name}".format(song_name = self.song_name))
        self.logger.info("There are %d pages of total %d comments!" % (page,total_comments_num))

        pack = page//threads
        threads_list = []
        for i in range(threads):
            begin_page = i*pack
            if i < threads-1:
                end_page = (i+1)*pack
            else:
                end_page = page
            t = Thread(target = self.save_pages_comments,args = (begin_page,end_page,total_comments_num))
            threads_list.append(t)
        for i in range(threads):
            threads_list[i].start()
        for i in range(threads):
            threads_list[i].join()
        end_time = time.time()
        self.logger.info("Using {threads} threads,it costs {cost_time} seconds to crawl <{song_name}>'s all comments!"
                .format(threads = threads,cost_time = (end_time - start_time),song_name = self.song_name))

    def save_pages_comments(self,begin_page,end_page,total_comments_num):
        '''
        保存从begin_page 到 end_page的评论(called by multi threading)
        :param begin_page: 开始页数
        :param end_page: 结束页数
        :param total_comments_num:全部评论数
        '''
        comments_info_list = [] # 保存全部评论的list,每条评论以json 字符串形式表示
        for i in range(begin_page,end_page):
            json_dict = self.get_page_comments_format_dict(self.comments_url,i+1)
            try:
                for item in json_dict[Constants.COMMENTS_KEY]:
                    json_str = self.extract_comment_info_as_json_str(item)
                    # 更新计数器,需要加锁
                    if self.lock.acquire():
                        self.no_counter += 1
                        self.logger.info("get %d/%d music comment succeed!" %(self.no_counter,total_comments_num))
                        self.lock.release()
                    comments_info_list.append(json_str)
            except KeyError as key_error:
                self.logger.error("Fail to get page {page}.".format(page = i+1))
                self.logger.error("Server parse error:{error}".format(error = key_error))
            except Exception as e:
                self.logger.error("Fail to get page {page}.".format(page = i+1))
                self.logger.error(e)
            else:
                self.logger.info("Successfully to save page {page}.".format(page = i+1))
        # 追加,加锁写入
        if self.lock.acquire():
            Helper.save_lines_to_file(comments_info_list,self.comments_file_path,"a")
            self.lock.release()
        self.logger.info("Write page {begin_page} to {end_page} successfully!".format(begin_page = begin_page,end_page = end_page))




    def save_all_comments_to_file(self):
        '''
        顺序保存全部评论到磁盘
        :return:
        '''
        Helper.check_file_exits_and_overwrite(self.comments_file_path)
        start_time = time.time() 
        all_comments_list = self.get_all_comments()
        # comment dict to json str
        all_comments_json_str_list = [self.extract_comment_info_as_json_str(comment) for comment in all_comments_list]
        Helper.save_lines_to_file(all_comments_json_str_list,self.comments_file_path)
        end_time = time.time() 
        print("It costs %.2f seconds to crawler <%s>." % (end_time - start_time,self.song_name))

    def get_lyrics_format_json(self):
        '''
        获取歌曲歌词(json格式)
        :return: json format music lyrics
        '''
        lyrics_url = "http://music.163.com/api/song/lyric?os=pc&id={id}&lv=-1&kv=-1&tv=-1".format(id = self.song_id)
        lyrics = requests.get(lyrics_url,
                              headers = Constants.REQUEST_HEADERS,
                              proxies = Constants.PROXIES).text
        return lyrics

    def save_lyrics_to_file(self):
        '''
        保存歌曲歌词到磁盘
        :return:
        '''
        save_path = os.path.join(self.song_path, "{song_name}_lyrics.txt".format(song_name=self.song_name))
        Helper.check_file_exits_and_overwrite(save_path)
        lyrics_json = json.loads(self.get_lyrics_format_json())
        lyrics_str = lyrics_json['lrc']['lyric']
        pattern = r'\[\d+:\d+\.\d+\](.+?\n)'
        lyrics_list = re.findall(pattern,lyrics_str)
        with open(save_path,"w",encoding = "utf-8") as f:
            f.write("{song_name}\n{singer_name}\n".format(song_name = self.song_name,singer_name = self.singer_name))
            f.writelines(lyrics_list)
        self.logger.info("save {save_path} successfully!".format(save_path = save_path))


    def save_singer_all_hot_comments_to_file(self):
        '''
        保存歌手的全部热门评论到磁盘
        :param singer_name: 歌手名字
        :param singer_id:歌手 id
        '''
        save_path = self.singer_all_hot_comments_file_path
        Helper.check_file_exits_and_overwrite(save_path)
        song_ids = Helper.get_singer_hot_songs_ids(self.singer_url) # 歌手全部歌曲id list
        if len(song_ids) == 0:
            self.logger.error("crawl from %s to get %s all hot songs ids failed!"
                              % (self.singer_url,self.singer_name))
            return
        # first line is headers
        all_hot_comments_list = []
        for song_id in song_ids:
            url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_{song_id}/?csrf_token=".format(song_id = song_id)
            hot_comments_list = self.get_hot_comments(url)
            all_hot_comments_list.extend(hot_comments_list)
        all_hot_comments_json_str_list = [self.extract_comment_info_as_json_str(comment) for comment in all_hot_comments_list]
        Helper.save_lines_to_file(all_hot_comments_json_str_list,save_path)

        self.logger.info("Write {singer_name}'s {num} hot songs hot comments successfully!".format(singer_name = self.singer_name,num = len(song_ids)))

    def generate_all_necessary_files(self,threads = 10):
        '''
        抓取并保存用于后续分析的全部基础数据,包括:
        1. 热门评论文件
        2. 全部评论文件
        '''
        self.save_all_comments_to_file_by_multi_threading(threads)
        self.save_singer_all_hot_comments_to_file()



    




