#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


def deal_lable(html_code):
    pattern = re.compile('<.*?>.*?</.*?>', re.S)
    result = re.sub(pattern, '', html_code)
    return result


def change_date_style(old_date):
    if old_date == '' or old_date == None:
        new_date = None
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
