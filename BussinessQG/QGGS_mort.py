#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import json
import logging
import sys
import time

import config
from  Public_code import Send_Request as Send_Request
from deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_mort = 'select gs_mort_id from gs_mort where gs_basic_id = %s and code = %s'
mort_string = 'insert into gs_mort(gs_basic_id,id,code, dates, dept, amount, status,cates,period, ranges, remark,updated)' \
              'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_mort = 'update gs_mort set dates = %s, dept = %s, amount = %s, status = %s,cates = %s,period = %s, ranges = %s, remark = %s,updated = %s ' \
              'where gs_mort_id = %s'

select_goods = 'select gs_mort_goods_id from gs_mort_goods where gs_mort_id = %s and name = %s and ownership = %s'
goods_string = 'insert into gs_mort_goods(gs_mort_id,id,gs_basic_id,name,ownership,situation,remark,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
update_goods = 'update gs_mort_goods set situation = %s,remark = %s,updated = %s where gs_mort_goods_id = %s'
goods_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-mortGuaranteeInfo-%s.html'
person_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-mortregpersoninfo-%s.html'
select_person = 'select gs_mort_person_id from gs_mort_person where gs_mort_id = %s and number = %s'
person_string = 'insert into gs_mort_person(gs_mort_id,id,gs_basic_id,name,cert,number,updated) values (%s,%s,%s,%s,%s,%s,%s)'
update_mort_person = 'update gs_mort_person set name = %s,cert = %s,updated = %s where gs_mort_person_id = %s'


def name(data):
    informaiton = {}
    for i in xrange(len(data)):
        singledata = data[i]
        code = singledata["morRegCNo"]
        dates = singledata["regiDate"]
        dates = change_date_style(dates)
        dept = singledata["regOrg_CN"]
        amount = singledata["priClaSecAm"]
        status = singledata["type"]
        if status == '1':
            status = '有效'
        elif status == '2':
            status = '无效'
        morReg_Id = singledata["morReg_Id"]
        url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-mortCreditorRightInfo-%s.html' % morReg_Id
        info = get_info(url, 'mortCreditorRightInfo')
        info = get_mort_credit(info)
        if info == None or len(info) == 0:
            cates, period, ranges, remark = None, None, None, None
        else:
            cates, period, ranges, remark = info[0][0], info[0][1], info[0][2], info[0][3]
        goods_info = get_mort_branch(morReg_Id, goods_url, 'mort_goods')
        person_info = get_mort_branch(morReg_Id, person_url, 'mort_person')
        # print person_info
        informaiton[i] = [code, dates, dept, amount, status, cates, period, ranges, remark, goods_info, person_info]
    return informaiton


def update_to_db(gs_basic_id, cursor, connect, info):
    update_flag, insert_flag = 0, 0
    for key in info.keys():
        code, dates, dept, amount = info[key][0], info[key][1], info[key][2], info[key][3]
        status, cates, period, ranges, remark = info[key][4], info[key][5], info[key][6], info[key][7], info[key][8]
        goods_info = info[key][9]
        person_info = info[key][10]
        try:
            count = cursor.execute(select_mort, (gs_basic_id, code))

            if count == 0:
                m = hashlib.md5()
                m.update(code)
                id = m.hexdigest()
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(mort_string, (
                gs_basic_id, id, code, dates, dept, amount, status, cates, period, ranges, remark, updated_time))
                gs_mort_id = connect.insert_id()
                insert_flag += flag
                connect.commit()
            elif int(count) == 1:
                gs_mort_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(update_mort, (
                dates, dept, amount, status, cates, period, ranges, remark, updated_time, gs_mort_id))
                update_flag += flag
                connect.commit()
            update_goods(gs_mort_id, gs_basic_id, cursor, connect, goods_info)
            update_person(gs_mort_id, gs_basic_id, cursor, connect, person_info)
        except Exception, e:
            print e
            logging.info('mort error :%s' % e)
    total = insert_flag + update_flag
    return total


# 更新抵押物品信息
# def update_goods(gs_mort_id,gs_basic_id,cursor,connect,goods_info):

def update_goods(gs_mort_id, gs_basic_id, cursor, connect, info):
    total = len(info)
    print 'mort_goods :%s' % total
    insert_flag, update_flag = 0, 0
    for key in info.keys():
        name, ownership, situation, remark = info[key][0], info[key][1], info[key][2], info[key][3]
        try:
            count = cursor.execute(select_goods, (gs_mort_id, name, ownership))
            if count == 0:
                m = hashlib.md5()
                m.update(name + ownership)
                id = m.hexdigest()
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(goods_string, (
                    gs_mort_id, id, gs_basic_id, name, ownership, situation, remark, updated_time))
                insert_flag += flag
                connect.commit()
            elif int(count) == 1:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                gs_mort_goods_id = cursor.fetchall()[0][0]
                flag = cursor.execute(update_goods, (situation, remark, updated_time, gs_mort_goods_id))
                update_flag += flag
        except Exception, e:
            logging.info('mort_goods error:%s' % e)
    total = insert_flag + update_flag
    print 'execute mort_goods :%s' % total


# 更新抵押人信息
def update_person(gs_mort_id, gs_basic_id, cursor, connect, info):
    total = len(info)
    print 'person_info :%s' % total
    insert_flag, update_flag = 0, 0
    for key in info.keys():
        name, cert, number = info[key][0], info[key][1], info[key][2]
        try:
            count = cursor.execute(select_person, (gs_mort_id, number))
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                m = hashlib.md5()
                m.update(number)
                id = m.hexdigest()
                flag = cursor.execute(person_string, (gs_mort_id, id, gs_basic_id, name, cert, number, updated_time))
                insert_flag += flag
                connect.commit()
            elif int(count) == 1:
                gs_mort_person_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(update_mort_person, (name, cert, updated_time, gs_mort_person_id))
                update_flag += flag
                connect.commit()
        except Exception, e:
            print e
            logging.info('mort_person error:%s' % e)
    total = insert_flag + update_flag
    print 'execute mort_person:%s' % total


# 向网页发送请求获取信息
def get_info(url, url_pattern):
    result, status_code = Send_Request().send_requests(url)
    data = json.loads(result)["data"]
    if status_code == 200:
        if len(data) == 0:
            data = None
            logging.info('暂无 %s' % url_pattern)
    return data


# 用于获取动产抵押分支信息
def get_mort_branch(morReg_Id, url_pattern, name):
    url = url_pattern % morReg_Id
    # print url
    information = {}
    # data = get_info(url,name)
    data, status = Send_Request().send_requests(url)
    if status == 200 and len(json.loads(data)) != 0:
        # recordsTotal = json.loads(data)["recordsTotal"]
        totalPage = json.loads(data)["totalPage"]
        perpage = json.loads(data)["perPage"]
        page = totalPage
        if page == 1:
            if name == 'mort_goods':
                information = get_info(url, 'mort_goods')
                information = get_single_goods(information)
            elif name == 'mort_person':
                information = get_info(url, 'mort_person')
                information = get_single_person(information)
        elif page > 1:
            if name == 'mort_goods':
                information = get_info(url, 'mort_goods')
                information = get_single_goods(information)
            elif name == 'mort_person':
                information = get_info(url, 'mort_person')
                information = get_single_person(information)
            # information = get_info(url, 'mort_goods')
            for i in range(1, page):
                start = perpage * i
                tempurl = url + '?start=%s' % start
                if name == 'mort_goods':
                    tempinfo = get_info(tempurl, 'mort_goods %s' % start)
                    tempinfo = get_single_goods(tempinfo)
                    information = dict(information, **tempinfo)
                elif name == 'mort_person':
                    tempinfo = get_info(tempurl, 'mort_person %s' % start)
                    tempinfo = get_single_person(tempinfo)
                    information = dict(information, **tempinfo)
    elif data == None:
        logging.info("暂无%s信息" % name)
    return information


# 获取单页的动产抵押信息
def get_single_goods(data):
    information = {}
    if data != None:
        for i in xrange(len(data)):
            singledata = data[i]
            guaId = singledata["guaId"]
            name = singledata["guaName"]
            ownership = singledata["own"]
            situation = singledata["guaDes"]
            remark = singledata["remark"]
            information[guaId] = [name, ownership, situation, remark]
    return information


# 获取单页的抵押人信息
# http://www.gsxt.gov.cn/corp-query-entprise-info-mortregpersoninfo-PROVINCENODENUM4300002c9902d558baa3de015a36605e6a0961.html
def get_single_person(data):
    information = {}
    if data != None:
        for i in xrange(len(data)):
            singledata = data[i]
            name = singledata["more"]
            cert = singledata["bLicType_CN"]
            number = singledata["bLicNo"]
            perId = singledata["perId"]
            information[perId] = [name, cert, number]
    return information


# 被担保主债权信息
# http://www.gsxt.gov.cn/corp-query-entprise-info-mortCreditorRightInfo-PROVINCENODENUM4300002c9902d558baa3de015a36605e6a0961.html

def get_mort_credit(data):
    information = {}
    # print data
    if data != None:
        data = data[0]
        cates = data["priClaSecKind_CN"]
        start_date = data["pefPerForm"]
        start_date = change_date_style(start_date)
        end_date = data["pefPerTo"]
        end_date = change_date_style(end_date)
        period = start_date + '至' + end_date
        ranges = data["warCov"]
        remark = data["remark"]
        information[0] = [cates, period, ranges, remark]
        return information
    elif data == None:
        return information
        logging('暂无被担保主债权信息！')
