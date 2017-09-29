#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Test3.py.py
# @Author: Lmm
# @Date  : 2017-09-04
# @Desc  :
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
from PublicCode import  config
import random
import requests
import urllib
headers = config.header
string = '气垫车'
cookies = {u'_gscbrs_761734625': '1', u'_gscs_761734625': '04507687ph9wit13|pv:1', u'WEE_SID': 'Z8tLoiljDx1kVabTNLtK8JrrWUujbjvzgWfYIlrwUc_bKNunoXUI!446741660!421874926!1504507472227', u'_gscu_761734625': '04507687yhtmjd13', u'JSESSIONID': 'Z8tLoiljDx1kVabTNLtK8JrrWUujbjvzgWfYIlrwUc_bKNunoXUI!446741660!421874926', u'IS_LOGIN': 'true'}


def get_keywords(key):
    string = unicode(key)
    
    key = ''
    for i, single in enumerate(string):
        temp = '[%s][ ]{0,}' % single
        key = key + temp
    return key
keywords = get_keywords(string)
print str(keywords)
rspage = 2
totpage = 0
user_agent = random.choice(config.USER_AGENTS)
headers["User-Agent"] = user_agent
url = config.searchurl
start = (int(rspage) - 1) * 12
# string = urllib.quote(string)
# keywords = urllib.quote(str(keywords))
#search_text = 'resultPagination.limit=12&resultPagination.sumLimit=10&resultPagination.start=12&resultPagination.totalCount=56140&searchCondition.searchType=Sino_foreign&search_scope= AND ((DOC_TYPE=((@@@@I@@@@))) OR (DOC_TYPE=((@@@@U@@@@))) OR (DOC_TYPE=((@@@@D@@@@)))) AND ((CC=(@@@@HK@@@@)) OR (CC=(@@@@MO@@@@)) OR (CC=(@@@@TW@@@@)) OR (CC=(@@@@CN@@@@)))&searchCondition.dbId=&searchCondition.searchExp=离心机&wee.bizlog.modulelevel=0200101&searchCondition.executableSearchExp=VDB:((TBI="建筑物" AND (DOC_TYPE="I" OR DOC_TYPE="U" OR DOC_TYPE="D") AND (CC="HK" OR CC="MO" OR CC="TW" OR CC="CN")))&searchCondition.literatureSF=复合文本=(离心机) AND ((DOC_TYPE=(("I"))) OR (DOC_TYPE=(("U"))) OR (DOC_TYPE=(("D")))) AND ((CC=("HK")) OR (CC=("MO")) OR (CC=("TW")) OR (CC=("CN")))&searchCondition.strategy=&searchCondition.searchKeywords=&searchCondition.searchKeywords=[离][ ]{0,}[心][ ]{0,}[机][ ]{0,}&searchCondition.searchKeywords=[ ]{0,}[T][ ]{0,}[W][ ]{0,}[ ]{0,}&searchCondition.searchKeywords=[ ]{0,}[M][ ]{0,}[O][ ]{0,}[ ]{0,}&searchCondition.searchKeywords=[ ]{0,}[H][ ]{0,}[K][ ]{0,}[ ]{0,}&searchCondition.searchKeywords=[ ]{0,}[C][ ]{0,}[N][ ]{0,}[ ]{0,}'
search_text = config.searchparams % (start, string, string, string, keywords)
# print search_text
# print search_text
result = requests.post(url, search_text, headers=headers, cookies=cookies)
print result.content