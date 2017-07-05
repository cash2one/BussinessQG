#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import time

from deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
stock_string = 'insert into gs_stock(gs_basic_id,equityNo,pledgor,pledBLicNo,impAm,impOrg,impOrgBLicNo,equPleDate,publicDate,type,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_stock = 'select gs_stock_id from gs_stock where gs_basic_id = %s and equityNo = %s'
update_stock = 'update gs_stock set gs_basic_id = %s,pledgor = %s,pledBLicNo = %s,impAm = %s,impOrg = %s,impOrgBLicNo = %s,equPleDate = %s,publicDate = %s,type = %s ,updated = %s where gs_stock_id = %s'


def name(data):
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
            type = None
        information[i] = [equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate, type]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        equityNo, pledgor, pledBLicNo = information[key][0], information[key][1], information[key][2]
        impAm, impOrg, impOrgBLicNo = information[key][3], information[key][4], information[key][5]
        equPleDate, publicDate, type = information[key][6], information[key][7], information[key][8]
        try:
            count = cursor.execute(select_stock, (gs_basic_id, equityNo))
            # print count
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(stock_string, (
                gs_basic_id, equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate, type,
                updated_time))
                insert_flag += rows_count
                connect.commit()
            elif count == 1:
                gs_stock_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                rows_count = cursor.execute(update_stock,
                                            (gs_basic_id, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate,
                                             publicDate, type, updated_time, gs_stock_id))
                update_flag += rows_count
                connect.commit()
        except Exception, e:
            # print "stock error:", e
            logging.error("stock error:" % e)
    flag = insert_flag + update_flag
    # print insert_flag, update_flag
    # print flag
    return flag
