# -*- coding: utf-8 -*-
# @File  : SHX_report_schange.py
# @Author: Lmm
# @Date  : 2017-10-24 15:37
# @Desc  : 用于获取年报中的股权变更信息
from PublicCode import deal_html_code
from PublicCode import config
import logging
import hashlib
import time

schange_string = 'insert into gs_report_schange(gs_basic_id,gs_report_id,province,name,percent_pre,percent_after,dates,uuid,created,updated)values' \
                 '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
class Report_Schange:
	def get_info(self,data):
		info = {}
		tr_list = data.xpath("//tr")
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			temp["name"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["percent_pre"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["percent_after"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			dates = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["dates"] = deal_html_code.change_chinese_date(dates)
			info[i] = temp

	def update_to_db(self, gs_report_id, gs_basic_id, cursor, connect, info):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			for key in info.keys():
				name, percent_pre, percent_after, dates = info[key][0], info[key][1], info[key][2], info[key][3]
				uuid = info[key][4]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id) + str(uuid))
				uuid = m.hexdigest()
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(schange_string, (
					gs_basic_id, gs_report_id, config.province, name, percent_pre, percent_after, dates, uuid,
					updated_time,
					updated_time))
				connect.commit()
				insert_flag += flag
		except Exception, e:
			remark = 100000006
			logging.error('schange error %s' % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag