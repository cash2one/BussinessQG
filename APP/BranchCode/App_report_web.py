#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report_web.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  : 用于获取APP接口中的网站信息，
import logging
import time
web_string = 'insert into gs_report_web(gs_basic_id,province,gs_report_id,name,types,website,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Web:
    def name(self,data):

        information = {}
        for i,singledata in enumerate(data):
            uuid = singledata["annlWebsiteId"]
            if "webTypeInterpreted" in singledata.keys():
                types = singledata["webTypeInterpreted"]
            else:
                types = ''
            if "webSitName" in singledata.keys():
                name = singledata["webSitName"]
            else:
                name = ''
            if "domain" in singledata.keys():
                website = singledata["domain"]
            else:
                website = ''
            information[i] = [types, name, website,uuid]
        return information


    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        insert_flag,update_flag= 0,0
        remark = 0
        total = len(information)
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
            return remark,total,insert_flag,update_flag

