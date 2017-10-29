#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_clear.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取清算信息,并将清算信息插入到数据库中
from lxml import etree
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Send_Request

import logging
from PublicCode.Public_code import Log

import time

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_clearInfo_wap.dhtml?reg_bus_ent_id=20e38b8b50c7d44f0150d043b6620ce2&clear=true'
gs_basic_id = '1900000787'
gs_py_id = '1'

insert_string = 'insert into gs_clear (gs_basic_id,person_name,positon,updated)values(%s,%s,%s,%s)'
select_string = 'select gs_clear_id from gs_clear where gs_basic_id = %s and person_name = %s and positon = %s'
update_string = 'update gs_clear set gs_clear_id = %s,updated = %s where gs_clear_id = %s'
update_clear_py = 'update gs_py set gs_py_id = %s,gs_clear = %s,updated = %s where gs_py_id = %s'


class Clear:
	def name(self, url):
		info = {}
		content, status_code = Send_Request().send_request(url)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding="utf-8"))
			dl = result.xpath("//div[@class= 'viewBox']/dl")[0]
			string = u"清算负责人"
			data = self.deal_dd_content(string, dl)
			if data != '':
				legal_list = data.split(u"、")
				for i, single in enumerate(legal_list):
					info[i] = [single, string]
			string = u"清算组成员"
			data = self.deal_dd_content(string, dl)
			if data != '':
				member_list = data.split(u"、")
				for j, single in enumerate(member_list, (i + 1)):
					info[j] = [single, string]
		else:
			flag = 100000004
		# print info,flag
		return info, flag
		# 用于处理dd标签中的内容
	
	def deal_dd_content(self, string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	
	def update_to_db(self, information, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
		logging.info("clear error:%s" % total)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				person_name = information[key][0]
				position = information[key][1]
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
			remark = 100000006
			logging.error("clear error: %s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				flag = insert_flag + update_flag
				logging.info("execute clear:%s" % flag)
				remark = flag
			return remark, total, insert_flag, update_flag


def main(gs_py_id, gs_basic_id, url):
	Log().found_log(gs_py_id, gs_basic_id)
	name = 'clear'
	flag = Judge_status().judge(gs_basic_id, name, Clear, url)
	Judge_status().update_py(gs_py_id, update_clear_py, flag)
	# if __name__ == '__main__':
	# 	main(gs_py_id, gs_basic_id, url)
	# object = Clear()
	# object.name(url)
