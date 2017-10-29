#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_branch.py
# @Author: Lmm
# @Date  : 2017-10-19 10:37
# @Desc  : 用于获取页面中的分支机构信息
from PublicCode import deal_html_code
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
import hashlib
import logging
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
branch_string = 'insert into gs_branch(gs_basic_id,id,code,name,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_string = 'select * from gs_branch where id = %s and gs_basic_id =%s'


class Branch:
	# data.xpath("//div[@class = 'baogao_part']//tr[@name= 'fzjg']")
	def get_info(self, data):
		info = {}
		for i, singledata in enumerate(data):
			temp = {}
			td_list = singledata.xpath("./td")
			# number = deal_html_code.remove_symbol(td_list[0].xpath("string(.)"))
			temp["code"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["name"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["gov_dept"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id):
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(info)
		try:
			for key, value in info.iteritems():
				name = value["name"]
				code = value["code"]
				gov_dept = value["gov_dept"]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(name))
				id = m.hexdigest()
				count = cursor.execute(select_string, (id, gs_basic_id))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(branch_string, (gs_basic_id, id, code, name, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			flag = 100000006
			logging.error('branch error: %s' % e)
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = insert_flag
			return flag, total, insert_flag, update_flag
