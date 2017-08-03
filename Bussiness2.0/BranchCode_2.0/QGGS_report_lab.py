#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_report_lab.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :年报中的社保信息

import logging
import sys
import time
import json
from PublicCode.Public_code import Send_Request

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

lab_string = 'insert into gs_report_lab(gs_basic_id,gs_report_id,uuid,province,if_owe, if_basenum, if_periodamount,birth_owe, birth_num, birth, birth_base' \
             ',old_num, old_owe, old, old_base,unemploy, unemploy_base, unemploy_owe, unemploy_num,medical, medical_base, medical_owe, medical_num, '\
    'injury, injury_owe, injury_num,created,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
lab_py = 'update gs_py set gs_py_id = %s,report_lab = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
def name(url):
    result,status_code =Send_Request().send_requests(url)
    recordsTotal = json.loads(result)["recordsTotal"]
    info = {}
    if status_code == 200:
        data = json.loads(result)["data"]
        if len(data)> 0:
            data = data[0]
            info = {}
            uuid = data["soseId"]
            if_owe = int(data["unpaidSocialInsDis"])
            if_basenum = int(data["totalWagesDis"])
            if_periodamount = int(data["totalPaymentDis"])
            birth_owe = data["unpaidSocialInsSo510"]
            birth_num = data["so510"]
            birth = data["totalPaymentSo510"]
            birth_base = data["totalWagesSo510"]
            old_num = data["so110"]
            old_owe = data["unpaidSocialInsSo110"]
            old = data["totalPaymentSo110"]
            old_base = data["totalWagesSo110"]
            unemploy = data["totalPaymentSo210"]
            unemploy_base = data["totalWagesSo210"]
            unemploy_owe = data["unpaidSocialInsSo210"]
            unemploy_num = data["so210"]
            medical = data["totalPaymentSo310"]
            medical_base = data["totalWagesSo310"]
            medical_owe = data["unpaidSocialInsSo310"]
            medical_num = data["so310"]
            injury = data["totalPaymentSo410"]
            injury_owe = data["unpaidSocialInsSo410"]
            injury_num = data["so410"]
            info[0] = [uuid,if_owe,if_basenum,if_periodamount,birth_owe,birth_num,birth,birth_base,old_num,old_owe,old,old_base,\
                       unemploy,unemploy_base,unemploy_owe,unemploy_num,medical,medical_base,medical_owe,medical_num,injury,injury_owe,injury_num]

    return info
def update_to_db(gs_report_id, gs_basic_id,gs_py_id, cursor, connect, info,province):
    remark = 0
    try:
        uuid, if_owe, if_basenum, if_periodamount = info[0][0],info[0][1],info[0][2],info[0][3]
        birth_owe, birth_num, birth, birth_base = info[0][4],info[0][5],info[0][6],info[0][7]
        old_num, old_owe, old, old_base = info[0][8],info[0][9],info[0][10],info[0][11]
        unemploy, unemploy_base, unemploy_owe, unemploy_num = info[0][12],info[0][13],info[0][14],info[0][15]
        medical, medical_base, medical_owe, medical_num = info[0][16],info[0][17],info[0][18],info[0][19]
        injury, injury_owe, injury_num = info[0][20],info[0][21],info[0][22]
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        row_count = cursor.execute(lab_string,(gs_basic_id,gs_report_id,uuid,province,if_owe, if_basenum, if_periodamount,birth_owe, birth_num, birth, birth_base \
                                       , old_num, old_owe, old, old_base, unemploy, unemploy_base, unemploy_owe,
                                   unemploy_num, medical, medical_base, medical_owe, medical_num,injury, injury_owe, injury_num,updated_time,updated_time))
        connect.commit()
    except Exception, e:
        remark = 100000001
        logging.error("lab error %s" % e)
    finally:
        if remark <100000001:
            remark = row_count
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        cursor.execute(lab_py,(gs_py_id,remark,updated_time,gs_basic_id,gs_py_id))
        connect.commit()
        return remark

