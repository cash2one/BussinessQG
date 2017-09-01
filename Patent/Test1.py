#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Test1.py.py
# @Author: Lmm
# @Date  : 2017-08-30
# @Desc  :
import sys
import urllib

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

string = '申请号'
string = unicode(string)
list = []
key = ''
for i, single in enumerate(string):
    temp = '[%s][]{0,}' % single
    key = key + temp

print key