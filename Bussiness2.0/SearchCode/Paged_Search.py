#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Paged_Search.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  :

import hashlib
import json
import re
import sys
import time
import urllib
import logging
import requests
from lxml import etree
from SPublicCode import config
from SPublicCode.Public_code import Connect_to_DB
from SPublicCode.deal_html_code import remove_symbol
from SPublicCode.deal_html_code import change_chinese_date
from SPublicCode.deal_html_code import judge_province
from SPublicCode import deal_html_code

# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# user_id = sys.argv[1]
# keyword = sys.argv[2]
# unique_id = sys.argv[3]
# pagenumber = sys.argv[4]
# totalpage = sys.argv[5]
# cookies_params = sys.argv[6]
# challenge_params = sys.argv[7]
# validate_params = sys.argv[8]
# jsluid = sys.argv[9]
# jsessionid = sys.argv[10]

user_id = 1
keyword = '上海点儿'
unique_id = '15021891972000'
pagenumber = 1
totalpage = 0
cookies_params = "23query_8080"
challenge_params = '401203212adb6e5579276c22849e7b9blb'
validate_params = '707dddd2229c733f8faf71c180152246'
jsluid = 'abe719e05908bcc8e42da76a00110d72'
jsessionid ='6992C9310A6349E9768EA0917E206918-n2:-1'

log_path = config.log_path
logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
					datefmt='%a, %d %b %Y %H:%M:%S',
					filename=log_path + '/log/py_search_%s_%s_%s.log' % (
						time.strftime("%Y-%m-%d", time.localtime()), user_id, unique_id),
					filemode='w')

session = requests.session()  # 用于保持会话
url_first = config.host
insert_string = "insert into gs_basic(id,province,name,code,ccode,legal_person,responser,investor,runner,reg_date,status,updated ) values (%s,%s,%s, %s, %s,%s,%s, %s,%s,%s, %s,%s)"
update_string = "update gs_basic set gs_basic_id = %s,name = %s ,legal_person = %s ,responser=%s,investor = %s,runner = %s,status = %s ,reg_date = %s,uuid = %s where gs_basic_id = %s"
update_ccode = 'update gs_basic set gs_basic_id = %s,ccode = %s ,name = %s,legal_person = %s,responser =%s,investor =%s,runner =%s,status =%s,reg_date=%s,uuid = %s where gs_basic_id =%s'
search_string = 'insert into gs_search(gs_basic_id,user_id,token,keyword,name,province,code,ccode,legal_person,runner,responser,investor,reg_date,status,if_new,uuid,page,created)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,uuid from gs_basic where code = %s or ccode = %s'
insert_history = 'insert into gs_basic_exp(gs_basic_id,history,updated)values(%s,%s,%s)'
select_basic_exp = 'select gs_basic_exp_id from gs_basic_exp where gs_basic_id = %s'
update_basic = 'update gs_basic_exp set gs_basic_exp_id =%s,gs_basic_id = %s,history = %s,updated = %s where gs_basic_exp_id = %s'


class Search_Info:
	# 用于获取网页cookies
	def get_cookies(self):
		i = 1
		cookies = None
		while i > 0:
			try:
				request = session.get("http://www.gsxt.gov.cn/index.html", headers=config.headersfirst,
									  proxies=config.proxies, timeout=5)
				status_code = request.status_code
				# print status_code
				if status_code == 200:
					cookies = request.cookies
					break
				else:
					i = i - 1
			except Exception, e:
				logging.info('cookies error:%s' % e)
				i = i - 1
				time.sleep(3)
		return cookies
	
	# 用于获取validate与challenge
	def break_password(self, cookies):
		url = config.break_url
		try:
			result = session.get(url, cookies=cookies, headers=config.headersfirst, proxies=config.proxies)
			pattern = re.compile('<html>.*</html>')
			fail = re.findall(pattern, result.content)
			if len(fail) == 0:
				json_list = json.loads(result.content)
				message = json_list["message"]
				if message == 'success':
					success_flag = json_list["success"]
					challenge = json_list["challenge"]
					validate = json_list["validate"]
				else:
					success_flag, challenge, validate = 0, None, None
			else:
				success_flag, challenge, validate = 0, None, None
		except Exception, e:
			logging.error('break error %s' % e)
			success_flag, challenge, validate = 0, None, None
		return success_flag, challenge, validate, cookies
	
	# 循环破解极验验证码
	def loop_break_password(self):
		success_flag = 0
		i = 2
		try:
			while i > 0:
				if success_flag == 0 or validate == None or cookies == None:
					cookies = self.get_cookies()
					# print cookies
					success_flag, challenge, validate, cookies = self.break_password(cookies)
					i = i - 1
				elif success_flag == 1 or i <= 0:
					break
		except Exception, e:
			challenge, validate = None, None
			logging.error('break password error: %s' % e)
		
		return challenge, validate, cookies
	
	# 循环得到validate
	def last_request(self, url, keyword, challenge, validate, cookies, pagenumber):
		encryed_string = urllib.quote(keyword)
		search_text = config.search_text % (encryed_string, challenge, validate, validate)
		
		if int(pagenumber) == 1:
			result = requests.post(url, search_text, cookies=cookies, headers=config.headers, proxies=config.proxies)
			result = etree.HTML(result.content)
			span = result.xpath("//span[@class='search_result_span1']")[0]
			spantext = span.xpath('string(.)')
			number = int(spantext)
			# print number
			information = self.get_need_info(result)
			if int(number) == 1:
				page = 1
				return information, page
			elif int(number) > 1:
				if int(number) % 10 == 0:
					page = int(number) / 10
				elif int(number) % 10 != 0:
					page = int(number) / 10 + 1
				return information, page
			elif int(number) == 0:
				page = 0
				return information, page
		elif int(pagenumber) > 1:
			result = requests.post(url, search_text, cookies=cookies, headers=config.headers)
			result = etree.HTML(result.content)
			information = self.get_need_info(result)
			return information, totalpage
	
	# 将搜索结果插入到search表中
	def insert_search(self, keyword, user_id, info, cursor, connect, pagenumber):
		insert_flag, update_flag = 0, 0
		remark = 0
		try:
			flag = len(info)
			for key in info.keys():
				url = info[key][0]
				company = info[key][1]
				status = info[key][2]
				code = info[key][3]
				provin = judge_province(code)
				daibiao = info[key][4]
				legal_person, investor, runner, responser = self.judge_position(daibiao)
				dates = info[key][5]
				history = info[key][6]
				count = cursor.execute(select_string, (code, code))
				if int(count) == 0:
					if_new = 1
					gs_basic_id = 0
					uuid = 'S'
					gs_basic_id = self.update_to_basic(int(count), info[key], cursor, connect, gs_basic_id, uuid)
					updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
					row_count = cursor.execute(search_string, (
					gs_basic_id, user_id, unique_id, keyword, company, provin, code, code, legal_person, runner,
					responser, investor, dates, status, if_new, url, pagenumber, updated))
					connect.commit()
					insert_flag += row_count
					
					if history != None:
						string = select_basic_exp % gs_basic_id
						count = cursor.execute(string)
						if count == 0:
							updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
							cursor.execute(insert_history, (gs_basic_id, history, updated_time))
							connect.commit()
						elif int(count) == 1:
							updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
							gs_basic_exp_id = cursor.fetchall()[0][0]
							cursor.execute(update_basic,
										   (gs_basic_exp_id, gs_basic_id, history, updated_time, gs_basic_exp_id))
							connect.commit()
				elif int(count) == 1:
					if_new = 0
					uuid = 'S'
					updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
					gs_basic_id = cursor.fetchall()[0][0]
					self.update_to_basic(int(count), info[key], cursor, connect, gs_basic_id, uuid)
					row_count = cursor.execute(search_string, (
						gs_basic_id, user_id, unique_id, keyword, company, provin, code, code, legal_person, runner,
						responser,
						investor, dates, status, if_new, url, pagenumber, updated))
					connect.commit()
					insert_flag += row_count
					update_flag += 1
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
						self.update_to_basic(remark, info[key], cursor, connect, gs_basic_id, uuid)
					counts = cursor.execute(search_string, (
						basic_id, user_id, unique_id, keyword, company, provin, code, code, legal_person, runner,
						responser,
						investor, dates, status, if_new, url, pagenumber, updated))
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
	
	# 用于将数据更新到basic表中
	def update_to_basic(self, count, info, cursor, connect, gs_basic_id, uuid):
		company = info[1]
		status = info[2]
		code = info[3]
		daibiao = info[4]
		provin = judge_province(code)
		legal_person, investor, runner, responser = self.judge_position(daibiao)
		dates = info[5]
		if count == 0:
			m = hashlib.md5()
			m.update(code)
			id = m.hexdigest()
			updated = deal_html_code.get_before_date()
			cursor.execute(insert_string, (
			(id, provin, company, code, code, legal_person, investor, runner, responser, dates, status, updated)))
			gs_basic_id = connect.insert_id()
			connect.commit()
			return gs_basic_id
		elif count == 1:
			pattern = re.compile('^9')
			reserach = re.findall(pattern, code)
			if len(reserach) == 1:
				# updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				cursor.execute(update_ccode, (
				gs_basic_id, code, company, legal_person, responser, investor, runner, status, dates, uuid,
				gs_basic_id))
				connect.commit()
			elif len(reserach) == 0:
				# updated = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
				cursor.execute(update_string, (
				gs_basic_id, company, legal_person, responser, investor, runner, status, dates, uuid, gs_basic_id))
				connect.commit()
			return 0
	
	def judge_position(self, daibiao):
		if len(daibiao.split(':')) == 2:
			position = daibiao.split(':')[0]
			poname = daibiao.split(':')[1]
		else:
			position = daibiao.split('：')[0]
			poname = daibiao.split('：')[1]
		
		if u'法定代表人' == position:
			legal_person = poname
			responser = None
			investor = None
			runner = None
		elif u'经营者' == position:
			runner = poname
			legal_person = None
			responser = None
			investor = None
		elif u'负责人' == position:
			responser = poname
			runner = None
			legal_person = None
			investor = None
		elif u'投资人' == position:
			investor = poname
			responser = None
			runner = None
			legal_person = None
		elif u'执行事务合伙人' == position:
			legal_person = poname
			list = re.split(u'、', legal_person)
			legal_person = list[0] + '等'
			investor = None
			runner = None
			responser = None
		return legal_person, investor, runner, responser
	
	# 用于获取所需信息
	def get_need_info(self, result):
		information = {}
		a_list = result.xpath("//div[@class='main-layout fw f14']/a[@class='search_list_item db']")
		for item in a_list:
			tempinfo = self.deal_info(item)
			information = dict(information, **tempinfo)
		return information
	
	# 用于抽取单条信息内容
	def deal_info(self, item):
		info = {}
		href = item.xpath("./@href")[0]
		url = url_first + href
		company = item.xpath('./h1[@class="f20"]')[0].xpath('string(.)')
		company = remove_symbol(company)
		status = item.xpath('./div[@class="wrap-corpStatus"]')[0].xpath('string(.)')
		status = remove_symbol(status)
		code = item.xpath('.//div[@class="div-map2"]')[0].xpath('string(.)')
		code = remove_symbol(code)
		# print code
		if len(code.split(':')) == 2:
			code = code.split(':')[1]
		else:
			code = code.split('：')[1]
		
		daibiao = item.find('.//div[@class="div-user2"]').xpath('string(.)')
		daibiao = remove_symbol(daibiao)
		dates = item.find('.//div[@class="div-info-circle2"]').xpath('string(.)')
		dates = remove_symbol(dates)
		dates = dates.split('：')[1]
		dates = change_chinese_date(dates)
		history_name = item.xpath('.//div[@class="div-info-circle3"]')
		
		if len(history_name) != 0:
			history = item.xpath('.//div[@class="div-info-circle3"]/span[@class="g3"]')[0].xpath('string(.)')
		else:
			history = None
		history = remove_symbol(history)
		if history != None:
			list = re.split('；', str(history))
			templist = []
			for k, temp in enumerate(list):
				if temp != u'':
					templist.append(temp)
			history = ';'.join(templist)
		
		info[code] = [url, company, status, code, daibiao, dates, history]
		return info
	
	def printinfo(self, flag, insert, update, unique, cookiesarray, validate, challenge, totalpage, rspage):
		info = {
			"flag": 0,
			"insert": 0,
			"update": 0,
			"unique": 0,
			"cookies": 0,
			"challenge": 0,
			"validate": 0,
			"totalpage": 0,
			"rspage": 0,
			"jsluid": 0,
			"jsessionid": 0
		}
		rspage = int(rspage)
		totalpage = int(totalpage)
		if rspage >= totalpage:
			rspage = 0
		# elif int(flag)!=1:
		#     rspage = 0
		# print type(cookiesarray)
		info["flag"] = int(flag)
		info["insert"] = int(insert)
		info["update"] = int(update)
		info["challenge"] = str(challenge)
		
		if flag != 100000001 and flag != 100000002:
			info["cookies"] = cookiesarray["tlb_cookie"]
		info["validate"] = str(validate)
		info["totalpage"] = int(totalpage)
		info["rspage"] = int(rspage)
		info["unique"] = unique
		if flag != 100000001 and flag != 100000002:
			info["jsluid"] = cookiesarray["__jsluid"]
			info["jsessionid"] = cookiesarray["JSESSIONID"]
		print info


# 函数入口
def main():
	flag, rspage, insert_flag, update_flag, challenge, validate, cookies, total_page = 0, 0, 0, 0, 0, 0, 0, 0
	try:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		searchobject = Search_Info()
		if int(pagenumber) == 1:
			url = config.search_url
			challenge, validate, cookies = searchobject.loop_break_password()
			# print cookies
			if cookies == None:
				flag = 100000001
				# print flag
				searchobject.printinfo(flag, insert_flag, update_flag, unique_id, cookies_params, validate_params,
									   challenge_params, total_page, rspage)
			elif challenge == None or validate == None:
				flag = 100000002
				searchobject.printinfo(flag, insert_flag, update_flag, unique_id, cookies_params, validate_params,
									   challenge_params, total_page, rspage)
			else:
				cookies = requests.utils.dict_from_cookiejar(cookies)
				info, total_page = searchobject.last_request(url, keyword, challenge, validate, cookies, pagenumber)
				flag, insert_flag, update_flag = searchobject.insert_search(keyword, user_id, info, cursor, connect,
																			pagenumber)
				searchobject.printinfo(flag, insert_flag, update_flag, unique_id, cookies, validate,
									   challenge, total_page, pagenumber)
		elif int(pagenumber) > 1:
			url = 'http://www.gsxt.gov.cn/corp-query-search-%s.html' % pagenumber
			cookiesarray = {
				'tlb_cookie': '',
				'__jsluid': '',
				'HttpOnly': None,
				'JSESSIONID': ''
			}
			cookiesarray["tlb_cookie"] = cookies_params
			cookiesarray["__jsluid"] = jsluid
			cookiesarray["JSESSIONID"] = jsessionid
			# cookies = eval(cookiesarray)
			cookies = requests.utils.cookiejar_from_dict(cookiesarray, cookiejar=None, overwrite=True)
			info, total_page = searchobject.last_request(url, keyword, challenge_params, validate_params, cookies,
														 pagenumber)
			flag, insert_flag, update_flag = searchobject.insert_search(keyword, user_id, info, cursor, connect,
																		pagenumber)
			searchobject.printinfo(flag, insert_flag, update_flag, unique_id, cookies, validate_params,
								   challenge_params, total_page, pagenumber)
	except Exception, e:
		flag = 100000005
		# print e
		searchobject.printinfo(flag, insert_flag, update_flag, unique_id, cookies, validate, challenge, total_page,
							   rspage)
		logging.error("error:%s" % e)
	finally:
		cursor.close()
		connect.close()


if __name__ == "__main__":
	# print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	# start = time.time()
	main()
	# print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
