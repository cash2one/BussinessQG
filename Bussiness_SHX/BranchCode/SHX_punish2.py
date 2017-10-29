#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_punish2.py
# @Author: Lmm
# @Date  : 2017-10-19 10:47
# @Desc  : 用于获取企业自行公示的行政处罚信息
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import logging
import time
punish_string = 'insert into gs_punish(gs_basic_id,id,number, types, content,date, pub_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'

class Punish:
	
	#data.xpath("//table[@id = table_qyxzcf]")
	def get_info(self,data):
		tr_list = data.xpath("./tr[@name = 'qyxzxf']")
		info = {}
		for i,singledata in enumerate(tr_list):
			td_list = singledata.xpath("./td")
			number = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			types = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			content = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			gov_dept = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			date = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
			date = deal_html_code.change_chinese_date(date)
			pub_date = deal_html_code.remove_symbol(td_list[6].xpath("string(.)"))
			pub_date = deal_html_code.change_chinese_date(pub_date)
			
			info[i] = [number, types, content, date, pub_date, gov_dept]
		return info
	def update_to_db(self,info,gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				number, types, content = info[key][0], info[key][1], info[key][2]
				date, pub_date, gov_dept = info[key][3], info[key][4], info[key][5]
				
				count = cursor.execute(select_punish, (gs_basic_id, number))
				if count == 0:
					id = ''
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(punish_string, (
						gs_basic_id, id, number, types, content, date, pub_date, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("punish error:%s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag