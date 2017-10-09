#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_branch.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于对分支机构信息的获取及更新
from PublicCode import  config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
from PublicCode import deal_html_code
from PublicCode.Public_Code import Judge
import logging
import time
import json
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()



headers = config.headers
branch_string = 'insert into gs_branch(gs_basic_id,id,code,ccode,name,gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select * from gs_branch where id = %s and gs_basic_id =%s'
update_branch_py = 'update gs_py set gs_py_id= %s, gs_branch = %s,updated = %s where gs_py_id = %s'



class Branch:
	def __init__(self, url, headers):
		self.url = url
		self.headers = headers
	#用于获取信息
	def get_info(self):
		result,status_code = Send_Request(self.url,self.headers).send_request()
		info = {}
		
		if status_code ==200:
			flag = 1
			data = json.loads(result.content)
			
			for i,singledata in enumerate(data):
				
				name = singledata["DIST_NAME"]
				if name ==None:
					name = ''
				code = singledata["DIST_REG_NO"]
				if code == None:
					code = ''
				
				#省份代号中没有以9开头的因此可以用是否以9开头区分是否为注册号
				if code.startswith('9'):
					ccode = code
					code = ''
				else:
					ccode = ''
				gov_dept = singledata["DIST_BELONG_ORG"]
				if name =='' and code == '':
					pass
				else:
					info[i] = [name, code,ccode, gov_dept]
		else:
			flag = 100000004
		return info,flag
	def update_to_db(self,info,gs_basic_id):
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		insert_flag,update_flag = 0,0
		flag = 0
		total = len(info)
		try:
			for key in info.keys():
				name = info[key][0]
				code = info[key][1]
				ccode = info[key][2]
				gov_dept = info[key][3]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(name))
				id = m.hexdigest()
				count = cursor.execute(select_string,(id, gs_basic_id))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(branch_string, (gs_basic_id,id, code,ccode, name, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			flag = 100000006
			logging.error('branch error: %s'%e)
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = insert_flag
			return flag,total,insert_flag,update_flag
def main(org,id,seq_id,regno,gs_basic_id,gs_py_id):
	pattern = "branch"
	flag = Judge().update_info1(pattern, org, id, seq_id, regno, Branch, gs_basic_id)
	Judge().update_py(gs_py_id,update_branch_py,flag)
	
	
	
# if __name__ == '__main__':
# 	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# 	start = time.time()
# 	main(org, id, seq_id, regno,gs_basic_id)
# 	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
