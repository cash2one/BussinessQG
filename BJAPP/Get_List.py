#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Get_List.py
# @Author: Lmm
# @Date  : 2017-09-05
# @Desc  : 用与获取搜素列表,并将基本信息更新至数据库中
import requests
import sys
from PublicCode import config
from lxml import etree
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import re
import time
import logging


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

headers = config.headers


code = '91110000100011743X'
ccode = '91110000100011743X'
gs_basic_id = '229417601'
gs_py_id = '1'

update_string = 'update gs_basic set gs_basic_id = %s, name = %s ,ccode = %s,status = %s ,types = %s ,legal_person = %s, \
responser = %s ,investor = %s,runner = %s ,reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s,updated = %s  where gs_basic_id = %s'
#用于获取搜索列表
def get_list(string):
	url = config.list_url
	info = {}
	try:
		params = config.list_parmas.format(string)
		result = requests.post(url, params, headers=headers)
		status_code = result.status_code
		if status_code ==200:
			content = etree.HTML(result.content)
			list = content.xpath("//li")
			for i,single in enumerate(list):
				item = single.xpath(".//a/@href")[0]
				url = config.host+item
				info[i] = url
	except Exception,e:
		print e
	finally:
		return info
#用于获取基本信息以及详情信息
def get_detail(info):
	detaillist = {}
	for key in info.keys():
		url = info[key]
		result = requests.get(url,headers=config.headers_detail)
		status = result.status_code
		if status ==200:
			content = result.content
			detaillist[key] = deal_single_info(content)
			print detaillist[key]
	return detaillist
		
#用于处理单条信息
def deal_single_info(result):
	infolist= {}
	#注意设置编码格式防止乱码
	content = etree.HTML(result,parser=etree.HTMLParser(encoding='utf-8'))
	url = config.host+content.xpath("//*[@class = 'moreInfo']/a/@href")[0]
	infolist["href"] = url
	ddlist = content.xpath("//dl/dt")
	codetemp = content.xpath("//dd[@style='color:red;']")
	if len(codetemp)==1:
		string = codetemp[0].xpath('string(.)')
		pattern = re.compile(r"\d+")
		code = re.findall(pattern,string)
		if len(code)==1:
			code = code[0]
		else:
			code = None
	else:
		code = None
	infolist['code'] = code
	for i,single in enumerate(ddlist,0):
		key = single.xpath("string(.)")
		key = deal_html_code.remove_symbol(key)
		dd = single.xpath("./following-sibling::*[1]")[0].xpath("string(.)")
		dd = deal_html_code.remove_symbol(dd)
		infolist[key] = dd
	#print infolist
	return infolist
#将基本信息插入到数据库中
def update_to_db(information, cursor, connect,gs_basic_id):
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
		sign_date =sign_date.strip()
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
	if end_date =='':
		end_date =None
	if '登记机关' in information.keys():
		reg_zone = information[u"登记机关"]
	if '住所' in information.keys():
		reg_address = information[u"住所"]
	elif '经营场所' in information.keys():
		reg_address = information[u"经营场所"]
	elif '主要经营场所' in information.keys():
		reg_address = information[u"主要经营场所"]
	elif '营业场所' in information.keys():
		reg_address = information[u"营业场所"]
	if '业务范围' in information.keys():
		scope = information[u"业务范围"]
	elif '经营范围' in information.keys():
		scope = information[u"经营范围"]
	updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
	row_count = 0
	flag = 0
	ccode = deal_html_code.remove_symbol(ccode)

	try:
		row_count = cursor.execute(update_string, (
			gs_basic_id, name, ccode, status, types,  legal_person, responser, investor, runner, sign_date,
			appr_date, reg_amount, start_date, end_date, reg_zone, reg_address, scope, updated_time, gs_basic_id))
		logging.info('update basic :%s' % row_count)
		connect.commit()
	except Exception, e:
		flag = 100000006
		logging.error("basic error:%s" % e)
	finally:
		if flag < 100000001:
			flag = row_count
		return flag


def main():
	try:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		string = '北京事务合伙人'
		#info = get_list(string)
		info = get_list(code)
		info_list = get_detail(info)
		update_to_db(info_list[0],cursor,connect,gs_basic_id)
	except Exception,e:
		print e
		flag = 100000005
		logging.error("unknow error:%s"%e)
	finally:
		cursor.close()
		connect.close()
  
if __name__ == '__main__':
    main()

