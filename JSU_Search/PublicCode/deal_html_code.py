#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deal_html_code.py
# @Author: Lmm
# @Date  : 2017-09-20
# @Desc  : 用于处理网页信息
import re
import time
import decimal
#用于去除空格和换行符,制表符
def remove_space(string):
    string = re.sub('\s', '', string)
    pattetn = re.compile(u'&nbsp')
    string = pattetn.sub('', string)
    string = string.replace("\xc2\xa0", "")
    return string
#对中文日期进行处理
def change_chinese_date(date):
    if date == ''or date ==None or date == ' ':
        date = None
    else:
        date = re.sub(re.compile(u'年|月'), '-', date)
        date = re.sub(re.compile(u'日'), '', date)
    return date
#把时间戳转换为0000-00-00类型,十二位以上的时间戳不做处理
def change_date_style(old_date):
    if old_date == '' or old_date == None:
        new_date = None
    elif len(str(old_date/1000)) >= 12:
        new_date = '9999-12-31'
    else:
        new_date = time.localtime(old_date / 1000)
        otherStyleTime = time.strftime('%Y-%m-%d ', new_date)
        new_date = otherStyleTime
    return new_date
#用于匹配浮点型数据
def match_float(finger):
    if finger == None or finger == '':
        finger = None
    elif "不公示" in finger:
        finger = None
    else:
        pattern = re.compile(u"[-+]?[0-9]*\.?[0-9]+")
        finger = re.findall(pattern, finger)
        finger = decimal.Decimal(finger[0])
    return finger

#将现在的时间减去一个月
def get_before_date():
    now = time.time()
    n = 30
    before = now - n * 24 * 3600  # 可以改变n 的值计算n天前的
    beforeDate = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime(before))
    return beforeDate