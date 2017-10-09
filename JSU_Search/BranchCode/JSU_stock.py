#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_stock.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获得股权出质登记信息
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
from PublicCode.Public_Code import Judge
from lxml import etree
import logging
import time


stock_string = 'insert into gs_stock(gs_basic_id,equityno,pledgor,pled_blicno,impam,imporg,imporg_blicno,equlle_date,public_date,type,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_stock = 'select gs_stock_id from gs_stock where gs_basic_id = %s and equityno = %s'
update_stock = 'update gs_stock set gs_basic_id = %s,pledgor = %s,pled_blicno = %s,impam = %s,imporg = %s,imporg_blicno = %s,equlle_date = %s,public_date = %s,type = %s ,updated = %s where gs_stock_id = %s'


class Stock:
	def deal_single_info(self, data, info):
		for i, singledata in enumerate(data):
			equityNo = singledata["REGISTER_NO"]
			impAm = singledata["MORTGAGOPR_STOCK"]
			pledBLicNo = singledata["IDENT_NO"]
			pledgor = singledata["MORTGAGOR_NAME"]
			type = singledata["STATUS"]
			equPleDate = singledata["START_DATE"]
			equPleDate = deal_html_code.change_chinese_date(equPleDate)
			publicDate = singledata["CREATE_DATE"]
			publicDate = deal_html_code.change_chinese_date(publicDate)
			D1 = data["D1"]
			data = etree.HTML(D1, parser=etree.HTMLParser(encoding="utf-8"))
			tdlist = data.xpath("//tr/td")
			impOrg = deal_html_code.remove_space(tdlist[5].xpath("/text()")[0])
			impOrgBLicNo = deal_html_code.remove_space(tdlist[6].xpath("/text()")[0])
			RN = singledata["RN"]
			info[RN] = [equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate, type]
	
	def update_to_db(self, info,gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				equityNo, pledgor, pledBLicNo = info[key][0], info[key][1], info[key][2]
				impAm, impOrg, impOrgBLicNo = info[key][3], info[key][4], info[key][5]
				equPleDate, publicDate, type = info[key][6], info[key][7], info[key][8]
				
				count = cursor.execute(select_stock, (gs_basic_id, equityNo))
				
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(stock_string, (
						gs_basic_id, equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate,
						type,
						updated_time))
					insert_flag += rows_count
					connect.commit()
				elif int(count) == 1:
					# print equityNo
					gs_stock_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					
					rows_count = cursor.execute(update_stock,
												(gs_basic_id, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo,
												 equPleDate,
												 publicDate, type, updated_time, gs_stock_id))
					# print rows_count
					update_flag += rows_count
					connect.commit()
		except Exception, e:
			cursor.close()
			connect.close()
			remark = 100000001
			# print "stock error:", e
			logging.error("stock error: %s" % e)
		finally:
			flag = insert_flag + update_flag
			if remark < 100000001:
				remark = flag
			# print remark
			return remark, total,insert_flag, update_flag


def main(org, id, seqid, regno, gs_basic_id):
	pattern = "stock"
	Judge().update_info2(pattern, org, id, seqid, regno, Stock, gs_basic_id)