#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,reg_amount,ra_date,ra_ways,true_amount,ta_date,ta_ways,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        name = singledata["inv"]

        subDetails = singledata["subDetails"]

        if len(subDetails)!=0:
            subDetails = singledata["subDetails"][0]
        else:
            subDetails = None
        if subDetails!= None:
            reg_amount = subDetails["subConAmStr"]
            ra_date = subDetails["currency"]
            ra_date = change_date_style(ra_date)
            ra_ways = subDetails["subConForm_CN"]
        else:
            reg_amount, ra_date, ra_ways = None,None,None
        aubDetails = singledata["aubDetails"]
        if len(aubDetails)!= 0:
            aubDetails = singledata["aubDetails"][0]
        else:
            aubDetails = None
        if subDetails!=None:
            true_amount = aubDetails["acConAmStr"]
            ta_date = aubDetails["conDate"]
            ta_date = change_date_style(ta_date)
            ta_ways = aubDetails["acConFormName"]
        else:
            true_amount, ta_date, ta_ways = None, None, None
        information[i] = [name,reg_amount,ra_date,ra_ways,true_amount,ta_date,ta_ways]
    return information
def update_to_db(gs_basic_id,cursor,connect,information):
    cate = 2
    insert_flag = 0
    remark = 0
    try:
        for key in information.keys():
            name, reg_amount, ra_date, ra_ways = information[key][0],information[key][1],information[key][2],information[key][3]
            true_amount, ta_date, ta_ways = information[key][4],information[key][5],information[key][6]

            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            rows_count = cursor.execute(share_string, (
                    gs_basic_id, name, cate, reg_amount, ra_date, ra_ways, true_amount, ta_date, ta_ways, updated_time))
            insert_flag += rows_count
            connect.commit()

    except Exception, e:
        remark = 100000001
        logging.error("gt_shareholder error: %s" % e)
    finally:
        if remark < 100000001:
            remark = insert_flag
        return remark






