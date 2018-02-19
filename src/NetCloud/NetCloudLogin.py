#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2018-02-19 12:49:59
# @Author  : lyrichu
# @Email   : 919987476@qq.com
# @Link    : http://www.github.com/Lyrichu
# @Version : 0.1
# @Description :
'''
module for NetNease Music login,including getting self info,
user music list etc.
reference:https://github.com/xiyouMc/ncmbot
'''
try:
	from NetCloudCrawler import NetCloudCrawl
	from NetCloudAnalyse import NetCloudAnalyse
except ImportError:
	from .NetCloudCrawler import NetCloudCrawl
	from .NetCloudAnalyse import NetCloudAnalyse
import requests 
import hashlib
import json
import os
from Crypto.Cipher import AES
import base64 
import traceback 
import codecs 

class NetCloudLogin(object):
	"""
	module for logging
	"""
	_METHODS = {
        # logging using cellphone
        'LOGIN': '/weapi/login/cellphone?csrf_token=',
        # logging using email
        'EMAIL_LOGIN': '/weapi/login?csrf_token=',
        # get user info
        'USER_INFO': '/weapi/subcount',
        # get user play list(star list),no need logging
        'USER_PLAY_LIST': '/weapi/user/playlist',
        # get user dj
        'USER_DJ': '/weapi/dj/program/%s',
        # get user follows
        'USER_FOLLOWS': '/weapi/user/getfollows/%s',
        # get user fans
        'USER_FOLLOWEDS': '/weapi/user/getfolloweds/',
        # get user event
        'USER_EVENT': '/weapi/event/get/%s',
        # get user play record
        'USER_RECORD': '/weapi/v1/play/record',
        # get user different events(including shared photos,videos,etc)
        'EVENT': '/weapi/v1/event/get',
        # get user high quality playlist
        'TOP_PLAYLIST_HIGHQUALITY': '/weapi/playlist/highquality/list',
        # get all play list by play list id
        'PLAY_LIST_DETAIL': '/weapi/v3/playlist/detail',
        # get music url by music id
        'MUSIC_URL': '/weapi/song/enhance/player/url',
        # get music lyric by music id
        'LYRIC': '/api/song/lyric?os=osx&id=%s&lv=-1&kv=-1&tv=-1',
        # get music all comments
        'MUSIC_COMMENT': '/weapi/v1/resource/comments/R_SO_4_%s/?csrf_token=',
        # get play list by keywords
        'SEARCH': '/api/search/get/',
        # get album comments
        'ALBUM_COMMENT': '/weapi/v1/resource/comments/R_AL_3_%s/?csrf_token=',
        # show likes on comment
        'LIKE_COMMENT': '/weapi/v1/comment/%s',
        # get music detail by music id
        'SONG_DETAIL': '/weapi/v3/song/detail',
        # get album content
        'ALBUM': '/weapi/v1/album/%s',
        # personal fm(need loggin)
        'PERSONAL_FM': '/weapi/v1/radio/get'
    }

	_HOST = 'http://music.163.com'

	def __init__(self,phone,password,email = None,rememberLogin = True):
		self.method = None
		self.data = {}
		self.params = {}
		self.response = Response()
		self.req = requests.Session()
		self.phone = phone
		self.password = password
		self.email = email
		self.rememberLogin = rememberLogin
		# encrypt params
		self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
		self.nonce = '0CoJUm6Qyw8W8jud'
		self.pubKey = '010001'

	def __repr__(self):
		return '<NCloudBot [%s]>' % (self.method)

	def __setattr__(self, name, value):
		if (name == 'method') and (value):
			if value not in self._METHODS.keys():
				raise InvalidMethod()
		object.__setattr__(self, name, value)

	def createSecretKey(self,size):
		try:
			return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]
		except:
			return (''.join(map(lambda xx: (hex(xx)[2:]), os.urandom(size))))[0:16]

	def aesEncrypt(self,text, secKey):
	    pad = 16 - len(text) % 16
	    if isinstance(text,bytes): # convert text to str
	        text = text.decode("utf-8")
	    text = text + pad * chr(pad)
	    encryptor = AES.new(secKey, 2, '0102030405060708')
	    ciphertext = encryptor.encrypt(text)
	    ciphertext = base64.b64encode(ciphertext)
	    return ciphertext

	def rsaEncrypt(self,text):
	    text = text[::-1]
	    try:
	    	rs = int(text.encode('hex'), 16) ** int(self.pubKey, 16) % int(self.modulus, 16)
	    except:
	    	rs = int(codecs.encode(bytes(text,'utf-8'),'hex_codec'), 16) ** int(self.pubKey, 16) % int(self.modulus, 16)
	    return format(rs, 'x').zfill(256)

	def encrypted_request(self,text):
	    text = json.dumps(text)
	    secKey = self.createSecretKey(16)
	    encText = self.aesEncrypt(self.aesEncrypt(text, self.nonce), secKey)
	    encSecKey = self.rsaEncrypt(secKey)
	    data = {
	        'params': encText,
	        'encSecKey': encSecKey
	    }
	    return data

	def _get_webapi_requests(self):
		"""
		Update headers of webapi for Requests.
		"""
		headers = {
		    'Accept':
		    '*/*',
		    'Accept-Language':
		    'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
		    'Connection':
		    'keep-alive',
		    'Content-Type':
		    'application/x-www-form-urlencoded',
		    'Referer':
		    'http://music.163.com',
		    'Host':
		    'music.163.com',
		    'User-Agent':
		    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
		}
		self.req.headers.update(headers)
		return self.req

	def _get_requests(self):
		headers = {
		    'Referer':
		    self._HOST,
		    'Cookie':
		    'appver=2.0.2;',
		    'Content-Type':
		    'application/x-www-form-urlencoded',
		    'User-Agent':
		    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
		}
		self.req.headers.update(headers)
		return self.req 


	def _build_response(self, resp):
	    """Build internal Response object from given response."""
	    self.response.content = resp.content
	    self.response.status_code = resp.status_code
	    self.response.headers = resp.headers

	def send(self):
		"""Send the request."""
		if self.method is None:
		    raise ParamsError()
		try:
		    if self.method == 'SEARCH':
		        req = self._get_requests()
		        _url = self._HOST + self._METHODS[self.method]
		        resp = req.post(_url, data=self.data)
		        self._build_response(resp)
		        self.response.ok = True
		    else:
		        if isinstance(self.data, dict):
		            data = self.encrypted_request(self.data)
		        req = self._get_webapi_requests()
		        _url = self._HOST + self._METHODS[self.method]
		        if self.method in ('USER_DJ', 'USER_FOLLOWS', 'USER_EVENT'):
		            _url = _url % self.params['uid']
		        if self.method in ('LYRIC','MUSIC_COMMENT'):
		            _url = _url % self.params['id']

		        if self.method in ('LYRIC'):
		            resp = req.get(_url)
		        else:
		            resp = req.post(_url, data=data)
		        self._build_response(resp)
		        self.response.ok = True
		except Exception as why:
		    traceback.print_exc()
		    print('Requests Exception', why)
		    self.response.error = why

	def login(self):
	    """ 
	    interface for logging，return :class:'Response' object
	    """
	    if (self.phone is None) and (self.email is None):
	        raise ParamsError()
	    if self.password is None:
	        raise ParamsError()
	    md5 = hashlib.md5()
	    md5.update(self.password.encode("utf-8"))
	    password = md5.hexdigest()
	    self.data = {'password': password, 'rememberLogin': self.rememberLogin}
	    if self.phone is not None:
	        self.data['phone'] = self.phone
	        self.method = 'LOGIN'
	    else:
	        self.data['username'] = self.email
	        self.method = 'EMAIL_LOGIN'
	    self.send()
	    return self.response

	def get_user_play_list(self,uid,offset=0,limit=1000):
		"""
		get user play list
		:param uid: user id,you can get it through logging or other method
		:param offset: (optional) the start position，default is 0
		:param limit: (optional) the limited lines count,defualt is 1000
		"""
		if uid is None:
		    raise ParamsError()
		self.method = 'USER_PLAY_LIST'
		self.data = {'offset': offset, 'uid': uid, 'limit': limit, 'csrf_token': ''}
		self.send()
		return self.response

	def get_self_play_list(self,offset=0,limit=1000):
		'''
		get self play list
		'''
		response = self.login()
		my_uid =response.json()['account']['id']
		return self.get_user_play_list(my_uid,offset,limit)

	def get_user_dj(self,uid, offset=0, limit=30):
		"""
		get user dj data
		:param uid: user id
		:param offset: (optional) the start position，default is 0
		:param limit: (optional) the limited lines count,defualt is 30
		"""
		if uid is None:
		    raise ParamsError()
		self.method = 'USER_DJ'
		self.data = {'offset': offset, 'limit': limit, "csrf_token": ""}
		self.params = {'uid': uid}
		self.send()
		return self.response

	def get_self_dj(self,offset=0, limit=30):
		'''
		get self dj
		'''
		response = self.login()
		my_uid =response.json()['account']['id']
		return self.get_user_dj(my_uid,offset,limit)

	def search(self,keyword,type_=1, offset=0, limit=30):
		"""
		search music info,support search music,singer,album etc. 
		:param keyword: search keyword
		:param type_: (optional) search type，1: single music, 100: singer, 1000: music play list, 1002: user
		:param offset: (optional) the start position，default is 0
		:param limit: (optional) the limited lines count,defualt is 30
		"""
		if keyword is None:
		    raise ParamsError()
		self.method = 'SEARCH'
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
		get user follows list
		:param uid: user id
		:param offset: (optional) the start position，default is 0
		:param limit: (optional) the limited lines count,defualt is 30
		"""
		if uid is None:
		    raise ParamsError()
		self.method = 'USER_FOLLOWS'
		self.params = {'uid': uid}
		self.data = {'offset': offset, 'limit': limit, 'order': True}
		self.send()
		return self.response

	def get_self_follows(self, offset=0, limit=30):
		'''
		get self follows list
		'''
		response = self.login()
		my_uid =response.json()['account']['id']
		return self.get_user_follows(my_uid,offset,limit)


	def get_user_fans(self,uid, offset=0, limit=30):
		"""
		get user fans list
		:param uid: user id
		:param offset: (optional) the start position，default is 0
		:param limit: (optional) the limited lines count,defualt is 30
		"""
		if uid is None:
		    raise ParamsError()
		self.method = 'USER_FOLLOWEDS'
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
		get self fans list
		'''
		response = self.login()
		my_uid =response.json()['account']['id']
		return self.get_user_fans(my_uid,offset,limit)

	def get_user_event(self,uid):
		"""
		get user event
		:param uid: user id
		"""
		if uid is None:
		    raise ParamsError()
		self.method = 'USER_EVENT'
		self.params = {'uid': uid}
		self.data = {'time': -1, 'getcounts': True, "csrf_token": ""}
		self.send()
		return self.response

	def get_self_event(self):
		response = self.login()
		my_uid =response.json()['account']['id']
		return self.get_user_event(my_uid)

	def get_user_record(self,uid, type_=0):
		"""
		get user play record list,logging is necessary
		:param uid: user id
		:param type_: (optional) data type，0：all datas，1： week data
		"""
		if uid is None:
		    raise ParamsError()
		self.method = 'USER_RECORD'
		self.data = {'type': type_, 'uid': uid, "csrf_token": ""}
		self.send()
		return self.response

	def get_self_record(self,type_ = 0):
		'''
		get self record
		'''
		response = self.login()
		my_uid =response.json()['account']['id']
		return self.get_user_record(uid = my_uid,type_ = type_)



	def get_friends_event(self):
		"""
		get friends(following people) event
		"""
		self.method = 'EVENT'
		self.data = {"csrf_token": ""}
		self.send()
		return self.response



	def get_top_playlist_highquality(self,cat='全部', offset=0, limit=20):
		"""
		get high quality play list
		:param cat: (optional) music play list type，default is ‘全部’，others like 华语、欧美 etc. 
		:param offset: (optional) the start position，default is 0
		:param limit: (optional) limited lines count,default is 200
		"""
		self.method = 'TOP_PLAYLIST_HIGHQUALITY'
		self.data = {'cat': cat, 'offset': offset, 'limit': limit}
		self.send()
		return self.response



	def get_play_list_detail(self,id, limit=20):
		"""
		get all detail music list of play list by play list id
		:param id: play list id
		:param limit: (optional) limited lines count
		"""
		if id is None:
		    raise ParamsError()
		self.method = 'PLAY_LIST_DETAIL'
		self.data = {'id': id, 'limit': limit, "csrf_token": ""}
		self.send()
		return self.response



	def get_music_download_url(self,ids=[]):
		"""
		get music download url by music id
		:param ids: music ids list 
		"""
		if not isinstance(ids, list):
		    raise ParamsError()
		self.method = 'MUSIC_URL'
		self.data = {'ids': ids, 'br': 999000, "csrf_token": ""}
		self.send()
		return self.response

	def get_lyric(self,id):
		"""
		get music lyric by music id
		:param id: music id
		"""
		if id is None:
		    raise ParamsError()
		self.method = 'LYRIC'
		self.params = {'id': id}
		self.send()
		return self.response


	def get_music_comments(self,id, offset=0, limit=20):
		"""
		get music all comments
		:param id: music id
		:param offset: (optional) the start position
		:param limit: (optional) the limited lines count
		"""
		if id is None:
		    raise ParamsError()
		self.method = 'MUSIC_COMMENT'
		self.params = {'id': id}
		self.data = {'offset': offset, 'limit': limit, 'rid': id,"csrf_token": ""}
		self.send()
		return self.response


	def get_album_comments(self,id, offset=0, limit=20):
		'''
		get album comments
		'''
		if id is None:
		    raise ParamsError()
		self.method = 'ALBUM_COMMENT'
		self.params = {'id': id}
		self.data = {'offset': offset, 'limit': limit, 'rid': id, "csrf_token": ""}
		self.send()
		return self.response



	def get_songs_detail(self,ids):
		"""
		get music detail info
		:param ids: music ids list
		"""
		if not isinstance(ids, list):
		    raise ParamsError()
		c = []
		for id in ids:
		    c.append({'id': id})
		self.method = 'SONG_DETAIL'
		self.data = {'c': json.dumps(c), 'ids': c, "csrf_token": ""}
		self.send()
		return self.response



	def get_self_fm(self):
		""" 
		get self fm
		"""
		self.method = 'PERSONAL_FM'
		self.data = {"csrf_token": ""}
		self.send()
		return self.response

	def pretty_print_self_info(self):
		info_dict = self.login().json()
		avatarUrl = info_dict['profile']['avatarUrl']
		signature = info_dict['profile']['signature']
		nickname = info_dict['profile']['nickname']
		userName = info_dict['account']['userName']
		province_id = info_dict['profile']['province']
		birthday_no = info_dict['profile']['birthday']
		if birthday_no < 0:
			birthday = "unknown"
		else:
			from_timestamp_to_date = NetCloudAnalyse(song_name = "",singer_name = "").from_timestamp_to_date
			birthday = from_timestamp_to_date(time_stamp = birthday_no*0.001,format = "%Y-%m-%d")
		description = info_dict['profile']['description']
		if info_dict['profile']['gender'] == 1:
			gender = 'male'
		elif info_dict['profile']['gender'] == 0:
			gender = 'female'
		else:
			gender = 'unknown'
		userId = info_dict['profile']['userId']
		cellphone = json.loads(info_dict['bindings'][0]['tokenJsonStr'])['cellphone']
		email = json.loads(info_dict['bindings'][1]['tokenJsonStr'])['email']
		print("Hello,{nickname}!\nHere is your personal info:".format(nickname = nickname))
		print("avatarUrl:{avatarUrl}\nsignature:{signature}\n"
				"nickname:{nickname}\n"
				"userName:{userName}\nprovince_id:{province_id}\n"
				"birthday:{birthday}\ndescription:{description}\n"
				"gender:{gender}\nuserId:{userId}\n"
				"cellphone:{cellphone}\nemail:{email}\n".format(
					avatarUrl = avatarUrl,
					signature = signature,
					nickname = nickname,
					userName = userName,
					province_id = province_id,
					birthday = birthday,
					description = description,
					gender = gender,
					userId = userId,
					cellphone = cellphone,
					email = email
					)
				)
	def pretty_print_user_play_list(self,uid,offset = 0,limit = 1000):
		play_list = self.get_user_play_list(uid,offset,limit).json()
		num = len(play_list['playlist'])
		print("UserId {UserId} has total {total} play list!".format(UserId = uid,total = num))
		from_timestamp_to_date = NetCloudAnalyse(song_name = "",singer_name = "").from_timestamp_to_date
		for i in range(num):
			playlist_dict = play_list['playlist'][i]
			print("-"*20," play list {index} ".format(index = i+1),"-"*20)
			createTime = from_timestamp_to_date(playlist_dict['createTime']*0.001,format = "%Y-%m-%d")
			updateTime = from_timestamp_to_date(playlist_dict['updateTime']*0.001,format = "%Y-%m-%d")
			tags_str = ",".join(playlist_dict['tags'])
			description = playlist_dict['description']
			coverImgUrl = playlist_dict['coverImgUrl']
			creator_user_id = playlist_dict['userId']
			creator_user_nickname = playlist_dict['creator']['nickname']
			creator_user_gender = playlist_dict['creator']['gender']
			if creator_user_gender == 1:
				creator_user_gender = "male"
			elif creator_user_gender == 0:
				creator_user_gender = "female"
			else:
				creator_user_gender = "unknown"
			creator_user_signature = playlist_dict['creator']['signature']
			creator_user_descrition = playlist_dict['creator']['description']
			creator_user_detailDescription = playlist_dict['creator']['detailDescription']
			creator_user_city_no = playlist_dict['creator']['city']
			creator_user_avatarUrl = playlist_dict['creator']['avatarUrl']
			creator_user_province_no = playlist_dict['creator']['province']
			backgroundUrl = playlist_dict['creator']['backgroundUrl']
			creator_user_birthday_no = playlist_dict['creator']['birthday']
			if creator_user_birthday_no < 0:
				creator_user_birthday = "unknown"
			else:
				creator_user_birthday = from_timestamp_to_date(creator_user_birthday_no*0.001,format = "%Y-%m-%d")
			artists = playlist_dict['artists']
			playlist_name = playlist_dict['name']
			highQuality = playlist_dict['highQuality']
			playlist_id = playlist_dict['id']
			playCount = playlist_dict['playCount']
			anonimous = playlist_dict['anonimous']
			music_count = playlist_dict['trackCount']
			print("play list name:{playlist_name}\ntags:{tags_str}\n"
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
						playlist_name = playlist_name,tags_str = tags_str,
						highQuality = highQuality,description = description,
						coverImgUrl = coverImgUrl,
						createTime = createTime,updateTime = updateTime,
						playlist_id = playlist_id,playCount = playCount,
						music_count = music_count,anonimous = anonimous,
						creator_user_id = creator_user_id,creator_user_nickname = creator_user_nickname,
						creator_user_gender = creator_user_gender,creator_user_signature = creator_user_signature,
						creator_user_descrition = creator_user_descrition,creator_user_detailDescription = creator_user_detailDescription,
						creator_user_province_no = creator_user_province_no,
						creator_user_city_no = creator_user_city_no,
						creator_user_avatarUrl = creator_user_avatarUrl,
						backgroundUrl = backgroundUrl,
						creator_user_birthday = creator_user_birthday,
						artists = artists
						)
					)
	def pretty_print_self_play_list(self,offset = 0,limit = 1000):
		response = self.login()
		my_uid =response.json()['account']['id']
		print("Your play list info is here:")
		self.pretty_print_user_play_list(my_uid,offset,limit)

	def _test_login(self):
		response = self.login()
		print(response.json())

	def _test_get_user_play_list(self):
		uid = 103413749
		response = self.get_user_play_list(uid)
		print(response.json())

	def _test_get_self_play_list(self):
		response = self.get_self_play_list()
		print(response.json())

	def _test_get_user_dj(self):
		uid = 103413749
		response = self.get_user_dj(uid)
		print(response.json())

	def _test_get_self_dj(self):
		response = self.get_self_dj()
		print(response.json())

	def _test_search(self):
		keyword = "周杰伦"
		type_ = 1002
		offset = 0
		limit = 30
		response = self.search(keyword = keyword,type_ = type_,offset = offset,limit = limit)
		print(response.json())

	def _test_get_user_follows(self):
		uid = 103413749
		offset = 0
		limit = 50
		response = self.get_user_follows(uid = uid,offset = offset,limit = limit)
		print(response.json())

	def _test_get_self_follows(self):
		response = self.get_me_follows()
		print(response.json())

	def _test_get_user_fans(self):
		uid = 103413749
		response = self.get_user_fans(uid = uid)
		print(response.json())

	def _test_get_self_fans(self):
		response = self.get_self_fans()
		print(response.json())

	def _test_get_user_event(self):
		uid = 82133317
		response = self.get_user_event(uid = uid)
		print(response.json())

	def _test_get_self_event(self):
		response = self.get_self_event()
		print(response.json())

	def _test_get_user_record(self):
		uid = 82133317
		type_ = 0 # all datas
		response = self.get_user_record(uid = uid,type_ = type_)
		print(response.json())

	def _test_get_self_record(self):
		response = self.get_self_record()
		print(response.json())

	def _test_get_friends_event(self):
		response = self.get_friends_event()
		print(response.json())

	def _test_get_top_playlist_highquality(self):
		response = self.get_top_playlist_highquality()
		print(response.json())

	def _test_get_play_list_detail(self):
		play_list_id = 92259156
		limit = 100
		response = self.get_play_list_detail(id = play_list_id,limit = limit)
		print(response.json())

	def _test_get_music_download_url(self):
		ids = [526464293]
		response = self.get_music_download_url(ids = ids)
		print(response.json())

	def _test_get_lyric(self):
		music_id = 526464293
		response = self.get_lyric(id = music_id)
		print(response.json())

	def _test_get_music_comments(self):
		music_id = 526464293
		offset = 0
		limit = 100
		response = self.get_music_comments(id = music_id,offset = offset,limit = limit)
		print(response.json())

	def _test_get_album_comments(self):
		album_id = 2975328
		offset = 0
		limit = 20
		response = self.get_album_comments(id = album_id,offset = offset,limit = limit)
		print(response.json())

	def _test_get_songs_detail(self):
		ids = [526464293]
		response = self.get_songs_detail(ids = ids)
		print(response.json())

	def _test_get_self_fm(self):
		response = self.get_self_fm()
		print(response.json())

	def _test_pretty_print_self_info(self):
		self.pretty_print_self_info()

	def _test_pretty_print_user_play_list(self):
		uid = 103413749
		self.pretty_print_user_play_list(uid = uid)

	def _test_pretty_print_self_play_list(self):
		self.pretty_print_self_play_list()

class Response(object):
    """
    The :class:`Response` object. All :class:`NetCloudLogin` objects contain a 
    :class:`NetCloudLogin.response <response>` attribute.
    """

    def __init__(self):
        self.content = None
        self.headers = None
        self.status_code = None
        self.ok = False
        self.error = None

    def __repr__(self):
        return '<Response [%s]>' % (self.status_code)

    def raise_for_status(self):
        if self.error:
            raise self.error

    def get_encoding_from_headers(headers):
	    """
	    Returns encodings from given HTTP Header Dict.
	    :param headers: dictionary to extract encoding from.
	    """
	    content_type = headers.get('content-type')
	    if not content_type:
	        return None
	    content_type, params = cgi.parse_header(content_type)
	    if 'charset' in params:
	        return params['charset'].strip("'\"")
	    if 'text' in content_type:
	    	return 'ISO-8859-1'


    def json(self):
        """Returns the json-encoded content of a response, if any."""
        if not self.headers and len(self.content) > 3:
            encoding = self.get_encoding_from_headers(self.headers)
            if encoding is not None:
                return json.loads(self.content.decode(encoding))
        return json.loads(self.content.decode("utf-8"))






class NetCloudLoginException(Exception):
    """ Exception for NetCloudLogin"""
    pass


class ParamsError(NetCloudLoginException):
    """Exception for parameters error """
    pass

class InvalidMethod(NetCloudLoginException):
	""" Exception for invalid method calling"""
	pass
	
	
# if __name__ == '__main__':
# 	phone = 'xxxxxxxxxxx'
# 	password = 'xxx'
# 	email = None
# 	rememberLogin = True
# 	login = NetCloudLogin(phone = phone,password = password,email = email,rememberLogin = rememberLogin)
# 	login._test_login()
# 	login._test_get_user_play_list()
# 	login._test_get_self_play_list()
# 	login._test_get_user_dj()
# 	login._test_get_self_dj()
# 	login._test_search()
# 	login._test_get_user_follows()
# 	login._test_get_self_follows()
# 	login._test_get_user_fans()
# 	login._test_get_self_fans()
# 	login._test_get_user_event()
# 	login._test_get_self_event()
# 	login._test_get_user_record()
# 	login._test_get_self_record()
# 	login._test_get_friends_event()
# 	login._test_get_top_playlist_highquality()
# 	login._test_get_play_list_detail()
# 	login._test_get_music_download_url()
# 	login._test_get_lyric()
# 	login._test_get_music_comments()
# 	login._test_get_album_comments()
# 	login._test_get_songs_detail()
# 	login._test_get_self_fm()
# 	login._test_pretty_print_self_info()
# 	login._test_pretty_print_user_play_list()
# 	login._test_pretty_print_self_play_list()
