#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Get_Info_new.py
# @Author: Lmm
# @Date  : 2017-10-10
# @Desc  : 通过名称搜索企业


import hashlib
import json
import logging
import time
import requests
import App_Update
from PublicCode import deal_html_code
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Log

select_name = 'select name from gs_basic where gs_basic_id = %s'
select_info = 'select gs_new_id,name,province from gs_new  where status = 1 limit 1'
update_status = 'update gs_new set gs_new_id = %s,status = 2,gs_basic_id = %s where gs_new_id = %s'
update_status1 = 'update gs_new set gs_new_id = %s,status = 404,gs_basic_id = 0 where gs_new_id = %s '
select_string = 'select gs_basic_id from gs_basic where code = %s or ccode = %s'
insert_string = "insert into gs_basic(uuid,id,province,name,code,ccode,legal_person,reg_date,status,updated ) values (%s, %s, %s,%s,%s, %s,%s,%s, %s,%s)"
# 用于获取信息列表
def get_index(code,province):
	first_url = config.url_list[province].format(code)
	# print first_url
	result = requests.get(first_url)
	status_code = result.status_code
	result = result.content
	second_url = None
	infomation ={}
	if status_code == 200:
		info = json.loads(result)["info"]
		if len(info) != 0:
			info = json.loads(result)["info"][0]
			uuid = info["uuid"]
			entName = info["entName"]
			ccode = info["uniScid"]
			code = info["regNo"]
			legal_person = info["lerep"]
			dates = info["estDate"]
			dates = deal_html_code.change_chinese_date(dates)
			status = info["opState"]
			infomation[0] = [entName, code, ccode, legal_person, dates, status]
			second_url = config.detail_list[province].format(uuid)
			flag = 1
		else:
			flag = 100000003
	else:
		flag = 100000001
	return second_url, flag, infomation
#将信息插入到gs_basic表中
def insert_to_basic(information,cursor,connect):
	entName = information[0][0]
	code = information[0][1]
	ccode = information[0][2]
	legal_person = information[0][3]
	dates = information[0][4]
	status = information[0][5]
	if code!=None and code!='':
		province = deal_html_code.judge_province(code)
	elif ccode!=None and ccode!='':
		province = deal_html_code.judge_province(code)
	m = hashlib.md5()
	m.update(code)
	id = m.hexdigest()
	updated = deal_html_code.get_befor_date()
	# updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	cursor.execute(insert_string, (('',id, province, entName, code, ccode, legal_person, dates, status, updated)))
	gs_basic_id = connect.insert_id()
	connect.commit()
	return gs_basic_id

def main():
	Log().found_log1()
	try:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		count = cursor.execute(select_info)
		if count == 0:
			logging.info("there is no task need to do!")
		else:
			for gs_new_id,name,province in cursor.fetchall():
				
				if province =='SHH' or province =="HEB" or province =="SCH" or province =="YUN":
					if name == '' and code == '' and code == '':
						logging.info("this is a useless info")
					else:
						second_url, flag, information = get_index(name,province)
						
						if flag == 1:
							code = information[0][1]
							ccode = information[0][2]
							if code!=None and ccode!=None:
								count = cursor.execute(select_string,(code,ccode))
								if int(count) ==1:
									gs_basic_id = cursor.fetchall()[0][0]
									Log().found_log(gs_basic_id)
									App_Update.update_all_info(gs_basic_id, second_url,province)
								elif count ==0:
									gs_basic_id = insert_to_basic(information,cursor,connect)
									logging.info("now the excute basic id is %s" % gs_basic_id)
									App_Update.update_all_info(gs_basic_id, second_url,province)
								cursor.execute(update_status,(gs_new_id,gs_basic_id,gs_new_id))
								connect.commit()
							elif code!=None:
								count = cursor.execute(select_string,(code,code))
								if int(count) == 1:
									gs_basic_id = cursor.fetchall()[0][0]
									logging.info("now the excute basic id is %s" % gs_basic_id)
									App_Update.update_all_info(gs_basic_id, second_url,province)
								elif count ==0:
									gs_basic_id = insert_to_basic(information, cursor, connect)
									logging.info("now the excute basic id is %s" % gs_basic_id)
									App_Update.update_all_info(gs_basic_id, second_url,province)
								
								cursor.execute(update_status, (gs_new_id, gs_basic_id, gs_new_id))
								connect.commit()
							elif ccode!=None:
								count = cursor.execute(select_string,(ccode,ccode))
								if int(count) == 1:
									gs_basic_id = cursor.fetchall()[0][0]
									logging.info("now the execute basic id is %s" % gs_basic_id)
									App_Update.update_all_info(gs_basic_id, second_url,province)
								elif count ==0:
									gs_basic_id = insert_to_basic(information, cursor, connect)
									logging.info("now the execute basic id is %s" % gs_basic_id)
									App_Update.update_all_info(gs_basic_id, second_url,province)
								cursor.execute(update_status, (gs_new_id, gs_basic_id, gs_new_id))
								connect.commit()
						else:
							logging.info("get cookies failed or there is no search info ,the status is %s"%flag)
							cursor.execute(update_status1, (gs_new_id, gs_new_id))
							connect.commit()
				else:
					logging.info("the province is out of range")
	except Exception, e:
		logging.info("get list error:%s" % e)
	finally:
		cursor.close()
		connect.close()
if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main()
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)

