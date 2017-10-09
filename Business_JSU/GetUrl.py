#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : GetUrl.py.py
# @Author: Lmm
# @Date  : 2017-09-20
# @Desc  :获得搜索信息
import requests
from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Connect_to_DB
from PublicCode import deal_html_code
import json
import logging
import re
import time

code = '913201007541328275'
ccode = '913201007541328275'
gs_basic_id ='1'


select_name = 'select name from gs_basic where gs_basic_id = %s'


#获得关键id
def get_keyid(string):
	cookies = None
	url = config.index_url
	headers = config.headers
	result,status_code = Send_Request(url,headers).send_request()
	if status_code ==200:
		flag =1
		cookies = result.cookies
		firsturl = config.first_url.format(string)
		result,status_code = Send_Request(firsturl,headers).send_request1(cookies)
		if status_code ==200:
			result = json.loads(result.content)
			name = result["bean"]["name"]
		else:
			flag = 100000002
	else:
		flag = 100000001
	return name,flag,cookies

#用于获取搜索信息
def get_search_info(name,cookies):
	items = []
	try:
		flag = 1
		second_url = config.second_url.format(name)
		result = requests.get(second_url,headers =config.headers,cookies = cookies)
		data = json.loads(result.content)
		error = data["ERROR"]
		if u"失败" in error:
			flag = 100000003
			logging.info(error)
		else:
			total = json.loads(result.content)["total"]
			if total > 0:
				items = json.loads(result.content)["items"]
			else:
				flag = 100000003
	except Exception,e:
		flag = 100000004
		logging.error("search error:%s"%e)
	return flag,items
#用于根据code 或者 ccode 进行搜索
def get_info(code,ccode,gs_basic_id):
	#正则匹配判断code 或者ccode 根据哪个进行查询
	pattern = re.compile(r'^9.*')
	result1 = re.findall(pattern, code)
	result2 = re.findall(pattern, ccode)
	if len(result1) == 0 and len(result2) == 0:
		string = code
	elif len(result1) == 1:
		string = code
	elif len(result2) == 1:
		string = ccode
	else:
		pass
	idname,flag,cookies = get_keyid(string)
	if flag ==1:
		flag,items = get_search_info(idname,cookies)
		org, id, seq_id, name = get_keyword(items)
	elif flag ==100000003:
		idname, flag, cookies = get_keyid(string)
		if flag ==1:
			flag, items = get_search_info(idname, cookies)
			org, id, seq_id, name = get_keyword(items)
			
		elif flag ==100000003:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			select_string = select_name % gs_basic_id
			cursor.execute(select_string)
			name = cursor.fetchall()[0][0]
			name = deal_html_code.remove_space(name)
			cursor.close()
			connect.close()
			idname, flag, cookies = get_keyid(string)
			flag,items = get_search_info(name,cookies)
			org, id, seq_id, se_name = get_keyword(items)
			#用来判断数据库中的公司名字跟搜索到的名字是否一致
			if name != se_name:
				flag =100000003
				org, id, seq_id = 0,0,0
	print_info(org, id, seq_id, flag)
def print_info(org, id, seq_id,flag):
	printinfo = {
		"org":0,
		"id":0,
		"seq_id":0,
		"flag":0
	}
	printinfo["org"] = org
	printinfo["id"] = id
	printinfo["seq_id"] = seq_id
	printinfo["flag"] = flag
	print printinfo
				
#用于获得拼接关键词
def get_keyword(items):
	items = items[0]
	org = items["ORG"]
	id = items["ID"]
	seq_id = items["SEQ_ID"]
	name = items["CORP_NAME"]
	return org, id, seq_id, name
def main():
	get_info(code, ccode, gs_basic_id)

if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main()
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)

	




