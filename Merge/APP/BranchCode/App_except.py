#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import time
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Judge_status
from PublicCode import deal_html_code

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

except_string = 'insert into gs_except(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,out_gov,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_except = 'select gs_except_id from gs_except where gs_basic_id = %s and in_date = %s'
update_except = 'update gs_except set gs_except_id = %s,types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,out_gov = %s,updated = %s where gs_except_id = %s'


class Except:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            types = '经营异常'
            if "speCauseInterpreted" in singledata.keys():
                in_reason = singledata["speCauseInterpreted"]
            else:
                in_reason = ''
            if 'abnTime' in singledata.keys():
                in_date = singledata["abnTime"]
                in_date = deal_html_code.change_chinese_date(in_date)
            else:
                in_date = '0000-00-00'

            if "remExcpResInterpreted" in singledata.keys():
                out_reason = singledata["remExcpResInterpreted"]
                out_reason = deal_html_code.remove_symbol(out_reason)
            else:
                out_reason = ''
            if 'remDate' in singledata.keys():
                out_date = singledata["remDate"]
                out_date = deal_html_code.change_chinese_date(out_date)
            else:
                out_date = '0000-00-00'
            if "decOrgInterpreted" in singledata.keys():
                gov_dept = singledata["decOrgInterpreted"]
            else:
                gov_dept = ''
            if "remOrganInterpreted" in singledata.keys():
                out_gov = singledata["remOrganInterpreted"]
            else:
                out_gov = ''
            information[i] = [types, in_reason, in_date, out_reason, out_date, gov_dept,out_gov]
        return information


    def update_to_db(self,gs_basic_id, information):
        update_flag, insert_flag = 0, 0
        remark = 0
        total = len(information)
        logging.info('except total:%s'%total)
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                types, in_reason, in_date = information[key][0], information[key][1], information[key][2]
                out_reason, out_date, gov_dept = information[key][3], information[key][4], information[key][5]
                out_gov = information[key][6]
                count = cursor.execute(select_except, (gs_basic_id, in_date))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(except_string, (
                    gs_basic_id, types, in_reason, in_date, out_reason, out_date, gov_dept, updated_time))
                    insert_flag += rows_count
                    connect.commit()
                elif count == 1:
                    gs_except_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(update_except, (
                        gs_except_id,types, in_reason,  out_reason, out_date, gov_dept,out_gov, updated_time, gs_except_id))
                    update_flag += rows_count
                    connect.commit()
        except Exception, e:
                remark = 100000006
                logging.error("except error: %s" % e)
        finally:
            cursor.close()
            connect.close()
            if remark < 100000001:
                remark = insert_flag+update_flag
                logging.info("excute except :%s"%remark)
            return remark,total,insert_flag,update_flag
def main(gs_basic_id,data):
   
    Judge_status().update_info(gs_basic_id,Except,"except",data)
   
