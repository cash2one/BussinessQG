#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_permit2.py
# @Author: Lmm
# @Date  : 2017-08-14
# @Desc  :


import logging
import sys
import time
from SPublicCode.Public_code import Judge_status
from SPublicCode import deal_html_code
from SPublicCode.Public_code import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and filename = %s and code = %s and start_date = %s and end_date = %s'
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,status,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
permit_alter = 'insert into gs_permit_alter(gs_permit_id,alt_name, alt_date, alt_af, alt_be,updated) values(%s,%s,%s,%s,%s,%s)'
select_permit =  'select gs_permit_alter_id from gs_permit_alter where gs_permit_id = %s and alt_name = %s and alt_date = %s'

class Permit:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            name = ''
            code = singledata["licNo"]
            if "licName" in singledata.keys():
                filename = singledata["licName"]
            else:
                filename = ''
            if 'valFrom' in singledata.keys():
                start_date = singledata["valFrom"]
                start_date = deal_html_code.change_chinese_date(start_date)
            else:
                start_date = None
            if "valTo" in singledata.keys():

                end_date = singledata["valTo"]
                end_date = deal_html_code.change_chinese_date(end_date)
            else:
                end_date = None
            if 'licItem' in singledata.keys():
                content = singledata["licItem"]
            else:
                content = ''
            if 'licAuth' in singledata.keys():
                gov_dept = singledata["licAuth"]
            else:
                gov_dept = ''
            if 'typeInterpreted' in singledata.keys():
                status = singledata["typeInterpreted"]
            else:
                status = ''
            entShrpmtAltItemSet = singledata["entOthAltItemSet"]
            if len(entShrpmtAltItemSet)== 0:
                logging.info('暂无行政许可变更信息！！！')
                alter_info = {}
            else:
                alter_info = singledata["entOthAltItemSet"]

            information[i] = [name, code, filename, start_date, end_date, content, gov_dept,status,alter_info]
        return information

    def get_alter_permit(self,info):
        information = {}

        for i, singledata in enumerate(info):
            alt_name = singledata["altName"]
            alt_date = singledata["altDate"]
            alt_date = deal_html_code.change_chinese_date(alt_date)
            if "altAf" in singledata.keys():
                alt_af = singledata["altAf"]
            else:
                alt_af = ''
            if 'altBe' in singledata.keys():
                alt_be = singledata["altBe"]
            else:
                alt_be = ''
            information[i] = [alt_name, alt_date, alt_af, alt_be]
        return information


    def update_to_db(self,cursor, connect, gs_basic_id,information):
        insert_flag,update_flag = 0,0
        remark = 0
        total = len(information)
        logging.info(" permit2 total: %s"%total)
        try:
            for key in information.keys():
                name, code, filename, start_date = information[key][0], information[key][1], information[key][2], \
                                                   information[key][3]
                end_date, content, gov_dept = information[key][4], information[key][5], information[key][6]
                status = information[key][7]
                alt_info = information[key][8]
                count = cursor.execute(select_string, (gs_basic_id, filename,code,start_date,end_date))
                id = ''

                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(permit_string, (
                        gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, status,updated_time))
                    gs_permit_id = connect.insert_id()
                    insert_flag += rows_count
                    connect.commit()
                    info = self.get_alter_permit(alt_info)
                    self.update_detail_info(info,cursor,connect,gs_permit_id)
                elif int(count)==1:
                    gs_permit_id = cursor.fetchall()[0][0]
                    info = self.get_alter_permit(alt_info)
                    self.update_detail_info(info, cursor, connect, gs_permit_id)
        except Exception, e:
            remark = 100000006
            logging.error("permit error: %s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
                logging.info("execute permit2:%s"%remark)
            # print remark
            return remark,total,insert_flag,update_flag
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
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    print_info = Judge_status().update_py(gs_basic_id,Permit,"permit2",data)
    return print_info


