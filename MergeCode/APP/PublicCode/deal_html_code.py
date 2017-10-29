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

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

#移除标签及标签之间的内容
def deal_lable(html_code):
    pattern = re.compile('<.*?>.*?</.*?>', re.S)
    result = re.sub(pattern, '', html_code)
    return result

#把时间戳转换为0000-00-00类型,十二位以上的时间戳不做处理
def change_date_style(old_date):
    if old_date == '' or old_date == None:
        new_date = '0000-00-00'
    elif len(str(old_date/1000))>=12:
        new_date = '9999-12-31'
    else:
        new_date = time.localtime(old_date / 1000)
        otherStyleTime = time.strftime('%Y-%m-%d ', new_date)
        new_date = otherStyleTime
    return new_date

#计算时间差
def caculate_time(now_date,old_date):

    #转化为时间数组
    timearray = time.strptime(old_date,"%Y-%m-%d %H:%M:%S")
    #转换时间为时间戳
    change_time = time.mktime(timearray)
    interval = float(now_date) - float(change_time)
    return interval

#判断省份
def judge_province(code):
    pattern = re.compile(r'^9.*')
    temp = re.findall(pattern, code)
    if len(temp) == 0:
        provin = config.province[code[0:2]]
    else:
        provin = config.province[code[2:4]]
    return provin
#一次性去除制表符，换行符,标签
def remove_symbol(string):
    if string =='' or string ==None or string == ' ':
        string = None
    else:
        string = re.sub('\s','',string)
        pattetn = re.compile(u'&nbsp')
        string = pattetn.sub('', string)
        pattern = re.compile(r'<[^>]+>', re.S)
        string = pattern.sub('', string)
    return string
#对中文日期进行处理
def change_chinese_date(date):
    if date == ''or date ==None or date == ' ':
        date = '0000-00-00'
    else:
        date = re.sub(re.compile(u'年|月'), '-', date)
        date = re.sub(re.compile(u'日'), '', date)
    return date
#用于获得一个月以前的时间
def get_befor_date():
    now = time.time()
    n = 30
    before = now - n * 24 * 3600  #可以改变n 的值计算n天前的
    beforeDate = time.strftime("%Y-%m-%d %H:%M:%S ",  time.localtime(before))
    return beforeDate
    


