#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_report.py
# @Author: Lmm
# @Date  : 2017-09-09
# @Desc  : 用于获取年报信息，并将年报信息插入到数据库中
from lxml import etree
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
import BJ_report_basic
import BJ_report_invest
import BJ_report_run
import BJ_report_schange
import BJ_report_share
import BJ_report_web
import BJ_report_permit
import requests
import re
import chardet
import logging
import random
import linecache
from PublicCode.Public_code import Judge_status

url = 'http://qyxy.baic.gov.cn/wapqyzb/wapqyzbAction!wapbsnd.dhtml?entId=ff80808153f02ac10153f36cdc4e7569'
select_report = 'select gs_report_id from gs_report where gs_basic_id = %s and year = %s'
province = 'BEJ'
gs_py_id = 1
gs_basic_id = 1243
a = random.randrange(1, 1001)  # 1-1000中生成随机数
# 从文件user-agent中对读取第a行的数据
theline = linecache.getline(r'user-agent.txt', a)
theline = theline.replace("\n", '')
headers = config.headers_detail
headers["User-Agent"] = theline
update_report_py = 'update gs_py set gs_py_id = %s ,report = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
update_run_py = 'update gs_py set gs_py_id = %s ,report_run = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
assure_py = 'update gs_py set gs_py_id = %s ,report_assure = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s '
invest_py = 'update gs_py set gs_py_id = %s ,report_invest = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
permit_py = 'update gs_py set gs_py_id = %s ,report_permit = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
schange_py = 'update gs_py set gs_py_id = %s ,report_schange = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
share_py = 'update gs_py set gs_py_id = %s,report_share = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
web_py = 'update gs_py set gs_py_id = %s,report_web = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
party_py = 'update gs_py set gs_py_id = %s ,report_party = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'


class Report:
	# 用与获取年报中各个年份的链接
	def get_year_href(self, url):
		href_list = {}
		result = requests.get(url, headers=headers)
		status_code = result.status_code
		cookies = result.cookies
		encode = chardet.detect(result.content)["encoding"]
		if status_code == 200 and encode == "utf-8":
			flag = 1
			content = result.content
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class= 'viewBox']//dl/dd")
			for i, single in enumerate(dl):
				href = config.host + single.xpath("./a/@href")[0]
				text = single.xpath("./a/text()")[0]
				pattern = re.compile("\d+")
				year = re.findall(pattern, text)[0]
				href_list[i] = [href, int(year)]
		else:
			flag = 100000004
		return flag, href_list, cookies
	
	# 用与获取年报各个部分分支的链接
	def get_report_branch_href(self, url, cookies):
		branch_list = {}
		content, status_code = Send_Request().send_request3(url, cookies, headers)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			div_list = result.xpath("//div[@class='categ_info_title_wz']")
			for i, single in enumerate(div_list):
				href = config.host + single.xpath('./a/@href')[0]
				text = single.xpath('./a/text()')[0]
				if '企业基本信息' in text:
					branch_list["basic"] = str(href)
				elif "股东及出资信息" in text:
					branch_list["share"] = str(href)
				elif "对外投资信息" in text:
					branch_list["invest"] = str(href)
				elif "企业资产状况信息" in text:
					branch_list["run"] = str(href)
				elif "生产经营情况" in text:
					branch_list["run"] = str(href)
				elif "担保信息" in text:
					branch_list["assure"] = str(href)
				elif "股权变更信息" in text:
					branch_list["schange"] = str(href)
				elif "网站或网店信息" in text:
					branch_list["web"] = str(href)
		else:
			flag = 100000004
		return branch_list, flag
	
	def get_all_report_info(self, href_list, cursor, connect, gs_basic_id, cookies):
		total = len(href_list)
		insert = 0
		error = 0
		for key in href_list.keys():
			href = href_list[key][0]
			year = href_list[key][1]
			count = cursor.execute(select_report, (gs_basic_id, year))
			if int(count) > 0:
				pass
			else:
				mark = self.get_single_report_info(href, year, cursor, connect, cookies, gs_basic_id)
				if mark == 1:
					insert += 1
				else:
					error += 1
		return total, insert, error
	
	def get_single_report_info(self, url, year, cursor, connect, cookies, gs_basic_id):
		branch_list, mark = self.get_report_branch_href(url, cookies)
		if mark == 1:
			if "basic" in branch_list.keys():
				basic_url = branch_list["basic"]
				info, flag = BJ_report_basic.name(basic_url, cookies, headers)
				if flag == 1:
					gs_report_id, remark = BJ_report_basic.update_to_db(gs_basic_id, info, year, cursor, connect,
																		province)
					if remark == 1:
						if "share" in branch_list.keys():
							share_url = branch_list["share"]
							info, flag = BJ_report_share.name(share_url)
							# print flag
							if flag == 1:
								remark, total, insert_flag, update_flag = BJ_report_share.update_to_db(gs_report_id,
																									   gs_basic_id,
																									   year, cursor,
																									   connect, info,
																									   province)
								Judge_status().update_py(gs_py_id, share_py, remark)
							else:
								Judge_status().update_py(gs_py_id, share_py, flag)
							
							# print remark, total, insert_flag, update_flag
						if "invest" in branch_list.keys():
							invest_url = branch_list["invest"]
							info, flag = BJ_report_invest.name(invest_url)
							if flag == 1:
								remark, total, insert_flag, update_flag = BJ_report_invest.update_to_db(gs_report_id,
																										gs_basic_id,
																										year, cursor,
																										connect, info,
																										province)
								Judge_status().update_py(gs_py_id, invest_py, remark)
							else:
								Judge_status().update_py(gs_py_id, invest_py, flag)
							# print remark, total, insert_flag, update_flag
						if "permit" in branch_list.keys():
							permit_url = branch_list["permit"]
							info, flag = BJ_report_permit.name(permit_url)
							if flag == 1:
								remark, total, insert_flag, update_flag = BJ_report_permit.update_to_db(gs_report_id,
																										gs_basic_id,
																										year, cursor,
																										connect, info,
																										province)
								Judge_status().update_py(gs_py_id, permit_py, remark)
							else:
								Judge_status().update_py(gs_py_id, permit_py, flag)
							# print remark, total, insert_flag, update_flag
						if "run" in branch_list.keys():
							run_url = branch_list["run"]
							info, flag = BJ_report_run.name(run_url, cookies, headers)
							# print info,flag
							if flag == 1 and len(info) > 0:
								remark = BJ_report_run.update_run_info(year, gs_report_id, gs_basic_id, cursor, connect,
																	   info, province)
								Judge_status().update_py(gs_py_id, update_run_py, remark)
							else:
								Judge_status().update_py(gs_py_id, update_run_py, flag)
						
						if "schange" in branch_list.keys():
							schange_url = branch_list["schange"]
							info, flag = BJ_report_schange.name(schange_url)
							if flag == 1:
								remark, total, insert_flag, update_flag = BJ_report_schange.update_to_db(gs_report_id,
																										 gs_basic_id,
																										 year, cursor,
																										 connect, info,
																										 province)
								Judge_status().update_py(gs_py_id, schange_py, remark)
							else:
								Judge_status().update_py(gs_py_id, schange_py, flag)
							# print remark, total, insert_flag, update_flag
						if "web" in branch_list.keys():
							web_url = branch_list["web"]
							info, flag = BJ_report_web.name(web_url)
							if flag == 1:
								remark, total, insert_flag, update_flag = BJ_report_web.update_to_db(gs_report_id,
																									 gs_basic_id, year,
																									 cursor,
																									 connect, info,
																									 province)
								Judge_status().update_py(gs_py_id, web_py, remark)
							else:
								Judge_status().update_py(gs_py_id, web_py, flag)
								# print remark, total, insert_flag, update_flag
				else:
					mark = flag
		else:
			mark = 100000006
			logging.info("get %s year report failed!")
		Judge_status().update_py(gs_py_id, update_report_py, mark)
		return mark


def main(gs_py_id, gs_basic_id):
	Log().found_log(gs_py_id, gs_basic_id)
	insert, error, total = 0, 0, 0
	info = {
		"flag": 0,
		"insert": 0,
		"error": 0,
		"total": 0
	}
	try:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		object = Report()
		flag, href_list, cookies = object.get_year_href(url)
		cookies = requests.utils.dict_from_cookiejar(cookies)
		if flag == 1:
			total, insert, error = object.get_all_report_info(href_list, cursor, connect, gs_basic_id, cookies)
	except Exception, e:
		# print e
		flag = 100000005
		logging.info("report error:%s" % e)
	finally:
		connect.close()
		cursor.close()
		info["flag"] = int(flag)
		info["total"] = int(total)
		info["insert"] = int(insert)
		info["error"] = int(error)
		print info


if __name__ == '__main__':
	main(gs_py_id, gs_basic_id)
