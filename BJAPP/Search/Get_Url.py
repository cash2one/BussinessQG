#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search.py
# @Author: Lmm
# @Date  : 2017-09-05
# @Desc  : 用与获取搜素列表,并将基本信息更新至数据库中
import requests
import sys
from PublicCode import config
from lxml import etree
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
import re
import time
import logging
import chardet
import random

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

headers = config.headers

code = '911100007693890511'
ccode = '911100007693890511'
gs_basic_id = '229421869'
gs_py_id = '1'
string = "技术咨询管理"

update_string = 'update gs_basic set gs_basic_id = %s, name = %s ,ccode = %s,status = %s ,types = %s ,legal_person = %s, \
responser = %s ,investor = %s,runner = %s ,reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s,updated = %s  where gs_basic_id = %s'
select_name = 'select name from gs_basic where gs_basic_id = %s'


# 用于获取搜索列表
def get_list(string):
	url = config.list_url
	info = {}
	flag = 0
	try:
		# 随机选取请求头
		headers["User-Agent"] = random.choice(config.USER_AGENTS)
		params = config.list_parmas.format(string)
		result = requests.post(url, params, headers=headers)
		status_code = result.status_code
		s = chardet.detect(result.content)["encoding"]
		print s
		if status_code == 200 and s == 'utf-8':
			pattern = re.compile(u".*无查询结果.*")
			match = re.findall(pattern, result.content)
			if len(match) == 0:
				content = etree.HTML(result.content)
				list = content.xpath("//li")
				for i, single in enumerate(list):
					item = single.xpath(".//a/@href")[0]
					url = config.host + item
					info[i] = url
				flag = 1
			else:
				flag = 100000003
		else:
			flag = 100000004
	except Exception, e:
		print e
		logging.error("search error:%s" % e)
		flag = 100000004
	finally:
		return info, flag


# 用于获取基本信息以及详情信息
def get_detail(info):
	detaillist = {}
	for key in info.keys():
		url = info[key]
		content, status_code = Send_Request().send_request(url)
		if status_code == 200:
			detaillist[key] = deal_single_info(content)
		time.sleep(0.5)
	return detaillist


# 用于处理单条信息
def deal_single_info(result):
	infolist = {}
	# 注意设置编码格式防止乱码
	content = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
	url = config.host + content.xpath("//*[@class = 'moreInfo']/a/@href")[0]
	infolist["href"] = url
	ddlist = content.xpath("//dl/dt")
	codetemp = content.xpath("//dd[@style='color:red;']")
	if len(codetemp) == 1:
		string = codetemp[0].xpath('string(.)')
		pattern = re.compile(r"\d+")
		code = re.findall(pattern, string)
		if len(code) == 1:
			code = code[0]
		else:
			code = None
	else:
		code = None
	infolist['code'] = code
	for i, single in enumerate(ddlist, 0):
		key = single.xpath("string(.)")
		key = deal_html_code.remove_symbol(key)
		dd = single.xpath("./following-sibling::*[1]")[0].xpath("string(.)")
		dd = deal_html_code.remove_symbol(dd)
		infolist[key] = dd
	return infolist


# 将基本信息插入到数据库中
def update_to_db(information, cursor, connect, gs_basic_id):
	if '企业名称' in information.keys():
		name = information[u"企业名称"]
	elif '名称' in information.keys():
		name = information[u"名称"]
	if '统一社会信用代码' in information.keys():
		code = information["code"]
		ccode = information[u"统一社会信用代码"]
	elif '注册号' in information.keys():
		code = information[u"注册号"]
		ccode = ''
	elif '统一社会信用代码/注册号' in information.keys():
		code = information[u"统一社会信用代码/注册号"]
		pattern = re.compile('^91.*|92.*|93.*')
		ccode = re.findall(pattern, code)
		if len(ccode) == 0:
			ccode = ''
		elif len(ccode) == 1:
			ccode = ccode[0]
	if '登记状态' in information.keys():
		status = information[u"登记状态"]
	elif '企业状态' in information.keys():
		status = information["企业状态"]
	elif '经营状态' in information.keys():
		status = information[u'经营状态']
	if '类型' in information.keys():
		types = information[u'类型']
	
	if '法定代表人' in information.keys():
		legal_person = information[u"法定代表人"]
		responser = None
		investor = None
		runner = None
	elif '经营者' in information.keys():
		runner = information[u"经营者"]
		legal_person = None
		responser = None
		investor = None
	elif '负责人' in information.keys():
		responser = information[u'负责人']
		runner = None
		legal_person = None
		investor = None
	elif '投资人' in information.keys():
		investor = information[u"投资人"]
		responser = None
		runner = None
		legal_person = None
	elif '投资人姓名' in information.keys():
		investor = information[u"投资人"]
		responser = None
		runner = None
		legal_person = None
	elif '执行事务合伙人' in information.keys():
		legal_person = information[u"执行事务合伙人"]
		list = re.split(u'、', legal_person)
		legal_person = list[0] + '等'
		investor = None
		runner = None
		responser = None
	
	if '成立日期' in information.keys():
		sign_date = information[u"成立日期"]
		sign_date = sign_date.strip()
	# print sign_date
	elif '注册日期' in information.keys():
		sign_date = information[u"注册日期"]
		sign_date = sign_date.strip()
	else:
		sign_date = None
	if '注册资本' in information.keys():
		reg_amount = information[u"注册资本"]
	elif '成员出资额' in information.keys():
		reg_amount = information[u"成员出资额"]
	else:
		reg_amount = None
	if '核准日期' in information.keys():
		appr_date = information[u"核准日期"]
	else:
		appr_date = None
	if '营业期限自' in information.keys():
		start_date = information[u"营业期限自"]
	elif '合伙期限自' in information.keys():
		start_date = information[u"合伙期限至"]
	else:
		start_date = None
	if '营业期限至' in information.keys():
		end_date = information[u"营业期限至"]
	elif '合伙期限至' in information.keys():
		end_date = information[u"合伙期限至"]
	else:
		end_date = None
	if end_date == '':
		end_date = None
	if '登记机关' in information.keys():
		reg_zone = information[u"登记机关"]
	elif '发照机关' in information.keys():
		reg_zone = information[u"发照机关"]
	if '住所' in information.keys():
		reg_address = information[u"住所"]
	elif '经营场所' in information.keys():
		reg_address = information[u"经营场所"]
	elif '主要经营场所' in information.keys():
		reg_address = information[u"主要经营场所"]
	elif '营业场所' in information.keys():
		reg_address = information[u"营业场所"]
	elif '企业住所' in information.keys():
		reg_address = information[u"企业住所"]
	if '业务范围' in information.keys():
		scope = information[u"业务范围"]
	elif '经营范围' in information.keys():
		scope = information[u"经营范围"]
	updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
	row_count = 0
	flag = 0
	ccode = deal_html_code.remove_symbol(ccode)
	href = information["href"]
	try:
		row_count = cursor.execute(update_string, (
			gs_basic_id, name, ccode, status, types, legal_person, responser, investor, runner, sign_date,
			appr_date, reg_amount, start_date, end_date, reg_zone, reg_address, scope, updated_time, gs_basic_id))
		logging.info('update basic :%s' % row_count)
		connect.commit()
	except Exception, e:
		flag = 100000006
		logging.error("basic error:%s" % e)
	finally:
		if flag < 100000001:
			flag = row_count
		return flag, href


# 用于获得搜索结果,及状态信息
def get_info(code, ccode):
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
	info, flag = get_list(string)
	if flag == 100000003:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		select_string = select_name % gs_basic_id
		cursor.execute(select_string)
		name = cursor.fetchall()[0][0]
		name = deal_html_code.remove_symbol(name)
		cursor.close()
		connect.close()
		info, flag = get_list(name)
	return info, flag


def main(string):
	printinfo = {}
	href = ''
	try:
		info, flag = get_list(string)
		print len(info)
		info_list = get_detail(info)
		print info_list
	# info,flag = get_list(code,ccode)
	# if flag ==1:
	# 	HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
	# 	connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
	# 	info_list = get_detail(info)
	# 	if info_list >0:
	# 		flag,href = update_to_db(info_list[0],cursor,connect,gs_basic_id)
	# 	else:
	# 		pass
	# else:
	# 	pass
	except Exception, e:
		print e
		flag = 100000005
		logging.error("unknow error:%s" % e)
	finally:
		printinfo["flag"] = int(flag)
		printinfo["url"] = href
		print printinfo


if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main(string)
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
