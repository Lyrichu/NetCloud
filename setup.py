#!/usr/bin/env python
# coding=utf-8
from setuptools import setup

setup(
    name="NetCloud",
    version="0.0.2",
    description='''Netease Cloud Music comments spider,you can use it to crawl all comments of 
a song,and also you can crawl the users info. With all this content,you can
do some interesting analyse like view the keywords of comments,the location distribution
of commenters,the age distribution etc. The class NetCloudCrawler does the job of crawler
comments,and the other class NetCloudAnalyse does the job of analyse of comments and users'
info. ''',
    author='lyrichu',
    author_email='919987476@qq.com',
    url = "http://www.github.com/Lyrichu",
    maintainer='lyrichu',
    maintainer_email='919987476@qq.com',
    packages=['NetCloud'],
    package_dir={'NetCloud': 'src/NetCloud'},
    package_data={'NetCloud': ['source/*']},
    # data_files=[('Lib/site-packages/NetCloud_src',['README.rst','requirements.txt','source/JayChou.jpg','source/simsun.ttc','source/stopwords.txt','source/province_cities.json'])
    #             ],
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
