#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Get_Url.py
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
from PublicCode.Public_code import Log
import re
import time
import logging
import chardet
import random
import linecache
import hashlib


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

headers = config.headers

# keyword = sys.argv[1]
# user_id = sys.argv[2]
# unique_id = sys.argv[3]

keyword = '技术科技'
user_id = '2'
unique_id = '12345566666'

update_string = 'update gs_basic set gs_basic_id = %s, name = %s ,ccode = %s,status = %s ,types = %s ,legal_person = %s, \
responser = %s ,investor = %s,runner = %s ,reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s,uuid = %s where gs_basic_id = %s'
insert_string = "insert into gs_basic(id,province,name,code,ccode,status,types,legal_person,responser,investor,runner,reg_date,appr_date,reg_amount,start_date,end_date,reg_zone,reg_address,scope,uuid,updated) values (%s,%s, %s, %s,%s,%s, %s,%s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s,%s,%s)"
search_string = 'insert into gs_search(gs_basic_id,user_id,token,keyword,name,province,code,ccode,legal_person,responser,investor,runner,reg_date,status,if_new,uuid,created)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,uuid from gs_basic where code = %s or ccode = %s '
select_string1 = 'select gs_basic_id,uuid from gs_basic where code= %s or ccode = %s'
select_string2 = 'select gs_basic_id,uuid from gs_basic where code = %s or ccode = %s'
#用于获取搜索列表
def get_list(string):
	info = {}
	flag = 0
	try:
		headers = config.headers_index
		content,status_code = Send_Request().send_request(config.index_url,headers)
		if status_code ==200:
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			id = result.xpath('//span[@class = "shouButton"]/@onclick')[0]
			pattern = re.compile(".*QueryIndex\('','(.*?)'\).*")
			match_id = re.findall(pattern, id)[0]
			url = config.list_url.format(match_id)
			#随机生成UA
			a = random.randrange(1, 1001)  # 1-1000中生成随机数
			headers = config.headers
			params = config.list_parmas.format(string)
			theline = linecache.getline(r'user-agent.txt', a)
			theline = theline.replace("\n", '')
			headers["User-Agent"] = theline
			result = requests.post(url, params, headers=headers)
			status_code = result.status_code
			s = chardet.detect(result.content)["encoding"]
			if status_code ==200 and s =='utf-8':
				pattern = re.compile(u".*无查询结果.*|.*访问频繁.*|.*访问异常.*")
				match = re.findall(pattern,result.content)
				if len(match) == 0:
					content = etree.HTML(result.content,parser=etree.HTMLParser(encoding='utf-8'))
					list = content.xpath("//li")
					for i,single in enumerate(list):
						item = single.xpath(".//a/@href")[0]
						url = config.host+item
						info[i] = url
					flag = 1
				else:
					flag = 100000003
			else:
				flag = 100000004
		else:
			flag = 10000004
	
	except Exception,e:
		logging.error("search error:%s"%e)
		flag = 100000004
	finally:
		return info,flag
#用于获取基本信息以及详情信息
def get_detail(info):
	detaillist = {}
	total = len(info)
	success = 0
	error = 0
	for key in info.keys():
		url = info[key]
		content,status_code = Send_Request().send_request(url,headers= config.headers_detail)
		if status_code == 200:
			success+=1
			detaillist[key] = deal_single_info(content)
		else:
			error+=1
		time.sleep(3)
	return detaillist,total,success,error
		
#用于处理单条信息
def deal_single_info(result):
	infolist = {}
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
			code = ''
	else:
		code = ''
	infolist['code'] = code
	for i,single in enumerate(ddlist,0):
		key = single.xpath("string(.)")
		key = deal_html_code.remove_symbol(key)
		dd = single.xpath("./following-sibling::*[1]")[0].xpath("string(.)")
		dd = deal_html_code.remove_symbol(dd)
		infolist[key] = dd
	return infolist
#将基本信息插入到数据库中
def update_to_basic(count,information, cursor, connect,gs_basic_id,uuid):
	province = 'BEJ'
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
		status = information[u"企业状态"]
	elif '经营状态' in information.keys():
		status = information[u'经营状态']
	if '类型' in information.keys():
		types = information[u'类型']
	elif "公司类型" in information.keys():
		types = information[u'公司类型']
	
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
	elif u"法定代表人姓名" in information.keys():
		legal_person = information[u"法定代表人姓名"]
		responser = None
		investor = None
		runner = None
	
	if '成立日期' in information.keys():
		sign_date = information[u"成立日期"]
		sign_date = sign_date
		# print sign_date
	elif '注册日期' in information.keys():
		sign_date = information[u"注册日期"]
		sign_date =sign_date
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
	if code =='' and ccode !='':
		code =ccode
	if count ==0:
		if code == ''and ccode!='':
			m = hashlib.md5()
			m.update(ccode)
			id = m.hexdigest()
		elif ccode ==''and code!='':
			m = hashlib.md5()
			m.update(code)
			id = m.hexdigest()
		elif code!='' and ccode!='':
			m = hashlib.md5()
			m.update(code)
			id = m.hexdigest()
		updated_time = deal_html_code.get_before_date()
		row_count = cursor.execute(insert_string,(id,province,name,code,ccode,status,types,legal_person,responser,investor,runner,sign_date,appr_date,reg_amount,start_date,end_date,reg_zone,reg_address,scope,uuid,updated_time))
		basic_id = connect.insert_id()
		connect.commit()
		
		logging.info('insert basic :%s' % row_count)
	elif count ==1:
		basic_id = 0
		row_count = cursor.execute(update_string, (
			gs_basic_id, name, ccode, status, types, legal_person, responser, investor, runner, sign_date,
			appr_date, reg_amount, start_date, end_date, reg_zone, reg_address, scope, uuid,gs_basic_id))
		connect.commit()
		logging.info('update basic :%s' % row_count)
	return basic_id
def update_to_search(information,keyword,user_id,unique_id,cursor,connect):
	province = 'BEJ'
	href = information["href"]
	insert_flag = 0
	if '企业名称' in information.keys():
		name = information[u"企业名称"]
	elif '名称' in information.keys():
		name = information[u"名称"]
	if '统一社会信用代码' in information.keys():
		code = information["code"]
		ccode = information[u"统一社会信用代码"]
		if code == None:
			code = ccode
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
		status = information[u"企业状态"]
	elif '经营状态' in information.keys():
		status = information[u'经营状态']
	
	
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
	elif u"法定代表人姓名" in information.keys():
		legal_person = information[u"法定代表人姓名"]
		responser = None
		investor = None
		runner = None
	
	if '成立日期' in information.keys():
		sign_date = information[u"成立日期"]
		sign_date = sign_date
		# print sign_date
	elif '注册日期' in information.keys():
		sign_date = information[u"注册日期"]
		sign_date =sign_date
	else:
		sign_date = None
	if code != '' and ccode != '':
		count = cursor.execute(select_string, (code, ccode))
	elif ccode == '':
		count = cursor.execute(select_string1, (code, code))
	elif code == '':
		count = cursor.execute(select_string, (ccode, ccode))
	if code =="" and ccode!="":
		code = ccode
		
	if count == 0:
		if_new = 1
		gs_basic_id = 0
		uuid = 'S'
		gs_basic_id = update_to_basic(int(count), information, cursor, connect, gs_basic_id, uuid)
		updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		
		row_count = cursor.execute(search_string, (
			gs_basic_id, user_id, unique_id, keyword, name, province, code, ccode, legal_person, responser, investor,
			runner, sign_date, status, if_new, href, updated))
		connect.commit()
		insert_flag += row_count
	elif int(count)==1:
		if_new = 0
		uuid = 'S'
		updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		gs_basic_id = cursor.fetchall()[0][0]
		update_to_basic(int(count), information, cursor, connect, gs_basic_id, uuid)
		
		row_count = cursor.execute(search_string, (
			gs_basic_id, user_id, unique_id, keyword, name, province, code, ccode, legal_person, responser, investor,
			runner, sign_date, status, if_new, href, updated))
		connect.commit()
		insert_flag += row_count
		

	elif int(count) >= 2:
		# print 1
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
			# print uuid
			update_to_basic(remark, information, cursor, connect, gs_basic_id, uuid)
		counts = cursor.execute(search_string, (
			basic_id, user_id, unique_id, keyword, name, province, code, ccode, legal_person, runner,
			responser,investor, sign_date, status, if_new, href, updated))
		connect.commit()
		insert_flag+= counts
	return insert_flag
#用于获得搜索结果,及状态信息
def get_info():
	Log().found_log(user_id,unique_id)
	success,error,insert = 0,0,0
	total = 0
	try:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		info, flag = get_list(keyword)
		if flag ==1:
			datalist, total, success, error = get_detail(info)
			for key in datalist.keys():
				information = datalist[key]
				tempinsert = update_to_search(information, keyword, user_id, unique_id, cursor, connect)
				if tempinsert == 1:
					insert+= 1
	except Exception, e:
		
		flag = 100000005
		logging.error("unknow error:%s" % e)
	finally:
		cursor.close()
		connect.close()
		return flag,total,success,error,insert


def main():
	printinfo = {}
	flag, total, success, error, insert = get_info()
	printinfo["flag"] = int(flag)
	printinfo["total"] = int(total)
	printinfo["success"] = int(success)
	printinfo["error"] = int(error)
	printinfo["insert"] = int(insert)
	printinfo["unique"] = unique_id
	print printinfo
	

		
		
	

if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main()
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)

