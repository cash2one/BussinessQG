#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search.py
# @Author: Lmm
# @Date  : 2017-10-17 11:00
# @Desc  : 获取广东省搜索列表
import requests
import sys
from PublicCode import config
from PublicCode import deal_html_code
import time
import json
import logging
from lxml import etree
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


class Search:
	#用于获得cookie值
	def get_cookies(self):
		cookies = None
		try:
			now_time = int(time.time()*1000)
			url = config.index_url.format(now_time)
			result = requests.get(url,headers=config.headers)
			status_code = result.status_code
			
			if status_code == 200:
				cookies = result.cookies
			else:
				cookies = None
		except Exception,e:
			
			logging.error("get cookies error:%s"%e)
		finally:
			return cookies
	#用获得加密后的字符串
	def get_transform_key(self,key_word,cookies):
		try:
			transform_url = config.tansform_key.format(key_word)
			result = requests.get(transform_url, headers=config.headers, cookies=cookies)
			status_code = result.status_code
			if status_code ==200:
				data = json.loads(result.content)
				status = data["status"]
				if status =="success":
					textfield = data["textfield"]
				else:
					logging.error("get tansform key faild")
					textfield = None
		except Exception,e:
			logging.error("get transform key error:%s"%e)
			textfield = None
		finally:
			return textfield
	def get_list(self,textfild,cookies):
		page = 1
		list_url = config.list_url.format(textfild,page)
		try:
			result = requests.get(list_url,headers=config.headers,cookies=cookies)
			status_code = result.status_code
			if status_code == 200:
				data = etree.HTML(result.content, parser=etree.HTMLParser(encoding='utf-8'))
				number = data.xpath('//div[@class="mianBodyStyle"]/div[@class="textStyle"]/span')[0].xpath("string(.)")
				
				if int(number) == 1:
					page = 1
				elif int(number) > 1:
					if int(number) % 10 == 0:
						page = int(number) / 10
					elif int(number) % 10 != 0:
						page = int(number) / 10 + 1
				elif int(number) == 0:
					page = 0
				
				self.get_need_info(data)
				# if number
		except Exception,e:
			logging.error("get info list error:%s"%e)
	#用于获得所有的搜索信息
	def get_need_info(self,data):
		information = {}
		list = data.xpath('//div[@class="mianBodyStyle"]//div[@class= "clickStyle"]')
		for i, items in enumerate(list):
			info = self.deal_single_info(items)
			information = dict(information,**info)
			print information
	#用于抽取一条所需信息
	def deal_single_info(self, items):
		info = {}
		url = items.xpath(".//a[@class='font16']/@href")[0]
		company = items.xpath(".//span[@class= 'rsfont']")[0].xpath("string(.)")
		company = deal_html_code.remove_symbol(company)
		status = items.xpath(".//span[@class= 'rsfont']/following-sibling::*[1]")[0].xpath("string(.)")
		status = deal_html_code.remove_symbol(status)
		tablelist = items.xpath(".//table[@class = 'textStyle']//span[@class = 'dataTextStyle']")
		code = tablelist[0].xpath("string(.)")
		code = deal_html_code.remove_symbol(code)
		legal_person = tablelist[1].xpath("string(.)")
		legal_person = deal_html_code.remove_symbol(legal_person)
		dates = tablelist[2].xpath("string(.)")
		dates = deal_html_code.change_chinese_date(dates)
		
		info[code] = [url,company,status,code,legal_person,dates]
		return info
	

			
		
		
		
		
object = Search()
cookies = object.get_cookies()

keyword = '文化传播'
textfild= object.get_transform_key(keyword,cookies)

object.get_list(textfild,cookies)



