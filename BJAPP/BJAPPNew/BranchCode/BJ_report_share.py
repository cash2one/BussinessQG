#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_report_share.py
# @Author: Lmm
# @Date  : 2017-09-11
# @Desc  : 用于处理年报中的股东及出资信息
from lxml import etree
import requests
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
import re
import time
import logging
import hashlib

share_string = 'insert into gs_report_share(gs_basic_id,gs_report_id,province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,created,updated) values ' \
			   '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
share_url = 'http://qyxy.baic.gov.cn/wapnb/wapnbAction!wapgdcz_bj.dhtml?entid={}&cid={}&pageNo={}&pageSize=&clear='
url = 'http://qyxy.baic.gov.cn/wapnb/wapnbAction!wapgdcz_bj.dhtml?clear=true&cid=6afec6bdec1d41da962d379704ea4ded&entid=3673C177A85C4D78BE51FF5917538C4D'


def name(url):
	headers = config.headers_detail
	content, status_code = Send_Request().send_request(url, headers)
	# print content
	info = {}
	if status_code == 200:
		flag = 1
		result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
		dl = result.xpath("//div[@class='viewBox']//dl")[0]
		
		datalist = etree.tostring(dl).split('<dt style="color:#333;margin-bottom:10px;"/>')
		datalist.remove(datalist[0])
		if len(datalist) > 0:
			pattern = re.compile(".*共(.*?)页.*")
			number = re.findall(pattern, content)
			if len(number) == 1:
				totalpage = int(number[0])
			else:
				totalpage = 0
			if int(totalpage) == 1:
				j = 0
				deal_single_info(datalist, info, j)
			else:
				j = 0
				deal_single_info(datalist, info, j)
				entid = deal_html_code.match_entid(url)
				cid = deal_html_code.match_cid(url)
				
				for k in xrange(2, totalpage + 1):
					href = share_url.format(entid, cid, k)
					content, status_code = Send_Request().send_request(href, headers)
					if status_code == 200:
						start = k * 5 + 1
						result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
						dl = result.xpath("//div[@class='viewBox']//dl")[0]
						datalist = etree.tostring(dl).split(
							'<dt style="color:#333;margin-bottom:10px;"/>')
						datalist.remove(datalist[0])
						
						if len(datalist) > 0:
							deal_single_info(datalist, info, start)
					else:
						pass
		else:
			logging.info("无股东及出资信息")
	else:
		flag = 100000004
	
	info = deal_html_code.remove_repeat(info)
	return info, flag


def deal_single_info(datalist, info, j):
	for i, single in enumerate(datalist, j):
		single = etree.HTML(single, parser=etree.HTMLParser(encoding='utf-8'))
		# print single.xpath('string(.)')
		string = u'股东'
		name = deal_dd_content(string, single)
		string = u'认缴出资额'
		reg_amount = deal_dd_content(string, single)
		string = u'认缴出资时间'
		reg_date = deal_dd_content(string, single)
		string = u'认缴出资方式'
		reg_way = deal_dd_content(string, single)
		string = u"认缴出资额"
		ac_amount = deal_dd_content(string, single)
		string = u'实缴出资时间'
		ac_date = deal_dd_content(string, single)
		string = u'实缴出资方式'
		ac_way = deal_dd_content(string, single)
		uuid = ''
		info[i] = [name, uuid, reg_amount, reg_way, reg_date, reg_way, ac_amount, ac_date, ac_way]


# 用于处理dd标签中的内容
def deal_dd_content(string, result):
	dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
	dd = dd[0]
	data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
	return data


def update_to_db(gs_report_id, gs_basic_id, year, cursor, connect, information, province):
	insert_flag, update_flag = 0, 0
	remark = 0
	total = len(information)
	try:
		for key in information.keys():
			name, uuid, reg_amount, reg_way = information[key][0], information[key][1], information[key][2], \
											  information[key][3]
			reg_date, reg_way, ac_amount, ac_date = information[key][4], information[key][5], information[key][6], \
													information[key][7]
			ac_way = information[key][8]
			m = hashlib.md5()
			m.update(str(gs_basic_id) + str(year) + str(name) + str(reg_amount))
			uuid = m.hexdigest()
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			flag = cursor.execute(share_string, (
				gs_basic_id, gs_report_id, province, name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date,
				ac_way, updated_time, updated_time))
			connect.commit()
			insert_flag += flag
	except Exception, e:
		remark = 100000006
		logging.error('share error %s' % e)
	finally:
		if remark < 100000001:
			remark = insert_flag
		return remark, total, insert_flag, update_flag
		# name(url)
