#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_permit.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :行政许可信息更新


import hashlib
import logging
import sys
import time
import json
from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Public_code import Send_Request
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()






select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and filename = %s and code = %s and start_date = %s and end_date = %s and source = 1'
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,status,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
permit_alter = 'insert into gs_permit_alter(gs_permit_id,alt_name, alt_date, alt_af, alt_be,updated) values(%s,%s,%s,%s,%s,%s)'
select_permit =  'select gs_permit_alter_id from gs_permit_alter where gs_permit_id = %s and alt_name = %s and alt_date = %s'

class Permit:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            name = singledata["entName"]
            code = singledata["licNo"]
            filename = singledata["licName_CN"]
            start_date = singledata["valFrom"]
            start_date = change_date_style(start_date)
            end_date = singledata["valTo"]
            end_date = change_date_style(end_date)
            content = singledata["licItem"]
            gov_dept = singledata["licAnth"]
            status = singledata["status"]
            licId = singledata["licId"]
            if status=='1':
                status = '有效'
            else:
                status = '无效'
            detail_url ="http://www.gsxt.gov.cn/corp-query-entprise-info-insLicenceDetailInfo-%s.html" % licId
            information[i] = [name, code, filename, start_date, end_date, content, gov_dept,detail_url,status]
        return information

    def get_detail_info(self,url):
        result,status_code = Send_Request().send_requests(url)
        info = {}
        if status_code ==200:
            data = json.loads(result)["list"]
            if len(data) ==0:
                logging.info("暂无permit详情信息")
            else:
                for i,singledata in enumerate(data):
                    alt_name = singledata["alt"]
                    alt_date = singledata["altDate"]
                    alt_date = change_date_style(alt_date)
                    alt_af = singledata["altAf"]
                    alt_be = singledata["altBe"]
                    info[i] = [alt_name,alt_date,alt_af,alt_be]
        return info
    def update_detail_info(self,info,cursor,connect,gs_permit_id):
        try:
            for key in info.keys():
                alt_name, alt_date, alt_af, alt_be = info[key][0],info[key][1],info[key][2],info[key][3]
                count = cursor.execute(select_permit,(gs_permit_id,alt_name,alt_date))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    cursor.execute(permit_alter,(gs_permit_id,alt_name, alt_date, alt_af, alt_be,updated_time))
                    connect.commit()
        except Exception,e:
            logging.error("permit detail error:%s"%e)


    def update_to_db(self,gs_basic_id,information):
        insert_flag,update_flag = 0,0
        remark = 0
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                name, code, filename, start_date = information[key][0], information[key][1], information[key][2], \
                                                   information[key][3]
                end_date, content, gov_dept = information[key][4], information[key][5], information[key][6]
                detail_url = information[key][7]
                status = information[key][8]
                count = cursor.execute(select_string, (gs_basic_id, filename,code,start_date,end_date))
                m = hashlib.md5()
                m.update(code)
                id = m.hexdigest()
                # print filename
                source = 1
                
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(permit_string, (
                        gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, status,source,updated_time))
                    gs_permit_id = connect.insert_id()
                    insert_flag += rows_count
                    connect.commit()
                    info = self.get_detail_info(detail_url)
                    if len(info)==0:
                        logging.info("暂无permit详情信息！")
                    else:
                        self.update_detail_info(info, cursor, connect, gs_permit_id)
                elif int(count )==1:
                    gs_permit_id = cursor.fetchall()[0][0]
                    info = self.get_detail_info(detail_url)
                    if len(info) == 0:
                        logging.info("暂无permit详情信息！")
                    else:
                        self.update_detail_info(info, cursor, connect, gs_permit_id)
        except Exception, e:
            remark = 100000006
            logging.error("permit error: %s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,insert_flag,update_flag

def main(gs_basic_id,url):
    Judge(gs_basic_id,url).update_branch(Permit,"permit2")

