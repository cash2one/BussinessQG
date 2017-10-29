#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json

import requests

from PublicCode import config
from PublicCode.Public_code import Log
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
from BranchCode import App_report
import logging



#用于获得信息并将信息进行解析，解析为方便理解的方式
def get_info_list(url):
    result = requests.get(url)
    status_code = result.status_code
    info = {}
    if status_code == 200:
        data = json.loads(result.content)
        info["basic"] = data
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
        info["punish"] = data["entPunishSet"]
        info["punish2"] = data["entOthPunishSet"]
        info["shareholder"] = data["entInvestorSet"]
        info["stock"] = data["entPledgeSet"]
        info["report"] = data["entAnnlBasicSet"]
    return info
#用于获得年报中各个年份的链接
def get_year_list(data,province):
    info = {}
    for i,singledata in enumerate(data):
        anCheYear = singledata["anCheYear"]
        annlId = singledata["annlId"]
        url = config.report_list[province].format(annlId)
        info[str(anCheYear)] = url
    return info
#用于更新所有的信息
def update_all_info(gs_basic_id,url,province):
   
    data_list = get_info_list(url)
    basicinfo = data_list["basic"]
    blackinfo = data_list["black"]
    branchinfo = data_list["branch"]
    brandinfo = data_list["brand"]
    changeinfo = data_list["change"]
    checkinfo = data_list["check"]
    clearinfo = data_list["clear"]
    exceptinfo = data_list["except"]
    freezeinfo = data_list["freeze"]
    mortinfo = data_list["mort"]
    permitinfo = data_list["permit"]
    permitinfo2 = data_list["permit2"]
    personinfo = data_list["person"]
    punishinfo = data_list["punish"]
    punishinfo2 = data_list["punish2"]
    reportinfo = data_list["report"]
    sharehinfo = data_list["shareholder"]
    stockinfo = data_list["stock"]
    App_basic.main(gs_basic_id,basicinfo)
    App_branch.main(gs_basic_id, branchinfo)
    App_black.main(gs_basic_id,blackinfo)
    App_brand.main(gs_basic_id,brandinfo)
    App_change.main(gs_basic_id,changeinfo)
    App_check.main(gs_basic_id,checkinfo)
    App_clear.main(gs_basic_id,clearinfo)
    App_except.main(gs_basic_id, exceptinfo)
    App_freeze.main(gs_basic_id,freezeinfo,province)
    App_mort.main(gs_basic_id,mortinfo,province)
    App_permit.main(gs_basic_id,permitinfo)
    App_permit2.main(gs_basic_id,permitinfo2)
    App_person.main(gs_basic_id,personinfo)
    App_punish.main(gs_basic_id,punishinfo)
    App_punish2.main(gs_basic_id,punishinfo2)
    App_shareholder.main(gs_basic_id,sharehinfo)
    App_stock.main(gs_basic_id,stockinfo)
    print 'report: %s '%len(reportinfo)
    logging.info('the total report is : %s '%len(reportinfo))
    if len(reportinfo) >0:
        info = get_year_list(reportinfo,province)
        for key in info.keys():
            App_report.main(url,key,gs_basic_id,province)
        print info





