#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PublicCode import config
import logging

import sys
import time
import requests
from PublicCode import deal_html_code
import json
from BranchCode import App_basic
from BranchCode import App_black
from BranchCode import App_branch
from BranchCode import App_brand
from BranchCode import App_change
from BranchCode import App_check
from BranchCode import App_clear
from BranchCode import App_except
from BranchCode import App_freeze
from BranchCode import App_mort
from BranchCode import App_permit
from BranchCode import App_permit2
from BranchCode import App_person
from BranchCode import App_punish
from BranchCode import App_punish2
from BranchCode import App_shareholder
from BranchCode import App_stock



# url = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_py_id = sys.argv[3]
# province = sys.argv[4]

url = 'http://sh.gsxt.gov.cn/notice/ws/data/ent_info/260000032013041100180'
gs_basic_id = '229417621'
gs_py_id = '1501'
province = 'SHH'

s = requests.session()
s.keep_alive = False


def get_info_list(url):
    result = requests.get(url)
    status_code = result.status_code
    # result = result.content
    # print result
    info = {}
    if status_code == 200:
        data = json.loads(result)
        info["basic"] = data
        province = config.province[data["regOrgan"][0:2]]
        info["black"] = data["entBlackSet"]
        info["branch"] = data["entBranchSet"]
        info["brand"] = data["entTmSet"]
        info["change"] = data["entChangeSet"]
        info["check"] = data["entSpotCheckSet"]
        info["clear"] = data["entClearSet"]
        info["except"] = data["entExceptListedSet"]
        info["freeze"] = data["entStockFreezeViSet"]
        info["mort"] = data["entMortgageSet"]
        info["permit"] = data["entShrPermitSet"]
        info["permit2"] = data["entOthPermitSet"]
        info["person"] = data["entMemberSet"]
        info["punish"] = data ["entPunishSet"]
        info["punish2"] = data["entOthPunishSet"]
        info["shareholder"] = data["entInvestorSet"]
        info["stock"] = data["entPledgeSet"]
        info["report"] = data["entAnnlBasicSet"]
        info["province"] = province
    return info
def get_year_list(data,province):
    info = {}
    for i,singledata in enumerate(data):
        anCheYear = singledata["anCheYear"]
        annlId = singledata["annlId"]
        url = config.report_list[province].format(annlId)
        info[str(anCheYear)] = url
    return info
def update_all_info(gs_py_id,gs_basic_id,url):
    data_list = get_info_list(url)
    province = data_list["province"]
    basicinfo = data_list["basic"]
    # blackinfo = data_list["black"]
    branchinfo = data_list["branch"]
    # brandinfo = data_list["brand"]
    # changeinfo = data_list["change"]
    # checkinfo = data_list["check"]
    # clearinfo = data_list["clear"]
    # exceptinfo = data_list["except"]
    # freezeinfo = data_list["freeze"]
    # mortinfo = data_list["mort"]
    # permitinfo = data_list["permit"]
    # permitinfo2 = data_list["permit2"]
    personinfo = data_list["person"]
    # punishinfo = data_list["punish"]
    # punishinfo2 = data_list["punish2"]
    # reportinfo = data_list["report"]
    sharehinfo = data_list["shareholder"]
    # stockinfo = data_list["stock"]
    # App_basic.main(gs_py_id,gs_basic_id,basicinfo)
    App_branch.main(gs_py_id,gs_basic_id,branchinfo)
    # App_black.main(gs_py_id,gs_basic_id,blackinfo)
    # App_brand.main(gs_py_id,gs_basic_id,brandinfo)
    # App_change.main(gs_py_id,gs_basic_id,changeinfo)
    # App_check.main(gs_py_id,gs_basic_id,checkinfo)
    # App_clear.main(gs_py_id,gs_basic_id,clearinfo)
    # App_except.main(gs_py_id, gs_basic_id, exceptinfo)
    # App_freeze.main(gs_py_id,gs_basic_id,freezeinfo,province)
    # App_mort.main(gs_py_id,gs_basic_id,mortinfo,province)
    
    # App_permit.main(gs_py_id,gs_basic_id,permitinfo)
    # App_permit2.main(gs_py_id,gs_basic_id,permitinfo2)
    App_person.main(gs_py_id,gs_basic_id,personinfo)
    # App_punish.main(gs_py_id,gs_basic_id,punishinfo)
    # App_punish2.main(gs_py_id,gs_basic_id,punishinfo2)
    App_shareholder.main(gs_py_id,gs_basic_id,sharehinfo)
    # App_stock.main(gs_py_id,gs_basic_id,stockinfo)
    # print 'report: %s '%len(reportinfo)
    # if len(reportinfo) >0:
    #     info = get_year_list(reportinfo,province)
    #     print info

    # App_report.main(gs_py_id,gs_basic_id,reportinfo,province)

if __name__ == "__main__":
    # print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # start = time.time()
    update_all_info(gs_py_id,gs_basic_id,url)
    # print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)





