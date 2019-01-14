#!/usr/bin/env python3
# encoding: utf-8
"""
@version: 0.1
@author: lyrichu
@license: Apache Licence 
@contact: 919987476@qq.com
@site: http://www.github.com/Lyrichu
@file: Helper.py
@time: 2019/01/05 20:00
@description:
通用工具类
"""
import base64
import codecs
import json
import logging

import os
import socket
import xml.dom.minidom as xmldom
import jieba
import re
import requests
import time
from Crypto.Cipher import AES
from urllib.request import urlretrieve
from netcloud.util import Constants

LOGGER = None # 全局变量

def get_logger():
    '''
    返回一个logger,同时输出到终端与日志文件
    :return:logger
    '''
    global LOGGER
    # 这里的判断是为了防止重复生成logger对象,这会导致同一条日志多次打印
    if LOGGER:
        return LOGGER
    log_file = Constants.LOGGER_FILEPATH
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.DEBUG)
    # 日志输出格式
    log_formatter = logging.Formatter(
        "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
    )
    # 创建一个handler,用于将日志输出到终端
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)

    # 创建一个handler,用于将日志输出到文件
    # 日志追加
    file_handler = logging.FileHandler(log_file,"a")
    file_handler.setFormatter(log_formatter)

    # 添加handler
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    LOGGER = logger
    return logger


def get_params(page):
    '''
    利用解密函数获得请求的必要参数
    :param page:评论页数
    '''
    first_key = Constants.REQUEST_FOURTH_PARAM
    second_key = 16 * 'F'
    iv = "0102030405060708"
    if page == 1:  # if it's the first page
        first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
        h_encText = AES_encrypt(first_param, first_key, iv)
    else:
        offset = str((page - 1) * 20)
        first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' % (offset, 'false')
        h_encText = AES_encrypt(first_param, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText

def AES_encrypt(text, key, iv):
    '''
    核心解密函数
    '''
    pad = 16 - len(text) % 16
    if isinstance(text,bytes): # convert text to str
        text = text.decode("utf-8")
    text += pad*chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text

def get_json(url,params):
    '''
    获取服务器返回的json格式的数据
    '''
    data = {
         "params": params,
         "encSecKey": Constants.REQUEST_ENCSECKEY
    }
    response = requests.post(
        url,
        headers = Constants.REQUEST_HEADERS,
        data = data,
        proxies = Constants.PROXIES
    )
    return response.content


def createSecretKey(size):
    try:
        return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]
    except:
        return (''.join(map(lambda xx: (hex(xx)[2:]), os.urandom(size))))[0:16]


def aesEncrypt(text,secKey):
    pad = 16 - len(text) % 16
    if isinstance(text, bytes):  # convert text to str
        text = text.decode("utf-8")
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey,2,'0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def rsaEncrypt(text):
    text = text[::-1]
    try:
        rs = int(text.encode('hex'), 16) ** int(Constants.PUBKEY, 16) % int(Constants.REQUEST_MODULUS, 16)
    except:
        rs = int(codecs.encode(bytes(text, 'utf-8'), 'hex_codec'), 16) ** int(Constants.PUBKEY, 16) % int(Constants.REQUEST_MODULUS, 16)
    return format(rs, 'x').zfill(256)


def encrypted_request(text):
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text,Constants.NONCE), secKey)
    encSecKey = rsaEncrypt(secKey)
    data = {
        'params': encText,
        'encSecKey': encSecKey
    }
    return data

def mkdir(path):
    '''
    如果路径不存在,则创建之
    :param path: 输入路径
    :return:None
    '''
    if not os.path.exists(path):
        os.makedirs(path)




def save_lines_to_file(lines,filename,mode = "w"):
    '''
    将list(str) 保存到磁盘
    '''
    with open(filename,mode,encoding='utf-8') as f:
        # 如果str结尾没有'\n',则添加一个
        for line in lines:
            if not line.endswith("\n"):
                line += "\n"
            f.write(line)


def load_file_format_json(comments_file_path):
    '''
    从磁盘加载json格式文件(each line is json format)
    @return:list(dict)
    '''
    comments_list = []
    with open(comments_file_path,"r") as f:
        for json_line in f:
            comments_list.append(json.loads(json_line.strip()))
    return comments_list

def from_timestamp_to_date(time_stamp,format = "%Y-%m-%d %H:%M:%S"):
    '''
    将时间戳转化为日期格式
    :param time_stamp: 时间戳
    :param format:指定日期格式
    '''
    real_date = time.strftime(format,time.localtime(time_stamp))
    return real_date

def get_current_file_abs_path():
    '''
    获取当前文件的绝对路径
    :return:
    '''
    return os.path.abspath(os.path.dirname(__file__))

def cut_text(text):
    '''
    基本的jieba 分词
    :param text: 原始字符串
    :return:
    '''
    return jieba.cut(text)


def load_stopwords():
    '''
    加载停用词
    '''
    stopwords_path = Constants.STOPWORDS_PATH
    with open(stopwords_path,"r",encoding = "utf-8") as f:
        stopwords = f.readlines()
    stopwords = [word.strip() for word in stopwords]
    return set(stopwords)

def load_all_cities():
    '''
    从磁盘加载全部的城市list
    '''
    province_cities_file = Constants.PROVINCE_CITIES_JSON_PATH
    all_cities = []
    with open(province_cities_file,"r",encoding = "utf-8") as fin:
        content = fin.read()
        d = json.loads(content)
        for province in d:
            for city in province['city']:
                all_cities.append(city['name'])
    return all_cities

def load_echarts_support_cities():
    '''
    加载pyecharts 目前支持的city list
    :return: list(str)
    '''
    with open(Constants.ECHARTS_SUPPORT_CITIES_JSON_PATH,"r",encoding="utf-8") as fin:
        content = fin.read()
        json_dict = json.loads(content)
    return set(json_dict.keys())


def check_file_exits_and_overwrite(file_path):
    # 如果文件已经存在,则覆盖之
    if os.path.exists(file_path):
        get_logger().warning("%s already exits!Now we will overwrite it!" % file_path)
        # 删除
        os.remove(file_path)


def get_singer_hot_songs_ids(singer_url):
    '''
    获取歌手全部id list
    :param singer_url: 歌手主页url
    '''
    ids_list = []
    html = requests.get(
        singer_url,headers = Constants.REQUEST_HEADERS,
        proxies = Constants.PROXIES).text
    pattern = re.compile(r'<a href="/song\?id=(\d+?)">.*?</a>')
    ids = re.findall(pattern,html)
    for id in ids:
        ids_list.append(id)
    return ids_list


def download_network_resource(url,save_path):
    '''
    从网络下载资源,保存到指定的位置
    :param url: 下载链接
    :param save_path: 保存位置
    :return:
    '''
    socket.setdefaulttimeout(Constants.MAX_TIMEOUT) # 下载歌曲最大超时时间(s)
    try:
        urlretrieve(url,save_path)
    except socket.timeout:
        get_logger().info("Download %s to %s socket timeout(max timeout = %d s)!" %(url,save_path,Constants.MAX_TIMEOUT))
    except Exception as e:
        get_logger().error("Download %s to %s error:%s" %(url,save_path,e))


def _parse_config_xml():
    '''
    解析配置xml文件
    :param config_xml:
    :return:dict
    '''
    config_dict = {
        "phone":None,
        "password":None,
        "email":None,
        "rememberLogin":None,
        "saveRootDir":None
    }
    try:
        dom = xmldom.parse(Constants.USER_CONFIG_FILE_PATH)
        for key in config_dict.keys():
            firstChild = dom.getElementsByTagName(key)[0].firstChild
            if firstChild:
                config_dict[key] = firstChild.data
    except Exception as e:
        get_logger().info("Parse config file %s failed:%s" %(Constants.USER_CONFIG_FILE_PATH,e))

    return config_dict

def get_save_root_dir():
    # 加载配置文件,得到文件保存地址
    save_root_dir = _parse_config_xml()["saveRootDir"]
    # 如果配置文件没有配置文件保存路径,则使用默认路径
    if save_root_dir is None:
        save_root_dir = Constants.DEFAULT_SAVE_ROOT_DIR
    return save_root_dir





