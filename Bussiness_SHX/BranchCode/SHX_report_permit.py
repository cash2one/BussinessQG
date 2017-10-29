#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_report_permit.py
# @Author: Lmm
# @Date  : 2017-10-24 15:36
# @Desc  : 用于获得行政许可信息

from PublicCode import deal_html_code
from PublicCode import config
import logging
import hashlib
import time

permit_string = 'insert into gs_report_permit(gs_basic_id,gs_report_id,uuid,province,types,valto,created,updated)' \
				'values(%s,%s,%s,%s,%s,%s,%s,%s)'


class Report_Permit:
	def get_info(self, data):
		tr_list = data.xpath("//tr")
		info = {}
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			if len(td_list) == 0:
				continue
			temp["types"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			valto = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["valto"] = deal_html_code.change_chinese_date(valto)
			info[i] = temp
	
	def update_to_db(self, info, gs_basic_id, gs_report_id, cursor, connect):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			for key, value in info.iteritems():
				types, valto = value["types"], value["valto"]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id) + str(key))
				uuid = m.hexdigest()
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(permit_string, (
					gs_basic_id, gs_report_id, uuid, config.province, types, valto, updated_time, updated_time))
				insert_flag += flag
				connect.commit()
		except Exception, e:
			remark = 100000006
			logging("permit error %s" % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
