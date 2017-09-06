#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  : 用于获取app接口年报中的数据
import hashlib
import json
import logging
import sys
import time
import requests
from PublicCode import config
from PublicCode import deal_html_code

import App_report_assure
import App_report_invest
import App_report_party
import App_report_permit
import App_report_schange
import App_report_share
import App_report_web
import App_report_lab
from PublicCode.Public_code import Log
from PublicCode.Public_code import Connect_to_DB

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# url = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_py_id =  sys.argv[3]
# year = sys.argv[4]
# province = sys.addr[5]
basic_string = 'insert into gs_report(gs_basic_id,year,province,name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, \
 holding, if_holding, mainbus, code, ccode, pripid,refuuid,if_invest,if_sharetrans,if_fwarnnt,if_website,if_net,report_mode,types,runner,amount,\
 created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_address = 'update gs_basic set gs_basic_id = %s,tel = %s,address = %s,email = %s,updated = %s where gs_basic_id = %s'
run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,loan,if_loan,subsidy,if_subsidy,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_basic_year = 'select reg_date from gs_basic where gs_basic_id = %s'
select_report = 'select gs_report_id from gs_report where gs_basic_id = %s and year = %s'
update_report_py ='update gs_py set gs_py_id = %s ,report = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
update_run_py = 'update gs_py set gs_py_id = %s ,report_run = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
assure_py = 'update gs_py set gs_py_id = %s ,report_assure = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s '
invest_py = 'update gs_py set gs_py_id = %s ,report_invest = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
permit_py = 'update gs_py set gs_py_id = %s ,report_permit = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
schange_py = 'update gs_py set gs_py_id = %s ,report_schange = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
share_py = 'update gs_py set gs_py_id = %s,report_share = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
web_py = 'update gs_py set gs_py_id = %s,report_web = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
party_py = 'update gs_py set gs_py_id = %s report_party = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
class Report:
    def __init__(self,gs_py_id):
        self.gs_py_id = gs_py_id

    def judge_status(self, update_sql, records, total,gs_basic_id,cursor,connect):
        if records == 0:
            flag = None
        elif records > 0 and total >= 0 and total < 100000001:
            flag = total
        elif records > 0 and total > 100000001:
            flag = 100000006
        if flag == None:
            flag = -1
        else:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_sql, (self.gs_py_id, flag, updated_time, gs_basic_id, self.gs_py_id))
            connect.commit()

    def update_all_info(self,gs_basic_id,year,url,province,cursor,connect):
        remark = 0
        try:
            information, runinfo, assureinfo, investinfo, labinfo, permitinfo, partyinfo, schangeinfo, shareinfo, webinfo = self.get_all_info(url)
            info = self.get_run_info(runinfo)
            report_id = self.update_base(gs_basic_id, information, year, cursor, connect)
            self.update_run_info(year,report_id,gs_basic_id,cursor,connect,province,info)

            assureinfo = App_report_assure.Assure().name(assureinfo)
            flag, total, insert_total, update_total = App_report_assure.Assure().update_to_db(report_id,gs_basic_id,cursor,connect,assureinfo,province)
            self.judge_status(assure_py,total,flag,gs_basic_id,cursor,connect)
            investinfo = App_report_invest.Invest().name(investinfo)
            flag, total, insert_total, update_total = App_report_invest.Invest().update_to_db(report_id, gs_basic_id,
                                                                                              cursor, connect, investinfo,
                                                                                              province)
            self.judge_status(invest_py, total, flag,gs_basic_id,cursor,connect)
            if len(labinfo) >0:
                labinfo = App_report_lab.Lab().name(labinfo)
                if len(labinfo) >0:
                    App_report_lab.Lab().update_to_db(report_id,gs_basic_id,self.gs_py_id,cursor,connect,labinfo,province)
            permitinfo = App_report_permit.Permit().name(permitinfo)
            flag, total, insert_total, update_total = App_report_permit.Permit().update_to_db(report_id, gs_basic_id,
                                                                                              cursor, connect, permitinfo,
                                                                                              province)
            self.judge_status(invest_py, total, flag,gs_basic_id,cursor,connect)

            partyinfo = App_report_party.Party().name(partyinfo)
            flag, total, insert_total, update_total = App_report_party.Party().update_to_db(report_id, gs_basic_id,
                                                                                              cursor, connect, partyinfo,
                                                                                              province)
            self.judge_status(party_py, total,flag,gs_basic_id,cursor,connect)

            schangeinfo = App_report_schange.Schange().name(schangeinfo)
            flag, total, insert_total, update_total = App_report_schange.Schange().update_to_db(report_id, gs_basic_id,
                                                                                             cursor, connect, schangeinfo,
                                                                                             province)
            self.judge_status(schange_py, total, flag,gs_basic_id,cursor,connect)
            shareinfo = App_report_share.Share().name(shareinfo)
            flag, total, insert_total, update_total = App_report_share.Share().update_to_db(report_id, gs_basic_id,
                                                                                               cursor, connect, shareinfo,
                                                                                               province)
            self.judge_status(share_py, total, flag,gs_basic_id,cursor,connect)

            webinfo = App_report_web.Web().name(webinfo)
            flag, total, insert_total, update_total = App_report_web.Web().update_to_db(report_id, gs_basic_id,
                                                                                             cursor, connect, webinfo,
                                                                                             province)
            self.judge_status(web_py, total, flag,gs_basic_id,cursor,connect)
            remark = 1
        except Exception,e:
            logging.error('update report error :%s'%e)
            remark= 100000006
        finally:
            return remark

    def get_all_info(self,url):
        print url
        information = {}
        result= requests.get(url).content
        # result,status
        data = json.loads(result)

        if "regNo" in data.keys():
            code = data["regNo"]
            province = deal_html_code.judge_province(code)
        else:
            code = ''
        if "uniScid" in data.keys():
            ccode = data["uniScid"]
            province = deal_html_code.judge_province(ccode)
        else:
            ccode = ''
        uuid = data["annlId"]
        name = data["entName"]
        if len(data["entAnnlEtpsSet"])!=0:
            entAnnlEtps = data["entAnnlEtpsSet"][0]
            tel = entAnnlEtps["tel"]
            if 'email' in entAnnlEtps.keys():
                email = entAnnlEtps["email"]
            else:
                email = ''
            if 'postalCode' in entAnnlEtps.keys():
                postcode = entAnnlEtps["postalCode"]
            else:
                postcode = ''
            if 'ifInvest' in entAnnlEtps.keys():
                if_invest = int(entAnnlEtps["ifInvest"])
            else:
                if_invest = 0
            if 'ifStocktrans' in entAnnlEtps.keys():
                if_sharetrans = int(entAnnlEtps["ifStocktrans"])
            else:
                if_sharetrans = 0
        else:
            tel = None
            email = None
            postcode = None
            if_invest = 0
            if_sharetrans = 0
        if "hasFwarnnt" in data.keys():
            if_fwarnnt = data["hasFwarnnt"]
        else:
            if_fwarnnt = 0
        address = data["addr"]
        status = data["opStateInterpreted"]
        if len(data["entAnnlEmployeeSet"])!=0:
            employees = data["entAnnlEmployeeSet"][0]
            employee = employees["empNum"]
            if_empnum = int(employees["empNumSign"])
        else:
            employee = None
            if_empnum = 0
        if "womEmpNum" in data.keys():
            womennum = data["womEmpNum"]
            if_womennum = int(data["womEmpNumSign"])
        else:
            womennum = None
            if_womennum = 0
        if "holdingsMsg" in data.keys():
            holding = data["holdingsMsg"]
            holding =config.holding[holding]
            if_holding = int(data["holdingsMsgSign"])
        else:
            holding = ''
            if_holding = 0
        if "mainBusiact" in data.keys():
            mainbus = data["mainBusiact"]
        else:
            mainbus = None
        if "priPid" in data.keys():
            pripid = data["priPid"]
        else:
            pripid = None
        refuuid = data["refUuid"]
        if_website = int(data["hasWebsite"])
        if_net = int(data["ifNet"])
        report_mode = data["reportMode"]
        report_mode = config.public_status[report_mode]
        if "reportType" in data.keys():
            types = config.company_type[data["reportType"]]
        else:
            types = None
        if len(data["entAnnlPeSet"])!=0:
            entAnnlPeSet = data["entAnnlPeSet"][0]
            runner = entAnnlPeSet["psnName"]
            amount = int(entAnnlPeSet["fundAm"])
            tel = entAnnlPeSet["tel"]
        else:
            runner = None
            amount = None
        fill_date = data["anCheDate"]
        fill_date = deal_html_code.change_chinese_date(fill_date)
        information[0] = [name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum,
                          holding, if_holding, mainbus, code, ccode, pripid,refuuid,if_invest,if_sharetrans,if_fwarnnt,if_website,if_net,report_mode,types,runner,amount,province,fill_date]
        runinfo = data["entAnnlRunSet"]
        assureinfo = data["entAnnlFwarnntSet"]
        investinfo = data["entAnnlOutinvSet"]
        labinfo = data["entAnnlSocSet"]
        permitinfo = data["entAnnlPermitSet"]
        partyinfo = data["entAnnlPartySet"]
        schangeinfo = data["entAnnlStocktransSet"]
        shareinfo = data["entAnnlInvestorSet"]
        webinfo = data["entAnnlWebsiteSet"]
        return information,runinfo,assureinfo,investinfo,labinfo,permitinfo,partyinfo,schangeinfo,shareinfo,webinfo


    def get_run_info(self,data):
        info = []
        if len(data)==0:
           pass
        else:
            data = data[0]
            if "assGro" in data.keys():
                asset = data["assGro"]
                if_asset = int(data["assGroSign"])
            else:
                asset = None
                if_asset = 0
            if "totEqu" in data.keys():
                benifit = data["totEqu"]
                if_benifit = int(data["totEquSign"])
            else:
                benifit = None
                if_benifit = 0
            if "vendInc" in data.keys():
                income = data["vendInc"]
                if_income = int(data["vendIncSign"])
            else:
                income = None
                if_income = 0
            if "proGro" in data.keys():
                profit = data["proGro"]
                if_profit =int(data["proGroSign"])
            else:
                profit = None
                if_profit = 0
            if "maiBusInc" in data.keys():
                main_income = data["maiBusInc"]
                if_main = int(data["maiBusIncSign"])
            else:
                main_income = None
                if_main = 0
            if "netInc" in data.keys():
                net_income = data["netInc"]
                if_net = int(data["netIncSign"])
            else:
                net_income = None
                if_net = 0
            if "ratGro" in data.keys():
                tax = data["ratGro"]
                if_tax = int(data["ratGroSign"])
            else:
                tax = None
                if_tax = 0
            if "liaGro" in data.keys():
                debt = data["liaGro"]
                if_debt = int(data["liaGroSign"])
            else:
                debt = None
                if_debt = 0

            if "priYeaLoan" in data.keys():
                loan = data["priYeaLoan"]
                if_loan = int(data["priYeaLoanSign"])
            else:
                loan = None
                if_loan = 0
            if "priYeaSub" in data.keys():
                subsidy = data["priYeaSub"]
                if_subsidy = int(data["priYeaSubSign"])
            else:
                subsidy = None
                if_subsidy = 0
            info = [asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,
                    tax,if_tax,debt,if_debt,loan,if_loan,subsidy,if_subsidy]
        return info

    def update_base(self, gs_basic_id, baseinfo, year, cursor, connect):
        name, uuid, tel, address = baseinfo[0][0],baseinfo[0][1],baseinfo[0][2],baseinfo[0][3]
        email, postcode, status, employee = baseinfo[0][4],baseinfo[0][5],baseinfo[0][6],baseinfo[0][7]
        if_empnum, womennum, if_womennum,holding = baseinfo[0][8],baseinfo[0][9],baseinfo[0][10],baseinfo[0][11]
        if_holding, mainbus, code, ccode = baseinfo[0][12],baseinfo[0][13],baseinfo[0][14],baseinfo[0][15]
        pripid, refuuid, if_invest, if_sharetrans = baseinfo[0][16],baseinfo[0][17],baseinfo[0][18],baseinfo[0][19]
        if_fwarnnt, if_website, if_net, report_mode = baseinfo[0][20],baseinfo[0][21],baseinfo[0][22],baseinfo[0][23]
        types, runner, amount, province = baseinfo[0][24],baseinfo[0][25],baseinfo[0][26],baseinfo[0][27]
        m = hashlib.md5()
        m.update(str(gs_basic_id) + str(year))
        uuid = m.hexdigest()
        remark = 0
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        cursor.execute(update_address, (gs_basic_id, tel, address, email, updated_time, gs_basic_id))
        connect.commit()
        # print pripid
        try:

            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            count = cursor.execute(basic_string,(gs_basic_id,year,province,name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, \
            holding, if_holding, mainbus, code, ccode, pripid,refuuid,if_invest,if_sharetrans,if_fwarnnt,if_website,if_net,report_mode,types,runner,amount,updated_time,updated_time))
            gs_report_id = connect.insert_id()
            connect.commit()
        except Exception,e:
            remark = 100000006
            logging.error('report basic error:%s'%e)
        finally:
            if remark < 100000001:
                remark = count
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_report_py, (self.gs_py_id, remark, updated_time, gs_basic_id, self.gs_py_id))
            connect.commit()
            #print 'update report basic %s'%count
            return gs_report_id
    def update_run_info(self,year,gs_report_id,gs_basic_id,cursor,connect,province,runinfo):
        asset, if_asset, benifit, if_benifit = runinfo[0],runinfo[1],runinfo[2],runinfo[3]
        income, if_income, profit, if_profit = runinfo[4],runinfo[5],runinfo[6],runinfo[7]
        main_income, if_main, net_income, if_net = runinfo[8],runinfo[9],runinfo[10],runinfo[11]
        tax, if_tax, debt, if_debt = runinfo[12],runinfo[13],runinfo[14],runinfo[15]
        loan, if_loan, subsidy, if_subsidy = runinfo[16],runinfo[17],runinfo[18],runinfo[19]
        m = hashlib.md5()
        m.update(str(gs_basic_id) + str(year))
        uuid = m.hexdigest()
        remark = 0
        try:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            count = cursor.execute(run_string,(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,loan,if_loan,subsidy,if_subsidy,uuid,updated_time,updated_time))
            connect.commit()
        except Exception,e:
            remark = 100000006
            logging.error('%s run error:%s'%(year,e))
        finally:
            if remark <100000001:
                remark = count
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_run_py, (self.gs_py_id, remark, updated_time, gs_basic_id, self.gs_py_id))
            connect.commit()
            #print 'update run :%s '%remark
            return remark
def get_year_list(data):
    info = {}
    for i,singledata in enumerate(data):
        anCheYear = singledata["anCheYear"]
        annlId = singledata["annlId"]
        info[i] = [anCheYear,annlId]
    return info

def update_report_main(gs_basic_id,gs_py_id,yeardata,cursor,connect,province):
    total, insert_total = 0, 0
    update_total =0
    reportobject = Report(gs_py_id)
    yeardata = get_year_list(yeardata)
    for key in yeardata.keys():
        year = yeardata[key][0]
        count = cursor.execute(select_report, (gs_basic_id, year))
        if int(count) >0:
            pass
        else:
            annlId = yeardata[key][1]
            print province
            url = config.report_list[province].format(annlId)
            flag = reportobject.update_all_info(gs_basic_id,year,url,province,cursor,connect)
            insert_total+= flag
    return total,insert_total,update_total



def update_report(data,cursor,connect,gs_basic_id,gs_py_id,province):
    total, insert_total = 0, 0
    update_total = 0
    try:
        total = len(data)
        now_year = time.localtime(time.time())[0]
        select_string = select_basic_year % gs_basic_id
        cursor.execute(select_string)
        sign_date = str(cursor.fetchall()[0][0])[0:4]
        if now_year == int(sign_date):
            flag = -1
        elif now_year > int(sign_date):
            if len(data) ==0:
                flag = -1
            else:
                total,insert_total,update_total = update_report_main(gs_basic_id,gs_py_id,data,cursor,connect,province)
                flag = 1
    except Exception,e:
        flag = 100000006
        logging.error('report error:%s'%e)
    finally:
        return flag,total,insert_total,update_total


def main(gs_py_id,gs_basic_id,data,province):
    Log().found_log(gs_py_id, gs_basic_id)
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        flag, total, insert_total, update_total = update_report(data, cursor, connect, gs_basic_id, gs_py_id, province)
        string = 'report:'+str(flag)+'||'+str(total) +'||'+str(insert_total)+'||'+str(update_total)
        print string
    except Exception,e:
        logging.error('report error:%s'%e)
    finally:
        cursor.close()
        connect.close()








