#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_report_web.py
# @Author: Lmm
# @Date  : 2017-07-30
# @Desc  :年报网站信息

import logging
import sys
import time



reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

web_string = 'insert into gs_report_web(gs_basic_id,province,gs_report_id,name,types,website,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Web:
    def name(self,data):
        # print data
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            uuid = singledata["webId"]
            types = singledata["webType"]
            if types == "1":
                types = '网站'
            name = singledata["webSitName"]
            website = singledata["domain"]
            information[i] = [types, name, website,uuid]
        return information


    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        insert_flag,update_flag= 0,0
        remark = 0
        try:
            for key in information.keys():
                name, types, website = information[key][1], information[key][0], information[key][2]
                uuid = information[key][3]
                if name == '0' or website == '0' or name == '无' or website == '无':
                    logging.info('网站信息为零')
                else:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    flag = cursor.execute(web_string,
                    (gs_basic_id, province, gs_report_id, name, types, website,uuid,updated_time, updated_time))
                    connect.commit()
                    insert_flag += flag
        except Exception, e:
            remark = 100000001
            logging.error('web error %s' % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,insert_flag,update_flag
