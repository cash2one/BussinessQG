#!/usr/bin/env python
# -*- coding:utf-8 -*-
import hashlib
import json
import logging
import re
import sys
import time
import urllib

import MySQLdb
import requests
from bs4 import BeautifulSoup

from PublicCode import config

# import provincelist
# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

session = requests.session()  # 用于保持会话
url_first = "http://www.gsxt.gov.cn"

select_string = 'select gs_basic_id from gs_basic where code = %s'
insert_string = "insert into gs_basic(id,uuid,province,name,code,ccode,legal_person,reg_date,status,updated ) values (%s,%s,%s,%s, %s, %s,%s,%s, %s,%s)"
update_string = "update gs_basic set uuid = %s,name = %s,legal_person = %s,reg_date = %s,status = %s,updated = %s where gs_basic_id = %s"




# 用于获取网页cookies
def get_cookies():
    i = 10
    cookies = None
    while i > 0:
        try:
            request = session.get("http://www.gsxt.gov.cn/index.html", headers=config.headersfirst, timeout=5)
            # print request
            status_code = request.status_code
            if status_code == 200:
                cookies = request.cookies
                break
                # print cookies
        except Exception, e:
            i = i - 1
            time.sleep(3)
            logging.info('index error: %s'%e)

    return cookies


# 用于获取validate与challenge
def break_password(cookies):
    url = 'http://115.28.86.78/geetest/get?token=seo_test1&reg=http://www.gsxt.gov.cn/SearchItemCaptcha'
    try:
        result = session.get(url, cookies=cookies, headers=config.headersfirst)
        pattern = re.compile('<html>.*</html>')
        fail = re.findall(pattern, result.content)
        if len(fail) == 0:
            json_list = json.loads(result.content)
            message = json_list["message"]
            if message == 'success':
                success_flag = json_list["success"]
                challenge = json_list["challenge"]
                validate = json_list["validate"]
            else:
                success_flag, challenge, validate = 0, None, None
        else:
            success_flag, challenge, validate = 0, None, None
    except Exception, e:
        success_flag, challenge, validate = 0, None, None
        logging.error('break error: %s'% e)
    return success_flag, challenge, validate, cookies


# 循环破解极验验证码
def loop_break_password():
    success_flag = 0
    validate = ''
    try:
        while True:
            if success_flag == 0 or validate == None or cookies == None:
                cookies = get_cookies()
                success_flag, challenge, validate, cookies = break_password(cookies)
            elif success_flag == 1:
                break
    except Exception, e:
        logging.error('break password error: %s'%e)

    return challenge, validate, cookies


# 循环得到validate

def last_request(challenge, validate, code,ccode, cookies):
    pattern = re.compile(r'^9.*')

    result1 = re.findall(pattern,code)
    result2 = re.findall(pattern,ccode)
    if len(result1) == 0 and len(result2) == 0:
        string = code
    elif len(result1) == 1:
        string = code
    elif len(result2) == 1:
        string = ccode

    get_url = None
    url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
    encryed_string = urllib.quote(string)
    search_text = "tab=ent_tab&token=34911389&searchword=%s&geetest_challenge=%s&geetest_validate=%s&geetest_seccode=%s|7Cjordan" % (
        encryed_string, challenge, validate, validate)
    result = session.post(url, search_text, cookies=cookies, headers=config.headers)
    result = BeautifulSoup(result.content, "lxml")
    # print result
    span = result.find("span", {"class": "search_result_span1"})
    if span!= None:
        pattern = re.compile(r'>.*([0-9]+).*<')
        number = re.findall(pattern, str(span))
        if int(number[0]) == 1:
            get_url = get_need_info(result)
            flag = 100000001
            return get_url,flag
        elif int(number[0]) > 0:
            print '搜索结果不止一条'
            get_url = None
            flag = 100000002
            logging.error('搜索结果不止一条')
    else:
        print '无搜索信息'
        get_url = None
        flag = 100000004
        logging.info('无搜索信息')
    return get_url, flag


# 用于获取所需信息
def get_need_info(result):
    url = None
    a_list = result.find('div', {"class", "main-layout fw f14"}).find_all("a", {"class": "search_list_item db"})
    for item in a_list:
        href = item["href"]
        url = url_first + href
    return url
