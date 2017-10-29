#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_change.py
# @Author: Lmm
# @Date  : 2017-10-19 10:38
# @Desc  : 用于获取页面中的变更信息
from PublicCode import deal_html_code
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
import logging
import time
insert_string = 'insert into gs_change(gs_basic_id,types,item,content_before,content_after,change_date,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,content_after from gs_change where gs_basic_id = %s and item = %s and change_date = %s and source =0'

class Change:
	#data.xpath("//div[@class='baogao_part']//tr[@name = 'bgxx']")
	def get_info(self,data):
		info = {}
		for i,singledata in enumerate(data):
			temp = {}
			td_list = singledata.xpath("./td")
			# number = td_list[0].xpath("string(.)")
			if len(td_list)==0:
				continue
			temp["item"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["content_before"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["content_after"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			change_date = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["change_date"] = deal_html_code.change_chinese_date(change_date)
			info[i] = temp
		return info
	def update_to_db(self,info,gs_basic_id):
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(info)
		try:
			HOST,  USER,  PASSWD,  DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key,value in info.iteritems():
				content_before, content_after = value["content_before"], value["content_after"]
				change_date, item = value["change_date"], value["item"]
				types = '变更'
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				count = cursor.execute(select_string,(gs_basic_id,item,change_date))
				if count == 0:
					source = 0
					row_count = cursor.execute(insert_string, (
								gs_basic_id, types, item, content_before, content_after, change_date,source,updated_time))
					insert_flag += row_count
					connect.commit()
				elif int(count) >= 1:
					remark = 0
					for gs_basic_id, content in cursor.fetchall():
						if content == content_after:
							remark = 1
							break
					if remark == 0:
						row_count = cursor.execute(insert_string, (
							gs_basic_id, types, item, content_before, content_after, change_date, updated_time))
						insert_flag += row_count
						connect.commit()
		except Exception, e:
			flag = 100000006
			logging.error("change error :%s " % e)
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = insert_flag
			return flag, total, insert_flag, update_flag