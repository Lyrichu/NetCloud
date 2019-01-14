#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# @Time   : 2018/1/26
# @Author : Lyrichu
# @Email  : 919987476@qq.com
# @File   : NetCloudAnalyse.py
'''
@Description:
网易云音乐评论,用户等信息分析,使用pyecharts进行可视化
'''

from netcloud.crawler.Crawler import NetCloudCrawler
from pyecharts import Bar,Geo
import requests 
import re 
import time 
import json
from wordcloud import WordCloud
import os 
from threading import Thread 
from scipy.misc import imread
from collections import Counter
from operator import itemgetter

from netcloud.util import Helper, Constants


class NetCloudAnalyse(NetCloudCrawler):
    """
    网易云音乐歌曲评论,用户信息分析
    """
    def __init__(self,song_name,singer_name,song_id = None,singer_id = None):
        super(NetCloudAnalyse, self).__init__(song_name = song_name,song_id = song_id,
                                            singer_name = singer_name,singer_id = singer_id)



    def get_users_info_list(self,users_url = None,total_urls_num = None):
        '''
        获取一周歌曲下全部用户信息list
        :param users_url: 传入用户url list
        :param total_urls_num: 全部urls 数量,默认是None,不为None时，说明正在进行多线程调用
        :return: list(dict)
        '''
        users_info_list = []
        if users_url is None:
            # 获取歌曲下全部用户url list
            users_url = self.load_all_users_url()
        num = len(users_url)
        # 遍历每个用户url
        for index, user_url in enumerate(users_url, 1):
            try:
                user_id = re.search(r'.*id=(\d+)', user_url).group(1)  # 用户id
                # 抓取时间
                crawler_time = Helper.from_timestamp_to_date(time_stamp=time.time())
                # 获取html
                html = requests.get(user_url, headers=Constants.REQUEST_HEADERS).text
                # 动态总数
                event_count_pattern = re.compile(r'<strong id="event_count">(\d+?)</strong>')
                event_count = re.search(event_count_pattern, html)
                if event_count:
                    event_count = event_count.group(1)
                else:
                    event_count = Constants.UNKNOWN_TOKEN
                # 用户关注数
                follow_count_pattern = re.compile(r'<strong id="follow_count">(\d+?)</strong>')
                follow_count = re.search(follow_count_pattern, html)
                if follow_count:
                    follow_count = follow_count.group(1)
                else:
                    follow_count = Constants.UNKNOWN_TOKEN
                # 用户粉丝数
                fan_count_pattern = re.compile(r'<strong id="fan_count">(\d+?)</strong>')
                fan_count = re.search(fan_count_pattern, html)
                if fan_count:
                    fan_count = fan_count.group(1)
                else:
                    fan_count = Constants.UNKNOWN_TOKEN
                # 用户所在地区
                location_pattern = re.compile('<span>所在地区：(.+?)</span>')
                location = re.search(location_pattern, html)
                if location:
                    location = location.group(1)
                else:
                    location = Constants.UNKNOWN_TOKEN
                # 用户个人描述
                description_pattern = re.compile('<div class="inf s-fc3 f-brk">个人介绍：(.*?)</div>')
                description = re.search(description_pattern, html)
                if description:
                    description = description.group(1)
                else:
                    description = Constants.UNKNOWN_TOKEN
                # 用户年龄
                age_pattern = re.compile(r'<span.*?data-age="(\d+)">')
                age = re.search(age_pattern, html)
                if age:
                    age = age.group(1)  # 时间戳形式
                    # 今年
                    current_year = int(Helper.from_timestamp_to_date(time_stamp=time.time(), format="%Y"))
                    # 得到用户真实年龄
                    age = (current_year - 1970) - int(age) // (1000 * 365 * 24 * 3600)
                else:
                    age = Constants.UNKNOWN_TOKEN
                # 累计听歌
                listening_songs_num_pattern = re.compile('<h4>累积听歌(\d+?)首</h4>')
                listening_songs_num = re.search(listening_songs_num_pattern, html)
                if listening_songs_num:
                    listening_songs_num = listening_songs_num.group(1)
                else:
                    listening_songs_num = Constants.UNKNOWN_TOKEN
                # 将用户信息以json形式保存到磁盘
                user_info_dict = {
                    Constants.USER_ID_KEY: user_id,
                    Constants.CRAWLER_TIME_KEY: crawler_time,
                    Constants.EVENT_COUNT_KEY: event_count,
                    Constants.FOLLOW_COUNT_KEY: follow_count,
                    Constants.FAN_COUNT_KEY: fan_count,
                    Constants.LOCATION_KEY: location,
                    Constants.USER_DESCRIPTION_KEY: description,
                    Constants.USER_AGE_KEY: age,
                    Constants.LISTENING_SONGS_NUM_KEY: listening_songs_num
                }
                user_info_json_str = json.dumps(user_info_dict, ensure_ascii=False)
                users_info_list.append(user_info_json_str)
                if total_urls_num: # 多线程调用
                    if self.lock.acquire():
                        self.no_counter += 1
                        self.logger.info(
                            "Write {current}/{total} user info to file successfully!".format(current=self.no_counter, total=total_urls_num))
                        self.lock.release()
                else: # 普通单线程调用
                    self.logger.info(
                        "Write {current}/{total} user info to file successfully!".format(current=index, total=num))
            except Exception as e:
                self.logger.error("Fail to get No.{index} comment user's info:{error}"
                                  .format(index=index, error=e))
        return users_info_list


    def save_all_users_info_to_file(self):
        '''
        保存一首歌曲下全部用户信息到磁盘
        :return:
        '''
        Helper.check_file_exits_and_overwrite(self.users_info_file_path)
        users_info_list = self.get_users_info_list()
        Helper.save_lines_to_file(users_info_list,self.users_info_file_path)


    def save_all_users_info_to_file_by_multi_threading(self,threads = 10):
        '''
        多线程加速保存用户信息到磁盘
        :param threads: 线程数
        '''
        Helper.check_file_exits_and_overwrite(self.users_info_file_path)
        start_time = time.time()
        users_url = self.load_all_users_url()
        num = len(users_url)
        pack = num//threads # 每个线程处理的url数量
        threads_list = []
        # 计数器初始化
        self.no_counter_init()
        for i in range(threads):
            if i < threads-1:
                urls = users_url[i*pack:(i+1)*pack]
            else:
                urls = users_url[i*pack:]
            t = Thread(target = self.save_users_info,args=(urls,num))
            threads_list.append(t)
        for i in range(threads):
            threads_list[i].start()
        for i in range(threads):
            threads_list[i].join()
        end_time = time.time()
        self.logger.info("Using {threads} threads to save users info done,costs {cost_time} seconds"
                .format(threads = threads,cost_time = (end_time - start_time)))

    def save_users_info(self,users_url,total_urls_num):
        '''
        保存用户信息到磁盘,该函数会被save_users_info_to_file_by_multi_threading 多线程函数调用
        :param users_url: 待处理的用户url list
        :param total:全部用户url数量
        :param total_urls_num:全部url数量
        '''
        # 追加写入
        users_info_list = self.get_users_info_list(users_url,total_urls_num)
        # 写入文件需要加锁
        if self.lock.acquire():
            Helper.save_lines_to_file(users_info_list,self.users_info_file_path,"a")
            self.lock.release()


    


    def load_all_users_url(self):
        '''
        从保存在磁盘的全部评论文件中,
        提取返回所有用户主页url list
        '''
        # list(dict)
        if not os.path.exists(self.comments_file_path):
            self.save_all_comments_to_file_by_multi_threading()
        comments_list = Helper.load_file_format_json(self.comments_file_path)
        # 全部用户id
        users_id = [comment[Constants.USER_ID_KEY] for comment in comments_list]
        # 全部用户数
        ids_num = len(users_id)
        # 用户id必须是数字字符串的形式
        users_id = [user_id for user_id in users_id if re.match(r'^\d+$',str(user_id))]
        users_url = []
        for user_id in users_id:
            users_url.append('http://music.163.com/user/home?id={user_id}'.format(user_id = user_id))
        # 去重
        return list(set(users_url))


    def draw_wordcloud(self,cutted_words_text,save_path,
                       background_path = None,font_path = None,
                       max_words = 2000,max_font_size = 40,background_color = 'white'):
        '''
        绘制词云,并保存图像到磁盘
        :param cutted_words_text: 已经切分好的,用空格分隔的word 字符串
        :param save_path: 保存路径
        :param background_path:背景图片地址
        :param font_path:字体文件地址
        :param max_words:最大单词数
        :param max_font_size:最大字体
        :param background_color:背景颜色
        :return:
        '''
        Helper.check_file_exits_and_overwrite(save_path)
        if background_path is None:
            background_path = Constants.DEFAULT_BACKGROUND_PATH
        if font_path is None:
            font_path = Constants.DEFAULT_FONT_PATH
        color_mask = imread(background_path)
        cloud = WordCloud(font_path = font_path,background_color=background_color,
                          mask=color_mask,max_words=max_words,max_font_size = max_font_size)
        # 产生词云
        word_cloud = cloud.generate(cutted_words_text)
        word_cloud.to_file(save_path)
        self.logger.info("Successfully generate wordcloud img to {save_path}!".format(save_path=save_path))

    def draw_all_comments_wordcloud(self):
        '''
        产生歌曲全部评论的词云图像,全部使用默认参数
        :return:
        '''
        # 如果磁盘不存在,则先加载之,并保存到磁盘
        if not os.path.exists(self.comments_file_path):
            self.save_all_comments_to_file()
        all_comments_list = Helper.load_file_format_json(self.comments_file_path)
        if len(all_comments_list) == 0:
            self.logger.error("Load %s failed!" % self.comments_file_path)
            return
        all_comments_conent = "".join([comment[Constants.COMMENT_CONTENT_KEY] for comment in all_comments_list])
        stopwords = Helper.load_stopwords()
        wordcloud_text = " ".join([word for word in Helper.cut_text(all_comments_conent) if word not in stopwords])
        save_path = os.path.join(self.song_path,"%s_all_comments.png" % self.song_name)
        self.draw_wordcloud(wordcloud_text,save_path)

    def draw_singer_all_hot_comments_wordcloud(self):
        '''
        产生歌手全部热门评论的词云图像,全部使用默认参数
        :return:
        '''
        # 如果文件已经存在则直接从磁盘加载
        # 否则先从网络加载,保存到磁盘
        if not os.path.exists(self.singer_all_hot_comments_file_path):
            self.save_singer_all_hot_comments_to_file()
        all_hot_comments_list = Helper.load_file_format_json(self.singer_all_hot_comments_file_path)
        if len(all_hot_comments_list) == 0:
            self.logger.error("Load %s failed!" % self.singer_all_hot_comments_file_path)
            return
        all_hot_comments_conent = "".join([comment[Constants.COMMENT_CONTENT_KEY] for comment in all_hot_comments_list])
        stopwords = Helper.load_stopwords()
        wordcloud_text = " ".join([word for word in Helper.cut_text(all_hot_comments_conent) if word not in stopwords])
        save_path = os.path.join(self.song_path, "%s_all_hot_comments.png" % self.singer_name)
        self.draw_wordcloud(wordcloud_text, save_path)

    def save_sorted_bar_plot(self,datas,label,title,key_index,
                             save_path,reverse = False):
        '''
        绘制有序的柱状图并保存
        :param datas: 输入数据
        :param label: 标签
        :param title: 标题
        :param key_index: 排序的key index
        :param reverse:是否翻转排序(递减,默认递增)
        :param save_path: 保存路径
        :return:
        '''
        Helper.check_file_exits_and_overwrite(save_path)
        x,y = zip(*(sorted(Counter(datas).items(), key=itemgetter(key_index),reverse=reverse)))
        bar = Bar(title)
        bar.add(label,x,y)
        bar.render(save_path)


    def core_visual_analyse(self):
        '''
        评论以及用户信息可视化,核心函数,使用pyecharts绘制
        1. 评论时间的分布,包括月和天,柱状图
        2. 赞同数分布,柱状图
        3. 去除停用词之后评论关键词的分布,柱状图
        4. 用户地理位置的分布,使用地图展示
        5. 用户地理位置的分布,使用柱状图展示
        6. 用户动态的分布,柱状图展示
        7. 用户关注人数的分布,柱状图展示
        8. 用户粉丝数的分布,柱状图展示
        9. 去停用词之后用户个人描述关键词分布,柱状图
        10. 用户年龄的分布,柱状图
        11. 用户听歌总数分布,柱状图
        '''
        plot_save_path = os.path.join(self.song_path,Constants.PLOTS_SAVE_NAME)
        Helper.mkdir(plot_save_path)
        # 加载全部评论
        comments_list = Helper.load_file_format_json(self.comments_file_path)
        # 加载全部用户信息
        users_info_list = Helper.load_file_format_json(self.users_info_file_path)


        # 1.评论时间的分布, 包括月和天, 柱状图
        comments_time = [comment[Constants.CREATE_TIME_STAMP_KEY] for comment in comments_list]
        # 年-月 格式的时间
        comments_date_year_month = []
        # 年-月-日 格式的时间
        comments_date_year_month_day = []
        for comment_time in comments_time:
            # 时间戳要除以1000得到实际的时间戳
            year_month = Helper.from_timestamp_to_date(comment_time*0.001,format = "%Y-%m")
            year_month_day = Helper.from_timestamp_to_date(comment_time*0.001,format = "%Y-%m-%d")
            comments_date_year_month.append(year_month)
            comments_date_year_month_day.append(year_month_day)

        self.save_sorted_bar_plot(
            datas = comments_date_year_month,
            label = "年-月",
            title = "歌曲<{song_name}>评论时间(年-月)数量分布".format(song_name = self.song_name),
            key_index = 0,
            save_path = os.path.join(plot_save_path,Constants.ECHARTS_COMMENTS_YEAR_MONTH_BAR_HTML)
        )

        self.save_sorted_bar_plot(
            datas = comments_date_year_month_day,
            label = "年-月-日",
            title = "歌曲<{song_name}>评论时间(年-月-日)数量分布".format(song_name=self.song_name),
            key_index = 0,
            save_path=os.path.join(plot_save_path, Constants.ECHARTS_COMMENTS_YEAR_MONTH_DAY_BAR_HTML)
        )


        # 2. 赞同数分布,柱状图
        liked_count_list = [int(comment[Constants.LIKED_COUNT_KEY]) for comment in comments_list
                            if comment[Constants.LIKED_COUNT_KEY] != Constants.UNKNOWN_TOKEN]
        self.save_sorted_bar_plot(
            datas = liked_count_list,
            label = "点赞数量",
            title = "歌曲<{song_name}>评论点赞数量分布".format(song_name = self.song_name),
            key_index = 0,
            save_path = os.path.join(plot_save_path, Constants.ECHARTS_LIKED_COUNT_BAR_HTML)
        )

        # 3. 去除停用词之后评论关键词的分布,柱状图
        comments_text = "".join([comment[Constants.COMMENT_CONTENT_KEY] for comment in comments_list])
        comments_keywords = Helper.cut_text(comments_text)
        # 移除长度小于2的词以及停用词
        stopwords = Helper.load_stopwords()
        comments_keywords = [keyword for keyword in comments_keywords if keyword not in stopwords and len(keyword) > 1]

        self.save_sorted_bar_plot(
            datas=comments_keywords,
            label="关键词",
            title="歌曲<{song_name}>评论关键词数量分布(已去除停用词)".format(song_name = self.song_name),
            key_index=1,
            save_path=os.path.join(plot_save_path, Constants.ECHARTS_COMMENTS_KEYWORDS_BAR_HTML),
            reverse=True
        )


        # 4. 用户地理位置的分布,使用地图展示
        users_location = [user_info[Constants.LOCATION_KEY] for user_info in users_info_list]
        users_city = [] # 用户所处城市
        all_support_cities = Helper.load_echarts_support_cities()
        for location in users_location:
            for city in all_support_cities:
                if city in location:
                    users_city.append(city)
                    break
        users_city_data = list(Counter(users_city).items()) 
        users_city_geo = Geo("歌曲<{song_name}>评论用户所在地区分布".format(song_name = self.song_name),title_color="#fff", title_pos="left",
                                width=1200, height=600, background_color='#404a59')
        attr, value = users_city_geo.cast(users_city_data)
        users_city_geo.add("", attr, value, visual_range=[0, 200], visual_text_color="#fff", symbol_size=15, is_visualmap=True)
        users_city_save_path = os.path.join(plot_save_path,Constants.ECHARTS_USERS_CITY_GEO_HTML)
        Helper.check_file_exits_and_overwrite(users_city_save_path)
        users_city_geo.render(users_city_save_path)



        # 5.用户地理位置分布的柱状图展示
        self.save_sorted_bar_plot(
            datas=users_location,
            label="用户所在地区",
            title="歌曲<{song_name}>评论用户所在地区分布".format(song_name = self.song_name),
            key_index=1,
            save_path=os.path.join(plot_save_path, Constants.ECHARTS_USERS_LOCATION_BAR_HTML),
            reverse=True
        )

        # 6. 用户动态数量的分布,柱状图展示
        events_count_list = [int(user_info[Constants.EVENT_COUNT_KEY]) for user_info in users_info_list
                             if user_info[Constants.EVENT_COUNT_KEY] != Constants.UNKNOWN_TOKEN]
        self.save_sorted_bar_plot(
            datas=events_count_list,
            label="用户动态总数",
            title="歌曲<{song_name}>评论用户动态总数分布".format(song_name = self.song_name),
            key_index=0,
            save_path=os.path.join(plot_save_path, Constants.ECHARTS_EVENTS_COUNT_BAR_HTML)
        )

        # 7. 用户关注人数的分布,柱状图展示
        follow_count_list = [int(user_info[Constants.FOLLOW_COUNT_KEY]) for user_info in users_info_list
                             if user_info[Constants.FOLLOW_COUNT_KEY] != Constants.UNKNOWN_TOKEN]
        self.save_sorted_bar_plot(
            datas=follow_count_list,
            label="用户关注人数",
            title="歌曲<{song_name}>评论用户关注人数分布".format(song_name = self.song_name),
            key_index=0,
            save_path=os.path.join(plot_save_path,Constants.ECHARTS_FOLLOW_COUNT_BAR_HTML)
        )

        # 8. 用户粉丝数的分布,柱状图展示
        fan_count_list = [int(user_info[Constants.FAN_COUNT_KEY]) for user_info in users_info_list
                          if user_info[Constants.FAN_COUNT_KEY] != Constants.UNKNOWN_TOKEN]
        self.save_sorted_bar_plot(
            datas=fan_count_list,
            label="用户粉丝人数",
            title="歌曲<{song_name}>评论用户粉丝人数分布".format(song_name = self.song_name),
            key_index=0,
            save_path=os.path.join(plot_save_path,Constants.ECHARTS_FAN_COUNT_BAR_HTML)
        )


        # 9. 去停用词之后用户个人描述关键词分布,柱状图
        description_text = "".join([user_info[Constants.USER_DESCRIPTION_KEY] for user_info in users_info_list])
        description_keywords = Helper.cut_text(description_text)
        description_keywords_list = [keyword for keyword in description_keywords if keyword not in stopwords and len(keyword) > 1]
        self.save_sorted_bar_plot(
            datas=description_keywords_list,
            label="用户简介关键词",
            title="歌曲<{song_name}>评论用户简介关键词数量分布(已去除停用词)".format(song_name = self.song_name),
            key_index=1,
            save_path=os.path.join(plot_save_path,Constants.ECHARTS_USER_DESCRIPTION_KEYWORDS_BAR_HTML),
            reverse=True
        )

        # 10. 用户年龄分布
        age_count_list = [int(user_info[Constants.USER_AGE_KEY]) for user_info in users_info_list
                          if user_info[Constants.USER_AGE_KEY] != Constants.UNKNOWN_TOKEN]

        age_count_list = [age for age in age_count_list if age >= 0] # 年龄必须要大于等于0
        self.save_sorted_bar_plot(
            datas=age_count_list,
            label="年龄",
            title="歌曲<{song_name}>评论用户年龄分布".format(song_name = self.song_name),
            key_index=0,
            save_path=os.path.join(plot_save_path,Constants.ECHARTS_USER_AGE_BAR_HTML)
        )

        # 11. 累计听歌数量分布
        listening_songs_num_list = [int(user_info[Constants.LISTENING_SONGS_NUM_KEY]) for user_info in users_info_list
                                    if user_info[Constants.LISTENING_SONGS_NUM_KEY] != Constants.UNKNOWN_TOKEN]
        # 听歌数量离散化(因为极差太大)
        listening_songs_dict = {'0-100':0,'100-1000':0,'1000-10000':0,'>10000':0}
        for c in listening_songs_num_list:
            if c < 100:
                listening_songs_dict['0-100'] += 1
            elif c < 1000:
                listening_songs_dict['100-1000'] += 1
            elif c < 10000:
                listening_songs_dict['1000-10000'] += 1
            else:
                listening_songs_dict['>10000'] += 1

        self.save_sorted_bar_plot(
            datas=listening_songs_dict,
            label="听歌总数",
            title="歌曲<{song_name}>评论用户听歌总数分布".format(song_name = self.song_name),
            key_index=1,
            save_path=os.path.join(plot_save_path,Constants.ECHARTS_LISTENING_SONGS_NUM_BAR_HTML),
            reverse=True
        )


    def generate_all_analyse_files(self,threads = 10):
        '''
        一次性产生全部分析的文件,包括:
        1. 用户信息文件
        2. 歌曲全部评论词云图像
        3. 歌手全部热门评论词云图像
        4. 一些echarts html 可视化分析文件
        '''
        self.save_all_users_info_to_file_by_multi_threading(threads)
        self.draw_all_comments_wordcloud()
        self.draw_singer_all_hot_comments_wordcloud()
        self.core_visual_analyse()
        


    



