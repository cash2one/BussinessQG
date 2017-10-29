#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : GetUrl.py
# @Author: Lmm
# @Date  : 2017-10-16
# @Desc  : 获取链接,通过名称进行搜索，若无搜索结果则返回，若有搜索结果则取第一条

import json
import logging
import re
import sys
import time
import urllib
import requests
from lxml import etree
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code


# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

session = requests.session()  # 用于保持会话
url_first = config.host



select_name = 'select name from gs_basic where gs_basic_id = %s'
update_basic = 'update gs_basic_exp set gs_basic_exp_id =%s,gs_basic_id = %s,history = %s,updated = %s where gs_basic_exp_id = %s'
insert_history = 'insert into gs_basic_exp(gs_basic_id,history,updated)values(%s,%s,%s)'
select_basic = 'select gs_basic_exp_id from gs_basic_exp where gs_basic_id = %s'

# 用于获取网页cookies

def get_cookies():
    i = 1
    cookies = None
    while i > 0:
        try:
            request = session.get("http://www.gsxt.gov.cn/index.html", headers=config.headersfirst,timeout=5)
            status_code = request.status_code
            if status_code == 200:
                cookies = request.cookies
                break
        except Exception, e:
            print e
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
            if "message" in json_list.keys():
                message = json_list["message"]
                if message == 'success':
                    success_flag = json_list["success"]
                    challenge = json_list["challenge"]
                    validate = json_list["validate"]
                else:
                    success_flag, challenge, validate = 0, None, None
            else:
                success_flag, challenge, validate = 0, None, None
        else:
            success_flag, challenge, validate = 0, None, None
    except Exception, e:
        print e
        logging.error("break error:%s"%e)
        success_flag, challenge, validate = 0, None, None
    return success_flag, challenge, validate, cookies


# 循环破解极验验证码
def loop_break_password():
    
    success_flag = 0
    # 可以自定义循环次数
    i = 1
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

#用于获取url,company,history_name
def get_url_info(challenge, validate,string,cookies):
    information = {}
    url = config.search_url
    encryed_string = urllib.quote(str(string))
    search_text = config.search_text % (encryed_string, challenge, validate, validate)
    result = session.post(url, search_text, cookies=cookies, headers=config.headers)
    status_code = result.status_code
    
    if status_code !=200:
        flag = 100000004
        logging.info("request the search url is failed!")
    else:
        result = etree.HTML(result.content)
        span = result.xpath("//span[@class='search_result_span1']")[0]
        spantext = span.xpath('string(.)')
        number = int(spantext)
        if int(number)==0:
            logging.info("there is no search information!")
            flag = 100000003
        else:
            information = get_need_info(result)
            flag = 1
    return information,flag
# 用于获取所需信息
def get_need_info(result):
    a_list = result.xpath("//div[@class='main-layout fw f14']/a[@class='search_list_item db']")
    #取第搜索结果的第一条
    item = a_list[0]
    information = deal_info(item)
    return information
    
# 用于抽取单条信息内容
def deal_info(item):
    info = {}
    href = item.xpath("./@href")[0]
    url = url_first + href
    company = item.xpath('./h1[@class="f20"]')[0].xpath('string(.)')
    company = deal_html_code.remove_symbol(company)
    status = item.xpath('./div[@class="wrap-corpStatus"]')[0].xpath('string(.)')
    status = deal_html_code.remove_symbol(status)
    code = item.xpath('.//div[@class="div-map2"]')[0].xpath('string(.)')
    code = deal_html_code.remove_symbol(code)
    # print code
    if len(code.split(':')) == 2:
        code = code.split(':')[1]
    else:
        code = code.split('：')[1]
    
    daibiao = item.find('.//div[@class="div-user2"]').xpath('string(.)')
    daibiao = deal_html_code.remove_symbol(daibiao)
    dates = item.find('.//div[@class="div-info-circle2"]').xpath('string(.)')
    dates = deal_html_code.remove_symbol(dates)
    dates = dates.split('：')[1]
    dates = deal_html_code.change_chinese_date(dates)
    history_name = item.xpath('.//div[@class="div-info-circle3"]')
    
    if len(history_name) != 0:
        history = item.xpath('.//div[@class="div-info-circle3"]/span[@class="g3"]')[0].xpath('string(.)')
    else:
        history = None
    history = deal_html_code.remove_symbol(history)
    if history != None:
        list = re.split('；', str(history))
        templist = []
        for k, temp in enumerate(list):
            if temp != u'':
                templist.append(temp)
            history = ';'.join(templist)
    
    info[0] = [url, company, status, code, daibiao, dates, history]
    return info


def main(name):
    #首先获取极验破解的challenge,validate,cookies
    challenge, validate, cookies = loop_break_password()
    information = {}
    if cookies == None:
        flag = 100000001
    elif challenge==None or validate==None:
        flag = 100000002
    else:
        information, flag = get_url_info(challenge, validate,name,cookies)
    return information,flag
    
   
    





