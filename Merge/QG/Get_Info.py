#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Get_Info.py
# @Author: Lmm
# @Date  : 2017-10-16
# @Desc  : 用于获得国家的全部信息

from BranchCode import GetUrl
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode import Bulid_Log
import QG_Update
import logging
import hashlib
import time
import re
import sys
# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_info = 'select gs_new_id,name,province from gs_new  where status = 1 limit 1'
update_status = 'update gs_new set gs_new_id = %s,status = 2,gs_basic_id = %s where gs_new_id = %s'
update_status1 = 'update gs_new set gs_new_id = %s,status = 404,gs_basic_id = 0 where gs_new_id = %s '
select_string = 'select gs_basic_id from gs_basic where code = %s or ccode = %s'
insert_string = "insert into gs_basic(uuid,id,province,name,code,ccode,legal_person, investor, runner, responser,reg_date,status,updated ) values (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
insert_history = 'insert into gs_basic_exp(gs_basic_id,history,updated)values(%s,%s,%s)'
select_basic_exp = 'select gs_basic_exp_id from gs_basic_exp where gs_basic_id = %s'
update_basic = 'update gs_basic_exp set gs_basic_exp_id =%s,gs_basic_id = %s,history = %s,updated = %s where gs_basic_exp_id = %s'

#新增一条信息到gs_basic表中
def insert_to_basic(information,cursor,connect,province):
	
	company = information[0][1]
	status = information[0][2]
	code = information[0][3]
	leader = information[0][4]
	dates = information[0][5]
	legal_person, investor, runner, responser = judge_position(leader)
	m = hashlib.md5()
	m.update(code)
	id = m.hexdigest()
	uuid = 'S'
	#将更新时间设置为当前时间减去30天，便于用户更新
	updated = deal_html_code.get_before_date()
	cursor.execute(insert_string, ((uuid,id, province, company, code, code, legal_person, investor, runner, responser, dates, status, updated)))
	gs_basic_id = connect.insert_id()
	connect.commit()
	return gs_basic_id
#用于判定是法定代表人还是经营者还是负责人等
def judge_position(daibiao):
	#根据中文冒号和英文冒号进行分割
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
#对信息进行更新
def update_info(cursor,connect,info,gs_new_id,province):
	url = info[0][0]
	code = info[0][3]
	history = info[0][6]
	count = cursor.execute(select_string, (code, code))
	if int(count) ==1:
		gs_basic_id = cursor.fetchall()[0][0]
		print "now the gs_basic_id is %s"%gs_basic_id
		cursor.execute(update_status, (gs_new_id, gs_basic_id, gs_new_id))
		connect.commit()
		QG_Update.update_all_info(url, gs_basic_id)
	elif count == 0:
		gs_basic_id = insert_to_basic(info,cursor,connect,province)
		print "now the gs_basic_id is %s" % gs_basic_id
		cursor.execute(update_status, (gs_new_id, gs_basic_id, gs_new_id))
		connect.commit()
		logging.info("now the excute basic id is %s" % gs_basic_id)
		QG_Update.update_all_info(url, gs_basic_id)
	else:
		pass #保留代码，以供以后有新的逻辑加入
	
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
	else:
		pass

#函数入口
def main():
	Bulid_Log.Log().found_log()
	try:
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		count = cursor.execute(select_info)
		if count == 0:
			print "there is no task need to do!"
		else:
			for gs_new_id,name,province in cursor.fetchall():
				print "now the gs_new_id is %s"%gs_new_id
				logging.info("now the gs_new id is %s"%gs_new_id)
				name = deal_html_code.remove_symbol(name)
				if province =='SHH' or province =="HEB" or province =="SCH" or province =="YUN" or province=="JSU":
					print "the province is out of range"
					logging.info("the province is out of range")
				elif name =='':
					print "this is an useless information!"
					logging.info("this is an useless information!")
				else:
					info, flag = GetUrl.main(name)
					if flag==1 and len(info)>0:
						update_info(cursor,connect,info,gs_new_id,province)
					else:
						logging.info("get cookies failed or there is no search information ,the status is %s" % flag)
						cursor.execute(update_status1, (gs_new_id, gs_new_id))
						connect.commit()
	except Exception,e:
		logging.info("unknown error:%s"%e)
if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main()
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
