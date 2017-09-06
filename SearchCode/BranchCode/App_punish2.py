#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_punish2.py
# @Author: Lmm
# @Date  : 2017-08-14
# @Desc  : 用于获取工商公示的信息
import hashlib
import logging
import sys
import time
from SPublicCode.Public_code import Judge_status
from SPublicCode import deal_html_code
from SPublicCode.Public_code import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


punish_string = 'insert into gs_punish(gs_basic_id,id,number, types, content,date, pub_date, gov_dept,name,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'

class Punish:
    #entOthPunishSet
    def name(self,data):
        information = {}
        if len(data)>0:
            for i,singledata in enumerate(data):
                number = singledata["penDecNo"]
                if "illegActType" in data.keys():
                    types = singledata["illegActType"]
                elif "illegAct" in data.keys():
                    types = singledata["illegAct"]
                if "penPunishCon" in singledata.keys():
                    content = singledata["penPunishCon"]
                else:
                    content = ''
                if 'penDecissDate' in singledata.keys():
                    date = singledata["penDecissDate"]
                    date = deal_html_code.change_chinese_date(date)
                else:
                    date = ''
                if "noticeDate"  in singledata.keys():
                    updateDate = singledata["noticeDate"]
                    pub_date = deal_html_code.change_chinese_date(updateDate)
                else:
                    pub_date = None
                if "penOrgan" in singledata.keys():
                    gov_dept = singledata["penOrgan"]
                else:
                    gov_dept = ''
                name = None
                information[i] = [number, types, content, date, name, gov_dept,pub_date]
        return information


    def update_to_db(self, cursor, connect,gs_basic_id, information):
        insert_flag,update_flag = 0,0
        remark = 0
        total = len(information)
        logging.info("punish2 total:%s"%total)
        try:
            for key in information.keys():
                number, types, content = information[key][0], information[key][1], information[key][2]
                date, name, gov_dept = information[key][3], information[key][4], information[key][5]
                pdfurl,pub_date = information[key][6],information[key][7]
                count = cursor.execute(select_punish, (gs_basic_id, number))
                if count == 0:
                    m = hashlib.md5()
                    m.update(str(number))
                    id = m.hexdigest()
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(punish_string, (
                    gs_basic_id, id,number, types, content, date, pub_date, gov_dept,name,pdfurl, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("punish2 error:%s" % e)
        finally:
            if remark<100000001:
                remark = insert_flag
                logging.info("execute punish2:%s "%remark)
            # print remark
            return remark,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    print_info = Judge_status().updaye_py(gs_basic_id,Punish,"punish2",data)
    return print_info

