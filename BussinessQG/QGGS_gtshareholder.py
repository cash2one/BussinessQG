#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import sys
import time

from deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and reg_amount = %s and true_amount = %s and cate = %s'
share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,reg_amount,ra_date,ra_ways,true_amount,ta_date,ta_ways,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_string = 'update gs_shareholder set ra_date = %s,ra_ways = %s,ta_date = %s,ta_ways = %s,updated = %s where gs_shareholder_id = %s '
def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        name = singledata["inv"]
        subDetails = singledata["subDetails"][0]
        reg_amount = subDetails["subConAmStr"]
        ra_date = subDetails["currency"]
        ra_date = change_date_style(ra_date)
        ra_ways = subDetails["subConForm_CN"]
        aubDetails = singledata["aubDetails"][0]
        true_amount = aubDetails["acConAmStr"]
        ta_date = aubDetails["conDate"]
        ta_date = change_date_style(ta_date)
        ta_ways = aubDetails["acConFormName"]
        information[i] = [name,reg_amount,ra_date,ra_ways,true_amount,ta_date,ta_ways]
    return information
def update_to_db(gs_basic_id,cursor,connect,information):
    cate = 2
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name, reg_amount, ra_date, ra_ways = information[key][0],information[key][1],information[key][2],information[key][3]
        true_amount, ta_date, ta_ways = information[key][4],information[key][5],information[key][6]

        try:
            count = cursor.execute(select_string, (gs_basic_id, name, reg_amount,true_amount, cate))

            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(share_string, (
                    gs_basic_id, name, cate, reg_amount, ra_date, ra_ways, true_amount, ta_date, ta_ways, updated_time))
                insert_flag += rows_count
                connect.commit()
            elif int(count) == 1:
                gs_shareolder_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(update_string, (
                    ra_date, ra_ways, ta_date, ta_ways,updated_time, gs_shareolder_id))
                update_flag += rows_count
                connect.commit()
        except Exception, e:
            # print "shareholder error:", e
            print e
            logging.error("gt_shareholder error:" % e)

    # print insert_flag,update_flag
    flag = insert_flag + update_flag
    return flag






