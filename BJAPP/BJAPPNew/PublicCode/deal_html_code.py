#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deal_html_code.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 常用的几个html处理方法，其中时间戳转换只能处理11以下的时间戳
import re
import sys
import time
import config
import datetime
from lxml import etree
import decimal
import operator

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


# 一次性去除制表符，换行符,标签
def remove_symbol(string):
	if string == '' or string == None or string == ' ':
		string = None
	else:
		string = re.sub('\s', '', string)
		pattetn = re.compile(u'&nbsp')
		string = pattetn.sub('', string)
		pattern = re.compile(r'<[^>]+>', re.S)
		string = pattern.sub('', string)
		string = re.sub(' ', '', string)
		string = string.replace("\xc2\xa0", "")
	return string


# 用于去处空格和换行符
def remove_space(string):
	string = re.sub('\s', '', string)
	pattetn = re.compile(u'&nbsp')
	string = pattetn.sub('', string)
	string = string.replace("\xc2\xa0", "")
	return string


def get_before_date():
	now = time.time()
	n = 30
	before = now - n * 24 * 3600  # 可以改变n 的值计算n天前的
	# date = time.strftime("%Y-%m-%d %H:%M:%S ",  time.localtime(now))
	beforeDate = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime(before))
	return beforeDate


# 用来匹配链接
def match_href(data):
	onclick = data.xpath('./@onclick')[0]
	pattern = re.compile(".*href='(.*?)'")
	# 匹配链接
	href = config.host + re.findall(pattern, onclick)[0]
	return href


def match_id(data):
	pattern = re.compile(".*id=(.*)&.*")
	id = re.findall(pattern, data)[0]
	return id


def match_entid(url):
	pattern = re.compile(".*id=(.*)&.*")
	entid = re.findall(pattern, url)[0]
	return entid


def match_cid(url):
	pattern = re.compile(".*cid=(.*)&.*")
	entid = re.findall(pattern, url)[0]
	return entid


# 计算两个字符串之间的时间差
def caltime(date1, date2):
	date1 = time.strptime(date1, "%Y-%m-%d")
	date2 = time.strptime(date2, "%Y-%m-%d")
	date1 = datetime.datetime(date1[0], date1[1], date1[2])
	date2 = datetime.datetime(date2[0], date2[1], date2[2])
	intervel = (date2 - date1).days
	return intervel


# 用于匹配字符按串中的浮点型数据
def match_finger(finger):
	pattern = re.compile(u"-?([1-9]\d*|[1-9]\d*\.\d*|0\.\d*[1-9]\d*|0?\.0+|0)")
	finger = re.findall(pattern, finger)
	finger = decimal.Decimal(finger[0])
	return finger


# 用于字典去重
def remove_repeat(info):
	items = list(info.values())
	items.sort(key=operator.itemgetter(1))
	i = 0
	while i < len(items) - 2:
		j = i + 1
		if items[i] == items[j]:
			items.remove(items[j])
		else:
			i = j
	#
	list = xrange(len(items))
	dictionary = dict(zip(list, items))
	return dictionary
