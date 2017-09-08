#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_share_history.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取投资历史信息

from lxml import etree
import requests
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_czlsxx_wap.dhtml?reg_bus_ent_id=26B8239E652E4DA1AD3FFADE573DC6E8&clear=true&fqr='
class Share_History:
	def name(self,url):
		result = requests.get(url,headers=config.headers_detail)
		status_code = result.status_code
		if status_code ==200:
			content = result.content
			# print content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class='viewBox']//dl")[0]
			datalsit = deal_html_code.remove_space(etree.tostring(dl)).split('<br/>')
			datalsit.remove(datalsit[-1])
			print len(datalsit)
			datalsit = list(set(datalsit))
			print len(datalsit)

object = Share_History()
object.name(url)