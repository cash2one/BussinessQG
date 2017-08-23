#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import sys

from BranchCode import App_punish
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request

# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)

code = sys.argv[1]
province = sys.argv[2]
gs_basic_id = sys.argv[3]
gs_py_id = sys.argv[4]



code = '9131000013221158XC'
# province = ''
gs_basic_id = 229418511
gs_py_id = 1


def get_index(code):
    province = deal_html_code.judge_province(code)
    first_url = config.url_list[province].format(code)
    result,status_code = Send_Request().send_requests(first_url)
    data = None
    if status_code ==200:
        info = json.loads(result)["info"][0]
        uuid = info["uuid"]
        second_url = config.detail_list[province].format(uuid)
        data = Send_Request().send_requests(second_url)[0]
    return data
def get_info_list(data):
    info = {}
    if data!= None:
        data = json.loads(data)
        info["basic"] = data
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
        info["punish"] = data["entShrPunishSet"]
        info ["punish2"] = data[""]
        info["share"] = data["entInvestorSet"]
        info["stock"] = data["entPledgeSet"]
    return info
def get_all_info(cursor,connect,gs_basic_id):
    province = deal_html_code.judge_province(code)
    data = get_index(code)
    data_list = get_info_list(data)
    # basicinfo = App_basic.name(data)
    # App_basic.update_to_db(cursor, connect, gs_basic_id, basicinfo)
    # branchinfo = data_list["branch"]
    # branchinfo = App_branch.name(branchinfo)
    # App_branch.update_to_db(cursor,connect,gs_basic_id,branchinfo)
    # brandinfo = data_list["brand"]
    # brandinfo = App_brand.name(brandinfo)
    # App_brand.update_to_db(cursor,connect,gs_basic_id,brandinfo)
    # changeinfo = data_list["change"]
    # changeinfo = App_change.name(changeinfo)
    # App_change.update_to_db(cursor,connect,gs_basic_id,changeinfo)
    # clearinfo = data_list["clear"]
    # clearinfo = App_clear.name(clearinfo)
    # App_clear.update_to_db(cursor,connect,gs_basic_id,clearinfo)
    # exceptinfo = data_list["except"]
    # exceptinfo = App_except.name(exceptinfo)
    # App_except.update_to_db(cursor,connect,gs_basic_id,exceptinfo)
    # freezeinfo = data_list["freeze"]
    # freezeinfo = App_freeze.name(freezeinfo,province)
    # App_freeze.update_to_db(cursor,connect,gs_basic_id,freezeinfo)
    # mortinfo = data_list["mort"]
    # mortinfo = App_mort.name(mortinfo,province)
    # App_mort.update_to_db(gs_py_id,cursor,connect,gs_basic_id,mortinfo)
    # permitinfo = data_list["permit"]
    # permitinfo = App_permit.name(permitinfo)
    # App_permit.update_to_db(cursor,connect,gs_basic_id,permitinfo)
    # personinfo = data_list["person"]
    # personinfo = App_person.name(personinfo)
    # App_person.update_to_db(cursor,connect,gs_basic_id,personinfo)
    punishinfo = data_list["punish"]

    punishinfo = App_punish.name(punishinfo)
    App_punish.update_to_db(cursor, connect, gs_basic_id, punishinfo)
    # shareinfo = data_list["share"]
    # shareinfo = App_shareholder.name(shareinfo)
    # App_shareholder.update_to_db(cursor,connect,gs_basic_id,shareinfo)
    # stockinfo = data_list["stock"]
    # stockinfo = App_stock.name(stockinfo)
    # App_stock.update_to_db(cursor,connect,gs_basic_id,stockinfo)


get_all_info(cursor,connect,gs_basic_id)















