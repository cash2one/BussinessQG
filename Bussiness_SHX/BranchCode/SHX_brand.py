#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_brand.py
# @Author: Lmm
# @Date  : 2017-10-19 10:38
# @Desc  : 用于获取页面中的商标信息
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode import deal_html_code
from lxml import etree
import urllib
import logging
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


url = 'http://sn.gsxt.gov.cn/ztxy.do?method=showAllSbxx&maent.entname={0}&pageNum={1}&random=1508825497952'
detail_url = 'http://sn.gsxt.gov.cn/ztxy.do?method=sbxxDetail&reg_num={0}&picname={1}&random=1508827638934'
host = 'http://sn.gsxt.gov.cn/'
brand_string = 'insert into ia_brand(gs_basic_id,ia_zch, ia_flh, ia_zcgg,ia_servicelist, ia_zyqqx, ia_zcdate,img_url,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_brand = 'select ia_brand_id from ia_brand where ia_zch = "%s"'
update_brand = 'update ia_brand set ia_brand_id = %s,gs_basic_id = %s,ia_flh = %s, ia_zcgg = %s ,ia_servicelist = %s, ia_zyqqx = %s,ia_zcdate = %s,img_url =%s,updated = %s where ia_brand_id = %s'

class Brand:
	def __init__(self,url,name,detail_url):
		self._url = url
		self._name = name.decode('utf-8').encode("gb2312")
		self._detail_url = detail_url
	#用于获得商标信息
	def get_info(self):
		info = {}
		name = urllib.quote(self._name)
		url = self._url.format(name, 1)
		result, status_code = Send_Request().send_requests(url, config.headers)
		if status_code == 200:
			start = 0
			data = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
			self.deal_single_page(info,data,start)
			totalpage = data.xpath("//input[@id = 'totalPage_sbxx']/@value")[0]
			for i in xrange(2, int(totalpage)+1):
				start = (i-1)*6 #定义开始位置
				url = self._url.format(name, i)
				result, start_code = Send_Request().send_requests(url,config.headers)
				data = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
				self.deal_single_page(info, data, start)
	#用于处理一页的商标信息
	def deal_single_page(self,info,data,start):
		sbxx_detail = data.xpath("//li[@name = 'sbxx']//a/@onclick")
		#enumerate(sbxx_date,start),start 代表的是i 的开始位置，enumerate详细用法找百度
		#是因为商标信息是需要进行翻页,保存信息的做法是用字典的（key,value）键值对,编号作为键值（key）,对应每条信息(value)
		#一是方便查找,二是便于存储,根据键值的唯一性,每一条信息都要有一个唯一的键值
		#如果页面中没有序号，就需要自己自定义每条信息的序号,页面中有序号的可以用页面中的序号作为键值,没有则可以采用这种做法
		for i,value in enumerate(sbxx_detail, start):
			tuple = deal_html_code.match_key_content(str(value))
			reg_num = tuple[0]
			picname = tuple[1]
			detail = self._detail_url.format(reg_num, picname)
			temp = self.get_single_info(detail)
			temp["ia_img"] = host+picname
			info[i] = temp
			
	#获取单条商标的详情信息
	def get_single_info(self,detail_url):
		dict = {
			u"注册号": "ia_zch",
			u"公告日期": "ia_zcdate",
			u"类别": "ia_flh",
			u"公告期号": "ia_zcgg",
			u"起止日期": "ia_zyqqx",
			u'服务项目': "ia_servicelist"
		}
		result, status_code = Send_Request().send_requests(detail_url, config.headers)
		temp = {}
		if status_code == 200:
			data = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
			
			for key, value in dict.iteritems():
				temp[value] = deal_html_code.get_match_info(key, data)
		else:
			temp["ia_zch"] = ''
			temp["ia_zcdate"] = ''
			temp["ia_flh"] = ''
			temp["ia_zcgg"] = ''
			temp["ia_zyqqx"] = ''
			temp["ia_servicelist"] = ''
		return temp
	#用于将数据更新到数据库中
	def update_to_db(self,info,gs_basic_id):
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(info)
		try:
			
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key, value in info.iteritems():
				ia_zch, ia_flh, ia_zcgg = value["ia_zch"], info["ia_flh"], value["ia_zcgg"]
				ia_servicelist, ia_zyqqx, ia_zcdate = info["ia_servicelist"], info["ia_zyqqx"], info["ia_zcdate"]
				ia_img_url = info["ia_img"]
	
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
												 ia_zcdate, ia_img_url, updated_time, gs_brand_id))
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


name ='西安银行股份有限公司'
object = Brand(url,name)
object.get_info()

			
		
		
	
	
	# def update_to_db(self,info,gs_basic_id):