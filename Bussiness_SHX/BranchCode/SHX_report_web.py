#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_report_web.py
# @Author: Lmm
# @Date  : 2017-10-24 15:37
# @Desc  : 用于获取年报中的网站信息
from PublicCode import config
from PublicCode import deal_html_code
import logging
import hashlib
import time

web_string = 'insert into gs_report_web(gs_basic_id,province,gs_report_id,name,types,website,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Report_Web:
	def get_info(self, data):
		tr_list = data.xpath(".//tr")
		info = {}
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			if len(td_list) == 0 or len(td_list) == 1:
				continue
			temp["name"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["types"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["website"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id, gs_report_id, cursor, connect):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			for key, value in info.iteritems():
				name, types, website = value["name"], value["types"], value["website"]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id) + str(key))
				uuid = m.hexdigest()
				if name == '0' or website == '0' or name == '无' or website == '无':
					logging.info('网站信息为零')
				else:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(web_string,
										  (gs_basic_id, config.province, gs_report_id, name, types, website, uuid,
										   updated_time,
										   updated_time))
					connect.commit()
					insert_flag += flag
		except Exception, e:
			remark = 100000006
			logging.error('web error %s' % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
