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
import decimal
import traceback
import logging

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


# 把时间戳转换为0000-00-00类型,十二位以上的时间戳不做处理
def change_date_style(old_date):
	if old_date == '' or old_date == None:
		new_date = '0000-00-00'
	elif len(str(old_date / 1000)) >= 12:
		new_date = '9999-12-31'
	else:
		new_date = time.localtime(old_date / 1000)
		otherStyleTime = time.strftime('%Y-%m-%d ', new_date)
		new_date = otherStyleTime
	return new_date


# 计算时间差
def caculate_time(now_date, old_date):
	# 转化为时间数组
	timearray = time.strptime(old_date, "%Y-%m-%d %H:%M:%S")
	# 转换时间为时间戳
	change_time = time.mktime(timearray)
	interval = float(now_date) - float(change_time)
	return interval


# 判断省份
def judge_province(code):
	pattern = re.compile(r'^9.*')
	temp = re.findall(pattern, code)
	if len(temp) == 0:
		provin = config.province[code[0:2]]
	else:
		provin = config.province[code[2:4]]
	return provin


# 一次性去除制表符，换行符,标签
def remove_symbol(string):
	if string == '' or string == None or string == ' ':
		string = ''
	else:
		string = re.sub('\s', '', string)
		pattetn = re.compile(u'&nbsp')
		string = pattetn.sub('', string)
		pattern = re.compile(r'<[^>]+>', re.S)
		string = pattern.sub('', string)
	return string


# 对中文日期进行处理
def change_chinese_date(date):
	if date == '' or date == None or date == ' ':
		date = '0000-00-00'
	else:
		date = re.sub(re.compile(u'年|月'), '-', date)
		date = re.sub(re.compile(u'日'), '', date)
	return date


# 用于获得一个月以前的时间
def get_before_date():
	now = time.time()
	n = 30
	before = now - n * 24 * 3600  # 可以改变n 的值计算n天前的
	# date = time.strftime("%Y-%m-%d %H:%M:%S ",  time.localtime(now))
	beforeDate = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime(before))
	return beforeDate


# 用于根据字符串对查找包含某个字符串的内容的标签，并进行处理
def deal_td_content(string, data):
	try:
		td = data.xpath(".//tr[contains(text(),'%s')]" % string)
		td = td[0]
		flag = 0
	except Exception, e:
		flag = 1
		print '获取%s中出错！' % string
	finally:
		return flag


# 用于根据指定路径下字符串查找包含该字符串的内容并标签中的内容做处理
def get_match_info(string, data):
	try:
		content = data.xpath(".//td[contains(.,'%s')]" % string)
		content = content[0]
		content = remove_symbol(content.xpath("string(.)"))
		content = content.split("：")[-1]
	except Exception, e:
		content = ''
	finally:
		
		return content


# 用于根据字符串内容寻找包含指定内容的最近节点
# 陕西各个分项页的内容保存在p标签里
def match_info(string, data):
	try:
		content = data.xpath(".//p[contains(text(),'%s')]/following-sibling::*[1]" % string)
		content = content[0]
	except Exception, e:
		logging.info(traceback.format_exc())
		content = ''
	finally:
		return content


# 匹配关键内容,传递参数为要匹配的字符串
def match_key_content(string):
	pattern = re.compile("'(.*?)'+")
	# 匹配的结果是个list类型
	tuple = re.findall(pattern, string)
	return tuple


# 用于匹配浮点型数据
def match_float(finger):
	if finger == None or finger == '':
		finger = 0
	elif u"不公示" in finger:
		finger = 0
	else:
		pattern = re.compile(u"[-+]?[0-9]*\.?[0-9]+")  # 正则表达式匹配规则
		finger = re.findall(pattern, finger)  # 利用匹配规则在指定的字符串中匹配所需内容
		finger = decimal.Decimal(finger[0])  # 将数据转化为浮点类型
	return finger
