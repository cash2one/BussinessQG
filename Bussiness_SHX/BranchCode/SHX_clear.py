#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_clear.py
# @Author: Lmm
# @Date  : 2017-10-19 10:40
# @Desc  : 用于获取页面中的清算信息
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import logging
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
insert_string = 'insert into gs_clear (gs_basic_id,person_name,positon,updated)values(%s,%s,%s,%s)'
select_string = 'select gs_clear_id from gs_clear where gs_basic_id = %s and person_name = %s and positon = %s'
update_string = 'update gs_clear set gs_clear_id = %s,updated = %s where gs_clear_id = %s'

class Clear:
	def get_info(self,data):
		info = {}
		string = u'清算组负责人'
		leader = deal_html_code.get_match_info(string,data)
		list = leader.split('、')
		for i,value in enumerate(list):
			temp = {}
			temp["person_name"] = value
			temp["position"] = string
			info[i] = temp
		string = u"清算组成员"
		member = deal_html_code.get_match_info(string, data)
		list = member.split('、')
		for j, value in enumerate(list, i+1):
			temp = {}
			temp["person_name"] = value
			temp["position"] = string
			info[j] = temp
		return info
	def update_to_db(self,info,gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key,value in info.iteritems():
				person_name = value["person_name"]
				position = value["position"]
				rows = cursor.execute(select_string, (gs_basic_id,person_name, position))
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
			return remark, total, insert_flag, update_flag
