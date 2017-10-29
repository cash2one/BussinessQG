#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_basic.py
# @Author: Lmm
# @Date  : 2017-10-18 16:48
# @Desc  : 用于获取页面上的基本信息

from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import logging
import re

update_string = 'update gs_basic set gs_basic_id = %s, name = %s ,ccode = %s,status = %s ,types = %s ,jj_type = %s,legal_person = %s, \
responser = %s ,investor = %s,runner = %s ,reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s ,updated = %s where gs_basic_id = %s'
update_string1 = 'update gs_basic set gs_basic_id = %s, name = %s ,status = %s ,types = %s ,jj_type = %s,legal_person = %s, \
responser = %s ,investor = %s,runner = %s ,reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s ,updated = %s where gs_basic_id = %s'
class Basic:
	#获取页面中的基础信息并对其进行处理
	#这一部分可以做成一个字典，键值为中文，value 为对应的字段
	def get_info(self,basic_data):
		#取出配置中基本信息的字典
		info_dict = config.info_dict
		info = {}
		#将info_dict的value值定义为info的key值
		for key,value in info_dict.items():
			info[value] = self.deal_td_content(key, basic_data)
			# print "info %s --> %s"%(value,info[value])
		if info["code"].startswith("9"):
			info["ccode"] = info["code"]
		else:
			info["ccode"] = ''
		
		info["start_date"] = deal_html_code.change_chinese_date(info["start_date"])
		info["end_date"] = deal_html_code.change_chinese_date(info["end_date"])
		
		# 确定注册日期取哪个,将最终结果给info["reg_date"]，
		# 若其中一个不为空则取其中一个作为最终值
		# 如果两个值都为空说明没有取到值
	    # 要么总结不够全面，要么页面中本来就没有该值，自定义值为''
		if info["reg_date1"]=='' and info["reg_date2"]=='':
			info["reg_date"] = '0000-00-00'
		elif info["reg_date1"]!='':
			info["reg_date"] = deal_html_code.change_chinese_date(info["reg_date1"])
		elif info["reg_date"]!='':
			info["reg_date"] = deal_html_code.change_chinese_date(info["reg_date2"])
		#判断法定代表人取哪个,思路与上面注册日期的取法类似
		if info["legal_person1"] =='' and info["legal_peraon2"] == '':
			info["legal_person"] = ''
		elif info["legal_person1"]!= '':
			info["legal_person"] = info["legal_person1"]
		elif info["legal_person2"]!= '':
			info["legal_person"] = re.split(u'、',info["legal_person2"])[0]+'等'
		#判断注册资本取哪个
		if info["reg_amount1"]=='' and info["reg_amount2"]=='':
			info["reg_amount"] = ''
		elif info["reg_amount1"]!='':
			info["reg_amount"] = info["reg_amount1"]
		elif info["reg_amount2"]!='':
			info["reg_amount"] = info["reg_amount2"]
		#判断场所取哪个
		if info["reg_address1"]=='' and info["reg_address2"]=='' and info["reg_address3"]:
			info["reg_address"] = ''
		elif info["reg_address1"]!='':
			info["reg_address"] = info["reg_address1"]
		elif info["reg_address2"]!='':
			info["reg_address"] = info["reg_address2"]
		elif info["reg_address3"]!='':
			info["reg_address3"] = info["reg_address3"]
		
		
		# for key,value in info.items():
		# 	print key + '-->'+value
		return info
		
		
	#用于根据字符串对查找包含某个字符串的内容的标签，并进行处理
	def deal_td_content(self, string, data):
		try:
			td = data.xpath(".//td[contains(.,'%s')]" % string)
			td = td[0]
			result = deal_html_code.remove_symbol(td.xpath("string(.)"))
			data = result.split("：")[1]
		except Exception,e:
			logging.info("find data error:%s"%e)
			data = ''
		finally:
			return data
	#将获取到的信息插入到数据库中
	def update_to_db(self,info,gs_basic_id):
		name, ccode, status, types = info["name"], info["code"], info["status"], info["types"]
		legal_person, runner, investor, responser = info["legal_person"], info["runner"], info["investor"],info["runner"]
		reg_date, appr_date, reg_amount, start_date = info["reg_date"], info["appr_date"], info["reg_amount"], info["start_date"]
		end_date, reg_zone, reg_address, scope = info["end_date"], info["reg_zone"], info["reg_address"], info["scope"]
		jj_type = info["jj_type"]
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		flag = 0
		try:
			if ccode !='':
				#这里时间更新为一个月前，是因为，是过更新为当天，普通用户就无法使用更新功能了
				updated_time = deal_html_code.get_before_date()
				row_count = cursor.execute(update_string, (
					gs_basic_id, name, ccode, status, types, jj_type, legal_person, responser, investor, runner, reg_date,
					appr_date, reg_amount, start_date, end_date, reg_zone, reg_address, scope, updated_time, gs_basic_id))
				logging.info('update basic :%s' % row_count)
				connect.commit()
			else:
				updated_time = deal_html_code.get_before_date()
				row_count = cursor.execute(update_string, (
					gs_basic_id, name, status, types, jj_type, legal_person, responser, investor, runner,
					reg_date,
					appr_date, reg_amount, start_date, end_date, reg_zone, reg_address, scope, updated_time,
					gs_basic_id))
				logging.info('update basic :%s' % row_count)
				connect.commit()
		except Exception, e:
			flag = 100000004
			logging.error("basic error:" % e)
		finally:
			if flag < 100000001:
				flag = row_count
			return flag