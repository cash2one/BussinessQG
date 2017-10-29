#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report_party.py
# @Author: Lmm
# @Date  : 2017-08-10
# @Desc  : 用于获取党建信息并更新至数据库

import logging
import time

from PublicCode import config

party_string = 'insert into gs_report_party(gs_basic_id,gs_report_id,uuid,province,if_leaderse,if_leader,types,number,created,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
class Party:
    def name(self,data):
        info = {}
        for i,singledata in enumerate(data):
            uuid = singledata["annlPartyId"]
            if "leaderSecretarySign" in singledata.keys():
                if_leaderse = int(singledata["leaderSecretarySign"])
            else:
                if_leaderse = 0
            if "leaderSign" in singledata.keys():
                if_leader =int(singledata["leaderSign"])
            else:
                if_leader = 0
            if "organType" in singledata.keys():
                types = config.party_type[singledata["organType"]]
            else:
                types = 0
            if "partyNum" in singledata.keys():
                number = int(singledata["partyNum"])
            else:
                number = 0
            info[i] = [uuid,if_leaderse,if_leader,types,number]
        return info

    def update_to_db(self, gs_report_id, gs_basic_id, cursor, connect, info, province):
        insert_flag, update_flag = 0, 0
        remark = 0
        total = len(info)
        try:
            for key in info.keys():
                uuid, if_leaderse, if_leader, types, number = info[key][0],info[key][1],info[key][2],info[key][3],info[key][4]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                count = cursor.execute(party_string,(gs_basic_id,gs_report_id,uuid,province,if_leaderse,if_leader,types,number,updated_time,updated_time))
                connect.commit()
                insert_flag+= count
        except Exception,e:
            remark = 100000006
            logging.error('report party error:%s' % e)
        finally:
            if remark< 100000001:
                remark = insert_flag
            return remark,total,insert_flag,update_flag


