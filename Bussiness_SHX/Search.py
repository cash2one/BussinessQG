#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search.py
# @Author: Lmm
# @Date  : 2017-10-18 10:12
# @Desc  : 用于获得陕西的搜索列表,
import hashlib
import sys

# 用于处理中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

from PublicCode import config
from PublicCode import deal_html_code
from lxml import etree
import logging
import requests
import urllib
import time
import re
import sys

insert_string = "insert into gs_basic(id,province,name,code,ccode,legal_person,responser,investor,runner,reg_date,status,updated) values (%s,%s,%s, %s, %s,%s,%s, %s,%s,%s, %s,%s)"
update_string = "update gs_basic set gs_basic_id = %s,name = %s ,legal_person = %s ,responser=%s,investor = %s,runner = %s,status = %s ,reg_date = %s,uuid = %s where gs_basic_id = %s"
update_ccode = 'update gs_basic set gs_basic_id = %s,ccode = %s ,name = %s,legal_person = %s,responser =%s,investor =%s,runner =%s,status =%s,reg_date=%s,uuid = %s where gs_basic_id =%s'
search_string = 'insert into gs_search(gs_basic_id,user_id,token,keyword,name,province,code,ccode,legal_person,runner,responser,investor,reg_date,status,if_new,uuid,created)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,uuid from gs_basic where code = %s or ccode = %s'

keyword = sys.argv[1]  # 搜索关键词
unique_id = sys.argv[2]  # 本次搜索的唯一标识
gs_search_id = sys.argv[3]  # gs_search表中的gs_search_id


class Search:
	# 获取搜索列表
	def get_search_info(self, keyword):
		# 初始设置页面为1
		page = 1
		search_info = {}
		# 这里要对其进行重新编码，是因为陕西的搜素关键词要是以gb2312编码的
		# 不知道哪个程序员设置的bug只承认中国的中文编码方式~-~
		keyword = keyword.decode("utf-8").encode("gb2312")
		string = urllib.quote(keyword)  # 对搜索关键词进行url加密，转码后这一步其实不必要，但以防万一，还是转码一下
		params = config.data.format(string, page)
		result = requests.post(config.url, params, headers=config.headers)
		status_code = result.status_code
		if status_code == 200:
			data = etree.HTML(result.text, parser=etree.HTMLParser(encoding="utf-8"))
			self.get_need_info(data, search_info, 0)
			info_list = data.xpath("//div[@class= 'search_result_box']//p[@class= 'result_desc']/span")[0]
			number = info_list.xpath("string(.)")
			# 计算搜素出来了多少页，用更普遍的方式的话，10也应该写到配置里面
			# 这段代码应该写入deal_html_code后期根据需要进行调整
			if int(number) == 1:
				page = 1
			elif int(number) > 1:
				if int(number) % 10 == 0:
					page = int(number) / 10
				elif int(number) % 10 != 0:
					page = int(number) / 10 + 1  # 注意这里要加一，这是因为若是不是10，小于10的也算一页
			elif int(number) == 0:
				page = 0
			for i in xrange(2, page + 1):
				params = config.data.format(string, i)
				result = requests.post(config.url, params, headers=config.headers)
				status_code = result.status_code
				# 每一页的开始索引
				start = (i - 1) * 10
				if status_code == 200:
					self.get_need_info(data, search_info, start)
				else:
					pass  # 保留代码，以供以后改动
		return search_info
	
	# 用于获取每一页的列表信息
	def get_need_info(self, data, search_info, start):
		info_list = data.xpath('//div[@class= "search_result_box"]//a[@class="result_item"]')
		# 让列表的索引位置从start开始,enumerate的用法找百度
		for i, items in enumerate(info_list, start):
			search_info[i] = self.get_single_info(items)
	
	# 用于获取单条基本信息
	def get_single_info(self, items):
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
		# 将企业负责人的职位确定出来
		self.judge_position(legal_person, dict)
		reg_date = items.xpath(".//span[@class= 'clrq']")[0].xpath("string(.)")
		reg_date = reg_date.split("：")[1]
		reg_date = deal_html_code.change_chinese_date(reg_date)
		dict["reg_date"] = reg_date
		return dict
	
	# 将搜索结果插入到search表中
	def insert_search(self, keyword, user_id, info, cursor, connect):
		insert_flag, update_flag = 0, 0
		remark = 0
		try:
			flag = len(info)
			for key, value in info.iteritems():
				unique, name, code = value["prirpid"] + value["types"], value["company"], value["code"]
				legal_person, status, start_date = value["legal_person"], value["status"], value["reg_date"]
				runner = value["runner"]
				responser = value["responser"]
				investor = value["investor"]
				
				provin = config.province
				count = cursor.execute(select_string, (code, code))
				# 当数据库中不存在带有code 的该条信息时，则向gs_basic表中插入一条信息
				if int(count) == 0:
					if_new = 1
					gs_basic_id = 0
					uuid = 'S'
					gs_basic_id = self.update_to_basic(int(count), info[key], cursor, connect, gs_basic_id, uuid)
					updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				
				# 当数据库中有且仅有一条信息时，则更新gs_basic表中的该条数据
				elif int(count) == 1:
					if_new = 0
					uuid = 'S'
					updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
					gs_basic_id = cursor.fetchall()[0][0]
					self.update_to_basic(int(count), info[key], cursor, connect, gs_basic_id, uuid)
					row_count = cursor.execute(search_string, (
						gs_basic_id, user_id, unique_id, keyword, name, provin, code, code, legal_person, runner,
						responser, investor, start_date, status, if_new, unique, updated))
					connect.commit()
					insert_flag += row_count
					update_flag += 1
				
				# 当数据库中存在大于一条数据信息时，查找这些信息中是否有uuid标记为R的情况
				# 如果有则将其他新信息标记为R，如果没有则选取id最大的那一条id更新为S
				# 其他的更新为R
				
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
						self.update_to_basic(remark, info[key], cursor, connect, gs_basic_id, uuid)
					update_flag += count
				# 最后向数据库gs_search表中插入一条数据
				counts = cursor.execute(search_string, (
					basic_id, user_id, unique_id, keyword, name, provin, code, code, legal_person, runner,
					responser, investor, start_date, status, if_new, unique, updated))
				connect.commit()
				insert_flag += counts
		
		except Exception, e:
			remark = 100000006
			logging.error("update error:%s" % e)
		finally:
			if remark < 100000001:
				remark = flag
			return remark, insert_flag, update_flag
	
	# 用于将数据更新到basic表中
	def update_to_basic(self, count, info, cursor, connect, gs_basic_id, uuid):
		name, code = info["company"], info["code"]
		legal_person, status, start_date = info["legal_person"], info["status"], info["reg_date"]
		provin = config.province
		legal_person, investor, runner, responser = info["legal_person"], info["investor"], info["runner"], info[
			"responser"]
		
		if count == 0:
			# 利用相应的包对code进行MD5加密
			m = hashlib.md5()
			m.update(code)
			id = m.hexdigest()
			# 将时间更新为一个月以前的时间，方便用户进行点击更新
			updated = deal_html_code.get_before_date()
			cursor.execute(insert_string, (
				(id, provin, name, code, code, legal_person, investor, runner, responser, start_date, status, updated)))
			gs_basic_id = connect.insert_id()
			connect.commit()
			return gs_basic_id
		elif count == 1:
			# 如果code是以9开头的则更新ccode
			if code.startswith("9"):
				cursor.execute(update_ccode, (
					gs_basic_id, code, name, legal_person, responser, investor, runner, status, start_date, uuid,
					gs_basic_id))
				connect.commit()
			else:
				# 如果不是则不更新ccode
				cursor.execute(update_string, (
					gs_basic_id, name, legal_person, responser, investor, runner, status, start_date, uuid,
					gs_basic_id))
				connect.commit()
			return 0
		# 用于判断法定代表人的职位
	
	def judge_position(self, legal_person, dict):
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
			dict["legal_person"] = list[0] + '等'
			dict["investor"] = ''
			dict["runner"] = ''
			dict["responser"] = ''


object = Search()
keyword = '西安银行股份有限公司'
object.get_search_info(keyword)
