#!/usr/bin/env python
# coding=utf-8
from setuptools import setup

setup(
    name="NetCloud",
    version="1.0.2",
    description='''网易云音乐综合爬虫,可以实现:
                    1.对于网易云音乐评论以及用户信息的爬取,并且可视化展示;
                    2.支持模拟登录,提供包括音乐,歌手,歌单,dj等全方位的api支持''',
    author='lyrichu',
    author_email='lyrichu@foxmail.com',
    url = "http://www.github.com/Lyrichu/NetCloud",
    maintainer='lyrichu',
    maintainer_email='lyrichu@foxmail.com',
    packages=['netcloud.analyse','netcloud.crawler',
              'netcloud.login','netcloud.util',
              'netcloud.demo','netcloud.test'],
    package_data={'netcloud.util': ['source/*']},
    install_requires=[
        'pycrypto',
        'requests',
        'pyecharts',
        'pandas',
        'jieba',
        'wordcloud',
        'scipy'
        ]
)
