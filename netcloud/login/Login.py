#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-02-19 12:49:59
# @Author  : lyrichu
# @Email   : 919987476@qq.com
# @Link    : http://www.github.com/Lyrichu
# @Version : 0.1
# @Description :
'''
网易云音乐和登录相关的功能实现
reference:https://github.com/xiyouMc/ncmbot
'''
import cgi
from threading import Thread, Lock

import requests 
import hashlib
import json
import os
import re
import traceback

import time

from netcloud.util import Constants, Helper


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
		self.logger = Helper.get_logger()
		self.method = None
		self.data = {}
		self.params = {}
		self.response = Response()
		self.req = requests.Session() # 构造一个请求session
		if (not args or len(args) <= 1) and (not kwargs and len(kwargs.keys()) <= 1):
			try:
				# 从用户机器配置文件加载登录信息
				config_dict = Helper._parse_config_xml()
				self.phone = config_dict['phone']
				self.password = config_dict['password']
				self.email = None if not config_dict['email'] else config_dict['email']
				self.rememberLogin = True if config_dict['rememberLogin'].lower() == "true" else False
				self.logger.info("Load login info from %s succeed!" % Constants.USER_CONFIG_FILE_PATH)
			except Exception as e:
				self.logger.error("NetCloud login failed:%s" % e)
				return
		else:
			# 优先选择按照名字传入的参数,再选择顺序参数
			if "phone" in kwargs.keys():
				self.phone = kwargs["phone"]
			else:
				if len(args) >= 1:
					self.phone = args[0]
				else:
					self.logger.error("Get 'phone' paramerter failed!")
					return
			if "password" in kwargs.keys():
				self.password = kwargs["password"]
			else:
				if len(args) >= 2:
					self.password = args[1]
				else:
					self.logger.error("Get 'password' paramerter failed!")
					return
			if "email" in kwargs.keys():
				self.email = kwargs["email"]
			else:
				if len(args) >= 3:
					self.email = args[2]
				else:
					self.email = None # 默认值
			if "rememberLogin" in kwargs.keys():
				self.rememberLogin = kwargs["rememberLogin"]
			else:
				if len(args) >= 4:
					self.rememberLogin = args[3]
				else:
					self.rememberLogin = True # 默认值
		# 计数器
		self.no_counter = 0
		# 多线程锁,防止文件写入冲突以及计数冲突
		self.lock = Lock()


	def __repr__(self):
		'''
		打印调用的方法名
		:return:
		'''
		return '<%s [%s]>' % (Constants.PROJECT_NAME,self.method)

	def __setattr__(self, name, value):
		if (name == 'method') and (value):
			if value not in Constants.REQUEST_METHODS.keys():
				raise InvalidMethod()
		object.__setattr__(self, name, value)

	def _get_webapi_requests(self):
		"""
		得到web api 的请求
		"""
		# 更新headers
		self.req.headers.update(Constants.WEBAPI_REQUEST_HEADERS)
		return self.req

	def _get_requests(self):
		'''
		普通的请求
		:return:
		'''
		# 更新头部信息
		self.req.headers.update(Constants.COMMON_REQUEST_HEADERS)
		# 返回请求
		return self.req 


	def _build_response(self, resp):
		'''
		对于服务器返回的原始响应,
		封装成一个Response对象
		:param resp: 原始的服务器响应
		:return: Response
		'''
		self.response.content = resp.content
		self.response.status_code = resp.status_code
		self.response.headers = resp.headers

	def send(self):
		'''
		发送请求(核心请求函数)
		:return:
		'''
		# 请求方法不能为空
		if self.method is None:
			raise ParamsError()
		try:
			# 搜索方法
			if self.method == Constants.SEARCH_REQUEST_METHOD:
				# 构造请求
				req = self._get_requests()
				# 构造请求的url
				_url = Constants.MUSIC163_BASE_URL + Constants.REQUEST_METHODS[self.method]
				# 发送请求
				resp = req.post(_url, data=self.data)
				# 构建一个Response
				self._build_response(resp)
				# 设置请求的状态为ok
				self.response.ok = True
			else:
				# 非搜索方法
				if isinstance(self.data, dict): # data是字典编码的形式
					# 对请求data进行加密
					data = Helper.encrypted_request(self.data)
				# 使用webapi请求的形式
				req = self._get_webapi_requests()
				# 构造请求的url
				_url = Constants.MUSIC163_BASE_URL + Constants.REQUEST_METHODS[self.method]
				# 用户dj,用户关注情况,用户动态
				# 需要填充用户自身的id
				if self.method in (Constants.USER_DJ_REQUEST_METHOD,
								   Constants.USER_FOLLOWS_REQUEST_METHOD,
								   Constants.USER_EVENT_REQUEST_METHOD):
					_url = _url % self.params['uid']
				# 歌词,音乐评论
				# 需要填充歌曲id
				if self.method in (Constants.LYRIC_REQUEST_METHOD,
								   Constants.MUSIC_COMMENT_REQUEST_METHOD,
								   Constants.ALBUM_COMMENT_REQUEST_METHOD
								   ):
					_url = _url % self.params['id']
				# 获取歌词不需要格外post数据
				if self.method == Constants.LYRIC_REQUEST_METHOD:
					resp = req.get(_url)
				else:
					# 其他的请求需要附加数据
					resp = req.post(_url, data=data)
				self._build_response(resp)
				self.response.ok = True
		except Exception as why:
			# 打印报错栈
			traceback.print_exc()
			self.logger.info('Requests Exception', why)
			# 设置响应的异常信息
			self.response.error = why

	def login(self):
		"""
		核心登录接口,
		返回一个登录后的Response
		"""
		# 电话和邮箱至少要填一个
		if (self.phone is None) and (self.email is None):
			raise ParamsError()
		# 密码是必填项
		if self.password is None:
			raise ParamsError()
		md5 = hashlib.md5()
		# 密码使用md5加密
		md5.update(self.password.encode("utf-8"))
		password = md5.hexdigest()
		# 要post的data
		self.data = {'password': password, 'rememberLogin': self.rememberLogin}
		# 使用电话登录
		if self.phone is not None:
			self.data['phone'] = self.phone
			self.method = Constants.LOGIN_REQUEST_METHOD
		else:
			# 使用邮箱登录
			self.data['username'] = self.email
			self.method = Constants.EMAIL_LOGIN_REQUEST_METHOD
		# 发送请求
		self.send()
		# 返回封装之后的Response
		return self.response

	def get_user_play_list(self,uid,offset=0,limit=1000):
		"""
		得到用户的歌单
		:param uid: 用户id
		:param offset: 起始位置
		:param limit: 最大数量限制
		"""
		# 用户id是必填项
		if uid is None:
			raise ParamsError()
		self.method = Constants.USER_PLAY_LIST_REQUEST_METHOD
		# 构造请求的数据
		self.data = {'offset': offset, 'uid': uid, 'limit': limit, 'csrf_token': ''}
		self.send()
		return self.response

	def get_self_id(self):
		'''
		通过登录得到自身的id
		:return:
		'''
		response = self.login()
		return response.json()['account']['id']

	def get_self_play_list(self,offset=0,limit=1000):
		'''
		得到用户自身的歌单
		:param offset: 起始位置
		:param limit: 最大数量限制
		:return:
		'''
		my_uid = self.get_self_id()
		return self.get_user_play_list(my_uid,offset,limit)

	def get_user_dj(self,uid, offset=0, limit=30):
		"""
		通过用户id得到用户的dj信息
		:param uid: 用户id
		:param offset: 起始位置
		:param limit: 最大数量限制
		"""
		if uid is None:
			raise ParamsError()
		self.method = Constants.USER_DJ_REQUEST_METHOD
		self.data = {'offset': offset, 'limit': limit, "csrf_token": ""}
		# 更新params
		self.params = {'uid': uid}
		self.send()
		return self.response

	def get_self_dj(self,offset=0, limit=30):
		'''
		返回自身的dj信息
		:param offset: 起始位置
		:param limit: 最大数量限制
		:return:
		'''
		my_uid = self.get_self_id()
		return self.get_user_dj(my_uid,offset,limit)

	def search(self,keyword,type_=1, offset=0, limit=30):
		"""
		搜索接口,支持搜索音乐,专辑,用户等等
		:param keyword: 搜索关键词
		:param type_: (可选) search type各种取值含义为，1: 音乐, 100:歌手, 1000: 歌单, 1002: 用户
		:param offset: (可选) 起始位置
		:param limit: (可选) 最大数量限制
		"""
		# 搜索关键词是必填项
		if keyword is None:
			raise ParamsError()
		self.method = Constants.SEARCH_REQUEST_METHOD
		# 构造请求数据
		self.data = {
		    's': keyword,
		    'limit': str(limit),
		    'type': str(type_),
		    'offset': str(offset)
		}
		self.send()
		return self.response

	def get_user_follows(self,uid, offset=0, limit=30):
		"""
		得到用户关注列表信息
		:param uid: 用户id
		:param offset: 起始位置
		:param limit: 最大数量限制
		"""
		# 用户id是必填项
		if uid is None:
			raise ParamsError()
		self.method = Constants.USER_FOLLOWS_REQUEST_METHOD
		# 请求参数
		self.params = {'uid': uid}
		self.data = {'offset': offset, 'limit': limit, 'order': True}
		self.send()
		return self.response

	def get_self_follows(self, offset=0, limit=30):
		'''
		得到自身的关注列表
		'''
		my_uid = self.get_self_id()
		return self.get_user_follows(my_uid,offset,limit)


	def get_user_fans(self,uid, offset=0, limit=30):
		"""
		得到用户粉丝列表
		:param uid: 输入用户id
		:param offset: 起始位置
		:param limit: 最大数量限制
		"""
		if uid is None:
			raise ParamsError()
		self.method = Constants.USER_FOLLOWEDS_REQUEST_METHOD
		self.data = {
		    'userId': uid,
		    'offset': offset,
		    'limit': limit,
		    "csrf_token": ""
		}
		self.send()
		return self.response

	def get_self_fans(self,offset=0, limit=30):
		'''
		得到自身粉丝列表
		:param offset: 起始位置
		:param limit: 最大数量限制
		:return:
		'''
		my_uid = self.get_self_id()
		return self.get_user_fans(my_uid,offset,limit)

	def get_user_event(self,uid):
		"""
		得到用户的动态
		:param uid: 用户id
		"""
		# 用户id是必填项
		if uid is None:
			raise ParamsError()
		self.method = Constants.USER_EVENT_REQUEST_METHOD
		self.params = {'uid': uid}
		self.data = {'time': -1, 'getcounts': True, "csrf_token": ""}
		self.send()
		return self.response

	def get_self_event(self):
		'''
		得到自身的动态信息
		:return:
		'''
		my_uid = self.get_self_id()
		return self.get_user_event(my_uid)

	def get_user_record(self,uid, type_=0):
		"""
		通过登录获取用户的历史播放列表
		:param uid: 输入用户id
		:param type_: (可选) 返回数据类型，0：全部数据，1： 一周内的数据
		"""
		# 用户id是必填项
		if uid is None:
			raise ParamsError()
		self.method = Constants.USER_RECORD_REQUEST_METHOD
		self.data = {'type': type_, 'uid': uid, "csrf_token": ""}
		self.send()
		return self.response

	def get_self_record(self,type_ = 0):
		'''
		得到自身的历史播放列表
		:param type_: (可选) 返回数据类型，0：全部数据，1： 一周内的数据
		:return:
		'''
		my_uid = self.get_self_id()
		return self.get_user_record(uid = my_uid,type_ = type_)



	def get_friends_event(self):
		"""
		获取好友(关注的人)的动态
		"""
		self.method = Constants.EVENT_REQUEST_METHOD
		self.data = {"csrf_token": ""}
		self.send()
		return self.response



	def get_top_playlist_highquality(self,cat='全部', offset=0, limit=20):
		"""
		获取高质量的歌单
		:param cat: (可选) 音乐歌单的类型，默认是 ‘全部’，其他可以传入的参数还有: '华语'、'欧美' 等等.
		:param offset: 起始位置
		:param limit: 最大数量限制
		"""
		self.method = Constants.TOP_PLAYLIST_HIGHQUALITY_REQUEST_METHOD
		self.data = {'cat': cat, 'offset': offset, 'limit': limit}
		self.send()
		return self.response



	def get_play_list_detail(self,id, limit=20):
		"""
		通过传入歌单id获取歌单详情
		:param id: 歌单id
		:param limit: 最大数量限制
		"""
		# id是必填参数
		if id is None:
			raise ParamsError()
		self.method = Constants.PLAY_LIST_DETAIL_REQUEST_METHOD
		self.data = {'id': id, 'limit': limit, "csrf_token": ""}
		self.send()
		return self.response



	def get_music_download_url(self,ids=[]):
		"""
		通过歌曲id 获取歌曲下载url
		:param ids: music ids list 
		"""
		# 注意传入id必须是list的形式
		if not isinstance(ids, list):
			raise ParamsError()
		self.method = Constants.MUSIC_URL_REQUEST_METHOD
		self.data = {'ids': ids, 'br': 999000, "csrf_token": ""}
		self.send()
		return self.response

	def get_lyric(self,id):
		"""
		通过歌曲id得到歌曲歌词
		:param id: 歌曲id
		"""
		if id is None:
			raise ParamsError()
		self.method = Constants.LYRIC_REQUEST_METHOD
		self.params = {'id': id} # 请求参数
		self.send()
		return self.response


	def get_music_comments(self,id, offset=0, limit=20):
		"""
		获取音乐全部评论
		:param id: 音乐id
		:param offset: 起始位置
		:param limit: 最大数量限制
		"""
		if id is None:
			raise ParamsError()
		self.method = Constants.MUSIC_COMMENT_REQUEST_METHOD
		self.params = {'id': id}
		self.data = {'offset': offset, 'limit': limit, 'rid': id,"csrf_token": ""}
		self.send()
		return self.response


	def get_album_comments(self,id, offset=0, limit=20):
		'''
		获取专辑评论
		:param id: 专辑id
		:param offset: 起始位置
		:param limit: 最大数量限制
		:return:
		'''
		# id是必须的
		if id is None:
			raise ParamsError()
		self.method = Constants.ALBUM_COMMENT_REQUEST_METHOD
		self.params = {'id': id}
		self.data = {'offset': offset, 'limit': limit, 'rid': id, "csrf_token": ""}
		self.send()
		return self.response



	def get_songs_detail(self,ids):
		"""
		获得歌曲详情
		:param ids: 歌曲id list
		"""
		# 传入ids必须是id list 的形式
		if not isinstance(ids, list):
			raise ParamsError()
		c = []
		for id in ids:
			c.append({'id': id})
		self.method = Constants.SONG_DETAIL_REQUEST_METHOD
		self.data = {'c': json.dumps(c), 'ids': c, "csrf_token": ""}
		self.send()
		return self.response



	def get_self_fm(self):
		""" 
		获取自身的个性化fm(而且也只能获取自身的个性化fm)
		"""
		self.method = Constants.PERSONAL_FM_REQUEST_METHOD
		self.data = {"csrf_token": ""}
		self.send()
		return self.response

	def get_download_urls_by_ids(self,ids_list):
		'''
		通过歌曲id list 获得歌曲的下载链接list
		:param ids_list: 歌曲id list
		:return:
		'''
		urls_list = []
		for content in self.get_music_download_url(ids = ids_list).json()['data']:
			urls_list.append(content['url']) 
		return urls_list

	def get_songs_name_list_by_ids_list(self,ids_list):
		'''
		通过歌曲id list 返回歌曲名字的list
		:param ids_list: 歌曲id list
		:return: 歌曲名字list
		'''
		songs_name_list = []
		for content in self.get_songs_detail(ids_list).json()['songs']:
			# 歌曲名字
			song_name = content['name']
			songs_name_list.append(song_name)
		return songs_name_list

	def get_songs_singer_name_list_by_ids_list(self,ids_list):
		'''
		通过歌曲id list 返回歌曲歌手的list,可能有多个歌手,所以歌手也以list保存
		:param ids_list: 歌手list
		:return: 歌手list
		'''
		songs_singer_name_list = []
		for content in self.get_songs_detail(ids_list).json()['songs']:
			# 歌手名字
			singer_list = [c['name'] for c in content['ar']]
			songs_singer_name_list.append(singer_list)
		return songs_singer_name_list


	def get_songs_name_and_singer_name_str_list_by_ids_list(self,ids_list):
		'''
		通过歌曲id list获取歌曲名字字符串(包括歌曲名以及作者名)list,
		字符串形式为:歌曲名(歌手1,歌手2)这样的形式
		:param ids_list: 歌曲id list
		:return:歌曲名字字符串list
		'''
		songs_name_and_singer_name_list = []
		for content in self.get_songs_detail(ids_list).json()['songs']:
			# 歌曲名字
			song_name = content['name']
			# 歌手名字
			singer_name = ",".join([c['name'] for c in content['ar']])
			songs_name_and_singer_name_list.append(song_name+"(%s)" %singer_name)

		return songs_name_and_singer_name_list


	def download_play_list_songs(self,play_list_id,limit = 1000):
		'''
		下载歌单中的全部歌曲,单线程
		:param play_list_id: 歌单id
		:param limit: 下载的最大数量
		:return:
		'''
		start_time = time.time()
		# 获取歌单详情
		res = self.get_play_list_detail(play_list_id,limit).json()
		songs_id_list = []
		# 获取歌单歌曲id list
		for content in res['playlist']["trackIds"]:
			songs_id_list.append(content['id'])
		# 歌单名字
		play_list_name = res['playlist']['name']
		# 歌单下载音乐保存地址
		save_path = os.path.join(Constants.PLAY_LIST_SAVE_DIR,play_list_name)
		Helper.mkdir(save_path)
		# 获取歌曲名+歌手名字符串列表
		songs_name_and_singer_name_str_list = self.get_songs_name_and_singer_name_str_list_by_ids_list(songs_id_list)
		# 获取歌曲下载url list
		urls_list = self.get_download_urls_by_ids(songs_id_list)
		# 全部歌曲数目
		total = len(urls_list)
		self.logger.info("play list %s has total %d songs!" %(play_list_name,total))
		self.logger.info("(single thread)Now start download musics of %s(save path is:%s):" %(play_list_name,save_path))
		for index,url in enumerate(urls_list,1):
			try:
				Helper.download_network_resource(url,os.path.join(save_path,"%s.mp3" %songs_name_and_singer_name_str_list[index-1]))
				self.logger.info("Successfully download %d/%d(%s)!" %(index,total,songs_name_and_singer_name_str_list[index-1]))
			except Exception:
				self.logger.info("Fail download %d/%d(%s)!" %(index,total,songs_name_and_singer_name_str_list[index-1]))
				continue
		end_time = time.time()
		self.logger.info("It costs %.2f seconds to download play list %s(id=%s)'s %d songs to %s "
						 "using single thread!" %((end_time-start_time),
												  play_list_name,play_list_id,total,save_path))

	def download_play_list_songs_by_multi_threading(self,play_list_id,limit = 1000,threads = 20):
		'''
		下载歌单中的全部歌曲,多线程
		:param play_list_id: 歌单id
		:param limit: 下载的最大数量
		:param threads:线程数
		:return:
		'''
		start_time = time.time()
		# 获取歌单详情
		res = self.get_play_list_detail(play_list_id, limit).json()
		songs_id_list = []
		# 获取歌单歌曲id list
		for content in res['playlist']["trackIds"]:
			songs_id_list.append(content['id'])
		# 歌单名字
		play_list_name = res['playlist']['name']
		# 歌单下载音乐保存地址
		save_path = os.path.join(Constants.PLAY_LIST_SAVE_DIR, play_list_name)
		Helper.mkdir(save_path)
		# 获取歌曲名+歌手名字符串列表
		songs_name_and_singer_name_str_list = self.get_songs_name_and_singer_name_str_list_by_ids_list(songs_id_list)
		# 获取歌曲下载url list
		urls_list = self.get_download_urls_by_ids(songs_id_list)
		# 全部歌曲数目
		total = len(urls_list)
		self.logger.info("play list %s has total %d songs!" % (play_list_name, total))
		self.logger.info(
			"(multi threads,thread_num = %d)Now start download musics of %s(save path is:%s):" % (threads,play_list_name, save_path))

		# 计数器初始化为
		self.no_counter = 0
		threads_list = []
		pack = total // threads
		for i in range(threads):
			begin_index = i * pack
			if i < threads - 1:
				end_index = (i + 1) * pack
			else:
				end_index = total
			urls = urls_list[begin_index:end_index]
			save_list = [os.path.join(save_path, "%s.mp3" % songs_name_and_singer_name_str_list[index])
						 for index in range(begin_index, end_index)]
			t = Thread(target=self._download_list_songs_to_file, args=(urls, save_list, total))
			threads_list.append(t)
		for thread in threads_list:
			thread.start()
		for thread in threads_list:
			thread.join()
		end_time = time.time()
		self.logger.info("Download play list %s(id=%s)'s all %d songs to %s succeed!"
						 "Costs %.2f seconds!" % (play_list_name,play_list_id,
												  total,save_path,(end_time-start_time)))



	def get_singer_id_by_name(self,singer_name,choose_index = 0):
		'''
		通过歌手名字获取歌手id
		:param singer_name: 歌手名
		:param choose_index:选择结果列表第几个结果
		:return:
		'''
		res = self.search(singer_name,type_ = 100).json()
		singer_id = res['result']['artists'][choose_index]["id"]
		return singer_id

	def get_song_id_by_name(self,song_name,condition = 0):
		'''
		通过歌曲名获取歌曲id
		:param song_name: 歌曲名
		:param condition:搜索一个歌曲,可能会返回多个结果,
		condition表示筛选条件,可以选择第几个结果,也可以按照
		歌手进行匹配
		:return:
		'''
		res = self.search(song_name,type_ = 1).json()
		songs = res['result']['songs']
		if isinstance(condition,int):
			if condition > len(songs):
				condition = 0
			return songs[condition]['id']
		# 使用歌手进行匹配
		elif isinstance(condition,str):
			for song in songs:
				artists = song['artists'] # 艺术家列表
				singer_names = [artist['name'] for artist in artists]
				# 如果有匹配的歌手
				if condition in singer_names:
					return song['id']
		# 最后默认返回第一条匹配的结果
		return songs[0]['id']


	def get_lyrics_list_by_id(self,song_id):
		'''
		通过歌曲id 获得歌词
		:param song_id: 歌曲id
		:return: 歌曲歌词
		'''
		lyrics_dict = self.get_lyric(song_id).json()
		lyrics_str = lyrics_dict['lrc']['lyric']
		pattern = r'\[\d+:\d+\.\d+\](.+?\n)'
		lyrics_list = re.findall(pattern,lyrics_str)
		return lyrics_list

	def get_lyrics_list_by_name(self,song_name):
		'''
		通过歌曲名字获取歌词
		:param song_name: 歌曲名字
		:return: 歌曲歌词
		'''
		# 先通过歌曲名得到歌曲id
		song_id = self.get_song_id_by_name(song_name)
		# 再通过歌曲id得到歌词
		return self.get_lyrics_list_by_id(song_id)


		
	def download_singer_hot_songs_by_name(self,singer_name):
		'''
		通过输入歌手名字来下载歌手的全部热门歌曲,单线程实现
		:param singer_name: 歌手名字
		:return:
		'''
		start_time = time.time()
		# 热门歌曲保存地址
		save_path = os.path.join(Constants.SINGER_SAVE_DIR,singer_name,Constants.HOT_SONGS_SAVE_NAME)
		# 根据名字得到歌手id
		uid = self.get_singer_id_by_name(singer_name)
		# 歌手主页地址
		singer_url = "http://music.163.com/artist?id=%d" % uid
		# 歌手全部热门歌曲id list
		hot_songs_ids = Helper.get_singer_hot_songs_ids(singer_url)
		# 通过歌曲id得到下载url
		urls_list = self.get_download_urls_by_ids(hot_songs_ids)
		# 通过歌曲id获得歌曲名
		songs_name_and_singer_name_str_list = self.get_songs_name_and_singer_name_str_list_by_ids_list(hot_songs_ids)
		# 全部热门歌曲数
		total = len(urls_list)
		Helper.mkdir(save_path)
		self.logger.info("%s has total %d hot songs!" %(singer_name,total))
		self.logger.info("(single thread)Now start download hot musics of %s(save path is:%s):" %(singer_name,save_path))
		for index,url in enumerate(urls_list,1):
			try:
				# 下载
				Helper.download_network_resource(url,os.path.join(save_path,"%s.mp3" %songs_name_and_singer_name_str_list[index-1]))
				self.logger.info("Successfully download %d/%d(%s)!" %(index,total,songs_name_and_singer_name_str_list[index-1]))
			except Exception:
				self.logger.info("Fail download %d/%d(%s)!" %(index,total,songs_name_and_singer_name_str_list[index-1]))
				continue
		end_time = time.time()
		self.logger.info("It costs %.2f seconds to download singer %s's %d hot songs to %s "
						 "using single thread!" % ((end_time - start_time),
												   singer_name,total, save_path))

	def download_singer_hot_songs_by_name_with_multi_threading(self, singer_name,threads = 20):
		'''
		通过输入歌手名字来下载歌手的全部热门歌曲,多线程实现
		:param singer_name: 歌手名字
		:param threads: 线程数
		:return:
		'''
		start_time = time.time()
		# 热门歌曲保存地址
		save_path = os.path.join(Constants.SINGER_SAVE_DIR, singer_name, Constants.HOT_SONGS_SAVE_NAME)
		# 根据名字得到歌手id
		uid = self.get_singer_id_by_name(singer_name)
		# 歌手主页地址
		singer_url = "http://music.163.com/artist?id=%d" % uid
		# 歌手全部热门歌曲id list
		hot_songs_ids = Helper.get_singer_hot_songs_ids(singer_url)
		# 通过歌曲id得到下载url
		urls_list = self.get_download_urls_by_ids(hot_songs_ids)
		# 通过歌曲id获得歌曲名
		songs_name_and_singer_name_str_list = self.get_songs_name_and_singer_name_str_list_by_ids_list(hot_songs_ids)
		# 全部热门歌曲数
		total = len(urls_list)
		Helper.mkdir(save_path)
		self.logger.info("%s has total %d hot songs!" % (singer_name, total))
		self.logger.info("(multi threads,thread_num = %d)Now start download hot musics of %s(save path is:%s):"
						 % (threads,singer_name, save_path))
		# 计数器初始化为
		self.no_counter = 0
		threads_list = []
		pack = total // threads
		for i in range(threads):
			begin_index = i * pack
			if i < threads - 1:
				end_index = (i + 1) * pack
			else:
				end_index = total
			urls = urls_list[begin_index:end_index]
			save_list = [os.path.join(save_path,"%s.mp3" % name)
									  for name in songs_name_and_singer_name_str_list[begin_index:end_index]]
			t = Thread(target = self._download_list_songs_to_file,args=(urls,save_list,total))
			threads_list.append(t)
		for thread in threads_list:
			thread.start()
		for thread in threads_list:
			thread.join()
		end_time = time.time()
		self.logger.info("Download %s's %d hot songs to %s succeed!"
						 "Costs %.2f seconds!" %(singer_name,total,save_path,(end_time-start_time)))


	def _download_list_songs_to_file(self,song_urls,save_path_list,total = None):
		'''
		批量通过歌曲的url list 下载歌曲到本地
		:param song_urls: 歌曲 download url list
		:param save_path_list: 歌曲保存地址list
		:return:
		'''
		n = len(song_urls)
		if n != len(save_path_list):
			raise ParamsError("len(song_urls) must be equal to len(save_path_list)!")
		for i in range(n):
			Helper.download_network_resource(song_urls[i],save_path_list[i])
			if total is None:
				self.logger.info("Download %d/%d %s to %s!" %(i+1,n,song_urls[i],save_path_list[i]))
			else:
				# 加锁,更新计数器
				if self.lock.acquire():
					self.no_counter += 1
					self.logger.info("Download %d/%d %s to %s!" %(self.no_counter,total,song_urls[i],save_path_list[i]))
					self.lock.release()



class Response(object):
	"""
	自定义的一个响应类
	"""

	def __init__(self):
		# 响应的内容
		self.content = None
		# 响应头部信息
		self.headers = None
		# 响应的状态码
		self.status_code = None
		# 是否正常标识符
		self.ok = False
		# 错误信息
		self.error = None

	def __repr__(self):
		# 打印 Response
		return '<Response [%s]>' % (self.status_code)

	def raise_for_status(self):
		'''
		如果发生了错误,则raise an error
		:return:
		'''
		if self.error:
			raise self.error

	def get_encoding_from_headers(headers):
		"""
		从http header 得到编码信息
		:param headers: 头部信息(dict)
		"""
		content_type = headers.get('content-type')
		if not content_type:
			return None
		content_type, params = cgi.parse_header(content_type)
		if 'charset' in params:
			# 返回编码信息
			return params['charset'].strip("'\"")
		if 'text' in content_type:
			return 'ISO-8859-1'


	def json(self):
		'''
		如果响应content包含json格式,则解析并返回
		:return:
		'''
		if not self.headers and len(self.content) > 3:
			encoding = self.get_encoding_from_headers(self.headers)
			# encoding 非空
			if encoding is not None:
				try:
					return json.loads(self.content.decode(encoding))
				except:
					# 默认使用utf-8编码
					return json.loads(self.content.decode('utf-8'))
		return json.loads(self.content.decode("utf-8"))






class NetCloudLoginException(Exception):
	'''
	专用于NetCloudLogin 的自定义异常
	'''
	pass


class ParamsError(NetCloudLoginException):
	'''
	参数解析错误的异常
	'''
	pass

class InvalidMethod(NetCloudLoginException):
	'''
	非法的方法异常
	'''
	pass
	
	

