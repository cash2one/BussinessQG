#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_person.py
# @Author: Lmm
# @Date  : 2017-10-19 10:36
# @Desc  : 用于获取页面中的主要人员信息
from PublicCode import deal_html_code
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from lxml import etree
import logging
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()




select_string = 'select gs_person_id,position from gs_person where gs_basic_id = %s and name = %s and source = 0'
insert_string = 'insert into gs_person(gs_basic_id,name,position,source,updated)values(%s,%s,%s,%s,%s)'
person_string = 'update gs_person set gs_person_id = %s,position = %s,updated = %s,quit =0 where gs_person_id = %s'

update_string = 'update gs_person set quit = 1 where gs_basic_id = %s '
update_quit = 'update gs_person set quit = 0,updated = %s where gs_basic_id = %s and gs_person_id = %s'
class Person:
	#data.xpath("")
	#人员，成员
	def get_info(self,data):
		info = {}
		tr_list = data.xpath(".//tr")
		
		for i,singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath(".//td")
			if len(td_list) == 0:
				continue
			
		
			temp["name"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["position"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			string = update_string % gs_basic_id
			cursor.execute(string)
			connect.commit()
			cursor.close()
			connect.close()
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key,value in info.iteritems():
				name = value["name"]
				position = value["position"]
				rows = cursor.execute(select_string, (gs_basic_id, name))
				# print name,position
				
				if int(rows) >= 1:
					# gs_person_id = cursor.fetchall()[0][0]
					sign = 0
					for gs_person_id, pos in cursor.fetchall():
						if pos == position:
							sign = 1
							updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
							count = cursor.execute(update_quit, (updated_time, gs_basic_id, gs_person_id))
							connect.commit()
						# update_flag += count
						elif pos == '' and position != '':
							updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
							count = cursor.execute(person_string, (gs_person_id, position, updated_time, gs_person_id))
							update_flag += count
							connect.commit()
							sign = 0
					if sign == 0:
						source = 0
						updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
						count = cursor.execute(insert_string, (gs_basic_id, name, position, source, updated_time))
						insert_flag += count
						connect.commit()
					else:
						pass
				elif rows == 0:
					source = 0
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					count = cursor.execute(insert_string, (gs_basic_id, name, position, source, updated_time))
					insert_flag += count
					connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("person error: %s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				flag = insert_flag + update_flag
				remark = flag
			return remark, total, insert_flag, update_flag
			
		
		
	

