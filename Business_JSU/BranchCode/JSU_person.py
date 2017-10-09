#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_person.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获得主要人员信息，并更新到数据库中

from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode import deal_html_code
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Judge
import time
import json
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()




select_string = 'select gs_person_id,position from gs_person where gs_basic_id = %s and name = %s and source = 1'
insert_string = 'insert into gs_person(gs_basic_id,name,position,source,updated)values(%s,%s,%s,%s,%s)'
person_string = 'update gs_person set gs_person_id = %s,position = %s,updated = %s,quit =0 where gs_person_id = %s'
update_person_py = 'update gs_py set gs_py_id = %s,gs_person = %s,updated = %s where  gs_py_id = %s '
update_string = 'update gs_person set quit = 1 where gs_basic_id = %s '
update_quit = 'update gs_person set quit = 0,updated = %s where gs_basic_id = %s and gs_person_id = %s'


class Person:
	def __init__(self,url,headers):
		self.url = url
		self.headers = headers
	def get_info(self):
		result,status_code = Send_Request(self.url,self.headers).send_request()
		info = {}
		if status_code ==200:
			flag =1
			data = json.loads(result.content)
			for i,single in enumerate(data):
				name = single["PERSON_NAME"]
				position = single["POSITION_NAME"]
				if position == None:
					position = ''
				info[i] = [name,position]
		else:
			flag = 100000004
		return info,flag
	
	def update_to_db(self,  information,gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
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
			for key in information.keys():
				name = str(information[key][0])
				position = information[key][1]
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
						elif pos == None and position != None:
							updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
							count = cursor.execute(person_string, (gs_person_id, position, updated_time, gs_person_id))
							update_flag += count
							connect.commit()
							sign = 0
					if sign == 0:
						source = 1
						updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
						count = cursor.execute(insert_string, (gs_basic_id, name, position, source, updated_time))
						insert_flag += count
						connect.commit()
					else:
						pass
				elif rows == 0:
					source = 1
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
			return remark,total, insert_flag, update_flag
def main(org, id, seqid, regno, gs_basic_id, gs_py_id):
	pattern = "person"
	flag = Judge().update_info1(pattern, org, id, seqid, regno, Person, gs_basic_id)
	Judge().update_py(gs_py_id, update_person_py, flag)
