#!/usr/bin/env python3
# encoding: utf-8
"""
@version: 0.1
@author: lyrichu
@license: Apache Licence 
@contact: 919987476@qq.com
@site: http://www.github.com/Lyrichu
@file: NetCloudPrinter.py
@time: 2019/01/08 22:20
@description:
打印和网易云音乐,音乐以及用户相关的信息
"""
import json

from netcloud.login.Login import NetCloudLogin
from netcloud.util import Helper


class NetCloudPrinter(object):
    '''
    格式化打印一些信息
    '''
    def __init__(self,*args,**kwargs):
        self.logger = Helper.get_logger()
        # 初始化一个NetCloudLogin 对象
        if len(args) == 0 and len(kwargs.keys()) == 0:
            self.netcloud_login = NetCloudLogin()
        else:
            self.netcloud_login = NetCloudLogin(args,kwargs)



    def pretty_print_self_info(self):
        '''
        格式化打印个人信息
        :return:
        '''
        info_dict = self.netcloud_login.login().json()
        avatarUrl = info_dict['profile']['avatarUrl'] # 头像地址
        signature = info_dict['profile']['signature'] # 个性签名
        nickname = info_dict['profile']['nickname'] # 昵称
        userName = info_dict['account']['userName'] # 用户名
        province_id = info_dict['profile']['province'] # 省份信息
        birthday_no = info_dict['profile']['birthday'] # 生日
        if birthday_no < 0:
            birthday = "unknown"
        else:
            birthday = Helper.from_timestamp_to_date(time_stamp=birthday_no * 0.001, format="%Y-%m-%d")
        description = info_dict['profile']['description']
        if info_dict['profile']['gender'] == 1:
            gender = 'male'
        elif info_dict['profile']['gender'] == 0:
            gender = 'female'
        else:
            gender = 'unknown'
        userId = info_dict['profile']['userId']
        cellphone = json.loads(info_dict['bindings'][0]['tokenJsonStr'])['cellphone'] # 手机号
        email = json.loads(info_dict['bindings'][1]['tokenJsonStr'])['email'] # 邮箱
        self.logger.info("Hello,{nickname}!\nHere is your personal info:".format(nickname=nickname))
        self.logger.info("avatarUrl:{avatarUrl}\nsignature:{signature}\n"
                         "nickname:{nickname}\n"
                         "userName:{userName}\nprovince_id:{province_id}\n"
                         "birthday:{birthday}\ndescription:{description}\n"
                         "gender:{gender}\nuserId:{userId}\n"
                         "cellphone:{cellphone}\nemail:{email}\n".format(
            avatarUrl=avatarUrl,
            signature=signature,
            nickname=nickname,
            userName=userName,
            province_id=province_id,
            birthday=birthday,
            description=description,
            gender=gender,
            userId=userId,
            cellphone=cellphone,
            email=email
        )
        )

    def pretty_print_user_play_list(self, uid, offset=0, limit=1000):
        '''
        格式化打印用户播放歌单
        :param uid: 用户id
        :param offset: 起始位置
        :param limit: 最大数量限制
        :return:
        '''
        play_list = self.netcloud_login.get_user_play_list(uid, offset, limit).json()
        num = len(play_list['playlist']) # 歌单数量
        self.logger.info("UserId {UserId} has total {total} play list!".format(UserId=uid, total=num))
        # 循环打印歌单内容
        for i in range(num):
            playlist_dict = play_list['playlist'][i]
            self.logger.info("-" * 20 + " play list {index} ".format(index=i + 1) + "-" * 20)
            # 歌单创建时间
            createTime = Helper.from_timestamp_to_date(playlist_dict['createTime'] * 0.001, format="%Y-%m-%d")
            # 歌单更新时间
            updateTime = Helper.from_timestamp_to_date(playlist_dict['updateTime'] * 0.001, format="%Y-%m-%d")
            # 标签
            tags_str = ",".join(playlist_dict['tags'])
            # 歌单描述
            description = playlist_dict['description']
            # 封面url
            coverImgUrl = playlist_dict['coverImgUrl']
            # 创建用户id
            creator_user_id = playlist_dict['userId']
            # 创建用户昵称
            creator_user_nickname = playlist_dict['creator']['nickname']
            # 创建用户性别
            creator_user_gender = playlist_dict['creator']['gender']
            if creator_user_gender == 1:
                creator_user_gender = "male"
            elif creator_user_gender == 0:
                creator_user_gender = "female"
            else:
                creator_user_gender = "unknown"
            # 创建用户签名
            creator_user_signature = playlist_dict['creator']['signature']
            # 创建用户描述
            creator_user_descrition = playlist_dict['creator']['description']
            # 创建用户的描述详情
            creator_user_detailDescription = playlist_dict['creator']['detailDescription']
            # 创建用户的city
            creator_user_city_no = playlist_dict['creator']['city']
            # 创建用户头像url
            creator_user_avatarUrl = playlist_dict['creator']['avatarUrl']
            # 创建用户省份
            creator_user_province_no = playlist_dict['creator']['province']
            # 背景url
            backgroundUrl = playlist_dict['creator']['backgroundUrl']
            creator_user_birthday_no = playlist_dict['creator']['birthday']
            # 创建用户的生日
            if creator_user_birthday_no < 0:
                creator_user_birthday = "unknown"
            else:
                creator_user_birthday = Helper.from_timestamp_to_date(creator_user_birthday_no * 0.001,
                                                                      format="%Y-%m-%d")
            # 艺术家
            artists = playlist_dict['artists']
            # 歌单名字
            playlist_name = playlist_dict['name']
            # 是否是高质量
            highQuality = playlist_dict['highQuality']
            # 歌单id
            playlist_id = playlist_dict['id']
            # 播放次数
            playCount = playlist_dict['playCount']
            # 是否匿名
            anonimous = playlist_dict['anonimous']
            # 音乐总数
            music_count = playlist_dict['trackCount']
            # 格式化打印信息
            self.logger.info("play list name:{playlist_name}\ntags:{tags_str}\n"
                             "high quality:{highQuality}\n"
                             "description:{description}\nplay list cover image url:{coverImgUrl}\n"
                             "create time:{createTime}\nupdate time:{updateTime}\n"
                             "playlist id:{playlist_id}\n"
                             "play count:{playCount}\n"
                             "music count:{music_count}\n"
                             "anonimous:{anonimous}\n"
                             "creator user id:{creator_user_id}\ncreator user nickname:{creator_user_nickname}\n"
                             "creator user gender:{creator_user_gender}\ncreator user signature:{creator_user_signature}\n"
                             "creator user descrition:{creator_user_descrition}\n"
                             "creator user detailDescription:{creator_user_detailDescription}\n"
                             "creator user province no:{creator_user_province_no}\n"
                             "creator user city no:{creator_user_city_no}\n"
                             "creator user avatarUrl:{creator_user_avatarUrl}\n"
                             "background url:{backgroundUrl}\n"
                             "creator user birthday:{creator_user_birthday}\n"
                             "artists:{artists}\n".format(
                playlist_name=playlist_name, tags_str=tags_str,
                highQuality=highQuality, description=description,
                coverImgUrl=coverImgUrl,
                createTime=createTime, updateTime=updateTime,
                playlist_id=playlist_id, playCount=playCount,
                music_count=music_count, anonimous=anonimous,
                creator_user_id=creator_user_id, creator_user_nickname=creator_user_nickname,
                creator_user_gender=creator_user_gender, creator_user_signature=creator_user_signature,
                creator_user_descrition=creator_user_descrition,
                creator_user_detailDescription=creator_user_detailDescription,
                creator_user_province_no=creator_user_province_no,
                creator_user_city_no=creator_user_city_no,
                creator_user_avatarUrl=creator_user_avatarUrl,
                backgroundUrl=backgroundUrl,
                creator_user_birthday=creator_user_birthday,
                artists=artists
            )
            )

    def pretty_print_self_play_list(self, offset=0, limit=1000):
        '''
        格式化打印自身的歌单
        :param offset: 起始位置
        :param limit: 最高返回数量
        :return:
        '''
        response = self.netcloud_login.login()
        my_uid = response.json()['account']['id']
        self.logger.info("Your play list info is here:")
        self.pretty_print_user_play_list(my_uid, offset, limit)

    def pretty_print_search_song(self, search_song_name, offset=0, limit=30):
        '''
        格式化打印搜索一首歌返回的结果
        :param search_song_name: 搜索歌曲的名字
        :param offset: 起始位置
        :param limit: 最高返回数量
        :return:
        '''
        # 调用搜索接口
        res = self.netcloud_login.search(keyword=search_song_name, type_=1, offset=offset, limit=limit).json()
        # 搜索结果数量
        num = len(res['result']['songs'])  # search result num
        self.logger.info("Your search song name is:%s" % search_song_name)
        self.logger.info("Here is your search result(total %d):" % num)
        # 逐个打印搜索结果
        for index, content in enumerate(res['result']['songs'], 1):
            self.logger.info("-" * 20 + "  search result %d  " % index + "-" * 20)
            # 歌曲名字
            self.logger.info("song name:%s" % content['name'])
            # 歌曲别名
            self.logger.info("alias:%s" % content['alias'])
            # 歌手名(注意可能有多个歌手)
            self.logger.info("singer:")
            for artist in content['artists']:
                self.logger.info(artist['name'])
            # 专辑名
            self.logger.info("\nalbum:%s" % content['album']['name'])
            # 专辑发布时间(年月日)
            self.logger.info("album publish time:%s" %
                             Helper.from_timestamp_to_date(content['album']['publishTime'] * 0.001, format="%Y-%m-%d"))
            # 歌曲时长
            self.logger.info("song duration:%s m,%s s." % (content['duration'] // 60000,(content['duration'] // 1000 % 60)))
            # 歌曲id
            self.logger.info("song id:%s" % content["id"])
            # 歌手id(可能有多个歌手)
            self.logger.info("singer id:")
            for artist in content["artists"]:
                self.logger.info(artist['id'])
            # 专辑 id
            self.logger.info("\nalbum id:%s" % content['album']['id'])
            # mv id
            self.logger.info("mv id:%s" % content["mvid"])

    def pretty_print_search_singer(self, search_singer_name, offset=0, limit=30):
        '''
        格式化打印搜索歌手的结果
        :param search_singer_name:搜索歌手名
        :param offset:起始位置
        :param limit:最高返回数量
        '''
        res = self.netcloud_login.search(search_singer_name, type_=100, offset=offset, limit=limit).json()
        self.logger.info("Your search singer name is:%s" % search_singer_name)
        # 返回歌手的总数量
        total = res['result']['artistCount']
        self.logger.info("Here is your search result(total %d):" % total)
        for index, content in enumerate(res['result']['artists'], 1):
            self.logger.info("-" * 20 + "  search result %d  " % index + "-" * 20)
            # 歌手名
            self.logger.info("singer name:%s" % content['name'])
            # 别名
            self.logger.info("alias:")
            for alia in content['alias']:
                self.logger.info(alia)
            # 歌手id
            self.logger.info("\nsinger id:%s" % content["id"])
            # 歌手封面图片url
            self.logger.info("singer image url:%s" % content["img1v1Url"])
            # 歌手mv数量
            self.logger.info("singer mv count:%s" % content["mvSize"])
            # 歌手专辑数量
            self.logger.info("singer album count:%s" % content["albumSize"])

    def pretty_print_search_play_list(self, keyword, offset=0, limit=30):
        '''
        格式化打印搜索专辑的结果
        :param keyword: 搜索关键字
        :param offset: 起始位置
        :param limit: 最高返回数量
        :return:
        '''
        res = self.netcloud_login.search(keyword, type_=1000, offset=offset, limit=limit).json()
        # 歌单总数量
        total = res['result']['playlistCount']
        num = len(res['result']['playlists'])  # search limit result count
        self.logger.info("Your search play list keyword is:%s" % keyword)
        self.logger.info("There are total %d play lists!" % total)
        self.logger.info("Here is your search result(%d count):" % num)
        for index, content in enumerate(res['result']['playlists'], 1):
            self.logger.info("-" * 20 + "  search result %d  " % index + "-" * 20)
            # 歌单名称
            self.logger.info("play list name:%s" % content['name'])
            # 创建用户昵称
            self.logger.info("play list creator name:%s" % content['creator']['nickname'])
            # 创建用户id
            self.logger.info("play list creator id:%s" % content['creator']['userId'])
            # 歌单 播放次数
            self.logger.info("play list play count:%s" % content['playCount'])
            # 歌单封面url
            self.logger.info("play list cover image url:%s" % content["coverImgUrl"])
            # 是否是高质量歌单
            self.logger.info("high quality:%s" % content["highQuality"])
            # 歌单歌曲总数
            self.logger.info("play list song count:%s" % content["trackCount"])

    def pretty_print_search_user(self, keyword, offset=0, limit=30):
        '''
        格式化打印搜索用户的信息
        :param keyword: 搜索关键字
        :param offset: 起始位置
        :param limit: 最高返回数量
        :return:
        '''
        res = self.netcloud_login.search(keyword, type_=1002, offset=offset, limit=limit).json()
        # 返回用户总数总数
        num = len(res['result']["userprofiles"])
        # 搜索用户关键字
        self.logger.info("Your search user keyword is:%s" % keyword)
        self.logger.info("Here is your search result(%d count):" % num)
        for index, content in enumerate(res['result']['userprofiles'], 1):
            self.logger.info("-" * 20 + "  search result %d  " % index + "-" * 20)
            # 用户名
            self.logger.info("user name:%s" % content['nickname'])
            # 用户签名
            self.logger.info("user signature:%s" % content["signature"])
            # 用户描述
            self.logger.info("user description:%s" % content["description"])
            # 用户具体描述
            self.logger.info("user detail description:%s" % content["detailDescription"])
            # 用户id
            self.logger.info("user id:%s" % content["userId"])
            # 省份信息
            self.logger.info("province id:%s" % content["province"])
            # 城市信息
            self.logger.info("city id:%s" % content["city"])
            # 性别
            self.logger.info("gender:%s" % "male" if content["gender"] == 1 else "female")
            # 生日
            self.logger.info("birthday:%s" % Helper.from_timestamp_to_date(content["birthday"] * 0.001, "%Y-%m-%d"))
            # 头像url
            self.logger.info("avatar url:%s" % content["avatarUrl"])
            # 背景图像url
            self.logger.info("background image url:%s" % content["backgroundUrl"])

    def pretty_print_user_follows(self, uid, offset=0, limit=30):
        '''
        格式化打印用户关注的用户信息
        :param uid: 用户id
        :param offset: 起始位置
        :param limit: 最高返回数量
        :return:
        '''
        res = self.netcloud_login.get_user_follows(uid, offset=offset, limit=limit).json()
        # 用户关注的总数
        num = len(res['follow'])
        self.logger.info("User id %d 's follows list is(count %d):" % (uid, num))
        # 逐个遍历打印用户关注的用户的信息
        for index, content in enumerate(res['follow'], 1):
            self.logger.info("-" * 20 + "  follow %d  " % index + "-" * 20)
            # 用户昵称
            self.logger.info("user name:%s" % content["nickname"])
            # 用户id
            self.logger.info("user id:%s" % content["userId"])
            # 用户签名
            self.logger.info("user signature:%s" % content["signature"])
            # 用户性别
            self.logger.info("gender:%s" % "male" if content["gender"] == 1 else "female")
            # 用户头像地址
            self.logger.info("avatar url:%s" % content["avatarUrl"])
            # 用户歌单数量
            self.logger.info("play list count:%s" % content["playlistCount"])
            # 用户动态数
            self.logger.info("event count:%s" % content["eventCount"])
            # 用户粉丝数
            self.logger.info("fans count:%s" % content["followeds"])
            # 用户关注数
            self.logger.info("follows count:%s" % content["follows"])

    def pretty_print_user_fans(self, uid, offset=0, limit=30):
        '''
        格式化打印用户粉丝信息
        :param uid: 用户id
        :param offset: 起始位置
        :param limit: 最高返回数量
        :return:
        '''
        res = self.netcloud_login.get_user_fans(uid, offset=offset, limit=limit).json()
        # 用户粉丝总数
        num = len(res['followeds'])
        self.logger.info("User id %d 's fans list is(count %d):" % (uid, num))
        # 逐个打印用户粉丝的信息
        for index, content in enumerate(res['followeds'], 1):
            self.logger.info("-" * 20 + "  fans %d  " % index + "-" * 20)
            # 用户昵称
            self.logger.info("user name:%s" % content["nickname"])
            # 用户id
            self.logger.info("user id:%s" % content["userId"])
            # 用户签名
            self.logger.info("user signature:%s" % content["signature"])
            # 用户性别
            self.logger.info("gender:%s" % "male" if content["gender"] == 1 else "female")
            # 用户头像地址
            self.logger.info("avatar url:%s" % content["avatarUrl"])
            # 用户歌单数量
            self.logger.info("play list count:%s" % content["playlistCount"])
            # 用户动态数量
            self.logger.info("event count:%s" % content["eventCount"])
            # 粉丝数量
            self.logger.info("fans count:%s" % content["followeds"])
            # 关注者数量
            self.logger.info("follows count:%s" % content["follows"])
            # 关注当前用户的时间(年月日)
            self.logger.info("follow time:%s" % Helper.from_timestamp_to_date(content["time"] * 0.001, "%Y-%m-%d"))

    def pretty_print_self_fans(self, offset=0, limit=30):
        '''
        格式化打印用户自身的粉丝信息
        :param offset: 起始位置
        :param limit: 最高返回数量
        :return:
        '''
        res = self.netcloud_login.get_self_fans(offset=offset, limit=limit).json()
        # 用户粉丝数
        num = len(res['followeds'])
        self.logger.info("My fans list is(count %d):" % num)
        # 逐个打印我的粉丝信息
        for index, content in enumerate(res['followeds'], 1):
            self.logger.info("-" * 20 + "  fans %d  " % index + "-" * 20)
            # 用户名
            self.logger.info("user name:%s" % content["nickname"])
            # 用户 id
            self.logger.info("user id:%s" % content["userId"])
            # 用户签名
            self.logger.info("user signature:%s" % content["signature"])
            # 用户性别
            self.logger.info("gender:%s" % "male" if content["gender"] == 1 else "female")
            # 头像地址
            self.logger.info("avatar url:%s" % content["avatarUrl"])
            # 歌单数量
            self.logger.info("play list count:%s" % content["playlistCount"])
            # 动态数量
            self.logger.info("event count:%s" % content["eventCount"])
            # 粉丝数量
            self.logger.info("fans count:%s" % content["followeds"])
            # 关注的人数
            self.logger.info("follows count:%s" % content["follows"])
            # 粉丝关注当前用户的信息(年月日)
            self.logger.info("follow time:%s" % Helper.from_timestamp_to_date(content["time"] * 0.001, "%Y-%m-%d"))


