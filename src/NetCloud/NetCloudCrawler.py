#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# @Time   : 2018/1/26
# @Author : Lyrichu
# @Email  : 919987476@qq.com
# @File   : NetCloudCrawler
'''
@Description:
Netease Cloud Music comments spider,you can use it to crawl all comments of 
a song,and also you can crawl the users info. WIth all this content,you can
do some interesting analyse like view the keywords of comments,the location distribution
of commenters,the age distribution etc. The class NetCloudCrawler does the job of crawler
comments,and the other class NetCloudAnalyse does the job of analyse of comments and users'
info. 
reference:@平胸小仙女's article(address:https://www.zhihu.com/question/36081767)
post encryption part can be found in the following articles:
author：平胸小仙女
link：https://www.zhihu.com/question/36081767/answer/140287795
source：知乎
-----------------------
version2,add multithreading crawler,add supporting to python3.x
'''
from Crypto.Cipher import AES
import base64
import requests
import json
import time
import os
import re 
from threading import Thread


class NetCloudCrawl(object):
    '''
    the main crawler class
    '''
    def __init__(self,song_name,song_id,singer_name,singer_id):
        self.song_name = song_name
        self.song_id = song_id
        self.singer_name = singer_name
        self.singer_id = singer_id
        self.comments_url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_{song_id}/?csrf_token=".format(song_id = song_id)
        self.singer_url = 'http://music.163.com/artist?id={singer_id}'.format(singer_id = singer_id)
        # save all songs file to directory songs_root_dir
        self.songs_root_dir = "songs"
        if not os.path.exists(self.songs_root_dir):
            os.mkdir(self.songs_root_dir)
        self.singer_path = os.path.join(self.songs_root_dir,self.singer_name)
        if not os.path.exists(self.singer_path):
            os.mkdir(self.singer_path)
        self.song_path = os.path.join(self.singer_path,self.song_name)
        if not os.path.exists(self.song_path):
            os.mkdir(self.song_path)
        # where to save crawled comments file
        self.comments_file_path = os.path.join(self.song_path,self.song_name+".csv")
        # comment users info file path
        self.users_info_file_path = os.path.join(self.song_path,"users_info.csv")
        # headers info
        self.headers = {
        'Host':"music.163.com",
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
        'Accept-Language':"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        'Accept-Encoding':"gzip, deflate",
        'Content-Type':"application/x-www-form-urlencoded",
        'Cookie':"_ntes_nnid=754361b04b121e078dee797cdb30e0fd,1486026808627; _ntes_nuid=754361b04b121e078dee797cdb30e0fd; JSESSIONID-WYYY=yfqt9ofhY%5CIYNkXW71TqY5OtSZyjE%2FoswGgtl4dMv3Oa7%5CQ50T%2FVaee%2FMSsCifHE0TGtRMYhSPpr20i%5CRO%2BO%2B9pbbJnrUvGzkibhNqw3Tlgn%5Coil%2FrW7zFZZWSA3K9gD77MPSVH6fnv5hIT8ms70MNB3CxK5r3ecj3tFMlWFbFOZmGw%5C%3A1490677541180; _iuqxldmzr_=32; vjuids=c8ca7976.15a029d006a.0.51373751e63af8; vjlast=1486102528.1490172479.21; __gads=ID=a9eed5e3cae4d252:T=1486102537:S=ALNI_Mb5XX2vlkjsiU5cIy91-ToUDoFxIw; vinfo_n_f_l_n3=411a2def7f75a62e.1.1.1486349441669.1486349607905.1490173828142; P_INFO=m15527594439@163.com|1489375076|1|study|00&99|null&null&null#hub&420100#10#0#0|155439&1|study_client|15527594439@163.com; NTES_CMT_USER_INFO=84794134%7Cm155****4439%7Chttps%3A%2F%2Fsimg.ws.126.net%2Fe%2Fimg5.cache.netease.com%2Ftie%2Fimages%2Fyun%2Fphoto_default_62.png.39x39.100.jpg%7Cfalse%7CbTE1NTI3NTk0NDM5QDE2My5jb20%3D; usertrack=c+5+hljHgU0T1FDmA66MAg==; Province=027; City=027; _ga=GA1.2.1549851014.1489469781; __utma=94650624.1549851014.1489469781.1490664577.1490672820.8; __utmc=94650624; __utmz=94650624.1490661822.6.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; playerid=81568911; __utmb=94650624.23.10.1490672820",
        'Connection':"keep-alive",
        'Referer':'http://music.163.com/',
        'Upgrade-Insecure-Requests':"1"
        }
        # set the proxies
        self.proxies= {
            'http:':'http://122.114.31.177',
            'https:':'https://39.86.40.74'
        }
        # value of offset is:(comment_page-1)*20,if it's the first page,total is True,else False
        # first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}' # first parameter
        self.second_param = "010001" # 第二个参数
        # the third parameter
        self.third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        # the fourth parameter
        self.forth_param = "0CoJUm6Qyw8W8jud"
        self.encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"

        
    def get_params(self,page): 
        '''
        get the necesarry parameters
        :param page: the input page
        '''
        first_key = self.forth_param
        second_key = 16 * 'F'
        iv = "0102030405060708"
        if(page == 1): # if it's the first page
            first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
            h_encText = self.AES_encrypt(first_param, first_key,iv)
        else:
            offset = str((page-1)*20)
            first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' %(offset,'false')
            h_encText = self.AES_encrypt(first_param, first_key, iv)
        h_encText = self.AES_encrypt(h_encText, second_key, iv)
        return h_encText

    
    def AES_encrypt(self,text, key, iv):
        '''
        the function of deciphering
        '''
        pad = 16 - len(text) % 16
        if isinstance(text,bytes): # convert text to str
            text = text.decode("utf-8")
        text += pad*chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text)
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text

    
    def get_json(self,url,params, encSecKey):
        '''
        get the comments json data
        '''
        data = {
             "params": params,
             "encSecKey": encSecKey
        }
        response = requests.post(url, headers=self.headers, data=data,proxies = self.proxies)
        return response.content

    
    def get_hot_comments(self,url):
        '''
        get the hot comments list
        :param url:the crawl url
        :return:the hot comments list
        '''
        hot_comments_list = []
        params = self.get_params(1) # the first page
        json_text = self.get_json(url,params,self.encSecKey)
        if isinstance(json_text,bytes):
            json_text = json_text.decode("utf-8") # convert json_text from bytes to str
        json_dict = json.loads(json_text)
        try:
            hot_comments = json_dict['hotComments'] # hot comments
            print("There are %d hot comments!" % len(hot_comments))
            for item in hot_comments:
                    comment = item['content'] # comments content
                    # replace comma to blank,because we want save text as csv format,
                    # which is seperated by comma,so the commas in the text might cause confusions
                    comment = comment.replace(","," ").replace("\n"," ")
                    likedCount = item['likedCount'] # the total agreements num
                    comment_time = item['time'] # comment time(formatted in timestamp)
                    userID = item['user']['userId'] # the commenter id
                    nickname = item['user']['nickname'] # the nickname
                    nickname = nickname.replace(","," ")
                    avatarUrl = item['user']['avatarUrl'] 
                    # the comment info string
                    comment_info = "{userID},{nickname},{avatarUrl},{comment_time},{likedCount},{comment}\n".format(
                        userID = userID,nickname = nickname,avatarUrl = avatarUrl,comment_time = comment_time,
                        likedCount = likedCount,comment = comment
                        )
                    hot_comments_list.append(comment_info)
        except KeyError as key_error:
            print("Server parse error:{error}".format(error = key_error))
        except Exception as e:
            print("Fail to get all hot comments:{error}".format(error = e))
        finally:
            print("Get hot comments done!")
        return hot_comments_list

    
    def get_all_comments(self):
        '''
        get a song's all comments in order,note
        that if the comments num is big,this will cost maybe a long time,
        you can use the function threading_save_all_comments_to_file() to speed the crawling. 
        but this will ensure the comments we crawled is in order,but the multi threaidng crawling 
        will not. 
        '''
        all_comments_list = [] # put all comments here
        all_comments_list.append("用户ID,用户昵称,用户头像地址,评论时间,点赞总数,评论内容\n") # headers
        params = self.get_params(1)
        json_text = self.get_json(self.comments_url,params,self.encSecKey)
        if isinstance(json_text,bytes):
            json_text = json_text.decode("utf-8") # convert json_text from bytes to str
        json_dict = json.loads(json_text)
        comments_num = int(json_dict['total'])
        if(comments_num % 20 == 0):
            page = comments_num // 20
        else:
            page = int(comments_num / 20) + 1
        print("Song name:{song_name}".format(song_name = self.song_name))
        print("There are %d pages of comments!" % page)
        for i in range(page):  # crawl in pages' order
            params = self.get_params(i+1)
            json_text = self.get_json(self.comments_url,params,self.encSecKey)
            if isinstance(json_text,bytes):
                json_text = json_text.decode("utf-8") # convert json_text from bytes to str
            json_dict = json.loads(json_text)
            if i == 0:
                print("There are total %d comments!" % comments_num) # all comments count
            try:
                for item in json_dict['comments']:
                    comment = item['content'] # the comments content
                    # replace comma to blank,because we want save text as csv format,
                    # which is seperated by comma,so the commas in the text might cause confusions
                    comment = comment.replace(","," ")
                    likedCount = item['likedCount'] 
                    comment_time = item['time'] 
                    userID = item['user']['userId'] 
                    nickname = item['user']['nickname'] 
                    avatarUrl = item['user']['avatarUrl'] 
                    comment_info = "{userID},{nickname},{avatarUrl},{comment_time},{likedCount},{comment}\n".format(
                        userID = userID,nickname = nickname,avatarUrl = avatarUrl,comment_time = comment_time,
                        likedCount = likedCount,comment = comment
                        )
                    all_comments_list.append(comment_info)
            except KeyError as key_error:
                print("Fail to get page {page}.".format(page = i+1))
                print("Server parse error:{error}".format(error = key_error))
            except Exception as e:
                print("Fail to get page {page}.".format(page = i+1))
                print(e)
            else:
                print("Successfully to get page {page}.".format(page = i+1))
        return all_comments_list

    def threading_save_all_comments_to_file(self,threads = 10):
        '''
        use multi threading to get all comments,note that will not
        ensure the crawled comments' order
        :param threads: the threads num we use
        '''
        start_time = time.time()
        with open(self.comments_file_path,"w",encoding = "utf-8") as fout:
            fout.write("用户ID,用户昵称,用户头像地址,评论时间,点赞总数,评论内容\n") # headers
        params = self.get_params(1)
        json_text = self.get_json(self.comments_url,params,self.encSecKey)
        if isinstance(json_text,bytes):
            json_text = json_text.decode("utf-8") # convert json_text from bytes to str
        json_dict = json.loads(json_text)
        comments_num = int(json_dict['total'])
        if(comments_num % 20 == 0):
            page = comments_num // 20
        else:
            page = int(comments_num / 20) + 1
        print("Song name:{song_name}".format(song_name = self.song_name))
        print("There are %d pages of total %d comments!" % (page,comments_num))
        pack = page//threads
        threads_list = []
        for i in range(threads):
            begin_page = i*pack
            if i < threads-1:
                end_page = (i+1)*pack
            else:
                end_page = page
            t = Thread(target = self.save_pages_comments,args = (begin_page,end_page))
            threads_list.append(t)
        for i in range(threads):
            threads_list[i].start()
        for i in range(threads):
            threads_list[i].join()
        end_time = time.time()
        print("Using {threads} threads,it costs {cost_time} seconds to crawl <{song_name}>'s all comments!"
                .format(threads = threads,cost_time = (end_time - start_time),song_name = self.song_name))

    def save_pages_comments(self,begin_page,end_page):
        '''
        save comments page between begin_page and end_page
        :param begin_page: the begin page
        :param end_page: the end page
        '''
        comment_info_list = []
        with open(self.comments_file_path,"a",encoding = "utf-8") as fout:
            for i in range(begin_page,end_page):  
                params = self.get_params(i+1)
                json_text = self.get_json(self.comments_url,params,self.encSecKey)
                if isinstance(json_text,bytes):
                    json_text = json_text.decode("utf-8") # convert json_text from bytes to str
                json_dict = json.loads(json_text)
                try:
                    for item in json_dict['comments']:
                        comment = item['content'] 
                        # replace comma to blank,because we want save text as csv format,
                        # which is seperated by comma,so the commas in the text might cause confusions
                        comment = comment.replace(","," ")
                        likedCount = item['likedCount'] 
                        comment_time = item['time'] 
                        userID = item['user']['userId'] 
                        nickname = item['user']['nickname'] 
                        nickname = nickname.replace(","," ")
                        avatarUrl = item['user']['avatarUrl'] 
                        # the comment info string
                        comment_info = "{userID},{nickname},{avatarUrl},{comment_time},{likedCount},{comment}\n".format(
                            userID = userID,nickname = nickname,avatarUrl = avatarUrl,comment_time = comment_time,
                            likedCount = likedCount,comment = comment
                            )
                        comment_info_list.append(comment_info)
                except KeyError as key_error:
                    print("Fail to get page {page}.".format(page = i+1))
                    print("Server parse error:{error}".format(error = key_error))
                except Exception as e:
                    print("Fail to get page {page}.".format(page = i+1))
                    print(e)
                else:
                    print("Successfully to save page {page}.".format(page = i+1))
            fout.writelines(comment_info_list)
            print("Write page {begin_page} to {end_page} successfully!".format(begin_page = begin_page,end_page = end_page))



    
    def save_to_file(self,comments_list,filename):
        '''
        save comments to file
        '''
        with open(filename,"w",encoding='utf-8') as f:
            f.writelines(comments_list)
        print("Write to file {filename} successfully".format(filename = filename))

    # save all comments to csv file
    def save_all_comments_to_file(self):
        start_time = time.time() 
        all_comments_list = self.get_all_comments()
        self.save_to_file(all_comments_list,self.comments_file_path)
        end_time = time.time() 
        print("It costs %.2f seconds to crawler <%s>." % (end_time - start_time,self.song_name))

    def get_singer_hot_songs_ids(self,singer_url):
        '''
        get a singer's all hot songs ids list
        :param singer_url: the singer domain page url
        '''
        ids_list = []
        html = requests.get(singer_url,headers = self.headers,proxies = self.proxies).text
        pattern = re.compile(r'<a href="/song\?id=(\d+?)">.*?</a>')
        ids = re.findall(pattern,html)
        for id in ids:
            ids_list.append(id)
        return ids_list

    def get_lyrics(self):
    	'''
    	get music lyrics
    	:return: json format music lyrics
    	'''
    	lyrics_url = "http://music.163.com/api/song/lyric?os=pc&id={id}&lv=-1&kv=-1&tv=-1".format(id = self.song_id)
    	lyrics = requests.get(lyrics_url,headers = self.headers,proxies = self.proxies).text 
    	return lyrics

    def save_lyrics_to_file(self):
    	lyrics_json = json.loads(self.get_lyrics())
    	lyrics_str = lyrics_json['lrc']['lyric']
    	pattern = r'\[\d+:\d+\.\d+\](.+?\n)'
    	lyrics_list = re.findall(pattern,lyrics_str)
    	save_path = os.path.join(self.song_path,"{song_name}_lyrics.txt".format(song_name = self.song_name))
    	with open(save_path,"w",encoding = "utf-8") as f:
    		f.write("{song_name}\n{singer_name}\n".format(song_name = self.song_name,singer_name = self.singer_name))
    		f.writelines(lyrics_list)
    	print("save {save_path} successfully!".format(save_path = save_path))


    def save_singer_all_hot_comments_to_file(self):
        '''
        get a singer's all hot songs' hot comments
        :param singer_name: the name of singer
        :param singer_id:the id of singer
        '''
        song_ids = self.get_singer_hot_songs_ids(self.singer_url) # get all hot songs ids
        # first line is headers
        all_hot_comments_list = ["用户ID,用户昵称,用户头像地址,评论时间,点赞总数,评论内容\n"]
        for song_id in song_ids:
            url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_{song_id}/?csrf_token=".format(song_id = song_id)
            hot_comments_list = self.get_hot_comments(url)
            all_hot_comments_list.extend(hot_comments_list)
        self.save_to_file(all_hot_comments_list,os.path.join(self.singer_path,"hot_comments.csv"))
        print("Write {singer_name}'s {num} hot songs hot comments successfully!".format(singer_name = self.singer_name,num = len(song_ids)))

    def generate_all_necessary_files(self,threads = 10):
        '''
        generate all necessary files,including:
        1. hot comments file
        2. full comments file
        '''
        self.threading_save_all_comments_to_file(threads)
        self.save_singer_all_hot_comments_to_file()


    def _test_save_singer_all_hot_comments_to_file(self):
        self.save_singer_all_hot_comments_to_file()

    def _test_get_singer_hot_songs_ids(self):
        print(self.get_singer_hot_songs_ids(self.singer_url))

    def _test_save_all_comments_to_file(self):
        self.save_all_comments_to_file()

    def _test_threading_save_all_comments_to_file(self):
        self.threading_save_all_comments_to_file()

    def _test_get_lyrics(self):
    	lyrics = self.get_lyrics()
    	print(lyrics)
    	print(type(lyrics))

    def _test_save_lyrics_to_file(self):
    	self.save_lyrics_to_file()

    def _test_netcloudcrawler_all(self):
        '''
        run all test functions
        '''
        self._test_get_singer_hot_songs_ids()
        self._test_save_all_comments_to_file()
        self._test_save_singer_all_hot_comments_to_file()
        self._test_threading_save_all_comments_to_file()





# if __name__ == '__main__':
#     song_name = '七里香'
#     song_id = 186001
#     singer_name = '周杰伦'
#     singer_id = 6452
#     netcloud_spider = NetCloudCrawl(song_name = song_name, song_id = song_id,
#                                     singer_name = singer_name,singer_id = singer_id)
#     #netcloud_spider._test_netcloudcrawler_all()
#     #netcloud_spider.generate_all_necessary_files(100)
#     #netcloud_spider._test_get_lyrics()
#     netcloud_spider._test_save_lyrics_to_file()
    




