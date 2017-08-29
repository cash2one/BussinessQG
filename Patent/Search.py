#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search.py
# @Author: Lmm
# @Date  : 2017-08-29
# @Desc  : 用于根据关键词搜索专利
from PublicCode import config
import random
import re
import requests
from lxml import etree
import Login
headers = config.header
string = '农业'
def search_info(string):
    cookies, flag,driver= Login.main()
    print cookies,flag
    cookies["IS_LOGIN"] = 'true'
    user_agent = random.choice(config.USER_AGENTS)
    headers["User-Agent"] = user_agent
    url = config.searchurl
    search_text = config.search_text%string
    result = requests.post(url, search_text, headers=headers, cookies=cookies)
    print result.content
    return result.content,cookies,driver

def get_need_info(result):
    pattern = re.compile(".*您的访问出错了.*")
    match = re.findall(pattern,result)
    print match
    if len(match) ==0:
        result = etree.HTML(result)
        totalpage = result.xpath("//form[@id='resultlistForm_top']/input[@id='resultPagination.totalCount']/@value")[0]
        print totalpage
        first_info = result.xpath("//li[contains(@class,'patent')]")
        print len(first_info)
        for i,single in first_info:
            #文献标识
            cid = single.xpath("./input[@name='vIdHidden']")[0]
            #文献唯一标识
            sid = single.xpath("./input[@name= 'idHidden']")[0]

def get_single_info(cid,sid):

        # cid =
        # first_info= result.xpath("//")
result,cookies ,driver= search_info(string)
get_need_info(result)
driver.quit()
# params = 'nrdAn=CN201510222267&cid=CN201510222267.X20150715FM&sid=CN201510222267.X20150715FM&wee.bizlog.modulelevel=0201101'
# url = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/viewAbstractInfo-viewAbstractInfo.shtml'
# user_agent = random.choice(config.USER_AGENTS)
# headers["User-Agent"] = user_agent
# result = requests.post(url,params,headers = headers)
# pattern = re.compile(".*您的访问出错了.*")
# match = re.findall(pattern, result.content,cookies)
# print len(match)
# print result.content


