#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Lmm
# @Date  : 2017-08-26
# @Desc  : 用于专利搜索的一些常用配置，数据库等

#验证码识别环境配置Start-----------------------------------------------------------------------
#windows 环境验证码训练集路径设置
tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
#linux 环境验证码训练集路径设置
#tessdata_dir_config = '--tessdata-dir "/usr/share/tesseract-ocr/tessdata/"'

#验证码识别环境配置End-------------------------------------------------------------------------

#数据库配置Start-----------------------------------------------------------------------------
HOST, USER, PASSWD, DB, PORT = '127.0.0.1', 'root', '123456', 'test', 3306
#数据库配置End-------------------------------------------------------------------------------

#网页链接Start--------------------------------------------------------------------------------
firsturl = 'http://www.pss-system.gov.cn/sipopublicsearch/portal/uiIndex.shtml'
searchurl = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/executeSmartSearch1207-executeSmartSearch.shtml'
search_text = 'searchCondition.searchExp=%s&search_scope=&searchCondition.dbId=VDB&resultPagination.limit=12&searchCondition.searchType=Sino_foreign&wee.bizlog.modulelevel=0200101'
#详情链接
viewurl = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/viewAbstractInfo-viewAbstractInfo.shtml'
#法律状态链接
lawurl = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/ui_searchLawState-showPage.shtml'
#摘要图片链接
imgurl= 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/retrieveUrls.shtml'
#网页链接End----------------------------------------------------------------------------------

#网页登录的用户名和密码Start------------------------------------------------------------------
username = "79data"
password = "mm481002"
#网页登录的用户名和密码End--------------------------------------------------------------------


#搜索页面的请求头信息仿照Start----------------------------------------------------------------
header = {
"Host": "www.pss-system.gov.cn",
"Connection": "keep-alive",
"Content-Length": "180",
"Pragma": "no-cache",
"Cache-Control": "no-cache",
"Accept": "*/*",
"Origin": "http://www.pss-system.gov.cn",
"X-Requested-With": "XMLHttpRequest",
#"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.8",
}
#搜索页面的请求头信息仿照End------------------------------------------------------------------

#常用的User-Agent Start-----------------------------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36 OPR/37.0.2178.32",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.9.2.1000 Chrome/39.0.2146.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.277.400 QQBrowser/9.4.7658.400",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 UBrowser/5.6.12150.8 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.154 Safari/537.36 LBBROWSER ",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36 TheWorld 7"
]

#长用的User-Agent End-------------------------------------------------------------------------