#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_report_invest.py
# @Author: Lmm
# @Date  : 2017-10-24 15:34
# @Desc  : 用于获取年报中的对外投资信息
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import traceback
import hashlib
import logging
import time

out_invest_string = 'insert into gs_report_invest(gs_basic_id,gs_report_id,province,name, code, ccode,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Report_Invest:
	def get_info(self, data):
		info = {}
		tr_list = data.xpath(".//tr")
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			if len(td_list) == 0 or len(td_list) == 1:
				continue
			temp["name"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["code"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			if temp["code"].startswith("9"):
				temp["ccode"] = temp["code"]
			else:
				temp["ccode"] = ''
			info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id, gs_report_id, cursor, connect):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			
			for key, value in info.iteritems():
				name = value["name"]
				code = value["code"]
				ccode = value["ccode"]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id) + str(key))
				uuid = m.hexdigest()
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				# print out_invest_string % (
				# 	gs_basic_id, gs_report_id, config.province, name, code, ccode, uuid, updated_time, updated_time)
				flag = cursor.execute(out_invest_string, (
					gs_basic_id, gs_report_id, config.province, name, code, ccode, uuid, updated_time, updated_time))
				connect.commit()
				insert_flag += flag
		except Exception, e:
			print traceback.format_exc()
			remark = 100000006
			logging.error('invest error %s' % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
