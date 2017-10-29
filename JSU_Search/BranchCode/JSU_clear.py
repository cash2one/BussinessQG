#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_clear.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获得清算信息
from PublicCode import config
from PublicCode.Public_Code import Log
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Judge
import time
import logging
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
insert_string = 'insert into gs_clear (gs_basic_id,person_name,positon,updated)values(%s,%s,%s,%s)'
select_string = 'select gs_clear_id from gs_clear where gs_basic_id = %s and person_name = %s and positon = %s'
update_string = 'update gs_clear set gs_clear_id = %s,updated = %s where gs_clear_id = %s'



class Clear:
	def __init__(self,url,headers):
		self.url = url
		self.headers = headers
		
	def get_info(self):
		result,status_code = Send_Request(self.url,self.headers).send_request()
		info = {}
		if status_code ==200:
			flag = 1
			data = json.loads(result.content)
			if len(data)>0:
				data = data[0]
				leader = data["ACCOUNT_MAN"]
				member =data["ACCOUNT_MEMBER"]
				position1 = "清算组负责人"
				position2 = "清算组成员"
				if leader!=None:
					info[0] = [leader,position1]
				if member!=None:
					memberlist = member.split("、")
					for i,single in enumerate(memberlist,1):
						info[i] = [single,position2]
		else:
			flag = 100000004
		return info,flag
	
	def update_to_db(self,information,gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				person_name = str(information[key][0])
				position = str(information[key][1])
				rows = cursor.execute(select_string, (gs_basic_id, person_name, position))
				if int(rows) == 1:
					gs_clear_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					count = cursor.execute(update_string, (gs_clear_id, updated_time, gs_clear_id))
					update_flag += count
					connect.commit()
				elif rows == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					count = cursor.execute(insert_string, (gs_basic_id, person_name, position, updated_time))
					insert_flag += count
					connect.commit()
		except Exception, e:
			cursor.close()
			connect.close()
			remark = 100000006
			logging.error("clear error: %s" % e)
		finally:
			if remark < 100000001:
				flag = insert_flag + update_flag
				remark = flag
			return remark,total, insert_flag, update_flag


def main(org,id,seq_id,regno,gs_basic_id):
	pattern = "clear"
	flag = Judge().update_info1(pattern, org, id, seq_id, regno, Clear, gs_basic_id)


