#!/usr/bin/env python
# -*- coding:utf-8 -*-
import hashlib
import logging
import sys
import time



reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

web_string = 'insert into gs_report_web(gs_basic_id,province,gs_report_id,name,types,website,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_web = 'select gs_report_web_id from gs_report_web where gs_report_id = %s and name = %s and website = %s '
update_web = 'update gs_report_web set types = %s,uuid = %s ,updated = %s where gs_report_web_id = %s'


def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        uuid = singledata["anCheId"]
        types = singledata["webType"]
        if types == "1":
            types = '网站'
        name = singledata["webSitName"]
        website = singledata["domain"]
        information[i] = [types, name, website,uuid]
    return information


def update_to_db(gs_report_id, gs_basic_id, cursor, connect, information,province):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name, types, website = information[key][1], information[key][0], information[key][2]
        uuid = information[key][3]
        if name == '0' or website == '0' or name == '无' or website == '无':
            logging.info('网站信息为零')
        else:
            try:
                count = cursor.execute(select_web, (gs_report_id, name, website))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    # print web_string %(gs_basic_id,id, gs_report_id, name, types, website)
                    flag = cursor.execute(web_string,
                                          (gs_basic_id, province, gs_report_id, name, types, website,uuid,updated_time, updated_time))

                    connect.commit()
                    insert_flag += flag
                elif int(count) == 1:
                    gs_report_web_id = cursor.fetchall()[0][0]
                    # print gs_report_web_id
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    flag = cursor.execute(update_web, (types, uuid, updated_time, gs_report_web_id))
                    connect.commit()
                    update_flag += flag
            except Exception, e:
                # print e
                logging.error('web error %s' % e)
    total = insert_flag + update_flag
    return total
