#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report_schange.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  :用于app年报中的股权变更信息并插入到数据库中

import logging
import time

from PublicCode.deal_html_code import change_chinese_date

schange_string = 'insert into gs_report_schange(gs_basic_id,gs_report_id,province,name,percent_pre,percent_after,dates,uuid,created,updated)values' \
                 '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Schange:
    def name(self,data):
        information = {}
        for i,singledata in enumerate(data):
            uuid = singledata["annlStocktransId"]
            if "invBe" in singledata.keys():
                name = singledata["invBe"]
            else:
                name = ''
            if "transamProBe" in singledata.keys():
                percent_pre = singledata["transamProBe"]
            else:
                percent_pre = ''
            if "transamProAf" in singledata.keys():
                percent_after = singledata["transamProAf"]
            else:
                percent_after = ''
            if "altDate" in singledata.keys():
                dates = singledata["altDate"]
                dates = change_chinese_date(dates)
            else:
                dates = '0000-00-00'

            information[i] = [name, percent_pre, percent_after, dates,uuid]
        return information


    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        insert_flag,update_flag = 0,0
        remark = 0
        total = len(information)
        try:
            for key in information.keys():
                name, percent_pre, percent_after, dates = information[key][0], information[key][1], information[key][2], \
                                                          information[key][3]
                uuid = information[key][4]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(schange_string, (
                        gs_basic_id, gs_report_id,province, name, percent_pre, percent_after, dates,uuid,updated_time, updated_time))
                connect.commit()
                insert_flag += flag

        except Exception, e:
            remark = 100000006
            logging.error('schange error %s' % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,total,insert_flag,update_flag
