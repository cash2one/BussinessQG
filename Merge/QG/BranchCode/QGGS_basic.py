#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_basic.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取基本信息，并对数据进行更新，返回分支链接列表
import logging
import re
import sys
import time
from bs4 import BeautifulSoup
from PublicCode.Public_code import Send_Request
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.deal_html_code import remove_symbol
from PublicCode.deal_html_code import change_chinese_date

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()



update_string = 'update gs_basic set gs_basic_id = %s, name = %s ,ccode = %s,status = %s ,types = %s ,jj_type = %s,legal_person = %s, \
responser = %s ,investor = %s,runner = %s ,reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s ,updated = %s where gs_basic_id = %s'

update_py = 'update gs_py set gs_py_id = %s,gs_basic = %s,updated = %s where gs_py_id = %s'
select_report = 'select tel,address,email from gs_report where gs_basic_id = %s order by year desc  LIMIT 1 '
update_address = 'update gs_basic set gs_basic_id = %s,tel = %s,address = %s,email = %s,updated = %s where gs_basic_id = %s'
def get_url_list(url):
    result, status_code = Send_Request().send_requests(url)
    pattern = re.compile(".*返回首页.*|.*'/index/invalidLink'.*")
    fail = re.findall(pattern, result)
    if status_code == 200 and len(fail) == 0:
        information, flag = get_basic_info(result, status_code)
        url = get_singleinfo_url(result)
    else:
        information = None
        flag = 100000004
        url = {}
    return information,flag,url

#正则匹配url
def get_url(pattern, url_content):
    url = re.findall(pattern, str(url_content))
    real_url = config.host + url[0]
    return real_url

# 用于获取各分支的url的链接
def get_singleinfo_url(result):
    url = {}
    try:
        url_content = BeautifulSoup(result, 'lxml').find("div", {"id": "url"}).find("script")
        # print url_content
        shareholder_url = get_url(config.shareholder_pattern, url_content)
        person_url = get_url(config.person_pattern, url_content)
        branch_url = get_url(config.branch_pattern, url_content)
        change_url = get_url(config.change_pattern, url_content)
        gtchange_url = get_url(config.gtchange_pattern, url_content)
        check_url = get_url(config.check_pattern, url_content)
        permit_url = get_url(config.permit_pattern, url_content)
        punish_url = get_url(config.punish_pattern, url_content)
        gt_punish_url = get_url(config.gtpunish_pattern, url_content)
        except_url = get_url(config.except_pattern, url_content)
        freeze_url = get_url(config.freeze_pattern, url_content)
        stock_url = get_url(config.stock_pattern, url_content)
        gt_permit_url = get_url(config.gt_permit, url_content)
        brand_url = get_url(config.brand_pattern, url_content)
        mort_url = get_url(config.mort_pattern, url_content)
        report_url = get_url(config.report_pattern, url_content)
        gt_share_url = get_url(config.gtshare_pattern, url_content)
        clear_url = get_url(config.liquidation_pattern, url_content)
        black_url = get_url(config.black_pattern,url_content)
        # print brand_url
        url["branch"] = branch_url
        url["shareholder"] = shareholder_url
        url["person"] = person_url
        url["change"] = change_url
        url["change2"] = gtchange_url
        url["check"] = check_url
        url["permit"] = permit_url
        url["except"] = except_url
        url["punish"] = punish_url
        url["freeze"] = freeze_url
        url["stock"] = stock_url
        url["permit2"] = gt_permit_url
        url["brand"] = brand_url
        url["report"] = report_url
        url["mort"] = mort_url
        url["shareholder2"] = gt_share_url
        url["punish2"] = gt_punish_url
        url["clear"] = clear_url
        url["black"] = black_url
    except Exception,e:
        logging.info('get url error %s'%e)

    return url

#用于获取基本信息
def get_basic_info(result, status_code):
    information = {}
    result = BeautifulSoup(result, 'lxml')
    flag = 0
    pattern = re.compile(r'.*返回首页.*')
    fail = re.findall(pattern, str(result))
    try:
        if status_code == 200 and len(fail) == 0:
            basic_info = result.find("div", {"id": "primaryInfo"}).find_all("dl")
            if len(basic_info) > 0:
                for item in basic_info:
                    temp = re.sub(re.compile(''), '', item.text)
                    temp = re.sub(re.compile(u'·'), '', temp)
                    templist = re.split(u'：', temp)
                    if len(templist) == 1:
                        templist = re.split(u':', temp)
                    templist[1] = templist[1].replace('\n','').replace('\t','').replace(' ','')
                    information[templist[0].strip()] = templist[1]
        elif len(fail)!= 0:
            flag = 100000004
            logging.info('访问失败，重新返回首页')
    except Exception, e:
        flag = 100000005
        logging.info('basic error %s' % e)
    return information,flag

#更新基础信息
def update_basic(information, connect, cursor, gs_basic_id):
    if '企业名称' in information.keys():
        name = information[u"企业名称"]
    elif '名称' in information.keys():
        name = information[u"名称"]
    if '统一社会信用代码' in information.keys():
        code = information[u"统一社会信用代码"]
        ccode = information[u"统一社会信用代码"]
        ccode = str(ccode).replace('\t','').replace('\n','').replace(' ','')
    elif '注册号' in information.keys():
        code = information[u"注册号"]
        ccode = ''
    elif '统一社会信用代码/注册号' in information.keys():
        code = information[u"统一社会信用代码/注册号"]
        pattern = re.compile('^91.*|92.*|93.*')
        ccode = re.findall(pattern,code)
        if len(ccode) == 0:
            ccode = ''
        elif len(ccode) == 1:
            ccode = ccode[0]
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
        list = re.split(u'、',legal_person)
        legal_person = list[0] +'等'
        investor = None
        runner = None
        responser = None

    if '成立日期' in information.keys():
        sign_date = information[u"成立日期"]
        sign_date = change_chinese_date(sign_date)
    elif '注册日期' in information.keys():
        sign_date = information[u"注册日期"]
        sign_date = change_chinese_date(sign_date)
    else:
        sign_date = None

    if '注册资本' in information.keys():
        reg_amount = information[u"注册资本"]
    elif '成员出资额' in information.keys():
        reg_amount = information[u"成员出资额"]
    else:
        reg_amount = None
    if '核准日期' in information.keys():
        appr_date = information[u"核准日期"]
        appr_date = change_chinese_date(appr_date)
    else:
        appr_date = None
    if '营业期限自' in information.keys():
        start_date = information[u"营业期限自"]
        start_date = change_chinese_date(start_date)
    elif '合伙期限自' in information.keys():
        start_date = information[u"合伙期限至"]
        start_date = change_chinese_date(start_date)
    else:
        start_date = None
    if '营业期限至' in information.keys():
        end_date = information[u"营业期限至"]
        end_date = change_chinese_date(end_date)
    elif '合伙期限至' in information.keys():
        end_date = information[u"合伙期限至"]
        end_date = change_chinese_date(end_date)
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
    row_count = 0
    flag = 0
    ccode = remove_symbol(ccode)

    try:
        row_count = cursor.execute(update_string, (
            gs_basic_id, name, ccode, status, types, jj_type, legal_person, responser, investor, runner, sign_date,
            appr_date, reg_amount, start_date, end_date, reg_zone, reg_address, scope, updated_time, gs_basic_id))
        logging.info('update basic :%s' % row_count)
        connect.commit()
    except Exception, e:
        flag = 100000004
        logging.error("basic error:" % e)
    finally:
        if flag < 100000001:
            flag = row_count
        return flag

def main(url,gs_basic_id):
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    try:
        select_string = select_report % gs_basic_id
        count = cursor.execute(select_string)
        if count == 1:
            for data1,data2,data3 in cursor.fetchall():
                if data1 ==u'无' or data1=='':
                    data1 = None
                if data2 ==u'无' or data2 =='':
                     data2 = None
                if data3 == u'无' or data3 == '':
                    data3 = None
                tel = data1
                address = data2
                email = data3
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_address,(gs_basic_id,tel,address,email,updated_time,gs_basic_id))
            connect.commit()
        info,flag,url_list = get_url_list(url)
        if flag < 100000001:
            flag = update_basic(info, connect, cursor, gs_basic_id)
    except Exception,e:
        flag = 100000005
        logging.error('basic error %s'%e)
    finally:
        print url_list
        cursor.close()
        connect.close()
        return url_list,flag



