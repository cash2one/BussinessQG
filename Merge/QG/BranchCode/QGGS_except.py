#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_except.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取异常名录信息，并进行更新

import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Get_BranchInfo
from PublicCode.Judge_Status import Judge

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()



except_string = 'insert into gs_except(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,out_gov,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_except = 'select gs_except_id from gs_except where gs_basic_id = %s and in_date = %s'
select_except_py = 'select  updated from gs_except where gs_basic_id = %s order by updated desc  LIMIT 1'
update_except = 'update gs_except set gs_except_id = %s,types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,out_gov = %s,updated = %s where gs_except_id = %s'


class Except:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            types = '经营异常'
            in_reason = singledata["speCause_CN"]
            in_date = singledata["abntime"]
            in_date = change_date_style(in_date)
            out_reason = singledata["remExcpRes_CN"]
            out_date = singledata["remDate"]
            out_date = change_date_style(out_date)
            gov_dept = singledata["decOrg_CN"]
            information[i] = [types, in_reason, in_date, out_reason, out_date, gov_dept]
        return information


    def update_to_db(self,gs_basic_id,  information):
        update_flag, insert_flag = 0, 0
        remark = 0
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
                    gs_basic_id, types, in_reason, in_date, out_reason, out_date, gov_dept,out_gov, updated_time))
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

            return remark,insert_flag,update_flag

def main(gs_basic_id,url):
    Judge(gs_basic_id, url).update_branch(Except, "except")
   
   

  

