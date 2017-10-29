#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search.py
# @Author: Lmm
# @Date  : 2017-10-18 10:12
# @Desc  : 用于获得陕西的搜索列表,
import hashlib
import sys
#用于处理中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

from PublicCode import config
from PublicCode import deal_html_code
import requests
from lxml import etree
import re
import urllib

insert_string = "insert into gs_basic(id,province,name,code,ccode,legal_person,responser,investor,runner,reg_date,status,updated) values (%s,%s,%s, %s, %s,%s,%s, %s,%s,%s, %s,%s)"
update_string = "update gs_basic set gs_basic_id = %s,name = %s ,legal_person = %s ,responser=%s,investor = %s,runner = %s,status = %s ,reg_date = %s,uuid = %s where gs_basic_id = %s"
update_ccode = 'update gs_basic set gs_basic_id = %s,ccode = %s ,name = %s,legal_person = %s,responser =%s,investor =%s,runner =%s,status =%s,reg_date=%s,uuid = %s where gs_basic_id =%s'
search_string = 'insert into gs_search(gs_basic_id,user_id,token,keyword,name,province,code,ccode,legal_person,runner,responser,investor,reg_date,status,if_new,uuid,created)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,uuid from gs_basic where code = %s or ccode = %s'


class Search:
	#获取搜索列表
	def get_search_info(self,keyword):
		page = 1
		search_info = {}
		#这里要对其进行重新编码，是因为陕西的搜素关键词要是以gb2312编码的
		#不知道哪个程序员设置的bug只承认中国的中文编码方式~-~
		keyword = keyword.decode("utf-8").encode("gb2312")
		string = urllib.quote(keyword)
		params = config.data.format(string, page)
		result = requests.post(config.url, params, headers=config.headers)
		status_code = result.status_code
		if status_code == 200:
			data = etree.HTML(result.text, parser=etree.HTMLParser(encoding="utf-8"))
			self.get_need_info(data, search_info, 0)
			info_list = data.xpath("//div[@class= 'search_result_box']//p[@class= 'result_desc']/span")[0]
			number = info_list.xpath("string(.)")
			#计算搜素出来了多少页，用更普遍的方式的话，10也应该写到配置里面
			#这段代码应该写入deal_html_code后期根据需要进行调整
			if int(number) == 1:
				page = 1
			elif int(number) > 1:
				if int(number) % 10 == 0:
					page = int(number) / 10
				elif int(number) % 10 != 0:
					page = int(number) / 10 + 1 #注意这里要加一，这是因为若是不是10，小于10的也算一页
			elif int(number) == 0:
				page = 0
			for i in xrange(2, page+1):
				params = config.data.format(string, i)
				result = requests.post(config.url, params, headers=config.headers)
				status_code = result.status_code
				#每一页的开始索引
				start = (i-1)*10
				if status_code ==200:
					self.get_need_info(data, search_info, start)
				else:
					pass
					
				
	
	#用于获取每一页的列表信息
	def get_need_info(self,data,search_info,start):
		info_list = data.xpath('//div[@class= "search_result_box"]//a[@class="result_item"]')
		#让列表的索引位置从start开始,enumerate的用法找百度
		for i,items in enumerate(info_list,start):
			search_info[i] = self.get_single_info(items)
	#用于获取单条基本信息
	def get_single_info(self,items):
		dict = {}
		openView = items.xpath("./@onclick")
		pattern = re.compile("openView\('(.*?)','(.*?)','(.*?)','(.*?)'\)")
		tuple = re.findall(pattern, str(openView))[0]
		pripid = tuple[0]
		dict["prirpid"] = pripid
		types = tuple[3]
		dict["types"] = types
		company = items.xpath(".//span[@id = 'mySpan']/@title")[0]
		dict["company"] = company
		status = items.xpath(".//span[@id = 'mySpan']/following-sibling::*[1]")
		status = status[0].xpath("string(.)")
		status = deal_html_code.remove_symbol(status)
		dict["status"] = status
		code = items.xpath("//span[@class = 'shxydm']")[0]
		code = code.xpath("string(.)").split("：")[1]
		dict["code"] = code
		legal_person = items.xpath(".//span[@class = 'fddbr']")[0].xpath("string(.)")
		legal_person = deal_html_code.remove_symbol(legal_person)
		self.judge_position(legal_person,dict)
		reg_date = items.xpath(".//span[@class= 'clrq']")[0].xpath("string(.)")
		reg_date = reg_date.split("：")[1]
		reg_date = deal_html_code.change_chinese_date(reg_date)
		dict["reg_date"] = reg_date
		return dict
	
	def judge_position(self,legal_person,dict):
		position = legal_person.split("：")[0]
		leader = legal_person.split("：")[1]
		if u'法定代表人' == position:
			dict["legal_person"] = leader
			dict["responser"] = ''
			dict["investor"] = ''
			dict["runner"] = ''
		elif u'经营者' == position:
			dict["runner"] = leader
			dict["legal_person"] = ''
			dict["responser"] = ''
			dict["investor"] = ''
		elif u'负责人' == position:
			dict["responser"] = leader
			dict["runner"] = ''
			dict["legal_person"] = ''
			dict["investor"] = ''
		elif u'投资人' == position:
			dict["investor"] = leader
			dict["responser"] = ''
			dict["runner"] = ''
			dict["legal_person"] = ''
		elif u'执行事务合伙人' == position:
			
			list = re.split(u'、', leader)
			dict["legal_person"] = list[0]+'等'
			dict["investor"] = ''
			dict["runner"] = ''
			dict["responser"] = ''
		
	def update_to_basic(self,count, info, cursor, connect, gs_basic_id, uuid):
		name, code = info["company"], info["code"]
		legal_person, status, start_date = info["legal_person"], info["status"], info["reg_date"]
		provin = config.province
		legal_person, investor, runner, responser = info["legal_person"],info["investor"],info["runner"],info["responser"]
		
		if count == 0:
			m = hashlib.md5()
			m.update(code)
			id = m.hexdigest()
			#将时间更新为一个月以前的时间，方便用户进行点击更新
			updated = deal_html_code.get_before_date()
			cursor.execute(insert_string, (
			(id, provin, name, code, code, legal_person, investor, runner, responser, start_date, status, updated)))
			gs_basic_id = connect.insert_id()
			connect.commit()
			return gs_basic_id
		elif count == 1:
			if code.startswith("9"):
				cursor.execute(update_ccode, (
				gs_basic_id, code, name, legal_person, responser, investor, runner, status, start_date, uuid,
				gs_basic_id))
				connect.commit()
			else:
				cursor.execute(update_string, (
					gs_basic_id, name, legal_person, responser, investor, runner, status, start_date, uuid,
					gs_basic_id))
				connect.commit()
			return 0
		
	
		
	
object = Search()
keyword = '西安银行股份有限公司'
object.get_search_info(keyword)
