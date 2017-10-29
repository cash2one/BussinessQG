#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_freeze.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取司法协助信息并进行更新


import json
import logging
import sys
import time

from PublicCode.Public_code import Send_Request as Send_Request
from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge



reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()





freeze_string = 'insert into gs_freeze(gs_basic_id,executor, stock_amount, court, notice_no,status,items, rule_no, enforce_no,cert_cate,cert_code, start_date, end_date,period, pub_date,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_freeze = 'select gs_freeze_id from gs_freeze where gs_basic_id = %s and rule_no = %s and executor = %s'
update_freeze_py = 'update gs_py set gs_py_id = %s ,gs_freeze = %s ,updated = %s where gs_py_id = %s'

class Freeze:
    def name(self,data):
        information = {}
        provnum = 0
        for i in xrange(len(data)):
            singledata = data[i]
            executor = singledata["inv"]
            stock_amount = singledata["froAm"]
            if "foramme" in singledata.keys():
                foramme = singledata["foramme"]
            else:
                foramme = '万'

            stock_amount = str(stock_amount) + foramme
            court = singledata["froAuth"]
            notice_no = singledata["executeNo"]
            status = singledata["frozState_CN"]
            parent_Id = singledata["parent_Id"]
            uniscId = singledata["uniscId"]
            regNo = singledata["regNo"]
            if parent_Id != '':
                if uniscId!='':
                    provnum = uniscId[2:4] +'0000'
                    #print provnum
                elif uniscId == '' and regNo!='':
                    provnum = regNo[0:2] +'0000'
                elif regNo == ''and uniscId == '':
                    if parent_Id.startswith('1')==True or parent_Id.startswith('2'):
                        provnum = parent_Id[1:3]+'0000'
                    else:
                        provnum = parent_Id[0:2]+'0000'
                if len(parent_Id)>36:
                    parent_Id = parent_Id[0:36]
                # print regNo,uniscId,parent_Id
                # print provnum
                detail_url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-judiciaryStockfreeze-PROVINCENODENUM%s%s.html' % (
                provnum, parent_Id)
                # print detail_url
                items, rule_no, enforce_no, cert_cate, cert_code, start_date, end_date, period, pub_date = self.deal_detail_content(
                    detail_url)

            information[i] = [executor, stock_amount, court, notice_no, status, items, rule_no, enforce_no, cert_cate,
                              cert_code, start_date, end_date, period, pub_date]
        return information

    #用于处理详情页，获取详情页信息
    def deal_detail_content(self,detail_url):
        result, status_code = Send_Request().send_requests(detail_url)
        # print detail_url
        if status_code == 200:
            recordsTotal =json.loads(result)["data"]
            if recordsTotal!=0:
                data = json.loads(result)["data"][0]
                items = data["executeItem_CN"]
                rule_no = data["froDocNo"]
                enforce_no = data["executeNo"]
                cert_cate = data["bLicType_CN"]
                cert_code = data["bLicNo"]
                start_date = data["froFrom"]
                start_date = change_date_style(start_date)
                end_date = data["froTo"]
                end_date = change_date_style(end_date)
                period = data["frozDeadline"]
                pub_date = data["publicDate"]
                pub_date = change_date_style(pub_date)

        return items, rule_no, enforce_no, cert_cate, cert_code, start_date, end_date, period, pub_date


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag,update_flag = 0,0
        flag = 0
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():

                executor, stock_amount, court, notice_no = information[key][0], information[key][1], information[key][2], \
                                                           information[key][3]
                status, items, rule_no, enforce_no = information[key][4], information[key][5], information[key][6], \
                                                     information[key][7]
                cert_cate, cert_code, start_date, end_date = information[key][8], information[key][9], information[key][10], \
                                                             information[key][11]
                period, pub_date = information[key][12], information[key][13]
                count = cursor.execute(select_freeze, (gs_basic_id, rule_no,executor))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(freeze_string, (
                    gs_basic_id, executor, stock_amount, court, notice_no, status, items, rule_no, enforce_no,
                    cert_cate, cert_code, start_date, end_date, period, pub_date, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            logging.error("freeze error: %s" % e)
            flag = 100000006
        finally:
            cursor.close()
            connect.close()
            if flag <100000001:
                flag = insert_flag
            return flag,insert_flag,update_flag
def main(gs_basic_id,url):
    Judge(gs_basic_id,url).update_branch(Freeze,"freeze")
   
if __name__ =="__main__":
    main()