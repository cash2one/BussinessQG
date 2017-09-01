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
import logging
import time
import sys
from lxml import etree
from Update_Patent import Ia_Patent

headers = config.header
string = '农业'
# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# rspage = sys.argv[1]#当前页数
# cookies = sys.argv[2]#总共页数
rspage = 1

cookies ={u'_gscbrs_761734625': '1', u'_gscs_761734625': '04238325kds2xm96|pv:1', u'WEE_SID': 'V8s7lsx3RcFovJq7XMGiEiw6dMFPX3WMm65-qIniXVLFUFi_2ubV!-2138351820!1985999437!1504238292087', u'_gscu_761734625': '042383257ieq8r96', u'JSESSIONID': 'V8s7lsx3RcFovJq7XMGiEiw6dMFPX3WMm65-qIniXVLFUFi_2ubV!-2138351820!1985999437', u'IS_LOGIN': 'true'}
def search_info(string, keywords):
    if cookies["IS_LOGIN"] =='true':
        user_agent = random.choice(config.USER_AGENTS)
        headers["User-Agent"] = user_agent
        url = config.searchurl
        start = (int(rspage) - 1) * 12
        search_text = config.searchparams % (start, string, string, string, keywords)
        result = requests.post(url, search_text, headers=headers, cookies=cookies)
        print result.content
        return result.content, cookies


def get_need_info(result):
    pattern = re.compile(".*您的访问出错了.*")
    match = re.findall(pattern, result)
    page = 0
    flag = 1
    try:
        if len(match) == 0:
            result = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
            total = result.xpath("//form[@id='resultlistForm_top']/input[@id='resultPagination.totalCount']/@value")[0]
            perpage = result.xpath("//form[@id ='resultlistForm_top']/input[@id='resultPagination.limit']/@value")[0]
            page = caculate_page(total, perpage)
            first_info = result.xpath("//li[contains(@class,'patent')]")
        else:
            first_info = []
            flag = 100000004
    except Exception,e:
        print e
        flag = 100000004
        first_info

    return first_info,page,flag


def caculate_page(count, perpage):
    number = int(count)
    perpage = int(perpage)
    if int(number) % perpage == 0:
        page = int(number) / perpage
    elif int(number) % perpage != 0:
        page = int(number) / perpage + 1
    return page


def get_keywords(key):
    string = unicode(key)
    key = ''
    for i, single in enumerate(string):
        temp = '[%s][ ]{0,}' % single
        key = key + temp
    return key


def main():
    try:
        key = get_keywords(string)
        result,cookies = search_info(string,key)
        info, page, flag = get_need_info(result)
        print info,page,flag
        if flag ==1:
            object = Ia_Patent()
            info = Ia_Patent().get_info(info, cookies)

    except Exception, e:
        flag = 100000004



if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main()
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)