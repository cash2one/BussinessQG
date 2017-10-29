#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_shareholder.py
# @Author: Lmm
# @Date  : 2017-09-22
# @Desc  : 用于获得股东出资信息

from PublicCode import  config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Connect_to_DB
from PublicCode import deal_html_code
from PublicCode.Public_Code import Log
from PublicCode.Public_Code import Judge
import re
import logging
import time
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,types,license_type,license_code,ra_date, ra_ways, true_amount,reg_amount,ta_ways,ta_date,country,address,iv_basic_id,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s and cate = %s'

select_name = 'select gs_basic_id from gs_unique where name = "%s"'
update_share = 'update gs_shareholder set quit = 1 where gs_basic_id = %s and cate = 0'
update_quit = 'update gs_shareholder set quit = 0,updated = %s where gs_shareholder_id = %s and gs_basic_id = %s'

sharedetail = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryGdczGdxx=true'
params = 'id={0}&org={1}&capiTypeName={2}&type={3}'

class Shareholder:
	def deal_single_info(self,data,info):
		for i,singledata in enumerate(data):
			name = singledata["STOCK_NAME"]
			license_code = singledata["IDENT_NO"]
			license_type = singledata["IDENT_TYPE_NAME"]
			types = singledata["STOCK_TYPE"]
			if types ==None:
				types = ''
			id = singledata["ID"]
			org = singledata["ORG"]
			country = singledata["COUNTRY"]
			address = singledata["STOCK_ADDR"]
			capiTypeName = singledata["CAPI_TYPE_NAME"]
			type = 'rj'
			rj_url = sharedetail+ params.format(id,org,capiTypeName,type)
			ra_date,ra_ways,reg_amount = self.get_detail_info(rj_url,type)
			type = 'sj'
			sj_url = sharedetail+ params.format(id,org,capiTypeName,type)
			ta_date,ta_ways,true_amount = self.get_detail_info(sj_url,type)
			
			info[i] = [name, license_code, license_type, types, ra_date, ra_ways, true_amount, reg_amount,
							  ta_ways,ta_date, country, address]
	
	#用于获得认缴,实际缴纳
	def get_detail_info(self,url,type):
		if type =="rj":
			result,status_code = Send_Request(url,config.headers).send_request()
			if status_code ==200:
				data = json.loads(result.content)["data"]
				if len(data)>0:
					data = data[0]
					ra_date = data["SHOULD_CAPI_DATE"]
					ra_ways = data["INVEST_TYPE_NAME"]
					reg_amount = data["SHOULD_CAPI_DATE"]
				else:
					logging.info("无认缴信息")
					ra_date, ra_ways, reg_amount = '0000-00-00','',''
			else:
				ra_date, ra_ways, reg_amount = '0000-00-00', '', ''
			return ra_date, ra_ways, reg_amount 
		elif type == "sj":
			result,status_code = Send_Request(url,config.headers).send_request()
			if status_code ==200:
				data = json.loads(result.content)["data"]
				if len(data)>0:
					data = data[0]
					ta_date = data["REAL_CAPI_DATE"]
					ta_ways = data["REAL_CAPI"]
					true_amount = data["INVEST_TYPE_NAME"]
				else:
					logging.info("无实缴信息")
					ta_date, ta_ways, true_amount = '0000-00-00','',''
			else:
				ta_date, ta_ways, true_amount = '0000-00-00', '', ''
			return ta_date, ta_ways, true_amount
		else:
			pass
		
	def update_to_db(self, info, gs_basic_id):
		cate = 0
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			string = update_share % gs_basic_id
			cursor.execute(string)
			connect.commit()
			cursor.close()
			connect.close()
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				name, license_code, license_type = info[key][0], info[key][1], info[key][2]
				types, ra_date, ra_ways, true_amount = info[key][3], info[key][4], info[key][5], info[key][6]
				reg_amount, ta_ways, ta_date = info[key][7], info[key][8], info[key][9]
				
				country, address = info[key][10], info[key][11]
				iv_basic_id = 0
				if name != '' or name != None:
					pattern = re.compile('.*公司.*|.*中心.*|.*集团.*|.*企业.*')
					result = re.findall(pattern, name)
					if len(result) == 0:
						iv_basic_id = 0
					else:
						select_unique = select_name % name
						number = cursor.execute(select_unique)
						if number == 0:
							iv_basic_id = 0
						elif int(number) == 1:
							iv_basic_id = cursor.fechall[0][0]
				else:
					iv_basic_id = 0
				
				count = cursor.execute(select_string, (gs_basic_id, name, types, cate))
				
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(share_string, (
						gs_basic_id, name, cate, types, license_type, license_code, ra_date, ra_ways, true_amount,
						reg_amount, ta_ways, ta_date, country, address, iv_basic_id, updated_time))
					insert_flag += rows_count
					connect.commit()
				elif int(count) == 1:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					gs_shareholder_id = cursor.fetchall()[0][0]
					cursor.execute(update_quit, (updated_time, gs_shareholder_id, gs_basic_id))
					connect.commit()
		except Exception, e:
			remark = 100000006
			logging.error("shareholder error:%s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag


def main(org, id, seqid, regno, gs_basic_id):
	pattern = "shareholder"
	flag = Judge().update_info2(pattern, org, id, seqid, regno, Shareholder, gs_basic_id)
	
		

