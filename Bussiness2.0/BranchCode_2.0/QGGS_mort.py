#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_mort.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取动产抵押信息并进行更新

import hashlib
import json
import logging
import sys
import time

from PublicCode.Public_code import Send_Request as Send_Request
from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Bulid_Log import Log

# url = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_py_id = sys.argv[3]
url = 'http://www.gsxt.gov.cn/%7BBkWuG51z8_CwdB0OOclio5jWh7D5HQNDl3t-DW8LlCq9-f5S12GIcLQPO3LJGqtdDhBCBt_kTIWdEjDWOtx234IoswVN4Lc1SFQGr-M3Ne47gm5vCVqCDHzOAwnsx6SN-1502677219108%7D'
gs_basic_id = 229421822
gs_py_id = 1501
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_mort = 'select gs_mort_id from gs_mort where gs_basic_id = %s and code = %s'
mort_string = 'insert into gs_mort(gs_basic_id,id,code, dates, dept, amount, status,cates,period, ranges, remark,updated)' \
              'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_mort = 'update gs_mort set gs_mort_id = %s ,dates = %s, dept = %s, amount = %s, status = %s,cates = %s,period = %s, ranges = %s, remark = %s,updated = %s ' \
              'where gs_mort_id = %s'

select_goods = 'select gs_mort_goods_id from gs_mort_goods where gs_mort_id = %s and name = %s and ownership = %s situation = %s'
goods_string = 'insert into gs_mort_goods(gs_mort_id,id,gs_basic_id,name,ownership,situation,remark,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
update_goods_sql = 'update gs_mort_goods set gs_mort_goods_id = %s,situation = %s,remark = %s,updated = %s where gs_mort_goods_id = %s'
goods_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-mortGuaranteeInfo-%s.html'
person_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-mortregpersoninfo-%s.html'
select_person = 'select gs_mort_person_id from gs_mort_person where gs_mort_id = %s and name = %s'
person_string = 'insert into gs_mort_person(gs_mort_id,id,gs_basic_id,name,cert,number,updated) values (%s,%s,%s,%s,%s,%s,%s)'
update_mort_person = 'update gs_mort_person set gs_mort_person_id = %s,name = %s,cert = %s,updated = %s where gs_mort_person_id = %s'

person_py = 'update gs_py set gs_py_id = %s,gs_mort_goods = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
goods_py = 'update gs_py set gs_py_id = %s, gs_mort_person = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'

update_mort_py = 'update gs_py set gs_py_id = %s,gs_mort = %s,updated = %s where gs_py_id = %s'
class Mort:

    def name(self,data):
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
            info = self.get_info(url, 'mortCreditorRightInfo')
            info = self.get_mort_credit(info)
            if info == None or len(info) == 0:
                cates, period, ranges, remark = None, None, None, None
            else:
                cates, period, ranges, remark = info[0][0], info[0][1], info[0][2], info[0][3]
            goods_info = self.get_mort_branch(morReg_Id, goods_url, 'mort_goods')
            person_info = self.get_mort_branch(morReg_Id, person_url, 'mort_person')
            # print person_info
            informaiton[i] = [code, dates, dept, amount, status, cates, period, ranges, remark, goods_info, person_info]
        return informaiton


    def update_to_db(self,gs_py_id,gs_basic_id, cursor, connect, info):
        update_flag, insert_flag = 0, 0
        mort_flag = 0
        try:
            for key in info.keys():
                code, dates, dept, amount = info[key][0], info[key][1], info[key][2], info[key][3]
                status, cates, period, ranges, remark = info[key][4], info[key][5], info[key][6], info[key][7], info[key][8]
                goods_info = info[key][9]
                person_info = info[key][10]

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
                    flag = cursor.execute(update_mort, (gs_mort_id,
                    dates, dept, amount, status, cates, period, ranges, remark, updated_time, gs_mort_id))
                    update_flag += flag
                    connect.commit()
                self.update_goods_py(gs_py_id,gs_mort_id, gs_basic_id, cursor, connect, goods_info)
                self.update_person_py(gs_py_id,gs_mort_id, gs_basic_id, cursor, connect, person_info)
        except Exception, e:
            logging.info('mort error :%s' % e)
            mort_flag = 100000006
        finally:
            total = insert_flag + update_flag
            if mort_flag <100000001:
                mort_flag = total
            return mort_flag,insert_flag,update_flag


    def update_goods_py(self,gs_py_id,gs_mort_id, gs_basic_id, cursor, connect, goods_info):
        try:
            total, execute = self.update_goods(gs_mort_id, gs_basic_id, cursor, connect, goods_info)
            if total == 0:
                flag = None
            elif total > 0 and execute>=0 and execute< 100000001:
                flag = execute
            elif total > 0 and execute > 100000001:
                flag = 100000006

        except Exception, e:
            flag = 100000006
            logging.error("mort goods error %s" % e)
        finally:
            if flag == None:
                pass
            else:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(goods_py, (gs_py_id,flag, updated_time,gs_basic_id,gs_py_id))
                connect.commit()

    def update_person_py(self,gs_py_id,gs_mort_id, gs_basic_id, cursor, connect, person_info):
        try:
            total, execute = self.update_person(gs_mort_id, gs_basic_id, cursor, connect, person_info)
            if total == 0:
                flag = None
            elif total > 0 and execute>=0 and execute< 100000001:
                flag = execute
            elif total > 0 and execute > 100000001:
                flag = 100000006

        except Exception, e:
            flag = 100000006
            logging.error("mort goods error %s" % e)
        finally:
            if flag == None:
                pass
            else:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(person_py, (gs_py_id,flag, updated_time ,gs_basic_id,gs_py_id))
                connect.commit()
    # 更新抵押物品信息
    def update_goods(self,gs_mort_id, gs_basic_id, cursor, connect, info):
        total = len(info)
        logging.info('mort_goods :%s' % total)
        goods_flag = 0
        insert_flag, update_flag = 0, 0
        try:
            for key in info.keys():
                name, ownership, situation, remark = info[key][0], info[key][1], info[key][2], info[key][3]

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
                    flag = cursor.execute(update_goods_sql, (gs_mort_goods_id,situation, remark, updated_time, gs_mort_goods_id))
                    update_flag += flag
        except Exception, e:
            goods_flag = 100000006
            logging.info('mort_goods error:%s' % e)
        finally:
            executetotal = insert_flag + update_flag
            if goods_flag < 100000001:
                goods_flag = executetotal
            logging.info( 'execute mort_goods :%s' % executetotal)
            return total,goods_flag




    # 更新抵押人信息
    def update_person(self,gs_mort_id, gs_basic_id, cursor, connect, info):
        total = len(info)
        logging.info('person_info :%s' % total)
        insert_flag, update_flag = 0, 0
        person_flag = 0
        try:
            for key in info.keys():
                name, cert, number = info[key][0], info[key][1], info[key][2]

                count = cursor.execute(select_person, (gs_mort_id, name))
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
                    flag = cursor.execute(update_mort_person, (gs_mort_person_id,name, cert, updated_time, gs_mort_person_id))
                    update_flag += flag
                    connect.commit()
        except Exception, e:
            person_flag = 100000006
            logging.info('mort_person error:%s' % e)
        finally:
            executetotal = insert_flag + update_flag
            if person_flag < 100000001:
                person_flag = executetotal
                logging.info('execute mort_person:%s' % executetotal)
            return total,person_flag



    # 向网页发送请求获取信息
    def get_info(self,url, url_pattern):
        result, status_code = Send_Request().send_requests(url)
        data = json.loads(result)["data"]
        if status_code == 200:
            if len(data) == 0:
                data = None
                logging.info('暂无 %s' % url_pattern)
        return data


    # 用于获取动产抵押分支信息
    def get_mort_branch(self,morReg_Id, url_pattern, name):
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
                    information = self.get_info(url, 'mort_goods')
                    information = self.get_single_goods(information)
                elif name == 'mort_person':
                    information = self.get_info(url, 'mort_person')
                    information = self.get_single_person(information)
            elif page > 1:
                if name == 'mort_goods':
                    information = self.get_info(url, 'mort_goods')
                    information = self.get_single_goods(information)
                elif name == 'mort_person':
                    information = self.get_info(url, 'mort_person')
                    information = self.get_single_person(information)
                # information = get_info(url, 'mort_goods')
                for i in range(1, page):
                    start = perpage * i
                    tempurl = url + '?start=%s' % start
                    if name == 'mort_goods':
                        tempinfo = self.get_info(tempurl, 'mort_goods %s' % start)
                        tempinfo = self.get_single_goods(tempinfo)
                        information = dict(information, **tempinfo)
                    elif name == 'mort_person':
                        tempinfo = self.get_info(tempurl, 'mort_person %s' % start)
                        tempinfo = self.get_single_person(tempinfo)
                        information = dict(information, **tempinfo)
        elif data == None:
            logging.info("暂无%s信息" % name)
        return information


    # 获取单页的动产抵押信息
    def get_single_goods(self,data):
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
    def get_single_person(self,data):
        information = {}
        if data != None:
            for i in xrange(len(data)):
                singledata = data[i]
                name = singledata["more"]
                cert = singledata["bLicType_CN"]
                number = singledata["bLicNo"]
                perId = singledata["perId"]
                # remark = singledata["remark"]
                information[perId] = [name, cert, number]
        return information


    # 被担保主债权信息
    # http://www.gsxt.gov.cn/corp-query-entprise-info-mortCreditorRightInfo-PROVINCENODENUM4300002c9902d558baa3de015a36605e6a0961.html

    def get_mort_credit(self,data):
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
def main():
    Log().found_log(gs_py_id,gs_basic_id)
    pages, perpages = 0, 0
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    Judge(gs_py_id,connect,cursor,gs_basic_id,url,pages,perpages).update_branch(update_mort_py,Mort,"mort")
    cursor.close()
    connect.close()

if __name__ =="__main__":
    main()
