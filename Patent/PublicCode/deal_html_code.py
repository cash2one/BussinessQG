#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : deal_html_code.py
# @Author: Lmm
# @Date  : 2017-08-30
# @Desc  : 用于对html页的处理
import re


# 一次性去除制表符，换行符,标签
def remove_symbol(string):
    if string == '' or string == None or string == ' ':
        string = None
    else:
        string = re.sub('\s', '', string)
        pattern = re.compile(u'&nbsp')
        string = pattern.sub('', string)
        pattern = re.compile(r'<[^>]+>', re.S)
        string = pattern.sub('', string)
        pattern = re.compile(' ')
        string = pattern.sub('', string)
    return string


def change_date(dates):
    if dates == '' or dates == None:
        dates = None
    else:
        dates = dates.replace('.', '-')
    return dates