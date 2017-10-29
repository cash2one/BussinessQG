#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_stock.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :用于更新股权出质登记信息

import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Bulid_Log import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()




stock_string = 'insert into gs_stock(gs_basic_id,equityno,pledgor,pled_blicno,impam,imporg,imporg_blicno,equlle_date,public_date,type,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_stock = 'select gs_stock_id from gs_stock where gs_basic_id = %s and equityno = %s'
update_stock = 'update gs_stock set gs_basic_id = %s,pledgor = %s,pled_blicno = %s,impam = %s,imporg = %s,imporg_blicno = %s,equlle_date = %s,public_date = %s,type = %s ,updated = %s where gs_stock_id = %s'
update_stock_py = 'update gs_py set gs_py_id = %s,gs_stock = %s ,updated = %s where gs_py_id = %s'

class Stock:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            equityNo = singledata["equityNo"]
            impAm = singledata["impAm"]
            impOrg = singledata["impOrg"]
            impOrgBLicNo = singledata["impOrgBLicNo"]
            # impOrgBLicType_CN = singledata["impOrgBLicType_CN"]
            # impOrgId = singledata["impOrgId"]
            # pledAmUnit = singledata["pledAmUnit"]
            pledBLicNo = singledata["pledBLicNo"]
            # pledBLicType_CN = singledata["pledBLicType_CN"]
            pledgor = singledata["pledgor"]
            type = singledata["type"]
            equPleDate = singledata["equPleDate"]
            equPleDate = change_date_style(equPleDate)
            publicDate = singledata["publicDate"]
            publicDate = change_date_style(publicDate)
            if type == '2':
                type = '无效'
            elif type == '1':
                type = '有效'
            elif type == 'K':
                type = ''
            information[i] = [equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate, type]
        return information


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag, update_flag = 0, 0
        remark = 0
        try:
            for key in information.keys():
                equityNo, pledgor, pledBLicNo = information[key][0], information[key][1], information[key][2]
                impAm, impOrg, impOrgBLicNo = information[key][3], information[key][4], information[key][5]
                equPleDate, publicDate, type = information[key][6], information[key][7], information[key][8]

                count = cursor.execute(select_stock, (gs_basic_id, equityNo))

                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(stock_string, (
                        gs_basic_id, equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate, type,
                        updated_time))
                    insert_flag += rows_count
                    connect.commit()
                elif int(count) == 1:
                    #print equityNo
                    gs_stock_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                    rows_count = cursor.execute(update_stock,
                                                    (gs_basic_id, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate,
                                                     publicDate, type, updated_time, gs_stock_id))
                    # print rows_count
                    update_flag += rows_count
                    connect.commit()
        except Exception, e:
            remark = 100000001
            # print "stock error:", e
            logging.error("stock error: %s" % e)
        finally:
            flag = insert_flag + update_flag
            if remark < 100000001:
                remark = flag
            # print remark
            return remark,insert_flag,update_flag
def main():
    
    pages, perpages = 0, 0
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    Judge(gs_py_id,connect,cursor,gs_basic_id,url,pages,perpages).update_branch(update_stock_py,Stock,"stock")
    cursor.close()
    connect.close()


