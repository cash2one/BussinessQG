#!/usr/bin/env python
# -*- coding:utf-8 -*-


import logging
import sys
import time

from PublicCode import deal_html_code
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

check_string = 'insert  into gs_check(gs_basic_id,types,result,check_date,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_check = 'select gs_check_id from gs_check where gs_basic_id = %s and check_date = %s and types = %s'
update_check_py = 'update gs_py set gs_py_id = %s,gs_check = %s,updated = %s where gs_py_id = %s'
class Check:
    def name(self,data):
        information = {}
        for i,singledata in enumerate(data):
            if "insTypeInterpreted" in singledata.keys():
                types = singledata["insTypeInterpreted"]
            else:
                types = ''
            if 'insResInterpreted' in singledata.keys():
                result = singledata["insResInterpreted"]
            else:
                result = ''
            if "insDate" in singledata.keys():
                check_date = singledata["insDate"]
                check_date = deal_html_code.change_chinese_date(check_date)
            else:
                check_date = '0000-00-00'
            if "insAuthInterpreted" in singledata.keys():
                gov_dept = singledata["insAuthInterpreted"]
            else:
                gov_dept = ''
            information[i] = [types, result, check_date, gov_dept]
        return information


    def update_to_db(self, cursor, connect, gs_basic_id,information):
        insert_flag, update_flag = 0, 0
        total = len(information)
        logging.info("check total:%s"%total)
        flag = 0
        try:
            for key in information.keys():
                types, result = information[key][0], information[key][1]
                check_date, gov_dept = information[key][2], information[key][3]

                count = cursor.execute(select_check, (gs_basic_id, check_date,types))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                    rows_count = cursor.execute(check_string,
                                                (gs_basic_id, types, result, check_date, gov_dept, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            logging.error("check error: %s" % e)
            flag = 100000006
        finally:
            if flag <100000001:
                flag = insert_flag
                logging.info('execute check :%s'%flag)
            return flag,total,insert_flag,update_flag




def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    Judge_status().update_py(gs_py_id,gs_basic_id,Check,"check",data,update_check_py)