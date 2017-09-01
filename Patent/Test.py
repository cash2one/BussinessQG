#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Test.py.py
# @Author: Lmm
# @Date  : 2017-08-28
# @Desc  :用于模拟登录
import pytesseract
from lxml import etree
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import  BeautifulSoup
import requests
import urllib

#用于保持会话
session = requests.session()
#windows 环境训练集路径设置
tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
url = 'http://www.pss-system.gov.cn/sipopublicsearch/portal/uiIndex.shtml'

# driver = webdriver.PhantomJS()
driver = webdriver.Chrome()
result = driver.get(url)
data = driver.get_cookies()
print data
print len(data)
# for i,single in enumerate(data):
#     print single
_gscbrs_761734625 = data[0]["value"]
_gscs_761734625 = data[1]["value"]
_gscu_761734625 = data[2]["value"]
JSESSIONID = data[3]["value"]
WEE_SID = data[5]["value"]

print _gscbrs_761734625,_gscs_761734625,_gscu_761734625,JSESSIONID,WEE_SID
# cookies = {
# "WEE_SID"	:str(WEE_SID),
# "IS_LOGIN"	:"flase",
# "_gscu_761734625":	str(_gscu_761734625),
# "avoid_declare"	:"declare_pass",
# "_gscs_761734625":	str(_gscs_761734625),
# "JSESSIONID"	:str(JSESSIONID),
# "_gscbrs_761734625"	:str(_gscbrs_761734625)
# }
codeurl = driver.find_element_by_xpath("//*[@id= 'codePic']").get_attribute("src")
print codeurl
for cookie in data:
    session.cookies.set(cookie['name'],cookie['value'])
result = session.get(codeurl)
print requests.utils.dict_from_cookiejar(result.cookies)
with open('./Image/code.jpg',"wb") as f:
    f.write(result.content)
result = Image.open("./Image/code.jpg")

code = pytesseract.image_to_string(result,config=tessdata_dir_config)
print code
username = u"79data"
password = u"mm481002"
elem = driver.find_element_by_xpath("//*[@id='j_username']")
elem.send_keys(username)
elem = driver.find_element_by_xpath("//*[@id= 'j_password_show']")
elem.send_keys(password)
elem = driver.find_element_by_xpath("//*[@id= 'j_validation_code']")
elem.send_keys(code)
elem = driver.find_element_by_class_name("btn")
elem.send_keys(Keys.ENTER)
cookies = driver.get_cookies()
print cookies
string = u"物理"
elem = driver.find_element_by_xpath("//*[@id= 'quickInput']")


elem.send_keys(string)
elem = driver.find_element_by_xpath("//*[@id= 'quickSearch']")
elem.send_keys(Keys.ENTER)
# print driver.page_source
# driver.quit()


# url = 'http://www.pss-system.gov.cn/sipopublicsearch/portal/app/home/declare.jsp'
# result = requests.get(url,headers = headers)
# cookies = result.cookies
#
# cookies = requests.utils.dict_from_cookiejar(cookies)
# print cookies
# url = 'http://www.pss-system.gov.cn/sipopublicsearch/'
# result = requests.get(url,cookies = cookies)
# print result.cookies
# cookies = requests.utils.dict_from_cookiejar(cookies)
# print cookies
# result = BeautifulSoup(result.content,"lxml")
# codePic = result.find("img",{"id":"codePic"})["src"]
# #
# codeurl = "http://www.pss-system.gov.cn"+codePic
# # print codeurl
# result = requests.get(codeurl)
# cookies = requests.utils.dict_from_cookiejar(result.cookies)
# print cookies
# j_loginsuccess_url = ''
# result = requests.get(codeurl)
# with open('./Image/code.jpg',"wb") as f:
#     f.write(result.content)
# result = Image.open("./Image/code.jpg")
# #
# code = pytesseract.image_to_string(result,config=tessdata_dir_config)
# print code
# print codeurl
# post_string = {
#     "j_loginsuccess_url":"",
#    "j_validation_code":	code,
#   "j_username":	"NzlkYXRh",
#    "j_password":"bW00ODEwMDI="
#
# }
#
# loginurl = 'http://www.pss-system.gov.cn:80/sipopublicsearch/wee/platform/wee_security_check'
# s = session.post(loginurl,post_string,cookies = cookies)
# print s
# cookies = s.cookies
# cookies = requests.utils.dict_from_cookiejar(cookies)
# print cookies
# header = {
# "Host": "www.pss-system.gov.cn",
# "Connection": "keep-alive",
# "Content-Length": "180",
# "Pragma": "no-cache",
# "Cache-Control": "no-cache",
# "Accept": "*/*",
# "Origin": "http://www.pss-system.gov.cn",
# "X-Requested-With": "XMLHttpRequest",
# "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
# "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
# "Accept-Encoding": "gzip, deflate",
# "Accept-Language": "zh-CN,zh;q=0.8",
# }
#
# cookies = {
# "WEE_SID"	:"aDcYZl1uYaRd1puVTr4jJa7LddcUoSoy_Y5lT0k3G4-_lR2-8W0M!-1564981156!879531882!1503647915374",
# "IS_LOGIN"	:"true",
# "_gscu_761734625":	"03615151zbuxwk15",
# "avoid_declare"	:"declare_pass",
# "_gscs_761734625":	"03647950qvujfx56|pv:4",
# "JSESSIONID"	:"aDcYZl1uYaRd1puVTr4jJa7LddcUoSoy_Y5lT0k3G4-_lR2-8W0M!-1564981156!879531882",
# "_gscbrs_761734625"	:"1"
# }
#
# url = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/executeSmartSearch1207-executeSmartSearch.shtml'
# search_text = 'searchCondition.searchExp=%E7%89%A9%E7%90%86&search_scope=&searchCondition.dbId=VDB&resultPagination.limit=12&searchCondition.searchType=Sino_foreign&wee.bizlog.modulelevel=0200101'
# result = session.post(url,search_text,headers = header,cookies = cookies)
# print result.content

# url = "http://www.pss-system.gov.cn/sipopublicsearch/portal/uilogin-forwardLogin.shtml"
# result = requests.get(url)
# url = "http://www.pss-system.gov.cn/sipopublicsearch/portal/uilogin-loginSuccess.shtml?params=991CFE73D4DF553253D44E119219BF31366856FF4B15222669397E093A956A2C&j_loginsuccess_url="
# result = BeautifulSoup(result.content,"lxml")
# codePic = result.find("img",{"id":"codePic"})["src"]
# url = "http://www.pss-system.gov.cn:80/sipopublicsearch/wee/platform/wee_security_check"
# codeurl = "http://www.pss-system.gov.cn"+codePic
#
# result = requests.get(codeurl)
# with open('./Image/code.jpg',"wb") as f:
#     f.write(result.content)
# result = Image.open("./Image/code.jpg")
# print result
# code = pytesseract.image_to_string(result,config=tessdata_dir_config)
# print code
# post_string = {
#     "j_loginsuccess_url":"",
#    "j_validation_code":	str(code),
#   "j_username":	"79data",
#    "j_password":"mm481002"
#
# }
# user_name = "79data"
#
# header = {
# "Host": "www.pss-system.gov.cn",
# "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
# "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
# "Accept-Encoding": "gzip, deflate",
# "Content-Type": "application/x-www-form-urlencoded",
# "Content-Length": "88",
# "Referer": "http://www.pss-system.gov.cn/sipopublicsearch/portal/uiIndex.shtml",
# #Cookie: WEE_SID=zron1Fx3cbvvSGfkwVoYhBPh14AOBS1sJmdqltBvAiePsyn1pgxX!-1520733268!2083373865!1503906782327; IS_LOGIN=false; JSESSIONID=zron1Fx3cbvvSGfkwVoYhBPh14AOBS1sJmdqltBvAiePsyn1pgxX!-1520733268!2083373865; _gscu_761734625=03907023fkqtt424; _gscs_761734625=03907023wosqsc24|pv:2; _gscbrs_761734625=1; avoid_declare=declare_pass
# "Connection": "keep-alive",
# "Upgrade-Insecure-Requests": "1"
# }
# loginurl = 'http://www.pss-system.gov.cn:80/sipopublicsearch/wee/platform/wee_security_check'
# s = session.post(loginurl,post_string,headers = header,cookies = cookies)
# # print s.cookies
# cookies = requests.utils.dict_from_cookiejar(s.cookies)
# print cookies
# # url = "http://www.pss-system.gov.cn/sipopublicsearch/portal/uilogin-loginSuccess.shtml?params=991CFE73D4DF553253D44E119219BF31366856FF4B15222669397E093A956A2C&j_loginsuccess_url="
# # result = requests.get(url)
# # print result.cookies
# # cookies = requests.utils.dict_from_cookiejar(s.cookies)
# # print cookies
# cookies = {
# "WEE_SID"	:str(WEE_SID),
# "IS_LOGIN"	:"true",
# "_gscu_761734625":	str(_gscu_761734625),
# "avoid_declare"	:"declare_pass",
# "_gscs_761734625":	str(_gscs_761734625),
# "JSESSIONID"	:str(JSESSIONID),
# "_gscbrs_761734625"	:str(_gscbrs_761734625)
# }
#
# header = {
# "Host": "www.pss-system.gov.cn",
# "Connection": "keep-alive",
# "Content-Length": "180",
# "Pragma": "no-cache",
# "Cache-Control": "no-cache",
# "Accept": "*/*",
# "Origin": "http://www.pss-system.gov.cn",
# "X-Requested-With": "XMLHttpRequest",
# "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
# "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
# "Accept-Encoding": "gzip, deflate",
# "Accept-Language": "zh-CN,zh;q=0.8",
# }
# print cookies
# url = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/executeSmartSearch1207-executeSmartSearch.shtml'
# search_text = 'searchCondition.searchExp=%E7%89%A9%E7%90%86&search_scope=&searchCondition.dbId=VDB&resultPagination.limit=12&searchCondition.searchType=Sino_foreign&wee.bizlog.modulelevel=0200101'
# result = session.post(url,search_text,headers = header,cookies = cookies)
# print result.content
#
