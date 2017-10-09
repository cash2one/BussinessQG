#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_brand.py
# @Author: Lmm
# @Date  : 2017-09-23
# @Desc  : 用于获得商标信息，并将所得信息插入到数据中
from PublicCode import config
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Log
from PublicCode.Public_Code import Judge
from PublicCode import deal_html_code
import logging
import time
import re
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

headers = config.headers
img_url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?querySbzcImg=true&intcls={0}&no={1}'
more_url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?querySbzc_more=true&intcls_={0}&reg_no_={1}'
service_url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?openSbzc=true&intcls_={0}&reg_no_={1}'

brand_string = 'insert into ia_brand(gs_basic_id,ia_zch, ia_flh, ia_zcgg,ia_servicelist, ia_zyqqx, ia_zcdate,img_url,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_brand = 'select ia_brand_id from ia_brand where ia_zch = "%s"'
update_brand = 'update ia_brand set ia_brand_id = %s,gs_basic_id = %s,ia_flh = %s, ia_zcgg = %s ,ia_servicelist = %s, ia_zyqqx = %s,ia_zcdate = %s,img_url =%s,updated = %s where ia_brand_id = %s'
update_brand_py = 'update gs_py set gs_py_id = %s ,gs_brand = %s,updated = %s where gs_py_id = %s'


class Brand:
	def __init__(self,url,headers):
		self.url = url
		self.headers = headers
	def get_info(self):
		result, status_code = Send_Request(self.url, self.headers).send_request()
		info = {}
		if status_code ==200:
			data = json.loads(result.content)
			flag = 1
			for i,data in enumerate(data):
				regno = data["REGNO"]
				intcls = data["INTCLS"]
				self.get_single_info(regno,intcls,info)
		else:
			flag = 100000004
		return info,flag
	#用于获得商标单条信息的内容
	def get_single_info(self,regno,intcls,info):
		
		url = more_url.format(intcls, regno)
		result,status_code = Send_Request(url, self.headers).send_request()
		if status_code ==200:
			data = json.loads(result.content)[0]
			ia_zch = regno
			ia_flh = intcls
			ia_zcgg = data["REGANNCNO"]
			url = service_url.format(intcls, regno)
			result,status_code = Send_Request(url, self.headers).send_request()
			if status_code == 200:
				servicedata = json.loads(result.content)
				ia_servicelist = ''
				for i, single in enumerate(servicedata):
					similarcode = single["SIMILARCODE"]
					goods = single["GOODS"]
					ia_servicelist = ia_servicelist+similarcode+'--'+goods
			else:
				ia_servicelist = ''
			
			begin = data["PERIBGN"]
			end = data["PERIEND"]
			
			if begin == '' and end == '':
				ia_zyqqx = ''
			else:
				ia_zyqqx = begin + '至' + end
			ia_zcdate = data["REGANNCDATE"]
			ia_zcdate = deal_html_code.change_chinese_date(ia_zcdate)
			tmImage = img_url.format(intcls,regno)
			info[regno] = [ia_zch, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate, tmImage]
	
	def update_to_db(self, info, gs_basic_id):
		
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				ia_zch, ia_flh, ia_zcgg = info[key][0], info[key][1], info[key][2]
				ia_servicelist, ia_zyqqx, ia_zcdate = info[key][3], info[key][4], info[key][5]
				ia_img_url = info[key][6]
				
				select_string = select_brand % ia_zch
				count = cursor.execute(select_string)
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(brand_string, (
						gs_basic_id, ia_zch, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate, ia_img_url,
						updated_time))
					insert_flag += rows_count
					connect.commit()
				elif count == 1:
					gs_brand_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(update_brand,
												(gs_brand_id, gs_basic_id, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx,
												 ia_zcdate,ia_img_url, updated_time, gs_brand_id))
					update_flag += rows_count
					connect.commit()
		except Exception, e:
			flag = 100000006
			logging.error("brand error: %s" % e)
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = insert_flag + update_flag
			return flag, total, insert_flag, update_flag


def main(org, id, seq_id, regno, gs_basic_id ):
	pattern = "brand"
	flag = Judge().update_info1(pattern, org, id, seq_id, regno, Brand, gs_basic_id)
	


