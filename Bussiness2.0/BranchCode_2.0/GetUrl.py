#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : GetUrl.py
# @Author: Lmm
# @Date  : 2017-07-30
# @Desc  : 获取链接

import json
import logging
import re
import sys
import time
import urllib
import requests
from bs4 import BeautifulSoup

from PublicCode import config
from PublicCode.Bulid_Log import Log
from PublicCode.Public_code import Connect_to_DB
from PublicCode.deal_html_code import remove_symbol


# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

session = requests.session()  # 用于保持会话
url_first = config.host

gs_py_id = sys.argv[1]
gs_basic_id = sys.argv[2]
code = sys.argv[3]
ccode = sys.argv[4]
# gs_py_id = 1501
# gs_basic_id = 229418502
# code = '91130000236047921'
# ccode = '91130000236047921'


update_py = 'update gs_py set gs_py_id = %s,gs_basic = %s,updated = %s where gs_py_id = %s'
select_name = 'select name from gs_basic where gs_basic_id = %s'
update_basic = 'update gs_basic_exp set gs_basic_exp_id =%s,gs_basic_id = %s,history = %s,updated = %s where gs_basic_exp_id = %s'
insert_history = 'insert into gs_basic_exp(gs_basic_id,history,updated)values(%s,%s,%s)'
select_basic = 'select gs_basic_exp_id from gs_basic_exp where gs_basic_id = %s'

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
    url,company,history_name = {},{},{}
    a_list = result.find('div', {"class", "main-layout fw f14"}).find_all("a", {"class": "search_list_item db"})
    for i,item in enumerate(a_list):
        href = item["href"]
        url[i] = url_first + href
        company[i] = item.find("h1", {"class": "f20"}).text.strip()
        company[i] = remove_symbol(company[i])
        if item.find("div", {"class": "div-info-circle3"})!=None:
            history = item.find("div", {"class": "div-info-circle3"}).find("span", {"class": "g3"}).text.strip()
        else:
            history = None
        history = remove_symbol(history)
        if history!=None:
            list = re.split('；',str(history))
            templist = []
            for k,temp in enumerate(list):
                if temp !=u'':
                    templist.append(temp)
            history = ';'.join(templist)
        history_name[i] = history

    return url,company,history_name


#用于获取url,company,history_name
def get_url_info(challenge, validate,string,cookies):
    url = config.search_url
    encryed_string = urllib.quote(string)
    search_text = config.search_text % (encryed_string, challenge, validate, validate)
    result = session.post(url, search_text, cookies=cookies, headers=config.headers)
    result = BeautifulSoup(result.content, "lxml")
    span = result.find("span", {"class": "search_result_span1"})
    if span!= None:
        pattern = re.compile(r'>([0-9]+)<')
        number = re.findall(pattern, str(span))
        if int(number[0]) >=1:
            get_url, company, history_name = get_need_info(result)
            flag = 1
            return get_url[0], company[0], history_name[0], flag
        elif int(number[0]) == 0:
            url, company, history_name = None,None,None
            flag = 100000003
            return url, company, history_name, flag
        else:
            pass
    else:
        flag = 100000003
        url,company,history_name = None, None, None
        return url, company, history_name, flag

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
    else:
        pass
    url, company, history_name, flag = get_url_info(challenge, validate,string,cookies)
    if flag == 100000003:
        challenge, validate, cookies = loop_break_password()
        if cookies ==None:
            flag = 100000001
        elif challenge == None or validate == None:
            flag = 100000002
        else:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            select_string = select_name % gs_basic_id
            cursor.execute(select_string)
            name = cursor.fetchall()[0][0]
            name = remove_symbol(name)
            cursor.close()
            connect.close()
            url,company,history_name,flag = get_url_info(challenge, validate,str(name),cookies)
            if flag == 100000003:
                url,company,history_name = None,None,None
            else:
                if name!=company:
                    url,company,history_name = None,None,None

    return url,company,history_name,flag


def main(code,ccode):
    info = {
        "url": '',
        "flag": '',
    }
    challenge, validate, cookies = loop_break_password()
    if cookies == None:
        flag = 100000001
        info["flag"] = flag

    elif challenge == None or validate == None:
        flag = 100000002
        info["flag"] = flag

    else:
        url, company, history_name, flag = last_request(challenge, validate, code, ccode, cookies)
        if url == None:
            info["flag"] = flag
        elif flag == 1:
            info["url"] = url
            info["flag"] = flag

    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        if history_name!=None:
            select_string = select_basic % gs_basic_id
            count = cursor.execute(select_string)
            if count ==0:
                cursor.execute(insert_history,(gs_basic_id,history_name,updated_time))
                connect.commit()
            elif int(count)==1:
                gs_basic_exp_id = cursor.fetchall()[0][0]
                cursor.execute(update_basic,(gs_basic_exp_id,gs_basic_id,history_name,updated_time,gs_basic_exp_id))
                connect.commit()
        cursor.execute(update_py,(gs_py_id,gs_basic_id,updated_time,gs_py_id))
        connect.commit()
    except Exception,e:
        logging.error('get url error %s' % e)
    finally:
        cursor.close()
        connect.close()
        print info



if __name__ == "__main__":
    Log().found_log(gs_py_id, gs_basic_id)
    main(code, ccode)

