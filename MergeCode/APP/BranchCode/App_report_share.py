#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report_share.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  : 用于获取年报中的发起人及出资信息
import logging
import time

from PublicCode.deal_html_code import change_chinese_date

share_string = 'insert into gs_report_share(gs_basic_id,gs_report_id,province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,unit,created,updated) values ' \
               '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Share:
    def name(self,data):
        information = {}

        for i,singledata in enumerate(data):

            uuid = singledata["annlInvestorId"]
            name = singledata["inv"]
            if len(singledata["entAnnlInvtSet"])!=0:
                entAnnlInvtSet = singledata["entAnnlInvtSet"][0]
                if "subConAm" in entAnnlInvtSet.keys():
                    reg_amount = entAnnlInvtSet["subConAm"]
                else:
                    reg_amount = ''
                if 'conDate' in entAnnlInvtSet.keys():
                    reg_date = entAnnlInvtSet["conDate"]
                    reg_date = change_chinese_date(reg_date)
                else:
                    reg_date = ''
                if "conFormInterpreted" in entAnnlInvtSet.keys():
                    reg_way = entAnnlInvtSet["conFormInterpreted"]
                else:
                    reg_way = ''
                if "currency" in entAnnlInvtSet.keys():
                    unit = entAnnlInvtSet["currency"]
                else:
                    unit = ''
            else:
                reg_amount = ''
                reg_date = '0000-00-00'
                reg_way = ''

            if len(singledata["entAnnlInvtactlSet"])!=0:
                entAnnlInvtactlSet = singledata["entAnnlInvtactlSet"][0]
                if "acConAm" in entAnnlInvtactlSet.keys():
                    ac_amount = entAnnlInvtactlSet["acConAm"]
                else:
                    ac_amount = ''
                if "conDate" in entAnnlInvtactlSet.keys():
                    ac_date = entAnnlInvtactlSet["conDate"]
                    ac_date = change_chinese_date(ac_date)
                else:
                    ac_date = ''
                if "conFormInterpreted" in entAnnlInvtactlSet.keys():
                    ac_way = entAnnlInvtactlSet["conFormInterpreted"]
                else:
                    ac_way = ''
                if "currency" in entAnnlInvtactlSet.keys():  
                    unit = entAnnlInvtactlSet["currency"]
                else:
                    unit = ''

            else:
                ac_amount = ''
                ac_date = ''
                ac_way = ''

            information[i] = [name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,unit]
        return information


    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        insert_flag,update_flag = 0,0
        remark = 0
        total = len(information)
        try:
            for key in information.keys():
                name, uuid, reg_amount, reg_date = information[key][0], information[key][1], information[key][2], \
                                                  information[key][3]
                reg_way, ac_amount, ac_date, ac_way = information[key][4], information[key][5], information[key][6], \
                                                         information[key][7]
                unit = information[key][8]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(share_string, (
                            gs_basic_id, gs_report_id,  province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,unit,updated_time,updated_time))
                connect.commit()
                insert_flag += flag
        except Exception, e:
            remark = 100000006
            logging.error('share error %s' % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,total,insert_flag,update_flag