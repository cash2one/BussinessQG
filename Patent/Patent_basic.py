#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Patent_basic.py
# @Author: Lmm
# @Date  : 2017-08-30
# @Desc  :
import json
import random
import time

import requests

from PublicCode import config
from PublicCode import deal_html_code

headers = config.header

# page = 1
# insert_string = 'insert into ia_patent()'
insert_patent = 'insert into ia_patent(name,code,app_date,applicant, address,inventor,main_cate,sub_cate,pub_code,pub_date,priority,remark,agent,agency,source,updated)' \
                'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_patent = 'select ia_patent_id from ia_patent where code = "%s"'
insert_law = 'insert into ia_patent_law(dates,code,vcode,content,ia_patent_id,updated)values(%s,%s,%s,%s,%s,%s)'
select_law = 'select ia_patent_law_id from ia_patent_law where ia_patent_id = %s and code = %s and dates = %s'
insert_same = 'insert into ia_patent_same(ia_patent_id,name,apply_code) values(%s,%s,%s)'
select_same = 'select ia_patent_same_id from ia_patent_same where ia_patent_id = %s and apply_code = %s'
params = 'nrdAn=%s&cid=%s&sid=%s&wee.bizlog.modulelevel=0201101'
lawparams = 'lawState.nrdPn=%s&lawState.nrdAn=%s&wee.bizlog.modulelevel=0202201&pagination.start=%s'
sameparams = 'cognationQC.radioValue=%s&cognationQC.radioKey=PN&wee.bizlog.modulelevel=0201901&pagination.start=0'


class Ia_Patent:
	# 用于获取基本信息
	def get_info(self, first_info, cookies):
		item = {}
		for i, single in enumerate(first_info):
			# 文献标识
			nrdAn = single.xpath(".//input[@name = 'nrdAnHidden']")[0].xpath('./@value')[0]
			# 文献唯一标识
			cid = single.xpath(".//input[@name='idHidden']")[0].xpath('./@value')[0]
			sid = cid
			nrdPn = single.xpath(".//input[@name ='nrdPnHidden']")[0].xpath('./@value')[0]
			str = u'代理机构'
			agency = self.deal_info(str, single)
			str = u'代理人'
			agent = self.deal_info(str, single)
			str = u'申请号'
			code = self.deal_info(str, single)
			code = code.split('CN')[-1]
			str = u'申请日'
			app_date = self.deal_info(str, single)
			app_date = deal_html_code.change_date(app_date)
			str = u'申请（专利权）人'
			applicant = self.deal_info(str, single)
			address = single.xpath(".//input[@name ='appAddrHidden']")[0].xpath('./@value')[0]
			str = u'发明人'
			inventor = self.deal_info(str, single)
			str = u'IPC分类号'
			main_cate = self.deal_info(str, single)
			str = u'IPC分类号'
			sub_cate = self.deal_info(str, single)
			str = u'公开（公告）号'
			pub_code = self.deal_info(str, single)
			str = u'公开（公告）日'
			pub_date = self.deal_info(str, single)
			pub_date = deal_html_code.change_date(pub_date)
			str = u'优先权日'
			priority_date = self.deal_info(str, single)
			str = u'优先权号'
			priority_code = self.deal_info(str, single)
			priority = priority_date + ' ' + priority_code
			name = single.xpath(".//input[@name ='titleHidden']")[0].xpath('./@value')[0]
			user_agent = random.choice(config.USER_AGENTS)
			headers["User-Agent"] = user_agent
			url = config.viewurl
			string = params % (nrdAn, cid, sid)
			result = requests.post(url, string, headers=headers, cookies=cookies)
			data = json.loads(result.content)
			list = data["abstractInfoDTO"]
			data = list
			remark = data["abIndexList"][0]["value"]
			remark = deal_html_code.remove_symbol(remark)
			source = 'pss-system'
			law_search_info = self.get_law_info(nrdAn, nrdPn, cookies)
			same_info = self.get_cognation_info(nrdPn, cookies)
			item[i] = [name, code, app_date, applicant, address, inventor, main_cate, sub_cate, pub_code, pub_date,
			             priority, remark, agent, agency, source, law_search_info, same_info]
			print item
		return item
	# 用于对信息进行处理
	def deal_info(self, str, item):
		string = item.xpath(".//p[contains(.,'%s')]" % str)
		if len(string) == 1:
			string = string[0].xpath("string(.)")
			string = string.split(":")[1]
			string = deal_html_code.remove_symbol(string)
		else:
			string = ''
		return string
	
	# 用于获取法律状态
	def get_law_info(self, nrdAn, nrdPn, cookies):
		law_info = {}
		start_flag = 0
		string = lawparams % (nrdPn, nrdAn, start_flag)
		user_agent = random.choice(config.USER_AGENTS)
		headers["User-Agent"] = user_agent
		url = config.lawurl
		result = requests.post(url, string, headers=headers, cookies=cookies).content
		lawdata = json.loads(result)["lawStateList"]
		for i, single in enumerate(lawdata):
			dates = single["prsDate"]
			dates = deal_html_code.change_date(dates)
			code = single["nrdAn"]
			code = code.split("CN")[-1]
			vcode = single["nrdPn"]
			# print vcode
			if vcode != '' and vcode != None:
				vcode = vcode.split("CN")[-1]
			else:
				vcode = ''
			content = single["lawStateExtendMeaning"]
			law_info[i] = [dates, code, vcode, content]
		
		return law_info
	
	# 用于获取同族信息
	def get_cognation_info(self, code, cookies):
		url = config.sameurl
		user_agent = random.choice(config.USER_AGENTS)
		headers["User-Agent"] = user_agent
		params = sameparams % code
		result = requests.post(url, params, headers=headers, cookies=cookies).content
		result = json.loads(result)
		list = result["cognationList"]
		info = {}
		for i, single in enumerate(list):
			name = single["invTitleNO"]
			apply_code = single["an"]
			info[i] = [name, apply_code]
		print info
		return info
	
	# 用于将基本信息更新到数据库中
	def update_basic_to_db(self, info, cursor, connect, ia_patent_id):
		try:
			for key in info.keys():
				name, code, app_date, applicant = info[key][0], info[key][1], info[key][2], info[key][3]
				address, inventor, main_cate, sub_cate = info[key][4], info[key][5], info[key][6], info[key][7]
				pub_code, pub_date, priority, remark = info[key][8], info[key][9], info[key][10], info[key][11]
				agent, agency, source = info[key][12], info[key][13], info[key][14]
				law_search_info, same_info = info[key][15], info[key][16], info[key][17]
				string = select_patent % code
				count = cursor.execute(string)
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(insert_patent, (
						name, code, app_date, applicant, address, inventor, main_cate, sub_cate, pub_code, pub_date,
						priority, remark, agent, agency, source, updated_time))
					connect.commit()
		except Exception, e:
			print e
	# #将采集到的法律信息更新到数据库中
	# def update_law_info(self,info,cursor,connect,ia_patent_id):
	# 	try:
	# 		for key in info.keys():
			
	#将法律信息采集更新到数据库中
	def upadte_law_info(self, info, cursor, connect, ia_patent_id):
		try:
			for key in info.keys():
				dates, code, vcode, content = info[key][0], info[key][1], info[key][2], info[key][3]
				count = cursor.execute(select_law,(ia_patent_id,code,dates))
				if count ==0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					cursor.execute(insert_law,(dates,code,vcode,content,ia_patent_id,updated_time))
					connect.commit()


		except Exception, e:
			print e
	
	# 将同族信息插入到数据库中
	def update_same_to_db(self, info, cursor, connect, ia_patent_id):
		try:
			for key in info.keys():
				name, apply_code = info[key][0], info[key][1]
				count = cursor.execute(select_same, (ia_patent_id, apply_code))
				if count == 0:
					flag = cursor.execute(insert_same, (ia_patent_id, name, apply_code))
					connect.commit()
		
		except Exception, e:
			print e
