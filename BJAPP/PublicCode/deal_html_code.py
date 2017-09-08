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
        string = re.sub(' ','',string)
        string = string.replace("\xc2\xa0","")
    return string

#用于去处空格和换行符
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


