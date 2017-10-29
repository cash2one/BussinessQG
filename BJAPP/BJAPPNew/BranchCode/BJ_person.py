#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_person.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 用于获取主要人员信息
import requests
import time
from PublicCode import config
from lxml import etree
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Log
from PublicCode.Public_code import Send_Request
import re
import logging

url = 'http://qyxy.baic.gov.cn/xycx/queryCreditAction!queryTzrxx_all.dhtml?reg_bus_ent_id=0CD1263D6BB2009EE053A0630264009E&moreInfo=&SelectPageSize=100&EntryPageNo=1&pageNo=1&pageSize=100&clear=true'
gs_basic_id = '1'
gs_py_id = '1'
select_string = 'select gs_person_id,position from gs_person where gs_basic_id = %s and name = %s and source = 0'
insert_string = 'insert into gs_person(gs_basic_id,name,position,sex,source,updated)values(%s,%s,%s,%s,%s,%s)'
person_string = 'update gs_person set gs_person_id = %s,position = %s,sex = %s,updated = %s,quit =0 where gs_person_id = %s'
update_person_py = 'update gs_py set gs_py_id = %s,gs_person = %s,updated = %s where  gs_py_id = %s '
update_string = 'update gs_person set quit = 1 where gs_basic_id = %s '
update_quit = 'update gs_person set quit = 0,updated = %s where gs_basic_id = %s and gs_person_id = %s'


class Person:
	def name(self, url):
		info = {}
		headers = config.headers_detail
		content, status_code = Send_Request().send_request(url, headers)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			total = result.xpath("//table[@id='tableIdStyle']//div/text()")[0]
			pattern = re.compile(u".*记录总数(.*?)条.*")
			number = re.findall(pattern, total)
			if len(number) == 1:
				temp = int(number[0])
			trlist = result.xpath("//table[@id = 'tableIdStyle']//tr")
			for i, single in enumerate(trlist):
				tdlist = single.xpath("./td")
				if len(tdlist) == 0 or len(tdlist) < 4:
					pass
				else:
					# number = tdlist[0].xpath('./text()')
					name = deal_html_code.remove_symbol(tdlist[1].xpath("string(.)"))
					position = deal_html_code.remove_symbol(tdlist[2].xpath("string(.)"))
					sex = deal_html_code.remove_symbol(tdlist[3].xpath("string(.)"))
					info[i] = [name, position, sex]
		else:
			flag = 100000004
		return info, flag
	
	def update_to_db(self, info, gs_basic_id):
		insert_flag, update_flag = 0, 0
		total = len(info)
		remark = 0
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
			for key in info.keys():
				name, position, sex = info[key][0], info[key][1], info[key][2]
				rows = cursor.execute(select_string, (gs_basic_id, name))
				if int(rows) >= 1:
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
							count = cursor.execute(person_string,
												   (gs_person_id, position, sex, updated_time, gs_person_id))
							update_flag += count
							connect.commit()
							sign = 0
					if sign == 0:
						source = 0
						updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
						count = cursor.execute(insert_string, (gs_basic_id, name, position, sex, source, updated_time))
						insert_flag += count
						connect.commit()
					else:
						pass
				elif rows == 0:
					source = 0
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					
					count = cursor.execute(insert_string, (gs_basic_id, name, position, sex, source, updated_time))
					insert_flag += count
					connect.commit()
		
		except Exception, e:
			print e
			remark = 100000006
			logging.error("person error: %s" % e)
		
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				flag = insert_flag + update_flag
				remark = flag
			return remark, total, insert_flag, update_flag


def main(gs_py_id, gs_basic_id, url):
	Log().found_log(gs_py_id, gs_basic_id)
	name = 'person'
	flag = Judge_status().judge(gs_basic_id, name, Person, url)
	
	# if __name__ == '__main__':
	#     main(gs_py_id,gs_basic_id,url)
