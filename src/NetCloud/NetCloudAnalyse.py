#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# @Time   : 2018/1/26
# @Author : Lyrichu
# @Email  : 919987476@qq.com
# @File   : NetCloudAnalyse.py
'''
@Description:
Simple Analysis for NetCloud music,including song comments,users info etc.
And we use pyecharts for visualization analyse. 
'''
try:
    from NetCloudCrawler import NetCloudCrawl
except ImportError:
    from .NetCloudCrawler import NetCloudCrawl
from pyecharts import Bar,Geo
import requests 
import re 
import time 
import json 
import pandas as pd 
import jieba 
from wordcloud import WordCloud
import os 
from threading import Thread 
from scipy.misc import imread
from collections import Counter
from operator import itemgetter

class NetCloudAnalyse(NetCloudCrawl):
    """
    analyse for NetCloud comments of songs,user info etc. 
    """
    def __init__(self,song_name,singer_name,song_id = 1,singer_id = 1):
        super(NetCloudAnalyse, self).__init__(song_name = song_name,song_id = song_id,
                                            singer_name = singer_name,singer_id = singer_id)
        self.threading_count = 0 # global count for threadings
        self.unknown = "" # blank str for unknown info

    def load_comments_csv(self):
        '''
        load crawler comments csv file
        '''
        comments_df = pd.read_csv(self.comments_file_path,engine = 'python',encoding = 'utf-8') # read csv file as dataframe
        return comments_df

    def save_users_info_to_file(self):
        with open(self.users_info_file_path,"w",encoding = "utf-8") as fout:
            fout.write("用户ID,抓取时间,动态总数,关注人数,粉丝人数,用户所在地区,用户简介,年龄,累计听歌数量\n")
            users_url = self.load_users_url()
            num = len(users_url)
            
            # iterate the users url list
            for index,user_url in enumerate(users_url,1):
                try:
                    user_id = re.search(r'.*id=(\d+)',user_url).group(1) # user id
                    # time to crawl this info
                    crawler_time = self.from_timestamp_to_date(time_stamp = time.time())
                    html = requests.get(user_url,headers = self.headers).text
                    # personal events counts
                    event_count_pattern = re.compile(r'<strong id="event_count">(\d+?)</strong>')
                    event_count = re.search(event_count_pattern,html)
                    if event_count:
                        event_count = event_count.group(1) 
                    else:
                        event_count = self.unknown
                    # how many people the user follow
                    follow_count_pattern = re.compile(r'<strong id="follow_count">(\d+?)</strong>')
                    follow_count = re.search(follow_count_pattern,html)
                    if follow_count:
                        follow_count = follow_count.group(1) 
                    else:
                        follow_count = self.unknown
                    # how many fans the user has
                    fan_count_pattern = re.compile(r'<strong id="fan_count">(\d+?)</strong>')
                    fan_count = re.search(fan_count_pattern,html)
                    if fan_count:
                        fan_count = fan_count.group(1)
                    else:
                        fan_count = self.unknown
                    # the location the user is in
                    location_pattern = re.compile('<span>所在地区：(.+?)</span>')
                    location = re.search(location_pattern,html)
                    if location:
                        location = location.group(1)
                    else:
                        location = self.unknown # unknown location
                    description_pattern = re.compile('<div class="inf s-fc3 f-brk">个人介绍：(.*?)</div>')
                    description = re.search(description_pattern,html)
                    if description:   # if user has a description
                        description = description.group(1)
                        description = description.replace(","," ")
                    else:
                        description = self.unknown
                    age_pattern = re.compile(r'<span.*?data-age="(\d+)">')
                    age = re.search(age_pattern,html) # if user age info exists
                    if age:
                        age = age.group(1) # note that this age is formatted as timestamp
                        # we should convert it into real age
                        current_year = int(self.from_timestamp_to_date(time_stamp = time.time(),format = "%Y"))
                        age = (current_year-1970) - int(age)//(1000*365*24*3600) # real age
                    else:
                        age = self.unknown
                    listening_songs_num_pattern = re.compile('<h4>累积听歌(\d+?)首</h4>')
                    # total listening songs count
                    listening_songs_num = re.search(listening_songs_num_pattern,html)
                    if listening_songs_num:
                        listening_songs_num = listening_songs_num.group(1) 
                    else:
                        listening_songs_num = self.unknown
                    # write user info to the file
                    fout.write("{user_id},{crawler_time},{event_count},{follow_count},{fan_count},{location},{description},{age},{listening_songs_num}\n"
                                .format(
                                    user_id = user_id,crawler_time = crawler_time,event_count = event_count,
                                    follow_count = follow_count,fan_count = fan_count,location = location,
                                    description = description,age = age,listening_songs_num = listening_songs_num
                                    ))
                    print("Write {current}/{total} user info to file successfully!".format(current = index,total = num))
                except Exception as e:
                    print("Fail to get No.{index} comment user's info:{error}"
                          .format(index = index,error = e))

    def threading_save_users_info_to_file(self,threads = 10):
        '''
        using multithreads to save users info to file
        :param threads: the threads count
        '''
        start_time = time.time()
        with open(self.users_info_file_path,"w",encoding = "utf-8") as fout:
            fout.write("用户ID,抓取时间,动态总数,关注人数,粉丝人数,用户所在地区,用户简介,年龄,累计听歌数量\n")
        users_url = self.load_users_url()
        num = len(users_url)
        pack = num//threads # urls count every threads process
        unknown = "" # blank str for unknown info
        threads_list = []
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
        print("Using {threads} threads to save users info done,costs {cost_time} seconds"
                .format(threads = threads,cost_time = (end_time - start_time)))

    def save_users_info(self,users_url,total):
        '''
        add users info to file,this function will be called in threadings
        :param users_url: the processing users url list
        :param total:total users ulr count
        '''
        users_info_list = []
        # note that we use add mode
        with open(self.users_info_file_path,"a",encoding = "utf-8") as fout:
            for user_url in users_url:
                    try:
                        user_id = re.search(r'.*id=(\d+)',user_url).group(1) # user id
                        # time to crawl this info
                        crawler_time = self.from_timestamp_to_date(time_stamp = time.time())
                        html = requests.get(user_url,headers = self.headers).text
                        # personal events counts
                        event_count_pattern = re.compile(r'<strong id="event_count">(\d+?)</strong>')
                        event_count = re.search(event_count_pattern,html)
                        if event_count:
                            event_count = event_count.group(1) 
                        else:
                            event_count = self.unknown
                        # how many people the user follow
                        follow_count_pattern = re.compile(r'<strong id="follow_count">(\d+?)</strong>')
                        follow_count = re.search(follow_count_pattern,html)
                        if follow_count:
                            follow_count = follow_count.group(1) 
                        else:
                            follow_count = self.unknown
                        # how many fans the user has
                        fan_count_pattern = re.compile(r'<strong id="fan_count">(\d+?)</strong>')
                        fan_count = re.search(fan_count_pattern,html)
                        if fan_count:
                            fan_count = fan_count.group(1)
                        else:
                            fan_count = self.unknown
                        # the location the user is in
                        location_pattern = re.compile('<span>所在地区：(.+?)</span>')
                        location = re.search(location_pattern,html)
                        if location:
                            location = location.group(1)
                        else:
                            location = self.unknown # unknown location
                        description_pattern = re.compile('<div class="inf s-fc3 f-brk">个人介绍：(.*?)</div>')
                        description = re.search(description_pattern,html)
                        if description:   # if user has a description
                            description = description.group(1)
                            description = description.replace(","," ")
                        else:
                            description = self.unknown
                        age_pattern = re.compile(r'<span.*?data-age="(\d+)">')
                        age = re.search(age_pattern,html) # if user age info exists
                        if age:
                            age = age.group(1) # note that this age is formatted as timestamp
                            # we should convert it into real age
                            current_year = int(self.from_timestamp_to_date(time_stamp = time.time(),format = "%Y"))
                            age = (current_year-1970) - int(age)//(1000*365*24*3600) # real age
                        else:
                            age = self.unknown
                        listening_songs_num_pattern = re.compile('<h4>累积听歌(\d+?)首</h4>')
                        # total listening songs count
                        listening_songs_num = re.search(listening_songs_num_pattern,html)
                        if listening_songs_num:
                            listening_songs_num = listening_songs_num.group(1) 
                        else:
                            listening_songs_num = self.unknown
                        # write user info to the file
                        user_info = "{user_id},{crawler_time},{event_count},{follow_count},{fan_count},{location},{description},{age},{listening_songs_num}\n".format(
                                        user_id = user_id,crawler_time = crawler_time,event_count = event_count,
                                        follow_count = follow_count,fan_count = fan_count,location = location,
                                        description = description,age = age,listening_songs_num = listening_songs_num
                                        )
                        users_info_list.append(user_info)
                        print("Get {current}/{total} user info to file successfully!".format(current = self.threading_count,total = total))
                    except Exception as e:
                        print("Fail to get No.{index} comment user's info:{error}"
                              .format(index = self.threading_count,error = e))
                    self.threading_count += 1
            fout.writelines(users_info_list)




    def count_comments_lines(self):
        '''
        count total comments lines
        '''
        with open(self.comments_file_path,"r",encoding = "utf-8") as fin:
            for total,_ in enumerate(fin,1):
                pass
        return total

    
    def from_timestamp_to_date(self,time_stamp,format = "%Y-%m-%d %H:%M:%S"):
        '''
        convert from timestamp to real date formatted in Year-Month-Day etc. 
        :param time_stamp: the time stamp
        :param format: the date format we want to convert
        '''
        real_date = time.strftime(format,time.localtime(time_stamp))
        return real_date

    def load_users_url(self):
        '''
        return all users domain page ulr list
        '''
        comments_df = self.load_comments_csv()
        users_id = comments_df['用户ID'].dropna() # user id
        ids_num = len(users_id) # all ids num
        # users id must be integers like string
        users_id = [users_id.iloc[i] for i in range(ids_num) if re.match(r'\d+',str(users_id.iloc[i]))]
        users_url = []
        for user_id in users_id:
            users_url.append('http://music.163.com/user/home?id={user_id}'.format(user_id = user_id))
        return list(set(users_url)) # remove the same user's ulr

                    
    def load_users_info_csv(self):
        '''
        load users info from file,
        return users info dataframe
        '''
        users_info_df = pd.read_csv(self.users_info_file_path,engine = 'python',encoding = 'utf-8')
        return users_info_df


    def draw_wordcloud(self,full_comments = True,background_path = "source/JayChou.jpg",font_path = "source/simsun.ttc"):
        '''
        darw wordcloud of full comments of one song or hot comments of a singer
        :param full_comments: True means full comments,False means hot comments
        :param background_path:background image path
        :param font_path: font path
        '''
        abs_path = os.path.split(os.path.realpath(__file__))[0]
        background_path = os.path.join(abs_path,background_path)
        font_path = os.path.join(abs_path,font_path)
        if full_comments:
            file_path = self.comments_file_path
            save_path = os.path.join(self.song_path,self.song_name+".jpg")
        else:
            file_path = os.path.join(self.singer_path,"hot_comments.csv")
            save_path = os.path.join(self.singer_path,self.singer_name+".jpg")
        comments_df = pd.read_csv(file_path,engine = 'python',encoding = 'utf-8')["评论内容"]
        comments_text = ""
        for i in range(len(comments_df)):
            comments_text += str(comments_df.iloc[i]) 
        cut_text = " ".join(jieba.cut(comments_text)) # use blank space to paste cut keywords to str
        color_mask = imread(background_path) # read the background image
        cloud = WordCloud(font_path=font_path,background_color='white',mask=color_mask,max_words=2000,max_font_size=40)
        word_cloud = cloud.generate(cut_text) # 产生词云
        word_cloud.to_file(save_path)
        print("Successfully generate {save_path}".format(save_path =save_path))

    def core_visual_analyse(self):
        '''
        core visual analyse for comments and users info,including:
        1. The distribution of comments time,both for months,days(bar to show)
        2. The distribution of comments agree count(bar to show)
        3. The distribution of comment keywords,excluded stopwords(bar to show)
        4. The distribution of users location,using geo to show(geo to show)
        5. The distribution of users location,using bar to show(bar to show)
        6. The distribution of events count(bar to show)
        7. The distribution of follow people count(bar to show)
        8. The distribution of fans count(bar to show)
        9. The distribution of description keywords(excluded stopwords)(bar to show)
        10. The distribution of users age(bar to show)
        11. The distribution of listening songs total count(bar to show)
        '''
        plot_save_path = os.path.join(self.song_path,"plots")
        if not os.path.exists(plot_save_path):
            os.mkdir(plot_save_path)
        comments_df = self.load_comments_csv()
        users_info_df = self.load_users_info_csv()
        # 1. The distribution of comments time,both for months,days and for hours(bar to show)
        comments_time = list(comments_df['评论时间'].dropna())
        # date formatted by year-month
        comments_date_year_month = []
        # date formatted by year-month-day
        comments_date_year_month_day = []
        for comment_time in comments_time:
            # note that the timestamp should divide by 1000 first
            year_month = self.from_timestamp_to_date(comment_time*0.001,format = "%Y-%m")
            year_month_day = self.from_timestamp_to_date(comment_time*0.001,format = "%Y-%m-%d")
            comments_date_year_month.append(year_month)
            comments_date_year_month_day.append(year_month_day)
        
        comments_date_year_month_x,comments_date_year_month_y = zip(*(sorted(Counter(comments_date_year_month).items(),key = itemgetter(0))))
        comments_date_year_month_day_x,comments_date_year_month_day_y = zip(*(sorted(Counter(comments_date_year_month_day).items(),key = itemgetter(0))))
        # year-month bar plot
        comments_date_year_month_bar = Bar(title = "歌曲<{song_name}>评论时间(年-月)数量分布".format(song_name = self.song_name))
        comments_date_year_month_bar.add("年-月",comments_date_year_month_x,comments_date_year_month_y)
        comments_date_year_month_save_path = os.path.join(plot_save_path,"comments_year_month_bar.html")
        comments_date_year_month_bar.render(comments_date_year_month_save_path)
        # year-month-day bar plot
        comments_date_year_month_day_bar = Bar(title = "歌曲<{song_name}>评论时间(年-月-日)数量分布".format(song_name = self.song_name))
        comments_date_year_month_day_bar.add("年-月-日",comments_date_year_month_day_x,comments_date_year_month_day_y)
        comments_date_year_month_day_save_path = os.path.join(plot_save_path,"comments_year_month_day_bar.html")
        comments_date_year_month_day_bar.render(comments_date_year_month_day_save_path)
        # 2. The distribution of comments agree count(bar to show)
        agree_count = list(comments_df['点赞总数'].dropna())
        agree_count_x,agree_count_y = zip(*(sorted(Counter(agree_count).items(),key = itemgetter(0))))
        agree_count_bar = Bar(title = "歌曲<{song_name}>评论点赞数量分布".format(song_name = self.song_name))
        agree_count_bar.add("点赞数量",agree_count_x,agree_count_y)
        agree_count_save_path = os.path.join(plot_save_path,"agree_count_bar.html")
        agree_count_bar.render(agree_count_save_path)
        # 3. The distribution of comment keywords,excluded stopwords(bar to show)
        comments_text = "".join(list(comments_df['评论内容'].dropna()))
        comments_keywords = jieba.cut(comments_text)
        # remove the stopwords and word that length less than 2
        stopwords = self.load_stopwords()
        comments_keywords = [keyword for keyword in comments_keywords if keyword not in stopwords and len(keyword) > 1]
        comments_keywords_x,comments_keywords_y = zip(*(sorted(Counter(comments_keywords).items(),key = itemgetter(1),reverse = True)))
        comments_keywords_bar = Bar(title = "歌曲<{song_name}>评论关键词数量分布(已去除停用词)".format(song_name = self.song_name))
        comments_keywords_bar.add("关键词",comments_keywords_x,comments_keywords_y)
        comments_keywords_save_path = os.path.join(plot_save_path,"comments_keywords_bar.html")
        comments_keywords_bar.render(comments_keywords_save_path)
        # 4. The distribution of users location,using geo to show(geo to show)
        users_location = list(users_info_df['用户所在地区'].dropna())
        users_city = [] # city users in
        all_cities = self.load_all_cities()
        for location in users_location:
            for city in all_cities:
                if city in location:
                    users_city.append(city.replace("市",""))
        users_city_data = list(Counter(users_city).items()) 
        users_city_geo = Geo("歌曲<{song_name}>评论用户所在地区分布".format(song_name = self.song_name),title_color="#fff", title_pos="left",
                                width=1200, height=600, background_color='#404a59')
        attr, value = users_city_geo.cast(users_city_data)
        users_city_geo.add("", attr, value, visual_range=[0, 200], visual_text_color="#fff", symbol_size=15, is_visualmap=True)
        users_city_save_path = os.path.join(plot_save_path,"users_city_geo.html")
        users_city_geo.render(users_city_save_path)

        # 5. The distribution of users location,using bar to show(bar to show)
        users_location_x,users_location_y = zip(*(sorted(Counter(users_location).items(),key = itemgetter(1),reverse = True)))
        users_location_bar = Bar(title = "歌曲<{song_name}>评论用户所在地区分布".format(song_name = self.song_name))
        users_location_bar.add("用户所在地区",users_location_x,users_location_y)
        users_location_save_path = os.path.join(plot_save_path,"users_location_bar.html")
        users_location_bar.render(users_location_save_path)
        # 6. The distribution of events count(pie to show)
        events_count = list(users_info_df['动态总数'].dropna())
        events_count_x,events_count_y = zip(*(sorted(Counter(events_count).items(),key = itemgetter(0))))
        events_count_bar = Bar(title = "歌曲<{song_name}>评论用户动态总数分布".format(song_name = self.song_name))
        events_count_bar.add("用户动态总数",events_count_x,events_count_y)
        events_count_save_path = os.path.join(plot_save_path,"events_count_bar.html")
        events_count_bar.render(events_count_save_path)
        # 7. The distribution of follow people count(bar to show)
        follow_count = list(users_info_df['关注人数'].dropna())
        follow_count_x,follow_count_y = zip(*(sorted(Counter(follow_count).items(),key = itemgetter(0))))
        follow_count_bar = Bar(title = "歌曲<{song_name}>评论用户关注人数分布".format(song_name = self.song_name))
        follow_count_bar.add("用户关注人数",follow_count_x,follow_count_y)
        follow_count_save_path = os.path.join(plot_save_path,"follow_count_bar.html")
        follow_count_bar.render(follow_count_save_path)
        # 8. The distribution of fans count(bar to show)
        fans_count = list(users_info_df['粉丝人数'].dropna())
        fans_count_x,fans_count_y = zip(*(sorted(Counter(fans_count).items(),key = itemgetter(0))))
        fans_count_bar = Bar(title = "歌曲<{song_name}>评论用户粉丝人数分布".format(song_name = self.song_name))
        fans_count_bar.add("用户粉丝人数",fans_count_x,fans_count_y)
        fans_count_save_path = os.path.join(plot_save_path,"fans_count_bar.html")
        fans_count_bar.render(fans_count_save_path)
        # 9. The distribution of description keywords(excluded stopwords)(bar to show)
        description_text = "".join(list(users_info_df['用户简介'].dropna()))
        description_keywords = jieba.cut(description_text)
        description_keywords = [keyword for keyword in description_keywords if keyword not in stopwords and len(keyword) > 1]
        description_keywords_x,description_keywords_y = zip(*(sorted(Counter(description_keywords).items(),key = itemgetter(1),reverse = True)))
        description_keywords_bar = Bar(title = "歌曲<{song_name}>评论用户简介关键词数量分布(已去除停用词)".format(song_name = self.song_name))
        description_keywords_bar.add("用户简介关键词",description_keywords_x,description_keywords_y)
        description_keywords_save_path = os.path.join(plot_save_path,"description_keywords_bar.html")
        description_keywords_bar.render(description_keywords_save_path)
        # 10. The distribution of users age(bar to show)
        age_count = list(users_info_df['年龄'].dropna())
        age_count = [age for age in age_count if age >= 0] # filter legal age
        age_count_x,age_count_y = zip(*(sorted(Counter(age_count).items(),key = itemgetter(0))))
        age_count_bar = Bar(title = "歌曲<{song_name}>评论用户年龄分布".format(song_name = self.song_name))
        age_count_bar.add("年龄",age_count_x,age_count_y)
        age_count_save_path = os.path.join(plot_save_path,"age_count_bar.html")
        age_count_bar.render(age_count_save_path)
        # 11. The distribution of listening songs total count(bar to show)
        listening_songs_count = list(users_info_df['累计听歌数量'].dropna())
        listening_songs = {'0-100':0,'100-1000':0,'1000-10000':0,'>10000':0}
        for c in listening_songs_count:
            if c < 100:
                listening_songs['0-100'] += 1
            elif c < 1000:
                listening_songs['100-1000'] += 1
            elif c < 10000:
                listening_songs['1000-10000'] += 1
            else:
                listening_songs['>10000'] += 1
        listening_songs_count_x,listening_songs_count_y = zip(*sorted(Counter(listening_songs).items(),key = itemgetter(1),reverse = True))
        listening_songs_count_bar = Bar(title = "歌曲<{song_name}>评论用户听歌总数分布".format(song_name = self.song_name))
        listening_songs_count_bar.add("听歌总数",listening_songs_count_x,listening_songs_count_y)
        listening_songs_count_save_path = os.path.join(plot_save_path,"listening_songs_count_bar.html")
        listening_songs_count_bar.render(listening_songs_count_save_path)




    def load_stopwords(self):
        '''
        load stopwords list
        '''
        abs_path = os.path.split(os.path.realpath(__file__))[0]
        stopwords_path = os.path.join(abs_path,"source","stopwords.txt")
        with open(stopwords_path,"r",encoding = "utf-8") as f:
            stopwords = f.readlines()
        stopwords = [word.strip() for word in stopwords]
        return list(set(stopwords))

    def load_all_cities(self):
        '''
        load all cities from province_cities.json file,
        to match city from location text
        '''
        abs_path = os.path.split(os.path.realpath(__file__))[0]
        province_cities_file = os.path.join(abs_path,"source","province_cities.json")
        all_cities = []
        with open(province_cities_file,"r",encoding = "utf-8") as fin:
            content = fin.read()
            d = json.loads(content)
            for province in d:
                for city in province['city']:
                    all_cities.append(city['name'])
        return all_cities

    def generate_all_analyse_files(self,threads = 10):
        '''
        generate all analyse files,including:
        1. generate users info file
        2. generate wordcloud picture
        3. generate core analyse files
        '''
        self.threading_save_users_info_to_file(threads)
        self.draw_wordcloud()
        self.core_visual_analyse()

    def _test_load_all_cities(self):
        all_cities = self.load_all_cities()
        print("There are %d cities." % len(all_cities))
        print(all_cities)

    def _test_load_stopwords(self):
        stopwords = self.load_stopwords()
        print('There are %d stopwords.' % len(stopwords))
        # print first 100 stopwords
        print(stopwords[:100])
        

    def _test_load_comments_csv(self):
        df = self.load_comments_csv()
        print(df.head)

    def _test_count_comments_lines(self):
        total = self.count_comments_lines()
        print("{file} has {total} comments.".format(file = self.comments_file_path,total = total))

    def _test_from_timestamp_to_date(self):
        comments_df = self.load_comments_csv()
        comments_timestamp = comments_df['评论时间'].dropna() # drop na value
        show_num = 10 # lines to show
        print(self.song_name)
        print("timestamp           real_date")
        for i in range(show_num):
            time_stamp = comments_timestamp.iloc[i]
            if time_stamp:
                real_date = self.from_timestamp_to_date(time_stamp)
                print("%s       %s" %(time_stamp,real_date))

    def _test_load_users_url(self):
        users_url = self.load_users_url()
        print("There are %d users ulr." % len(users_url))
        num = 10
        print("Top %d users ulr are:" % num)
        for i in range(num):
            print("{index}:{url}".format(index = i+1,url = users_url[i]))

    def _test_load_users_info_csv(self):
        users_info_df = self.load_users_info_csv()
        print(users_info_df.head())

    def _test_save_users_info_to_file(self):
        self.save_users_info_to_file()

    def _test_draw_wordcloud(self):
        full_comments = False
        self.draw_wordcloud(full_comments = full_comments)

    def _test_core_visual_analyse(self):
        self.core_visual_analyse()

    def _test_threading_save_users_info_to_file(self,threads = 10):
        self.threading_save_users_info_to_file(threads)

    def _test_netcloudanalyse_all(self):
        self._test_save_users_info_to_file()
        self._test_threading_save_users_info_to_file(20)
        self._test_load_comments_csv()
        self._test_count_comments_lines()
        self._test_from_timestamp_to_date()
        self._test_load_users_url()
        self._test_load_users_info_csv()
        self._test_draw_wordcloud()
        self._test_core_visual_analyse()
        self._test_load_stopwords()
        self._test_load_all_cities()
        

# if __name__ == '__main__':
#     song_name = '晴天'
#     song_id = 186016
#     singer_name = '周杰伦'
#     singer_id = 6452
#     netcloud_analyse = NetCloudAnalyse(song_name = song_name,song_id = song_id,singer_name = singer_name,
#                                         singer_id = singer_id)
#     #netcloud_analyse._test_netcloudanalyse_all()
#     netcloud_analyse.generate_all_analyse_files(100)
    



