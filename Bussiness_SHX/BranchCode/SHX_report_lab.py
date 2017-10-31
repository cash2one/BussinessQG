#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_report_lab.py
# @Author: Lmm
# @Date  : 2017-10-24 15:34
# @Desc  :

from PublicCode import deal_html_code
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
import hashlib
import logging
import time

lab_string = 'insert into gs_report_lab(gs_basic_id,gs_report_id,uuid,province,if_owe, if_basenum, if_periodamount,birth_owe, birth_num, birth, birth_base' \
			 ',old_num, old_owe, old, old_base,unemploy, unemploy_base, unemploy_owe, unemploy_num,medical, medical_base, medical_owe, medical_num, ' \
			 'injury, injury_owe, injury_num,created,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Report_Lab:
	def get_info(self, data):
		info = {}
		for key, value in config.report_lab_dict.iteritems():
			info[value] = deal_html_code.get_match_info(key, data)
		# 这两种情况的采集没有太大意义就不再入库
		if info["birth_num"] == '' or info["birth_num"] == '人':
			info = {}
		else:
			# 判定欠费金额，实际缴费金额，缴费基数 是否公示
			# 判定标准选取生育的各个对应信息进行标准，
			# 即认为如果生育、医疗、养老、失业中有一个欠费，实缴，基数是不公示的
			# 则其他的也是不公示的
			if info["birth_owe"] > 0:
				if_owe = 0
			else:
				if_owe = 1
			info["if_owe"] = if_owe
			if info["birth_base"] == 0:
				if_basenum = 0
			else:
				if_basenum = 1
			info["if_basenum"] = if_basenum
			if info["birth"] == 0:
				if_periodamount = 0
			else:
				if_periodamount = 1
			info["if_periodamount"] = if_periodamount
			for key, value in info.iteritems():
				print key, value
				if "if" in key:
					continue
				info[key] = deal_html_code.match_float(value)
		return info
	
	def update_to_db(self, info, gs_basic_id, gs_report_id, year, cursor, connect):
		m = hashlib.md5()
		m.update(str(gs_basic_id) + str(year))
		uuid = m.hexdigest()
		
		try:
			if_owe, if_basenum, if_periodamount = info["if_owe"], info["if_basenum"], info["if_periodamount"]
			birth_owe, birth_num, birth, birth_base = info["birth_owe"], info["birth_num"], info["birth"], info[
				"birth_base"]
			old_num, old_owe, old, old_base = info["old_num"], info["old_owe"], info["old"], info["old_base"]
			unemploy, unemploy_base, unemploy_owe, unemploy_num = info["unemploy"], info["unemploy_base"], info[
				"unemploy_owe"], info["unemploy_num"]
			medical, medical_base, medical_owe, medical_num = info["medical"], info["medical_base"], info[
				"medical_owe"], info["medical_num"]
			injury, injury_owe, injury_num = info["injury"], info["injury_owe"], info["injury_num"]
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			row_count = cursor.execute(lab_string, (
				gs_basic_id, gs_report_id, uuid, config.province, if_owe, if_basenum, if_periodamount, birth_owe,
				birth_num, birth,
				birth_base, old_num, old_owe, old, old_base, unemploy, unemploy_base, unemploy_owe,
				unemploy_num, medical, medical_base, medical_owe, medical_num, injury, injury_owe, injury_num,
				updated_time,
				updated_time))
			connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("lab error %s" % e)
		finally:
			if remark < 100000001:
				remark = row_count
			return remark
