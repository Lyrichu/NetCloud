#!/usr/bin/env python3
# encoding: utf-8
"""
@version: 0.1
@author: lyrichu
@license: Apache Licence 
@contact: 919987476@qq.com
@site: http://www.github.com/Lyrichu
@file: Constants.py
@time: 2019/01/05 19:49
@description:
主要用于存放一些全局常量
"""
import os
import platform

from main.util import Helper


PROJECT_NAME = "NetCloud"
MUSIC163_BASE_URL = "http://music.163.com"
# 文件默认下载路径
DEFAULT_SAVE_ROOT_DIR = "/tmp/.NetCloud" if platform.system() == "Linux" else "C:\\.NetCloud"
Helper.mkdir(DEFAULT_SAVE_ROOT_DIR)
# 请求头文件
REQUEST_HEADERS = {
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
# 代理
PROXIES = {
        'http:':'http://122.114.31.177',
        'https:':'https://39.86.40.74'
    }
# 一些请求参数
REQUEST_SECOND_PARAM = "010001"
REQUEST_THIRD_PARAM = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
REQUEST_FOURTH_PARAM = "0CoJUm6Qyw8W8jud"
REQUEST_ENCSECKEY = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"

# login 相关的加密参数
REQUEST_MODULUS = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
NONCE = "0CoJUm6Qyw8W8jud"
PUBKEY = "010001"


# 用户信息文件
USER_INFO_FILENAME = "user_info.json"
# 歌手全部热门评论文件
SINGER_ALL_HOT_COMMENTS_FILENAME = "singer_all_hot_comments.json"
# 日志名
LOGGER_FILEPATH = os.path.join(DEFAULT_SAVE_ROOT_DIR,"NetCloud.log")
# 可视化图形保存位置
PLOTS_SAVE_NAME = "plots"

COMMENTS_NUM_PER_PAGE = 20 # 一页评论数量

# 服务返回json结果的一些key(str) 映射成常量的形式
HOT_COMMENTS_KEY = "hotComments" # 热评
COMMENTS_KEY = "comments" # 评论
TOTAL_COMMENTS_NUM = "total" # 全部评论数量
COMMENT_CONTENT_KEY = "content" # 评论内容
LIKED_COUNT_KEY = "likedCount" # 赞同数量(点赞数量)
CREATE_TIME_STAMP_KEY = "time" # 评论创建时间戳
USER_KEY = "user" # 用户信息
USER_ID_KEY = "userId" # 用户Id
NICK_NAME_KEY = "nickname" # 用户昵称
AVATAR_URL_KEY = "avatarUrl" # 用户头像地址

CRAWLER_TIME_KEY = "crawler_time" # 抓取时间
EVENT_COUNT_KEY = "event_count" # 动态总数
FOLLOW_COUNT_KEY = "follow_count" # 用户关注总数
FAN_COUNT_KEY = "fan_count" # 用户粉丝总数
LOCATION_KEY = "location" # 用户所在地区
USER_DESCRIPTION_KEY = "user_description" # 用户个人描述
USER_AGE_KEY = "age" # 用户年龄
LISTENING_SONGS_NUM_KEY = "listening_songs_num" # 用户累计听歌数目


UNKNOWN_TOKEN = "unknown" # 标记未知的标识符
# 项目路径
PROJECT_BASE_PATH = Helper.get_current_file_abs_path()[:Helper.get_current_file_abs_path().find(PROJECT_NAME) + len(PROJECT_NAME)]
SOURCE_PATH = os.path.join(PROJECT_BASE_PATH,"source") # 资源文件

DEFAULT_BACKGROUND_PATH = os.path.join(SOURCE_PATH,"JayChou.jpg") # 默认背景图
DEFAULT_FONT_PATH = os.path.join(SOURCE_PATH,"simsun.ttc") # 字体文件
STOPWORDS_PATH = os.path.join(SOURCE_PATH,"stopwords.txt") # 停用词文件
PROVINCE_CITIES_JSON_PATH = os.path.join(SOURCE_PATH,"province_cities.json") # 省市文件

# echarts html file
# 评论年月分布
ECHARTS_COMMENTS_YEAR_MONTH_BAR_HTML = "comments_year_month_bar.html"
# 评论年月日分布
ECHARTS_COMMENTS_YEAR_MONTH_DAY_BAR_HTML = "comments_year_month_day_bar.html"
# 赞同数分布
ECHARTS_LIKED_COUNT_BAR_HTML = "liked_count_bar.html"
# 评论词的分布
ECHARTS_COMMENTS_KEYWORDS_BAR_HTML = "comments_keywords_bar.html"
# 用户地理位置分布,geo地图表示
ECHARTS_USERS_CITY_GEO_HTML = "users_city_geo.html"
# 用户地理位置分布,bar
ECHARTS_USERS_LOCATION_BAR_HTML = "users_location_bar.html"
# 用户动态数目分布
ECHARTS_EVENTS_COUNT_BAR_HTML = "events_count_bar.html"
# 用户关注人数分布
ECHARTS_FOLLOW_COUNT_BAR_HTML = "follow_count_bar.html"
# 用户粉丝人数分布
ECHARTS_FAN_COUNT_BAR_HTML = "fan_count_bar.html"
# 用户描述关键词分布
ECHARTS_USER_DESCRIPTION_KEYWORDS_BAR_HTML = "description_keywords_bar.html"
# 用户年龄分布
ECHARTS_USER_AGE_BAR_HTML = "age_count_bar.html"
# 用户累计听歌数量分布
ECHARTS_LISTENING_SONGS_NUM_BAR_HTML = "listening_songs_num_bar.html"


# 各种请求api
REQUEST_METHODS = {
        # 使用手机登录
        'LOGIN': '/weapi/login/cellphone?csrf_token=',
        # 使用邮箱登录
        'EMAIL_LOGIN': '/weapi/login?csrf_token=',
        # 获取用户信息
        'USER_INFO': '/weapi/subcount',
        # 获取用户播放歌单(喜爱歌曲),不需要登录
        'USER_PLAY_LIST': '/weapi/user/playlist',
        # 用户dj
        'USER_DJ': '/weapi/dj/program/%s',
        # 用户关注
        'USER_FOLLOWS': '/weapi/user/getfollows/%s',
        # 用户粉丝
        'USER_FOLLOWEDS': '/weapi/user/getfolloweds/',
        # 用户动态
        'USER_EVENT': '/weapi/event/get/%s',
        # 用户播放专辑
        'USER_RECORD': '/weapi/v1/play/record',
        # 用户分享动态
        'EVENT': '/weapi/v1/event/get',
        # 用户高质量播放清单
        'TOP_PLAYLIST_HIGHQUALITY': '/weapi/playlist/highquality/list',
        # 播放清单详情
        'PLAY_LIST_DETAIL': '/weapi/v3/playlist/detail',
        # music id 得到 music url
        'MUSIC_URL': '/weapi/song/enhance/player/url',
        # music id 得到歌词
        'LYRIC': '/api/song/lyric?os=osx&id=%s&lv=-1&kv=-1&tv=-1',
        # music 全部评论
        'MUSIC_COMMENT': '/weapi/v1/resource/comments/R_SO_4_%s/?csrf_token=',
        # 通过关键字得到播放清单
        'SEARCH': '/api/search/get/',
        # 专辑评论
        'ALBUM_COMMENT': '/weapi/v1/resource/comments/R_AL_3_%s/?csrf_token=',
        # show likes on comment
        'LIKE_COMMENT': '/weapi/v1/comment/%s',
        # 歌曲详情
        'SONG_DETAIL': '/weapi/v3/song/detail',
        # 专辑内容
        'ALBUM': '/weapi/v1/album/%s',
        # 个性化fm
        'PERSONAL_FM': '/weapi/v1/radio/get'
    }
