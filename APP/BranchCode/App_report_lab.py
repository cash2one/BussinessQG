#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report_lab.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  : App接口中的社保信息获取及更新
import logging
import time
import json

lab_string = 'insert into gs_report_lab(gs_basic_id,gs_report_id,uuid,province,if_owe, if_basenum, if_periodamount,birth_owe, birth_num, birth, birth_base' \
             ',old_num, old_owe, old, old_base,unemploy, unemploy_base, unemploy_owe, unemploy_num,medical, medical_base, medical_owe, medical_num, '\
    'injury, injury_owe, injury_num,created,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
lab_py = 'update gs_py set gs_py_id = %s,report_lab = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'


class Lab:
    def name(self,info):
        information = {}
        data = info[0]
        uuid = data["annlId"]
        if_owe = int(data["arrearsAmountSign"])
        if_basenum = int(data["baseNumSign"])
        if_periodamount = int(data["periodAmountSign"])
        birth_owe = data["socBirthArrearsAmount"]
        birth_num = data["socBirthNum"]
        birth = data["socBirthPeriodAmount"]
        birth_base = data["socBirthBaseNum"]
        old_num = data["socOldNum"]
        old_owe = data["socOldArrearsAmount"]
        old = data["socOldPeriodAmount"]
        old_base = data["socOldBaseNum"]
        unemploy = data["socUnemploymentPeriodAmount"]
        unemploy_base = data["socUnemploymentPeriodAmount"]
        unemploy_owe = data["socUnemploymentArrearsAmount"]
        unemploy_num = data["socUnemploymentNum"]
        medical = data["socMedicalPeriodAmount"]
        medical_base = data["socMedicalBaseNum"]
        medical_owe = data["socMedicalArrearsAmount"]
        medical_num = data["socMedicalMum"]
        injury = data["socInjuryPeriodAmount"]
        injury_owe = data["socInjuryArrearsAmount"]
        injury_num = data["socInjuryNum"]
        information[0] = [uuid,if_owe,if_basenum,if_periodamount,birth_owe,birth_num,birth,birth_base,old_num,old_owe,old,old_base,
                           unemploy,unemploy_base,unemploy_owe,unemploy_num,medical,medical_base,medical_owe,medical_num,injury,injury_owe,injury_num]

        return information
    def update_to_db(self,gs_report_id, gs_basic_id,gs_py_id,cursor, connect, info,province):
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
            remark = 100000006
            logging.error("lab error %s" % e)
        finally:
            if remark <100000001:
                remark = row_count
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(lab_py, (gs_py_id, remark, updated_time, gs_basic_id, gs_py_id))
            connect.commit()
            return remark