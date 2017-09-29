#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Test1.py.py
# @Author: Lmm
# @Date  : 2017-08-30
# @Desc  :协程测试
import sys
import urllib
import gevent

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# from lxml import etree
# string = u'<div class="item-content-body left"><p><b>申请号 : </b>CN201280070343.4</p></div>'
# data = etree.HTML(string)
# str = u'申请号'
# list = data.xpath(".//p[contains(text(),%s)]/text()"%str)
# print list[0]
# print etree.tostring(list)

# string = '申请号'
# string = unicode(string)
# list = []
# key = ''
# for i, single in enumerate(string):
#     temp = '[%s][]{0,}' % single
#     key = key + temp
#
# print key

import gevent
import requests
import time
import random


# from gevent import monkey; monkey.patch_all()
# import gevent
# import urllib2
# i = 1
# from gevent import monkey
# import gevent
# import time
# import requests
# monkey.patch_all()
# #对比得出 协程 运行出的更快
# #IO阻塞 自动切换任务。。
# def say(url):
#     print('get url',url)
#     resp = requests.get(url)
#     data = resp.content
#     print(len(data),url)
# t1_start = time.time()
# say('http://www.xiaohuar.com/')
# say('http://www.oldboyedu.com/')
# say('http://weibo.com/MMbdzx?from=myfollow_all&is_all=1#_rnd1482040021384')
# print("普通--time cost",time.time() - t1_start)
#
# t2_stat = time.time()
# gevent.joinall(
#     [gevent.spawn(say,'http://www.xiaohuar.com/'),
#      gevent.spawn(say,'http://www.oldboyedu.com/'),
#      gevent.spawn(say,'http://weibo.com/MMbdzx?from=myfollow_all&is_all=1#_rnd1482040021384')]
# )
# print("gevent---time cost",time.time() - t2_stat)