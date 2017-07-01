#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import json
import logging
import sys
import time

from  Public_code import Send_Request as Send_Request
from deal_html_code import deal_lable

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s and cate = %s'
share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,types,license_type,license_code,ra_date, ra_ways, true_amount,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_string = 'update gs_shareholder set types = %s ,license_type = %s ,license_code = %s ,ra_date = %s,ra_ways = %s,true_amount = %s ,updated = %s where gs_shareholder_id = %s '


def name(data):
    information = {}
    datalist = data
    # print data
    for i in range(len(datalist)):
        data = datalist[i]
        name = data["inv"]
        license_code = data["bLicNo"]
        license_code = deal_lable(license_code)
        types = data["invType_CN"]
        types = deal_lable(types)
        license_type = data["blicType_CN"]
        detail_check = data["detailCheck"]

        if detail_check == "true":
            detail_key = data["invId"]
            detail_url = "http://www.gsxt.gov.cn/corp-query-entprise-info-shareholderDetail-%s.html" % detail_key
            ra_date, ra_ways, true_amount = deal_detail_content(detail_url)
        else:
            logging.info('无 shareholder 详情信息')
            ra_date, ra_ways, true_amount = None, None, None
        information[i] = [name, license_code, license_type, types, ra_date, ra_ways, true_amount]
    return information


def deal_detail_content(detail_url):
    # print detail_url
    detail_code, status_code = Send_Request().send_requests(detail_url)
    if status_code == 200:
        detail_code = json.loads(detail_code)["data"]
        # if len(detail_code[0])== 0:
        #     content = detail_code[]
        if len(detail_code[1]) != 0:
            content1 = detail_code[1][0]
        elif len(detail_code[0]) != 0:
            content1 = detail_code[0][0]
        if len(content1) != 0:
            if "conDate" in content1.keys():
                ra_date = content1["conDate"]
                ra_date = datetime.datetime.utcfromtimestamp(ra_date / 1000)
                otherStyleTime = ra_date.strftime("%Y-%m-%d")
                ra_date = otherStyleTime
            else:
                ra_date = None
            if "conForm_CN" in content1.keys():
                ra_ways = content1["conForm_CN"]
            else:
                ra_ways = None
            if "subConAm" in content1.keys():
                true_amount = content1["subConAm"]
            else:
                true_amount = None
    return ra_date, ra_ways, true_amount


def update_to_db(gs_basic_id, cursor, connect, information):
    cate = 0
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name, license_code, license_type = information[key][0], information[key][1], information[key][2]
        types, ra_date, ra_ways, true_amount = information[key][3], information[key][4], information[key][5], \
                                               information[key][6]
        try:
            count = cursor.execute(select_string, (gs_basic_id, name, types, cate))

            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(share_string, (
                    gs_basic_id, name, cate, types, license_type, license_code, ra_date, ra_ways, true_amount,
                    updated_time))
                insert_flag += rows_count
                connect.commit()
            elif int(count) == 1:
                gs_shareolder_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(update_string, (
                    types, license_type, license_code, ra_date, ra_ways, true_amount, updated_time, gs_shareolder_id))
                update_flag += rows_count
                connect.commit()
        except Exception, e:
            # print "shareholder error:", e
            logging.error("shareholder error:" % e)

    # print insert_flag,update_flag
    flag = insert_flag + update_flag
    # print flag
    return flag
