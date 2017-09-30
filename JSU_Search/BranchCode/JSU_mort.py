#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_mort.py
# @Author: Lmm
# @Date  : 2017-09-22
# @Desc  : 用于获得动产抵押信息

from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Log

from PublicCode.Public_Code import Judge
import logging
import time
import json
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_mort = 'select gs_mort_id from gs_mort where gs_basic_id = %s and code = %s'
mort_string = 'insert into gs_mort(gs_basic_id,id,code, dates, dept, amount, status,cates,period, ranges, remark,cancle_cause,updated)' \
              'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_mort = 'update gs_mort set gs_mort_id = %s ,dates = %s, dept = %s, amount = %s, status = %s,cates = %s,period = %s, ranges = %s, remark = %s,cancle_cause = %s,updated = %s ' \
              'where gs_mort_id = %s'

select_goods = 'select gs_mort_goods_id from gs_mort_goods where gs_mort_id = %s and name = %s and ownership = %s and situation = %s'
goods_string = 'insert into gs_mort_goods(gs_mort_id,id,gs_basic_id,name,ownership,situation,remark,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
update_goods_sql = 'update gs_mort_goods set gs_mort_goods_id = %s,situation = %s,remark = %s,updated = %s where gs_mort_goods_id = %s'

select_person = 'select gs_mort_person_id from gs_mort_person where gs_mort_id = %s and name = %s'
person_string = 'insert into gs_mort_person(gs_mort_id,id,gs_basic_id,name,cert,number,updated) values (%s,%s,%s,%s,%s,%s,%s)'
update_mort_person = 'update gs_mort_person set gs_mort_person_id = %s,name = %s,cert = %s,updated = %s where gs_mort_person_id = %s'


person_url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryDcdyDyqrgk=true'
goods_url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/publicInfoQueryServlet.json?queryDcdyDywgk=true'

params = '&org={0}&id={1}&seqId={2}'


headers = config.headers
class Mort:
	def deal_single_info(self,data,info):
		
		for i,singledata in enumerate(data):
			org = singledata["ORG"]
			id = singledata["ID"]
			seqid = singledata["SEQ_ID"]
			code = singledata["GUARANTY_REG_NO"]
			dates = singledata["START_DATE"]
			dates = deal_html_code.change_chinese_date(dates)
			dept = singledata["CREATE_ORG"]
			amount = singledata["ASSURE_CAPI"]
			amount = deal_html_code.match_float(amount)
			status = singledata["STATUS"]
			cates = singledata["ASSURE_KIND"]
			start_date = singledata["ASSURE_START_DATE"]
			
			start_date = deal_html_code.change_date_style(start_date)
			end_date = singledata["ASSURE_END_DATE"]
			end_date = deal_html_code.change_date_style(end_date)
			period = "自"+start_date +"至" +end_date
			ranges = singledata["ASSURE_SCOPE"]
			remark = singledata["REMARK"]
			cancel_cause = singledata["WRITEOFF_REASON"]
			RN = singledata["RN"]
			types = 'mort_person'
			person_href = person_url+params.format(org,id,seqid)
			person_info = self.get_detail_info(person_href,types)
			types = 'mort_goods'
			goods_href = goods_url+params.format(org,id,seqid)
			# print goods_href
			goods_info = self.get_detail_info(goods_href,types)
			info[RN] = [code, dates, dept, amount, status, cates, period, ranges, remark, cancel_cause, person_info, goods_info]
		
	#获取动产抵押权人信息，动产抵押权物信息
	def get_detail_info(self,url,types):
		info = {}
		result,status_code = Send_Request(url,headers).send_request()
		if status_code == 200:
			data = json.loads(result.content)["data"]
			if types == 'mort_person':
				if len(data)>0:
					for i, singledata in enumerate(data):
						name = singledata["AU_NAME"]
						cert = singledata["AU_CER_NO"]
						number = singledata["AU_CER_TYPE"]
						info[i] = [name, cert, number]
				else:
					logging.info("无动产抵押权人信息！")
			elif types =="mort_goods":
				if len(data) >0:
					for i,singledata in enumerate(data):
						name = singledata["NAME"]
						ownership = singledata["BELONG_KIND"]
						situation = singledata["PA_DETAIL"]
						remark = singledata["REMARK"]
						info[i] = [name, ownership, situation, remark]
		else:
			logging.info("获取动产抵押权人信息失败！")
		return info
	def update_to_db(self,info,gs_basic_id):
		update_flag, insert_flag = 0, 0
		mort_flag = 0
		totalinfo = len(info)
		
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				code, dates, dept, amount = info[key][0], info[key][1], info[key][2], info[key][3]
				status, cates, period, ranges, remark = info[key][4], info[key][5], info[key][6], info[key][7], \
														info[key][8]
				cancel_cause = info[key][9]
				person_info = info[key][10]
				goods_info = info[key][11]
				count = cursor.execute(select_mort, (gs_basic_id, code))
				if count == 0:
					m = hashlib.md5()
					m.update(code)
					id = m.hexdigest()
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(mort_string, (
						gs_basic_id, id, code, dates, dept, amount, status, cates, period, ranges, remark,
						cancel_cause,updated_time))
					gs_mort_id = connect.insert_id()
					insert_flag += flag
					connect.commit()
				elif int(count) == 1:
					gs_mort_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(update_mort, (gs_mort_id,
														dates, dept, amount, status, cates, period, ranges, remark,cancel_cause,
														updated_time, gs_mort_id))
					update_flag += flag
					connect.commit()
				self.update_goods(gs_mort_id, gs_basic_id, cursor, connect, goods_info)
				self.update_person(gs_mort_id, gs_basic_id, cursor, connect, person_info)
		except Exception, e:
			# print e
			logging.info('mort error :%s' % e)
			mort_flag = 100000006
		finally:
			cursor.close()
			connect.close()
			total = insert_flag + update_flag
			if mort_flag < 100000001:
				mort_flag = total
			return mort_flag,totalinfo, insert_flag, update_flag
	
	def update_goods(self, gs_mort_id, gs_basic_id, cursor, connect, info):
		total = len(info)
		
		logging.info('mort_goods :%s' % total)
		goods_flag = 0
		insert_flag, update_flag = 0, 0
		try:
			for key in info.keys():
				name, ownership, situation, remark = info[key][0], info[key][1], info[key][2], info[key][3]
				
				count = cursor.execute(select_goods, (gs_mort_id, name, ownership,situation))
				if count == 0:
					m = hashlib.md5()
					m.update(name + ownership)
					id = m.hexdigest()
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(goods_string, (
						gs_mort_id, id, gs_basic_id, name, ownership, situation, remark, updated_time))
					insert_flag += flag
					connect.commit()
				elif int(count) == 1:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					gs_mort_goods_id = cursor.fetchall()[0][0]
					flag = cursor.execute(update_goods_sql,
										  (gs_mort_goods_id, situation, remark, updated_time, gs_mort_goods_id))
					update_flag += flag
		except Exception, e:
			# print e
			goods_flag = 100000006
			logging.info('mort_goods error:%s' % e)
		finally:
			executetotal = insert_flag + update_flag
			if goods_flag < 100000001:
				goods_flag = executetotal
			logging.info('execute mort_goods :%s' % executetotal)
			return total, goods_flag
	
	# 更新抵押人信息
	def update_person(self, gs_mort_id, gs_basic_id, cursor, connect, info):
		total = len(info)
		logging.info('person_info :%s' % total)
		insert_flag, update_flag = 0, 0
		person_flag = 0
		try:
			for key in info.keys():
				name, cert, number = info[key][0], info[key][1], info[key][2]
				
				count = cursor.execute(select_person, (gs_mort_id, name))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					m = hashlib.md5()
					m.update(number)
					id = m.hexdigest()
					flag = cursor.execute(person_string,
										  (gs_mort_id, id, gs_basic_id, name, cert, number, updated_time))
					insert_flag += flag
					connect.commit()
				elif int(count) == 1:
					gs_mort_person_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(update_mort_person,
										  (gs_mort_person_id, name, cert, updated_time, gs_mort_person_id))
					update_flag += flag
					connect.commit()
		except Exception, e:
			# print e
			person_flag = 100000006
			logging.info('mort_person error:%s' % e)
		finally:
			executetotal = insert_flag + update_flag
			if person_flag < 100000001:
				person_flag = executetotal
				logging.info('execute mort_person:%s' % executetotal)
			return total, person_flag
	
def main(org, id, seqid, regno, gs_basic_id):
	pattern = "mort"
	flag = Judge().update_info2(pattern, org, id, seqid, regno, Mort, gs_basic_id)
	

