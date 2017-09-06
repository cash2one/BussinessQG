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
from PublicCode.Public_code import Connect_to_DB

headers = config.header

# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
keyword = '帽类制品'
# keyword = sys.argv[1]#关键词
# rspage = sys.argv[2]#当前页数
# cookies = sys.argv[3]#cookies值
# totalpage = sys.argv[4]#总页数
rspage = 2
cookies = {u'_gscbrs_761734625': '1', u'_gscs_761734625': '04507687ph9wit13|pv:1', u'WEE_SID': 'Z8tLoiljDx1kVabTNLtK8JrrWUujbjvzgWfYIlrwUc_bKNunoXUI!446741660!421874926!1504507472227', u'_gscu_761734625': '04507687yhtmjd13', u'JSESSIONID': 'Z8tLoiljDx1kVabTNLtK8JrrWUujbjvzgWfYIlrwUc_bKNunoXUI!446741660!421874926', u'IS_LOGIN': 'true'}
totalpage = 0
def search_info(string, keywords):
    flag = 1
    cookies["IS_LOGIN"] ='true'
    if cookies["IS_LOGIN"] == 'true':
        user_agent = random.choice(config.USER_AGENTS)
        headers["User-Agent"] = user_agent
        url = config.searchurl
        start = (int(rspage) - 1) * 12
        search_text = config.searchparams % (start, string, string, string, str(keywords))
        # print search_text
        result = requests.post(url, search_text, headers=headers, cookies=cookies)
        # print result.content
        status = result.status_code
        if status ==200:
            information = result.content
        else:
            flag = 100000004
            information = ''
       
        return information, cookies,flag


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
    except Exception, e:
        logging.error("post search page error:%s"%e)
        flag = 100000004
        first_info = []
    finally:
        return first_info, page, flag


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
def printinfo(flag,rspage,totalpage,totalinfo,insert):
    print_info ={
        "flag":0,
        "rspage":0,
        "totalpage":0,
        "totalinfo":0,
        "insert":0
    }
    if int(rspage)>= int(totalpage):
        rspage = 0
    print_info["flag"] = int(flag)
    print_info["rspage"] = int(rspage)
    print_info["totalpage"] = int(totalpage)
    print_info["totalinfo"] = int(totalinfo)
    print_info["insert"] = int(insert)
    print print_info

def main():
    page,total,insert_flag = 0,0,0
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        key = get_keywords(keyword)
        if int(rspage) ==1:
            result, cookies,flag = search_info(keyword, key)
            if flag ==1:
                info, page, flag = get_need_info(result)
                if flag == 1:
                    object = Ia_Patent()
                    info = object.get_info(info, cookies)
                    remark, total, insert_flag = object.update_basic_to_db(info, cursor, connect)
                    if remark >100000001:
                        flag = 100000006
            elif flag ==100000004:
                page = 0
                
        elif int(rspage)>1:
            result, cookies, flag = search_info(keyword, key)
            if flag ==1:
                info, page, flag = get_need_info(result)
                if flag == 1:
                    object = Ia_Patent()
                    info = object.get_info(info, cookies)
                    remark, total, insert_flag = object.update_basic_to_db(info, cursor, connect)
                    if remark > 100000001:
                        flag = 100000006
    except Exception, e:
        logging.error("search error:%s"%e)
        flag = 100000005
    finally:
        cursor.close()
        connect.close()
        printinfo(flag,rspage,page,total,insert_flag)
        
        
        


if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main()
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
