#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_branch.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 用于获取北京信用分支机构信息并将信息插入到数据库中
import requests
from PublicCode import config
from PublicCode import deal_html_code
from lxml import etree
import re
import hashlib
import time

url = 'http://qyxy.baic.gov.cn/xycx/queryCreditAction!getEnt_Fzjgxx.dhtml?reg_bus_ent_id=0CD1263D6BB2009EE053A0630264009E&moreInfo=moreInfo&SelectPageSize=50&EntryPageNo=1&pageNo=1&pageSize=500&clear=true'
gs_basic_id = ''
branch_string = 'insert into gs_branch(gs_basic_id,id,code,name,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_string = 'select * from gs_branch where id = %s and gs_basic_id =%s'
class Branch:
	#用于获取网页信息
	def name(self,url):
		info = {}
		result = requests.get(url,headers=config.headers_detail)
		status_code = result.status_code
		if status_code ==200:
			result = etree.HTML(result.content,parser=etree.HTMLParser(encoding='utf-8'))
			total = result.xpath("//table[@id='tableIdStyle']//div/text()")[0]
			pattern = re.compile(u".*记录总数(.*?)条.*")
			number = re.findall(pattern,total)
			if len(number)==1:
				temp =int(number[0])
			trlist = result.xpath("//table[@id = 'tableIdStyle']//tr")
			for i,single in enumerate(trlist):
				tdlist = single.xpath("./td")
				if len(tdlist)==0 or len(tdlist)<4:
					pass
				else:
					# number = tdlist[0].xpath('./text()')
					name = deal_html_code.remove_symbol(tdlist[1].xpath("string(.)"))
					code = deal_html_code.remove_symbol(tdlist[2].xpath("string(.)"))
					gov_dept = deal_html_code.remove_symbol(tdlist[3].xpath("string(.)"))
					info[i] = [name,code,gov_dept]
		return info
	#将获取到的数据插入到数据库中
	def update_to_db(self,info,cursor,connect,gs_basic_id):
		insert_flag = 0
		update_flag = 0
		flag = 0
		try:
			for key in info.keys():
				name,code,gov_dept = info[key][0],info[key][1],info[key][2]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(name))
				id = m.hexdigest()
				count = cursor.execute(select_string, (id, gs_basic_id))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(branch_string, (gs_basic_id, id, code, name, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception,e:
			print e
			flag = 100000006
		finally:
			if flag < 100000001:
				flag = insert_flag
			return flag,insert_flag, update_flag
		
		
		
				
			
			
object = Branch()
object.name(url)

	