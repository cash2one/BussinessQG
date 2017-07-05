#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import logging
import re
import sys
import time

from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# gs_basic_id = 104589242

update_string = 'update gs_basic set id = %s, name = %s ,ccode = %s,status = %s ,types = %s ,jj_type = %s,legal_person = %s, \
responser = %s ,investor = %s,runner = %s ,reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s ,updated = %s where gs_basic_id = %s'
select_basic_id = 'select gs_basic_id from gs_basic where code = %s '


def get_basic_info(result, status_code):
    information = {}
    result = BeautifulSoup(result, 'lxml')
    if status_code == 200:
        basic_info = result.find("div", {"id": "primaryInfo"}).find_all("dl")
        if len(basic_info) > 0:
            try:
                for item in basic_info:
                    temp = re.sub(re.compile(''), '', item.text)
                    temp = re.sub(re.compile(u'·'), '', temp)
                    templist = re.split(u'：', temp)
                    if len(templist) == 1:
                        templist = re.split(u':', temp)

                    information[templist[0].strip()] = templist[1].strip()
            except Exception, e:
                print 'basic error', e
    # elif len(fail)!=0:
    #     print '访问失败，重新返回首页'

        return information


def update_basic(information, connect, cursor, gs_basic_id):
    if '企业名称' in information.keys():
        name = information[u"企业名称"]
    elif '名称' in information.keys():
        name = information[u"名称"]
    if '统一社会信用代码' in information.keys():
        code = information[u"统一社会信用代码"]
        # print code
        ccode = information[u"统一社会信用代码"]
    elif '注册号' in information.keys():
        code = information[u"注册号"]
        ccode = None
    if '登记状态' in information.keys():
        status = information[u"登记状态"]
    if '类型' in information.keys():
        types = information[u'类型']
    if '组成形式' in information.keys():
        jj_type = information[u'组成形式']
    else:
        jj_type = None
    if '法定代表人' in information.keys():
        legal_person = information[u"法定代表人"]
        responser = None
        investor = None
        runner = None
    elif '经营者' in information.keys():
        runner = information[u"经营者"]
        legal_person = None
        responser = None
        investor = None
    elif '负责人' in information.keys():
        responser = information[u'负责人']
        runner = None
        legal_person = None
        investor = None
    elif '投资人' in information.keys():
        investor = information[u"投资人"]
        responser = None
        runner = None
        legal_person = None
    elif '执行事务合伙人' in information.keys():
        legal_person = information[u"执行事务合伙人"]
        investor = None
        runner = None
        responser = None

    if '成立日期' in information.keys():
        sign_date = information[u"成立日期"]
        if sign_date == '':
            sign_date = None
        else:
            sign_date = re.sub(re.compile(u'年|月'), '-', sign_date)
            sign_date = re.sub(re.compile(u'日'), '', sign_date)
    else:
        sign_date = None
    if '注册资本' in information.keys():
        reg_amount = information[u"注册资本"]
    else:
        reg_amount = None
    if '核准日期' in information.keys():
        appr_date = information[u"核准日期"]
        if appr_date == '':
            appr_date = None
        else:
            appr_date = re.sub(re.compile(u'年|月'), '-', appr_date)
            appr_date = re.sub(re.compile(u'日'), '', appr_date)
    else:
        appr_date = None
    if '营业期限自' in information.keys():
        start_date = information[u"营业期限自"]
        if start_date == '':
            start_date = None
        else:
            start_date = re.sub(re.compile(u'年|月'), '-', start_date)
            start_date = re.sub(re.compile(u'日'), '', start_date)
    else:
        start_date = None
    if '营业期限至' in information.keys():
        end_date = information[u"营业期限至"]
        if end_date == '':
            end_date = None
        else:
            end_date = re.sub(re.compile(u'年|月'), '-', end_date)
            end_date = re.sub(re.compile(u'日'), '', end_date)
    else:
        end_date = None
    if '登记机关' in information.keys():
        reg_zone = information[u"登记机关"]
    if '住所' in information.keys():
        reg_address = information[u"住所"]
    elif '经营场所' in information.keys():
        reg_address = information[u"经营场所"]
    elif '主要经营场所' in information.keys():
        reg_address = information[u"主要经营场所"]
    elif '营业场所' in information.keys():
        reg_address = information[u"营业场所"]
    if '业务范围' in information.keys():
        scope = information[u"业务范围"]
    elif '经营范围' in information.keys():
        scope = information[u"经营范围"]
    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    m = hashlib.md5()
    m.update(code + 'A')
    id = m.hexdigest()
    try:
        row_count = cursor.execute(update_string, (
            id, name, ccode, status, types, jj_type, legal_person, responser, investor, runner, sign_date,
            appr_date, reg_amount, start_date, end_date, reg_zone, reg_address, scope, updated_time, gs_basic_id))
        print 'update basic :%s' % row_count
        connect.commit()
    except Exception, e:
        logging.error("basic error:" % e)
