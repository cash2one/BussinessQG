#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_report_assure.py
# @Author: Lmm
# @Date  : 2017-10-24 15:33
# @Desc  :用于获取年报中的对外担保信息

from PublicCode import config
from PublicCode import deal_html_code
import logging
import hashlib
import time

assure_string = 'insert into gs_report_assure(gs_basic_id,gs_report_id, uuid, province, creditor, debtor, cates, amount, deadline, period, ways,if_fwarnnt,created,updated) \
values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Report_Assure:
	def get_info(self, data):
		tr_list = data.xpath(".//tr")
		info = {}
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			if len(td_list) == 0 or len(td_list) == 1:
				continue
			temp["creditor"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["debtor"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["cates"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["amount"] = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["deadline"] = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
			temp["period"] = deal_html_code.remove_symbol(td_list[6].xpath("string(.)"))
			temp["ways"] = deal_html_code.remove_symbol(deal_html_code[7].xpath("string(.)"))
			info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id, gs_report_id, cursor, connect):
		remark = 0
		insert_flag, update_flag = 0, 0
		total = len(info)
		info = {}
		try:
			for key, value in info.keys():
				creditor, debtor, cates = value["creditor"], value["debtor"], value["cates"]
				amount, deadline, period, ways = value["amount"], value["deadline"], value["period"], value["ways"]
				if_fwarnnt = 1
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id) + str(key))
				uuid = m.hexdigest()
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(assure_string, (
					gs_basic_id, gs_report_id, uuid, config.province, creditor, debtor, cates, amount, deadline, period,
					ways,
					if_fwarnnt, updated_time, updated_time))
				insert_flag += flag
				connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("report assure error:%s" % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
