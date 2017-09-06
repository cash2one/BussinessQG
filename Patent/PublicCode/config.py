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
searchurl = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/showSearchResult-startWa.shtml'

#详情链接
viewurl = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/viewAbstractInfo-viewAbstractInfo.shtml'
#法律状态链接
lawurl = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/ui_searchLawState-showPage.shtml'
#摘要图片链接
imgurl= 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/retrieveUrls.shtml'
sameurl = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/showCognationInfo-showCognationList.shtml'
searchparams = "resultPagination.limit=12&resultPagination.sumLimit=10&resultPagination.start=%s&resultPagination.totalCount=&searchCondition.searchType=Sino_foreign&search_scope= AND ((DOC_TYPE=((@@@@I@@@@))) OR (DOC_TYPE=((@@@@U@@@@))) OR (DOC_TYPE=((@@@@D@@@@)))) AND ((CC=(@@@@HK@@@@)) OR (CC=(@@@@MO@@@@)) OR (CC=(@@@@TW@@@@)) OR (CC=(@@@@CN@@@@)))&searchCondition.dbId=&searchCondition.searchExp=%s&wee.bizlog.modulelevel=0200101&searchCondition.executableSearchExp=VDB:((TBI='%s' AND (DOC_TYPE='I' OR DOC_TYPE='U' OR DOC_TYPE='D') AND (CC='HK' OR CC='MO' OR CC='TW' OR CC='CN')))&searchCondition.literatureSF=复合文本=(%s) AND ((DOC_TYPE=(('I'))) OR (DOC_TYPE=(('U'))) OR (DOC_TYPE=(('D')))) AND ((CC=('HK')) OR (CC=('MO')) OR (CC=('TW')) OR (CC=('CN')))&searchCondition.strategy=&searchCondition.searchKeywords=&searchCondition.searchKeywords=%s&searchCondition.searchKeywords=[ ]{0,}[T][ ]{0,}[W][ ]{0,}[ ]{0,}&searchCondition.searchKeywords=[ ]{0,}[M][ ]{0,}[O][ ]{0,}[ ]{0,}&searchCondition.searchKeywords=[ ]{0,}[H][ ]{0,}[K][ ]{0,}[ ]{0,}&searchCondition.searchKeywords=[ ]{0,}[C][ ]{0,}[N][ ]{0,}[ ]{0,}"
#网页链接End----------------------------------------------------------------------------------

#网页登录的用户名和密码Start------------------------------------------------------------------
username = "79data"
password = "mm481002"
#网页登录的用户名和密码End--------------------------------------------------------------------


#搜索页面的请求头信息仿照Start----------------------------------------------------------------

header = {
"Host": "www.pss-system.gov.cn",
"Connection": "keep-alive",
"Content-Length": "1670",
"Accept": "text/html, */*; q=0.01",
"Origin": "http://www.pss-system.gov.cn",
"X-Requested-With": "XMLHttpRequest",
#User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36
"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
#Referer: http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/portal2HomeSearch-portalSearch.shtml?params=4C3F74C3281B65A97F2870FF32DEFA099C9A47BCE9F85DF3E7ABCC2069DA0B2891DAF6838DC9DE171DB66CA6F4F1049B64541E872BD0A61D34BA0F57977987786AF1C8BB8883CBE5CC4EA7180E2F44E1F7B8DFF8A99CAA5C022B2A6D205E4A18B690CAF964F59C6C437E41C7A1D6C3D934BA0F5797798778EBE9A26F910E388ABD71E45E7563F132CBF45670C95C94A78878779A38710B2E374F874806C720A62FDD908C867FF5E23D3E7B1524A77A487381605684C845807D3050CA3CD1EF0A703FCD3A8A4E9EA4B93519873E977E22337F1D136FCD1AE2B30AE55F05D1AE85A82FA94C4763A52F193D5708C9A494B19A7471FA7721AF4F
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.8"
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

#常用的User-Agent End-------------------------------------------------------------------------