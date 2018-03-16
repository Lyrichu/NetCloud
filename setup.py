#!/usr/bin/env python
# coding=utf-8
from setuptools import setup

setup(
    name="NetCloud",
    version="0.0.3",
    description='''Netease Cloud Music comments spider,you can use it to crawl all comments of 
a song,and also you can crawl the users info,download the music,login to get yourself and other
people's info and activities,and almost anything about NetEase Cloud Music! With all this content,you can
do some interesting analyse like view the keywords of comments,the location distribution
of commenters,the age distribution etc. The class NetCloudCrawler does the job of crawler
comments,and the class NetCloudAnalyse does the job of analyse of comments and users'
info,the NetCloudLogin class does the job of something with login.''',
    author='lyrichu',
    author_email='919987476@qq.com',
    url = "http://www.github.com/Lyrichu/NetCloud",
    maintainer='lyrichu',
    maintainer_email='919987476@qq.com',
    packages=['NetCloud'],
    package_dir={'NetCloud': 'src/NetCloud'},
    package_data={'NetCloud': ['source/*']},
    install_requires=[
        'pycrypto',
        'requests',
        'pyecharts',
        'pandas',
        'jieba',
        'wordcloud',
        'scipy',
        ]
)
