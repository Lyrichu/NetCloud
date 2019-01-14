## **NetCloud——一个完善的网易云音乐综合爬虫Python库**
### &nbsp;&nbsp;目前只需要使用命令pip3 install netcloud 即可以完成模块的安装，支持Windows与Linux系统，完全支持python3,不保证兼容python2,所以强烈建议使用python3.代码github的地址是[Netcloud](https://www.github.com/Lyrichu/NetCloud)
##&nbsp;&nbsp;项目结构:
netcloud/ \
├── analyse \
│   
├── crawler \
│   
├── demo \
│   
├── login \
│   
├── test \
│   
└── util - source

netcloud是模块根目录

analyse:网易云音乐评论以及用户信息可视化分析的模块

crawler:网易云音乐评论爬虫模块

demo:一些demo

login:网易云音乐模块登录模块,提供了丰富的网易云api,包括音乐评论,专辑,歌手等等

test:测试模块

util:工具类模块,其中也包括了source目录,主要存放一些资源文件

##&nbsp;&nbsp; 快速使用，一些简单的例子如下(也可以参考demo模块的demos,或者下面列出的核心api):
1. 抓取歌手歌曲的热门评论以及全部评论
```python
from netcloud.crawler.Crawler import NetCloudCrawler
singer_name = "林俊杰"
song_name = "豆浆油条"
nc_crawler = NetCloudCrawler(song_name = song_name,singer_name = singer_name)
# 保存歌手的全部热门评论
nc_crawler.save_singer_all_hot_comments_to_file()
# 使用多线程(20个线程)保存歌曲的全部评论
nc_crawler.save_all_comments_to_file_by_multi_threading(20)
```

2.对于歌曲的评论文件以及评论用户进行可视化分析
```python
from netcloud.analyse.Analyse import NetCloudAnalyse
singer_name = "王力宏"
song_name = "需要人陪"
nc_analyse = NetCloudAnalyse(song_name = song_name,singer_name = singer_name)
# 多线程抓取歌曲评论的全部用户相关信息并保存到磁盘
nc_analyse.save_all_users_info_to_file_by_multi_threading()
# 进行核心可视化分析,包括用户属性分布(年龄,地区,性别等)以及评论时间,关键词分布等),
# 生成的html文件可以在浏览器打开查看
nc_analyse.core_visual_analyse()
```

3.模拟登录网易云音乐,并尝试一些api
```python
from netcloud.login.Login import NetCloudLogin
# 模拟登录,如果不传任何参数,则表示从config.xml文件加载登录信息(用户名,密码等)
# 配置文件的默认路径是:当前登录用户home目录/.NetCloud/config/config.xml
nc_login = NetCloudLogin()
# 也可以显式传入用户名和密码等登录信息
#nc_login = NetCloudLogin(phone="xxxxxxxxxxx",password="xxxxxxx",email="xxxxx",rememberLogin=True)
# 打印登录用户的朋友动态,结果以json格式展示
print(nc_login.get_friends_event().json())
# 打印自身用户id
print(nc_login.get_self_id())
# 打印自己收藏的专辑(结果太长,这里略过)
print(nc_login.get_self_record().json())
# 单线程下载歌单中的全部歌曲到本地
nc_login.download_play_list_songs(2431814627,limit=1000)
# 打印自己的前10条fans信息
print(nc_login.get_self_fans(offset=0,limit=10).json())
```

4. 调用login的一些核心api,格式化打印一些信息
```python
from netcloud.login.Printer import NetCloudPrinter
# 同上,可以不传参数从配置文件加载登录信息
# 或者也可以显式传入登录参数
nc_printer = NetCloudPrinter()
# 格式化打印搜索api搜索歌手`韩红`的结果
nc_printer.pretty_print_search_singer(search_singer_name="韩红")
'''
2019-01-15 02:56:23,416 - Printer.py[line:246] - INFO: Your search singer name is:韩红
2019-01-15 02:56:23,417 - Printer.py[line:249] - INFO: Here is your search result(total 1):
2019-01-15 02:56:23,417 - Printer.py[line:251] - INFO: --------------------  search result 1  --------------------
2019-01-15 02:56:23,417 - Printer.py[line:253] - INFO: singer name:韩红
2019-01-15 02:56:23,418 - Printer.py[line:255] - INFO: alias:
2019-01-15 02:56:23,418 - Printer.py[line:259] - INFO: 
singer id:7891
2019-01-15 02:56:23,418 - Printer.py[line:261] - INFO: singer image url:http://p2.music.126.net/Se3mLHw_oKufAnG7VCka_g==/109951163096672305.jpg
2019-01-15 02:56:23,418 - Printer.py[line:263] - INFO: singer mv count:20
2019-01-15 02:56:23,418 - Printer.py[line:265] - INFO: singer album count:43
'''
# 格式化打印自己的信息
nc_printer.pretty_print_self_info()
'''
2019-01-15 03:33:21,658 - Printer.py[line:57] - INFO: Hello,Lyrichu!
Here is your personal info:
2019-01-15 03:33:21,659 - Printer.py[line:74] - INFO: avatarUrl:http://p2.music.126.net/OkEDo-a_rHCC1zEDbg7dYg==/8003345140341032.jpg
signature:热爱生活，热爱音乐！
nickname:Lyrichu
userName:0_m15527594439@163.com
province_id:420000
birthday:1995-02-12
description:
gender:male
userId:44818930
cellphone:xxxxxxx
email:xxxxxxxx@163.com
'''
```

##&nbsp;&nbsp;核心api:
- netcloud.crawler.Crawler.NetCloudCrawler:
```python
# 歌曲评论抓取
class NetCloudCrawler(object):
    '''
    the main crawler class
    '''
    def __init__(self,song_name,singer_name,song_id = None,singer_id = None):
    

    def get_hot_comments(self,url):
        '''
        获取热门评论,返回结果是list(dict)形式
        :param url:请求url
        :return:the hot comments list
        '''
        
    def get_all_comments(self):
        '''
        返回一首歌的全部评论,如果评论数过多,获取速度可能会较慢,
        此时可以考虑调用多线程方法,但是此时不保证评论的顺序与原始一致
        '''
        
    def save_all_comments_to_file(self):
        '''
        顺序保存全部评论到磁盘
        :return:
        '''
        
    def save_all_comments_to_file_by_multi_threading(self,threads = 10):
        '''
        使用多线程保存全部评论文件到磁盘
        :param threads:线程数
        '''
        
    def get_lyrics_format_json(self):
        '''
        获取歌曲歌词(json格式)
        :return: json format music lyrics
        '''
        
    def save_lyrics_to_file(self):
        '''
        保存歌曲歌词到磁盘
        :return:
        '''
        
    def save_singer_all_hot_comments_to_file(self):
        '''
        保存歌手的全部热门评论到磁盘
        :param singer_name: 歌手名字
        :param singer_id:歌手 id
        '''
        
    def generate_all_necessary_files(self,threads = 10):
        '''
        抓取并保存用于后续分析的全部基础数据,包括:
        1. 热门评论文件
        2. 全部评论文件
        '''
```
- netcloud.analyse.Analyse.NetCloudAnalyse
```python
# 可视化分析
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
        
    def save_all_users_info_to_file(self):
        '''
        保存一首歌曲下全部用户信息到磁盘
        :return:
        '''
    
    def save_users_info(self,users_url,total_urls_num):
        '''
        保存用户信息到磁盘,该函数会被save_users_info_to_file_by_multi_threading 多线程函数调用
        :param users_url: 待处理的用户url list
        :param total:全部用户url数量
        :param total_urls_num:全部url数量
        '''
        
    def load_all_users_url(self):
        '''
        从保存在磁盘的全部评论文件中,
        提取返回所有用户主页url list
        '''
        
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
        
    def draw_all_comments_wordcloud(self):
        '''
        产生歌曲全部评论的词云图像,全部使用默认参数
        :return:
        '''
        
    def draw_singer_all_hot_comments_wordcloud(self):
        '''
        产生歌手全部热门评论的词云图像,全部使用默认参数
        :return:
        '''
    
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
        
    def generate_all_analyse_files(self,threads = 10):
        '''
        一次性产生全部分析的文件,包括:
        1. 用户信息文件
        2. 歌曲全部评论词云图像
        3. 歌手全部热门评论词云图像
        4. 一些echarts html 可视化分析文件
        '''
```
- netcloud.login.Login.NetCloudLogin
```python
# 登录
class NetCloudLogin(object):
    """
    网易云音乐登录相关功能以及接口
    """
    def __init__(self,*args,**kwargs):
        '''
        登录初始化,有多种构造函数
        1.如果不传入任何参数,则表示,从配置文件读取参数值(用户名,密码等)
        2.否则必须一次传入:phone,password,email(可选,默认None),rememberLogin(可选,默认True)参数
        '''
    def send(self):
    '''
    发送请求(核心请求函数)
    :return:
    '''

    def login(self):
    """
    核心登录接口,
    返回一个登录后的Response
    """
    
    def get_self_id(self):
    '''
    通过登录得到自身的id
    :return:
    '''
    
    def get_self_play_list(self,offset=0,limit=1000):
    '''
    得到用户自身的歌单
    :param offset: 起始位置
    :param limit: 最大数量限制
    :return:
    '''
    
    def get_user_dj(self,uid, offset=0, limit=30):
    """
    通过用户id得到用户的dj信息
    :param uid: 用户id
    :param offset: 起始位置
    :param limit: 最大数量限制
    """
    
    def get_self_dj(self,offset=0, limit=30):
    '''
    返回自身的dj信息
    :param offset: 起始位置
    :param limit: 最大数量限制
    :return:
    '''
    
    def search(self,keyword,type_=1, offset=0, limit=30):
    """
    搜索接口,支持搜索音乐,专辑,用户等等
    :param keyword: 搜索关键词
    :param type_: (可选) search type各种取值含义为，1: 音乐, 100:歌手, 1000: 歌单, 1002: 用户
    :param offset: (可选) 起始位置
    :param limit: (可选) 最大数量限制
    """
    
    def get_user_follows(self,uid, offset=0, limit=30):
    """
    得到用户关注列表信息
    :param uid: 用户id
    :param offset: 起始位置
    :param limit: 最大数量限制
    """
    
    def get_self_follows(self, offset=0, limit=30):
    '''
    得到自身的关注列表
    '''
    
    def get_user_fans(self,uid, offset=0, limit=30):
    """
    得到用户粉丝列表
    :param uid: 输入用户id
    :param offset: 起始位置
    :param limit: 最大数量限制
    """
    
    def get_self_fans(self,offset=0, limit=30):
    '''
    得到自身粉丝列表
    :param offset: 起始位置
    :param limit: 最大数量限制
    :return:
    '''
    
    def get_user_event(self,uid):
    """
    得到用户的动态
    :param uid: 用户id
    """
    
    def get_self_event(self):
    '''
    得到自身的动态信息
    :return:
    '''
    
    def get_user_record(self,uid, type_=0):
    """
    通过登录获取用户的历史播放列表
    :param uid: 输入用户id
    :param type_: (可选) 返回数据类型，0：全部数据，1： 一周内的数据
    """
    
    def get_self_record(self,type_ = 0):
    '''
    得到自身的历史播放列表
    :param type_: (可选) 返回数据类型，0：全部数据，1： 一周内的数据
    :return:
    '''
    
    def get_friends_event(self):
    """
    获取好友(关注的人)的动态
    """
    
    def get_top_playlist_highquality(self,cat='全部', offset=0, limit=20):
    """
    获取高质量的歌单
    :param cat: (可选) 音乐歌单的类型，默认是 ‘全部’，其他可以传入的参数还有: '华语'、'欧美' 等等.
    :param offset: 起始位置
    :param limit: 最大数量限制
    """
		
    def get_play_list_detail(self,id, limit=20):
    """
    通过传入歌单id获取歌单详情
    :param id: 歌单id
    :param limit: 最大数量限制
    """
    
    def get_music_download_url(self,ids=[]):
    """
    通过歌曲id 获取歌曲下载url
    :param ids: music ids list 
    """
    
    def get_lyric(self,id):
    """
    通过歌曲id得到歌曲歌词
    :param id: 歌曲id
    """
    
    def get_music_comments(self,id, offset=0, limit=20):
    """
    获取音乐全部评论
    :param id: 音乐id
    :param offset: 起始位置
    :param limit: 最大数量限制
    """
    
    def get_album_comments(self,id, offset=0, limit=20):
    '''
    获取专辑评论
    :param id: 专辑id
    :param offset: 起始位置
    :param limit: 最大数量限制
    :return:
    '''
    
    def get_songs_detail(self,ids):
    """
    获得歌曲详情
    :param ids: 歌曲id list
    """
    
    def get_self_fm(self):
    """ 
    获取自身的个性化fm(而且也只能获取自身的个性化fm)
    """
    
    def get_download_urls_by_ids(self,ids_list):
    '''
    通过歌曲id list 获得歌曲的下载链接list
    :param ids_list: 歌曲id list
    :return:
    '''
    
    def get_songs_name_list_by_ids_list(self,ids_list):
    '''
    通过歌曲id list 返回歌曲名字的list
    :param ids_list: 歌曲id list
    :return: 歌曲名字list
    '''
    
    def get_songs_singer_name_list_by_ids_list(self,ids_list):
    '''
    通过歌曲id list 返回歌曲歌手的list,可能有多个歌手,所以歌手也以list保存
    :param ids_list: 歌手list
    :return: 歌手list
    '''
    
    def get_songs_name_and_singer_name_str_list_by_ids_list(self,ids_list):
    '''
    通过歌曲id list获取歌曲名字字符串(包括歌曲名以及作者名)list,
    字符串形式为:歌曲名(歌手1,歌手2)这样的形式
    :param ids_list: 歌曲id list
    :return:歌曲名字字符串list
    '''
    
    def download_play_list_songs(self,play_list_id,limit = 1000):
    '''
    下载歌单中的全部歌曲,单线程
    :param play_list_id: 歌单id
    :param limit: 下载的最大数量
    :return:
    '''
    
    def download_play_list_songs_by_multi_threading(self,play_list_id,limit = 1000,threads = 20):
    '''
    下载歌单中的全部歌曲,多线程
    :param play_list_id: 歌单id
    :param limit: 下载的最大数量
    :param threads:线程数
    :return:
    '''
    
    def get_singer_id_by_name(self,singer_name,choose_index = 0):
    '''
    通过歌手名字获取歌手id
    :param singer_name: 歌手名
    :param choose_index:选择结果列表第几个结果
    :return:
    '''
    
    def get_song_id_by_name(self,song_name,condition = 0):
    '''
    通过歌曲名获取歌曲id
    :param song_name: 歌曲名
    :param condition:搜索一个歌曲,可能会返回多个结果,
    condition表示筛选条件,可以选择第几个结果,也可以按照
    歌手进行匹配
    :return:
    '''
    
    def get_lyrics_list_by_id(self,song_id):
    '''
    通过歌曲id 获得歌词
    :param song_id: 歌曲id
    :return: 歌曲歌词
    '''
    
    def get_lyrics_list_by_name(self,song_name):
    '''
    通过歌曲名字获取歌词
    :param song_name: 歌曲名字
    :return: 歌曲歌词
    '''
    
    def download_singer_hot_songs_by_name(self,singer_name):
    '''
    通过输入歌手名字来下载歌手的全部热门歌曲,单线程实现
    :param singer_name: 歌手名字
    :return:
    '''
    
    def download_singer_hot_songs_by_name_with_multi_threading(self, singer_name,threads = 20):
    '''
    通过输入歌手名字来下载歌手的全部热门歌曲,多线程实现
    :param singer_name: 歌手名字
    :param threads: 线程数
    :return:
    '''
```

- netcloud.login.Printer.NetCloudPrinter
```python
# 格式化打印
class NetCloudPrinter(object):
    '''
    格式化打印
    '''
    def __init__(self,*args,**kwargs):
    
    def pretty_print_self_info(self):
    '''
    格式化打印个人信息
    :return:
    '''
    
    def pretty_print_user_play_list(self, uid, offset=0, limit=1000):
    '''
    格式化打印用户播放歌单
    :param uid: 用户id
    :param offset: 起始位置
    :param limit: 最大数量限制
    :return:
    '''
    
    def pretty_print_self_play_list(self, offset=0, limit=1000):
    '''
    格式化打印自身的歌单
    :param offset: 起始位置
    :param limit: 最高返回数量
    :return:
    '''
    
    def pretty_print_search_song(self, search_song_name, offset=0, limit=30):
    '''
    格式化打印搜索一首歌返回的结果
    :param search_song_name: 搜索歌曲的名字
    :param offset: 起始位置
    :param limit: 最高返回数量
    :return:
    '''
    
    def pretty_print_search_singer(self, search_singer_name, offset=0, limit=30):
    '''
    格式化打印搜索歌手的结果
    :param search_singer_name:搜索歌手名
    :param offset:起始位置
    :param limit:最高返回数量
    '''
    
    def pretty_print_search_play_list(self, keyword, offset=0, limit=30):
    '''
    格式化打印搜索专辑的结果
    :param keyword: 搜索关键字
    :param offset: 起始位置
    :param limit: 最高返回数量
    :return:
    '''
    
    def pretty_print_search_user(self, keyword, offset=0, limit=30):
    '''
    格式化打印搜索用户的信息
    :param keyword: 搜索关键字
    :param offset: 起始位置
    :param limit: 最高返回数量
    :return:
    '''
    
    def pretty_print_user_follows(self, uid, offset=0, limit=30):
    '''
    格式化打印用户关注的用户信息
    :param uid: 用户id
    :param offset: 起始位置
    :param limit: 最高返回数量
    :return:
    '''
    
    def pretty_print_user_fans(self, uid, offset=0, limit=30):
    '''
    格式化打印用户粉丝信息
    :param uid: 用户id
    :param offset: 起始位置
    :param limit: 最高返回数量
    :return:
    '''
    
    def pretty_print_self_fans(self, offset=0, limit=30):
    '''
    格式化打印用户自身的粉丝信息
    :param offset: 起始位置
    :param limit: 最高返回数量
    :return:
    '''
```

##&nbsp;&nbsp; tips
- Netcloud默认所有下载文件,生成文件的根目录为:

- 1.unix下:/home/${user}/.NetCloud,其中${user}表示当前用户名
- 2.windows下:C:\\\\${user}\\\\.NetCloud,其中${user}表示当前用户名

- 文件根目录结构为(下图是一个实例):
```python
/home/lyrichu/.NetCloud/
├── album
├── config - config.xml
├── play_list
│   ├── 攒了一大堆好听的歌想和你一起听
│   ├── 绝版歌曲，嗨到爆炸，英文纯音，应有尽有！
│   └── 【听说你好久不听中文歌】
├── singer
│   ├── 蔡健雅
│   │   └── hot_songs
│   ├── 金莎
│   │   └── hot_songs
│   ├── 林俊杰
│   │   ├── hot_songs
│   │   └── 豆浆油条
│   ├── 刘瑞琪
│   │   └── 离开的借口
│   ├── 吴青峰
│   │   └── hot_songs
│   └── 张国荣
│       └── 敢爱
└── user
│── NetCloud.log

album:存放和音乐专辑相关的文件
config:存放config.xml 配置文件,一个典型的config.xml配置文件如下:
<?xml version="1.0" encoding="utf-8"?>
<netcloud>
	<login>
		<phone>xxxxxxx</phone>
		<password>xxxxxxxx</password>
		<email></email>
		<rememberLogin>true</rememberLogin>
	</login>
	<file>
		<saveRootDir></saveRootDir>
	</file>
</netcloud>
其中:
phone:配置登录手机号
password:配置登录密码
email:配置登录邮箱账号,默认为空
rememberLogin:配置是否记住登录状态,默认为true
saveRootDir:配置文件下载生成根目录,默认为空,表示使用默认目录,也可以在这里配置成自己的路径

play_list:和歌单相关
singer:和歌手相关(比如歌手歌曲,歌手专辑下载等)
user:和用户相关
NetCloud.log:运行过程中日志记录
```

##&nbsp;&nbsp; 一些可能会出现的问题
- 4.1 在pip3 install NetCloud 的过程中，如果是在Windows下，wordcloud 以及 pycrypto 模块也许会安装失败，此时可以去[python非官方第三方库下载](https://www.lfd.uci.edu/~gohlke/pythonlibs/)下载对应pyhton版本的预编译wheel文件，然后手动pip安装即可。另外,numpy 需要 numpy+mkl形式的库，也可以在这个网站下载。
- 4.2 由于我没有测试完全，而且代码水平有限，因此代码肯定存在一些意想不到的bug，如果您对NetCloud感兴趣，在使用的过程中出现任何问题或者有任何建议，欢迎给我留言，当然最好的方式是去github提issue,地址是[NetCloud](https://www.github.com/Lyrichu/NetCloud)，同时欢迎star,fork or pull request，谢谢支持。