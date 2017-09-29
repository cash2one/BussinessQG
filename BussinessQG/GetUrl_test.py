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

from PublicCode import config
from PublicCode.Public_code import Connect_to_DB


# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

session = requests.session()  # 用于保持会话
url_first = "http://www.gsxt.gov.cn"

select_string = 'select gs_basic_id from gs_basic where code = %s'
# gs_basic_id = sys.argv[1]
insert_string = "insert into gs_basic(id,province,name,code,ccode,legal_person,reg_date,status,updated ) values (%s,%s,%s, %s, %s,%s,%s, %s,%s)"
update_string = "update gs_basic set name = %s,legal_person = %s,reg_date = %s,status = %s,updated = %s where gs_basic_id = %s"

# 代理服务器
proxyHost = "proxy.abuyun.com"
proxyPort = "9010"

# 代理隧道验证信息
proxyUser = "HQRMZT62299COJ2P"
proxyPass = "1B668ADB969075FD"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
      "host" : proxyHost,
      "port" : proxyPort,
      "user" : proxyUser,
      "pass" : proxyPass,
    }

proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
}
# 用于程序自我重启
def restart_program():
    python = sys.executable
    os.execl(python, python * sys.argv)


# 用于获取网页cookies
def get_cookies():
    try:
        request = session.get("http://www.gsxt.gov.cn/index.html", headers=config.headersfirst, timeout=5)
        cookies = request.cookies
        # print cookies
    except Exception, e:
        time.sleep(3)
        restart_program()
    return cookies


# 用于获取validate与challenge

def break_password(cookies):
    url = 'http://59.110.138.116/geetest/get?token=seo_dsboye&reg=http://www.gsxt.gov.cn/SearchItemCaptcha'
    result = session.get(url, cookies=cookies, headers=config.headersfirst)
    print result
    json_list = json.loads(result.content)
    success_flag = json_list["success"]
    if success_flag == 1:
        challenge = json_list["challenge"]
        validate = json_list["validate"]
    elif success_flag == 0:
        challenge = None
        validate = None
    return success_flag, challenge, validate, cookies


# 循环破解极验验证码
def loop_break_password():
    success_flag = 0
    while True:
        if success_flag == 0:
            cookies = get_cookies()
            success_flag, challenge, validate, cookies = break_password(cookies)
        elif success_flag == 1:
            break
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
    pattern = re.compile(r'[0-9]+')
    number = re.findall(pattern, span.text)
    information = get_need_info(result)
    if int(number[0]) == 1:
        return information
    elif int(number[0]) > 1:
        if int(number[0]) % 10 == 0:
            page = int(number[0]) / 10
        elif int(number[0]) % 10 != 0:
            page = int(number[0]) / 10 + 1
        for i in range(2, page + 1):
            url = 'http://www.gsxt.gov.cn/corp-query-search-%s.html' % i
            result = session.post(url, search_text, cookies=cookies, headers=config.headers)
            result = BeautifulSoup(result.content, "lxml")
            tempinformation = get_need_info(result)
            information = dict(information, **tempinformation)
        return information


# 将所获得的数据进行更新
def update_db(information, cursor, connect):
    update_flag, insert_flag = 0, 0
    for key in information.keys():
        url = information[key][0]
        url = MySQLdb.escape_string(url)
        code = information[key][3]
        pattern = re.compile(r"^91.*|92.*|93.*")
        ccode = re.findall(pattern, code)
        if len(ccode) == 0:
            ccode = code
        elif len(ccode) == 1:
            ccode = ccode[0]
            code = ccode
        m = hashlib.md5()
        m.update(code)
        id = m.hexdigest()
        updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        company, status, daibiao, dates = information[key][1], information[key][2], information[key][4], \
                                          information[key][5]
        list = re.split(u'、', daibiao)
        daibiao = list[0] +'等'

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
                                           (id, provin, company, code, ccode, daibiao, dates, status, updated))
                insert_flag += rows_flag
                connect.commit()
            elif len(basic_id) == 1:
                basic_id = basic_id[0][0]
                rows_flag = cursor.execute(update_string, (company, daibiao, dates, status, updated, basic_id))
                update_flag += rows_flag
                connect.commit()
        except Exception, e:
            print "error", e
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


# 函数入口
def main():
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        # string = '914100001711393654'
        string = '91110000740085820P'
        # string_list = [
        #                '四川五金店',
        #                '云南五金店',
        #                '河北五金店',
        #                '上海五金店']
        string_list = ['乐视信息技术']
        # string_list = [
        #     '北京知识产权',
        #     '天津知识产权',
        #     '河北知识产权',
        #     '山西知识产权',
        #     '内蒙古知识产权',
        #     '辽宁知识产权',
        #     '吉林知识产权',
        #     '黑龙江知识产权',
        #     '上海知识产权',
        #     '江苏知识产权',
        #     '浙江知识产权',
        #     '安徽知识产权',
        #     '福建知识产权',
        #     '江西知识产权',
        #     '山东知识产权',
        #     '河南知识产权',
        #     '湖北知识产权',
        #     '湖南知识产权',
        #     '广东知识产权',
        #     '广西知识产权',
        #     '海南知识产权',
        #     '重庆知识产权',
        #     '四川知识产权',
        #     '贵州知识产权',
        #     '云南知识产权',
        #     '西藏知识产权',
        #     '陕西知识产权',
        #     '甘肃知识产权',
        #     '青海知识产权',
        #     '宁夏知识产权',
        #     '新疆知识产权',
        #     '台湾知识产权',
        #     '香港知识产权',
        #     '澳门知识产权'
        # ]
        # string = '洛阳银行股份有限公司'
        for i,string in enumerate(string_list):
            print string
            try:
                challenge, validate, cookies = loop_break_password()
                print challenge,validate,cookies
                information = last_request(challenge, validate, string, cookies)
            except Exception,e:
                raise
            else:
                update_db(information, cursor, connect)
    except Exception, e:
        print e
        raise
    finally:
        cursor.close()
        connect.close()


if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main()
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
