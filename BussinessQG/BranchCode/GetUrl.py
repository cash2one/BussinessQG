#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import logging
import re
import sys
import time
import urllib
import requests
from bs4 import BeautifulSoup

from PublicCode import config


# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

session = requests.session()  # 用于保持会话
url_first = config.host


# code = sys.argv[1]
# ccode = sys.argv[2]
code = '310115002562777'
ccode = '91310115324507748U'
# 用于获取网页cookies
def get_cookies():
    i = 10
    cookies = None
    while i > 0:
        try:
            request = session.get("http://www.gsxt.gov.cn/index.html", headers=config.headersfirst, timeout=5)
            status_code = request.status_code
            if status_code == 200:
                cookies = request.cookies
                break
        except Exception, e:
            i = i - 1
            time.sleep(3)

    return cookies


# 用于获取validate与challenge
def break_password(cookies):
    url = config.break_url
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
    return success_flag, challenge, validate, cookies


# 循环破解极验验证码
def loop_break_password():
    success_flag = 0
    i = 10
    try:
        while i > 0:
            if success_flag == 0 or validate == None or cookies == None:
                cookies = get_cookies()
                success_flag, challenge, validate, cookies = break_password(cookies)
                i = i-1
            elif success_flag == 1:
                break
    except Exception, e:
        logging.error('break password error: %s'%e)
        challenge, validate = None, None

    return challenge, validate, cookies
# 用于获取所需信息
def get_need_info(result):
    url = {}
    a_list = result.find('div', {"class", "main-layout fw f14"}).find_all("a", {"class": "search_list_item db"})
    for i,item in enumerate(a_list):
        href = item["href"]
        url[i] = url_first + href
    return url

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
    url = config.search_url
    encryed_string = urllib.quote(string)
    search_text = config.search_text % (encryed_string, challenge, validate, validate)
    result = session.post(url, search_text, cookies=cookies, headers=config.headers)
    result = BeautifulSoup(result.content, "lxml")
    span = result.find("span", {"class": "search_result_span1"})
    if span!= None:
        pattern = re.compile(r'>.*([0-9]+).*<')
        number = re.findall(pattern, str(span))
        if int(number[0]) == 1:
            get_url = get_need_info(result)
            flag = 1
            return get_url[0], flag
        elif int(number[0]) > 1:
            get_url = get_need_info(result)
            url = get_url[0]
            flag = 1
            logging.info('搜索结果不止一条')
            return url, flag
    else:
        print '无搜索信息'
        get_url = None
        flag = 100000003
        logging.info('无搜索信息')
    return get_url, flag

def main(code,ccode):
    info = {
        "url":'',
        "flag":''
    }
    challenge, validate, cookies = loop_break_password()
    if cookies == None:
        flag = 100000001
        info["flag"] = flag
    elif challenge ==None or validate ==None:
        flag = 100000002
        info["flag"] = flag
    else:
        url, flag = last_request(challenge, validate, code, ccode, cookies)
        if url == None:
            info ["flag"] = flag
        elif flag == 1:
            info["url"] =url
            info["flag"] = flag
    print info


if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main(code,ccode)
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)







