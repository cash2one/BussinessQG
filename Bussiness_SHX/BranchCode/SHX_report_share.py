#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_report_share.py
# @Author: Lmm
# @Date  : 2017-10-24 15:38
# @Desc  : 用于获取年报中的股东及出资信息
from PublicCode import config
from PublicCode import deal_html_code
import hashlib
import logging
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

share_string = 'insert into gs_report_share(gs_basic_id,gs_report_id,province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,created,updated) values ' \
			   '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Report_Share:
	def get_info(self, data):
		tr_list = data.xpath(".//tr")
		info = {}
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			# 针对表头和为信息的情况进行特殊对待
			if len(td_list) == 0 or len(td_list) == 1:
				continue
			temp["name"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			reg_amount = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["reg_amount"] = deal_html_code.match_float(reg_amount)
			reg_date = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["reg_date"] = deal_html_code.change_chinese_date(reg_date)
			temp["reg_way"] = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			ac_amount = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
			temp["ac_amount"] = deal_html_code.match_float(ac_amount)
			ac_date = deal_html_code.remove_symbol(td_list[6].xpath("string(.)"))
			temp["ac_date"] = deal_html_code.change_chinese_date(ac_date)
			temp["ac_way"] = deal_html_code.remove_symbol(td_list[7].xpath("string(.)"))
			info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id, gs_report_id, cursor, connect):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			for key, value in info.iteritems():
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id) + str(key))
				uuid = m.hexdigest()
				name, reg_amount, reg_date = value["name"], value["reg_amount"], value["reg_date"]
				reg_way, ac_amount, ac_date, ac_way = value["reg_way"], value["ac_amount"], value["ac_date"], value[
					"ac_way"]
				
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(share_string, (
					gs_basic_id, gs_report_id, config.province, name, uuid, reg_amount, reg_date, reg_way, ac_amount,
					ac_date,
					ac_way, updated_time, updated_time))
				connect.commit()
				insert_flag += flag
		except Exception, e:
			remark = 100000006
			logging.error('share error %s' % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
