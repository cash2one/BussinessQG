#!/usr/bin/env python
# -*- coding:utf-8 -*-
import hashlib
import json
import os
import re
import sys
import time
import urllib

import MySQLdb
import requests
from bs4 import BeautifulSoup

import config

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
            time.sleep(3)
            print 'index error: ',e
            i = i-1
    return cookies


# 用于获取validate与challenge
def break_password(cookies):
    url = 'http://www.geev.website/geetest/get?token=seo_test1&reg=http://www.gsxt.gov.cn/SearchItemCaptcha'
    try:
        result = session.get(url, cookies=cookies, headers=config.headersfirst)
        # print result
        pattern = re.compile(r'<html>.*</html>')
        fail = re.findall(pattern,result.content)
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
        print 'break error:',e
        success_flag, challenge, validate = 0, None, None
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
        print 'break password error:', e
    return challenge, validate, cookies


# 循环得到validate

def last_request(challenge, validate, string, cookies):
    information = {}
    url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
    encryed_string = urllib.quote(string)
    search_text = "tab=ent_tab&token=36210782&searchword=%s&geetest_challenge=%s&geetest_validate=%s&geetest_seccode=%s|7Cjordan" % (
        encryed_string, challenge, validate, validate)
    result = session.post(url, search_text, cookies=cookies, headers=config.headers)
    result = BeautifulSoup(result.content, "lxml")
    span = result.find("span", {"class": "search_result_span1"})
    # print span
    if span!= None:
        pattern = re.compile(r'>.*([0-9]+).*<')
        number = re.findall(pattern, str(span))
        if int(number[0]) == 1:
            information = get_need_info(result)
            return information
        else:
            print '搜索结果不止一条'
    return information


# 将所获得的数据进行更新
def update_db(information, cursor, connect):
    update_flag, insert_flag = 0, 0
    if len(information) > 0:
        for key in information.keys():
            url = information[key][0]
            url = MySQLdb.escape_string(url)
            code = information[key][3]
            pattern = re.compile(r"^91.*|92.*|93.*")
            ccode = re.findall(pattern, code)
            if len(ccode) == 0:
                ccode = None
            elif len(ccode) == 1:
                ccode = ccode[0]
            m = hashlib.md5()
            m.update(code)
            id = m.hexdigest()
            updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            company, status, daibiao, dates = information[key][1], information[key][2], information[key][4], \
                                              information[key][5]
            try:
                cursor.execute(select_string, code)
                basic_id = cursor.fetchall()

                if len(basic_id) == 0:
                    pattern = re.compile(r'^9.*')
                    temp = re.findall(pattern, code)
                    if len(temp) == 0:
                        provin = config.province[code[0:2]]
                    else:
                        provin = config.province[code[2:4]]
                    # print insert_string %(id, url, provin, company, code, ccode, daibiao, dates, status, updated)
                    rows_flag = cursor.execute(insert_string,
                                               (id,url, provin, company, code, ccode, daibiao, dates, status, updated))
                    insert_flag += rows_flag
                    connect.commit()
                elif len(basic_id) == 1:
                    basic_id = basic_id[0][0]
                    rows_flag = cursor.execute(update_string, (url,company, daibiao, dates, status, updated, basic_id))
                    update_flag += rows_flag
                    connect.commit()
            except Exception, e:
                print "error", e
    elif len(information) == 0:
        print '无查询信息'
    print "url insert:%s" % insert_flag
    print "url updated:%s" % update_flag


# 用于获取所需信息
def get_need_info(result):
    information = {}
    a_list = result.find('div', {"class", "main-layout fw f14"}).find_all("a", {"class": "search_list_item db"})
    for item in a_list:
        href = item["href"]
        url = url_first + href
        company = item.find("h1", {"class": "f20"}).text.strip()
        status = item.find("div", {"class": "wrap-corpStatus"}).text.strip()
        code = item.find("div", {"class": "div-map2"}).find("span", {"class", "g3"}).text.strip()
        daibiao = item.find("div", {"class": "div-user2"}).find("span", {"class": "g3"}).text.strip()
        dates = item.find("div", {"class": "div-info-circle2"}).find("span", {"class": "g3"}).text.strip()
        dates = dates.replace("年", '-').replace("月", '-').replace("日", '')
        information[code] = [url, company, status, code, daibiao, dates]

    return information
