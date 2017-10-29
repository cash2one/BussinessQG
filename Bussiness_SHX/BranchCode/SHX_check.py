#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_check.py
# @Author: Lmm
# @Date  : 2017-10-19 10:40
# @Desc  : 用于获取页面中的抽查检查信息

from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from PublicCode import config
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

check_string = 'insert into gs_check(gs_basic_id,types,result,check_date,gov_dept,updated)values(%s,%s,%s,%s,%s,now())'
select_check = 'select gs_check_id from gs_check where gs_basic_id = %s and check_date = %s and types = %s'


class Check:
	# 用于获得抽查检查信息
	def get_info(self, data):
		# data.xpath("//table[@id = 'table_ccjc']//tr[@name = 'ccjc']")
		info = {}
		for i, singledata in enumerate(data):
			td_list = singledata.xpath("//td")
			temp = {}
			# number = deal_html_code.remove_symbol(td_list[0].xpath("string(.)"))
			temp["gov_dept"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["types"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["check_date"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["result"] = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			info[i] = temp
		return info
	
	# 将信息更新到数据库中
	def update_to_db(self, information, gs_basic_id):
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(information)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key, value in information.iteritems():
				types, result = value["types"], value["result"]
				check_date, gov_dept = value["check_date"], value["gov_dept"]
				count = cursor.execute(select_check, (gs_basic_id, check_date, types))
				if count == 0:
					rows_count = cursor.execute(check_string, (gs_basic_id, types, result, check_date, gov_dept))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			cursor.close()
			connect.close()
			flag = 100000006
			logging.error("check error: %s" % e)
		finally:
			if flag < 100000001:
				flag = insert_flag
			return flag, total, insert_flag, update_flag
