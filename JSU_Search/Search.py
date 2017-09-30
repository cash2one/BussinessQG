#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search.py
# @Author: Lmm
# @Date  : 2017-09-29
# @Desc  : 用于搜索信息，并将搜素结果更新到数据库中
from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode import deal_html_code
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
import Update_Info
import hashlib
import logging
import requests
import time
import json
import re
keyword = '南京银行股份有限公司'
unique_id = '1999999999912131212'
user_id = '1345'

insert_string = "insert into gs_basic(id,province,name,code,ccode,legal_person,responser,investor,runner,reg_date,status,updated) values (%s,%s,%s, %s, %s,%s,%s, %s,%s,%s, %s,%s)"
update_string = "update gs_basic set gs_basic_id = %s,name = %s ,legal_person = %s ,responser=%s,investor = %s,runner = %s,status = %s ,reg_date = %s,uuid = %s where gs_basic_id = %s"
update_ccode = 'update gs_basic set gs_basic_id = %s,ccode = %s ,name = %s,legal_person = %s,responser =%s,investor =%s,runner =%s,status =%s,reg_date=%s,uuid = %s where gs_basic_id =%s'
search_string = 'insert into gs_search(gs_basic_id,user_id,token,keyword,name,province,code,ccode,legal_person,runner,responser,investor,reg_date,status,if_new,uuid,created)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,uuid from gs_basic where code = %s or ccode = %s'


def get_keyid(string):
	cookies = None
	url = config.index_url
	headers = config.headers
	result, status_code = Send_Request(url, headers).send_request()
	if status_code == 200:
		flag = 1
		cookies = result.cookies
		firsturl = config.first_url.format(string)
		result, status_code = Send_Request(firsturl, headers).send_request1(cookies)
		if status_code == 200:
			result = json.loads(result.content)
			name = result["bean"]["name"]
		else:
			flag = 100000002
	else:
		flag = 100000001
	return name, flag, cookies
#用于获取搜索信息
def get_search_info(name,cookies):
	items = []
	try:
		flag = 1
		second_url = config.second_url.format(name)
		result = requests.get(second_url, headers=config.headers, cookies=cookies)
		data = json.loads(result.content)
		
		error = data["ERROR"]
		print error
		if u"失败" in error:
			flag = 100000003
			logging.info(error)
		else:
			total = json.loads(result.content)["total"]
			if total > 0:
				items = json.loads(result.content)["items"]
			else:
				flag = 100000003
	except Exception, e:
		flag = 100000004
		logging.error("search error:%s" % e)
	return flag, items
#用于获得拼接关键词
def get_keyword(items):
	info = {}
	for i, single in enumerate(items):
		org = single["ORG"]
		id = single["ID"]
		seq_id = single["SEQ_ID"]
		unique = str(org) + "||" + str(id) + '||' + str(seq_id)
		name = single["CORP_NAME"]
		code = single["REG_NO"]
		legal_person = single["OPER_MAN_NAME"]
		status = single["CORP_STATUS"]
		start_date = single["START_DATE"]
		position = single["OPER_MAN_CLM"]
		info[i] = [unique, name, code, legal_person, status, start_date, position]
	return info

	# 将搜索结果插入到search表中
def insert_search(keyword, user_id, info, cursor, connect):
	insert_flag, update_flag = 0, 0
	remark = 0
	try:
		flag = len(info)
		for key in info.keys():
			unique, name, code = info[key][0], info[key][1], info[key][2]
			legal_person, status, start_date = info[key][3], info[key][4], info[key][5]
			position = info[key][6]
			legal_person, investor, runner, responser = judge_position(legal_person,position)
			provin = config.province
			count = cursor.execute(select_string, (code, code))
			if int(count) == 0:
				if_new = 1
				gs_basic_id = 0
				uuid = 'S'
				gs_basic_id = update_to_basic(int(count), info[key], cursor, connect, gs_basic_id, uuid)
				updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				row_count = cursor.execute(search_string, (
					gs_basic_id, user_id, unique_id, keyword, name, provin, code, code, legal_person, runner,
					responser, investor, start_date, status, if_new, unique, updated))
				connect.commit()
				insert_flag += row_count
			
			elif int(count) == 1:
				if_new = 0
				uuid = 'S'
				updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				gs_basic_id = cursor.fetchall()[0][0]
				update_to_basic(int(count), info[key], cursor, connect, gs_basic_id, uuid)
				row_count = cursor.execute(search_string, (
					gs_basic_id, user_id, unique_id, keyword, name, provin, code, code, legal_person, runner,
					responser, investor, start_date, status, if_new, unique,  updated))
				connect.commit()
				insert_flag += row_count
				update_flag += 1
			elif int(count) >= 2:
				if_new = 0
				updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				list = {}
				basic_id = None
				for gs_basic_id, uuid in cursor.fetchall():
					list[gs_basic_id] = uuid
					if basic_id == None:
						if uuid == 'S':
							basic_id = gs_basic_id
				if basic_id == None:
					basic_id = gs_basic_id
				for gs_basic_id in list.keys():
					remark = 1
					if gs_basic_id == basic_id:
						uuid = 'S'
					else:
						uuid = 'R'
					update_to_basic(remark, info[key], cursor, connect, gs_basic_id, uuid)
				counts = cursor.execute(search_string, (
					basic_id, user_id, unique_id, keyword, name, provin, code, code, legal_person, runner,
					responser, investor, start_date, status, if_new, unique,updated))
				connect.commit()
				insert_flag += counts
				update_flag += count
	except Exception, e:
		remark = 100000006
		logging.error("update error:%s" % e)
	finally:
		if remark < 100000001:
			remark = flag
		return remark, insert_flag, update_flag
def update_to_basic(count, info, cursor, connect, gs_basic_id, uuid):
	name, code = info[1], info[2]
	legal_person, status, start_date = info[3], info[4], info[5]
	position = info[6]
	provin = config.province
	legal_person, investor, runner, responser = judge_position(legal_person,position)
	
	if count == 0:
		m = hashlib.md5()
		m.update(code)
		id = m.hexdigest()
		updated = deal_html_code.get_before_date()
		cursor.execute(insert_string, ((id, provin, name, code, code, legal_person, investor, runner, responser, start_date, status, updated)))
		gs_basic_id = connect.insert_id()
		connect.commit()
		return gs_basic_id
	elif count == 1:
		if code.startswith("9"):
			cursor.execute(update_ccode, (gs_basic_id, code, name, legal_person, responser, investor, runner, status, start_date, uuid,gs_basic_id))
			connect.commit()
		else:
			cursor.execute(update_string, (
				gs_basic_id, name, legal_person, responser, investor, runner, status, start_date, uuid, gs_basic_id))
			connect.commit()
		return 0
#用于判断法定代表人的职位
def judge_position(legal_person,position):
	
	if u'法定代表人' == position:
		legal_person = legal_person
		responser = None
		investor = None
		runner = None
	elif u'经营者' == position:
		runner = legal_person
		legal_person = None
		responser = None
		investor = None
	elif u'负责人' == position:
		responser = legal_person
		runner = None
		legal_person = None
		investor = None
	elif u'投资人' == position:
		investor = legal_person
		responser = None
		runner = None
		legal_person = None
	elif u'执行事务合伙人' == position:
		legal_person = legal_person
		list = re.split(u'、', legal_person)
		legal_person = list[0] + '等'
		investor = None
		runner = None
		responser = None
	return legal_person, investor, runner, responser

		
def printinfo(flag,insert,update,unique_id):
	info = {
		"flag": 0,
		"insert": 0,
		"update": 0,
		"unique": 0
	}
	info["flag"] = int(flag)
	info["insert"] = int(insert)
	info["update"] = int(update)
	info["unique"] = unique_id
	print info


def main():
	# Log().found_log(unique_id,user_id)
	insert_flag, update_flag = 0, 0
	try:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		string = keyword
		idname, flag, cookies = get_keyid(string)
		if flag == 1:
			flag, items = get_search_info(idname, cookies)
			info = get_keyword(items)
			flag, insert_flag, update_flag = insert_search(keyword, user_id, info, cursor, connect)
	except Exception, e:
		flag = 100000005
		logging.error("unknow error:%s" % e)
		
	finally:
		cursor.close()
		connect.close()
		printinfo(flag, insert_flag, update_flag, unique_id)
#用于对搜素结果进行更新
def update_search():
	select_string ="select gs_search_id,gs_basic_id,uuid from gs_search where token = %s and user_id = %s"
	HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
	connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
	cursor.execute(select_string, (unique_id, user_id))
	for gs_search_id,gs_basic_id,uuid in cursor.fetchall():
		print gs_basic_id
		Update_Info.main(uuid, gs_search_id, gs_basic_id)
		
	
if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main()
	update_search()
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
