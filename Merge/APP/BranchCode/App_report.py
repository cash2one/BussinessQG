# !/usr/bin/env python
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
from PublicCode.Public_code import Connect_to_DB

import App_report_assure
import App_report_invest
import App_report_lab
import App_report_party
import App_report_permit
import App_report_schange
import App_report_share
import App_report_web
from PublicCode import deal_html_code

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


basic_string = 'insert into gs_report(gs_basic_id,year,province,name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, \
 holding, if_holding, mainbus, code, ccode, pripid,refuuid,if_invest,if_sharetrans,if_fwarnnt,if_website,if_net,report_mode,types,runner,amount,\
 fill_date,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_address = 'update gs_basic set gs_basic_id = %s,tel = %s,address = %s,email = %s,updated = %s where gs_basic_id = %s'
run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,loan,if_loan,subsidy,if_subsidy,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_basic_year = 'select reg_date from gs_basic where gs_basic_id = %s'
select_report = 'select gs_report_id from gs_report where gs_basic_id = %s and year = %s'


class Report:
    def update_all_info(self, gs_basic_id, year, url, cursor, connect,province):
        remark = 0
        logging.info("now the gs_basic_id is %s,the report year is %s"%(gs_basic_id,year))
        try:
            information, runinfo, assureinfo, investinfo, labinfo, permitinfo, partyinfo, schangeinfo, shareinfo, webinfo = self.get_all_info(
                url,province)
            
            info = self.get_run_info(runinfo)
            report_id = self.update_base(gs_basic_id, information, year, cursor, connect)
            self.update_run_info(year, report_id, gs_basic_id, cursor, connect, province, info)

            assureinfo = App_report_assure.Assure().name(assureinfo)
            remark, total, insert_flag, update_flag = App_report_assure.Assure().update_to_db(report_id, gs_basic_id, cursor, connect, assureinfo, province)
            string = '%s_assure:' % year + str(remark) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(update_flag)
            logging.info(string)
            investinfo = App_report_invest.Invest().name(investinfo)
            remark, total, insert_flag, update_flag = App_report_invest.Invest().update_to_db(report_id, gs_basic_id,
                                                    cursor, connect, investinfo,
                                                    province)
            string = '%s_invest:' % year + str(remark) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(
                update_flag)
            logging.info(string)
            if len(labinfo) > 0:
                labinfo = App_report_lab.Lab().name(labinfo)
                if len(labinfo) > 0:
                    App_report_lab.Lab().update_to_db(report_id, gs_basic_id, cursor, connect, labinfo,
                                                      province)
            permitinfo = App_report_permit.Permit().name(permitinfo)
            remark, total, insert_flag, update_flag = App_report_permit.Permit().update_to_db(report_id, gs_basic_id,
                                                    cursor, connect, permitinfo,
                                                    province)
            string = '%s_permit:' % year + str(remark) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(
                update_flag)
            logging.info(string)
            partyinfo = App_report_party.Party().name(partyinfo)
            remark, total, insert_flag, update_flag = App_report_party.Party().update_to_db(report_id, gs_basic_id,
                                                  cursor, connect, partyinfo,
                                                  province)
            string = '%s_party:' % year + str(remark) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(
                update_flag)
            logging.info(string)
            schangeinfo = App_report_schange.Schange().name(schangeinfo)
            remark, total, insert_flag, update_flag = App_report_schange.Schange().update_to_db(report_id, gs_basic_id,
                                                      cursor, connect, schangeinfo,
                                                      province)
            string = '%s_schange:' % year + str(remark) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(
                update_flag)
            logging.info(string)
            shareinfo = App_report_share.Share().name(shareinfo)
            remark, total, insert_flag, update_flag = App_report_share.Share().update_to_db(report_id, gs_basic_id,
                                                  cursor, connect, shareinfo,
                                                  province)
            string = '%s_share:' % year + str(remark) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(
                update_flag)
            logging.info(string)
            webinfo = App_report_web.Web().name(webinfo)
            remark, total, insert_flag, update_flag = App_report_web.Web().update_to_db(report_id, gs_basic_id,
                                              cursor, connect, webinfo,
                                              province)
            string = '%s_web:' % year + str(remark) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(
                update_flag)
            logging.info(string)

            remark = 1
        except Exception, e:
            logging.error('update report error :%s' % e)
            remark = 100000006
        finally:
            return remark

    def get_all_info(self, url,province):
        information = {}
        result = requests.get(url).content

        data = json.loads(result)

        if "regNo" in data.keys():
            code = data["regNo"]

        else:
            code = ''
        if "uniScid" in data.keys():
            ccode = data["uniScid"]

        else:
            ccode = ''
        uuid = data["annlId"]
        name = data["entName"]
        if len(data["entAnnlEtpsSet"]) != 0:
            entAnnlEtps = data["entAnnlEtpsSet"][0]
            if 'tel' in entAnnlEtps.keys():
                tel = entAnnlEtps["tel"]
            else:
                tel = ''
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
            tel = ''
            email = ''
            postcode = ''
            if_invest = 0
            if_sharetrans = 0
        if "hasFwarnnt" in data.keys():
            if_fwarnnt = data["hasFwarnnt"]
        else:
            if_fwarnnt = 0
        if "addr" in data.keys():
            address = data["addr"]
        else:
            address = ''
        status = data["opStateInterpreted"]
        if len(data["entAnnlEmployeeSet"]) != 0:
            employees = data["entAnnlEmployeeSet"][0]
            employee = employees["empNum"]
            if_empnum = int(employees["empNumSign"])
        else:
            employee = ''
            if_empnum = 0
        if "womEmpNum" in data.keys():
            womennum = data["womEmpNum"]
            if_womennum = int(data["womEmpNumSign"])
        else:
            womennum = ''
            if_womennum = 0
        if "holdingsMsg" in data.keys():
            holding = data["holdingsMsg"]
            holding = config.holding[holding]
            if_holding = int(data["holdingsMsgSign"])
        else:
            holding = ''
            if_holding = 0
        if "mainBusiact" in data.keys():
            mainbus = data["mainBusiact"]
            mainbus = deal_html_code.remove_symbol(mainbus)
        else:
            mainbus = ''
        if "priPid" in data.keys():
            pripid = data["priPid"]
        else:
            pripid = ''
        refuuid = data["refUuid"]
        if "hasWebsite" in data.keys():
            if_website = int(data["hasWebsite"])
        else:
            if_website = 0
        if "ifNet" in data.keys():
            if_net = int(data["ifNet"])
        else:
            if_net = 0
        if "reportMode" in data.keys():
            report_mode = data["reportMode"]
        else:
            report_mode = ''
        if "reportType" in data.keys():
            types = config.company_type[data["reportType"]]
        else:
            types = ''
        if len(data["entAnnlPeSet"]) != 0:
            entAnnlPeSet = data["entAnnlPeSet"][0]
            if "psnName" in entAnnlPeSet.keys():
                runner = entAnnlPeSet["psnName"]
            else:
                runner = ''
            if "fundAm" in entAnnlPeSet.keys():
                amount = entAnnlPeSet["fundAm"]
            if "tel" in entAnnlPeSet.keys():
                tel = entAnnlPeSet["tel"]
            else:
                tel = ''
        else:
            runner = ''
            amount = ''
        fill_date = data["anCheDate"]
        fill_date = deal_html_code.change_chinese_date(fill_date)
        information[0] = [name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum,
                          holding, if_holding, mainbus, code, ccode, pripid, refuuid, if_invest, if_sharetrans,
                          if_fwarnnt, if_website, if_net, report_mode, types, runner, amount, province, fill_date]
        runinfo = data["entAnnlRunSet"]
        assureinfo = data["entAnnlFwarnntSet"]
        investinfo = data["entAnnlOutinvSet"]
        labinfo = data["entAnnlSocSet"]
        permitinfo = data["entAnnlPermitSet"]
        partyinfo = data["entAnnlPartySet"]
        schangeinfo = data["entAnnlStocktransSet"]
        shareinfo = data["entAnnlInvestorSet"]
        webinfo = data["entAnnlWebsiteSet"]
        return information, runinfo, assureinfo, investinfo, labinfo, permitinfo, partyinfo, schangeinfo, shareinfo, webinfo

    def get_run_info(self, data):
        info = []
        if len(data) == 0:
            pass
        else:
            data = data[0]
            if "assGro" in data.keys():
                asset = data["assGro"]
                if_asset = int(data["assGroSign"])
            else:
                asset = ''
                if_asset = 0
            if "totEqu" in data.keys():
                benifit = data["totEqu"]
                if_benifit = int(data["totEquSign"])
            else:
                benifit = ''
                if_benifit = 0
            if "vendInc" in data.keys():
                income = data["vendInc"]
                if_income = int(data["vendIncSign"])
            else:
                income = ''
                if_income = 0
            if "proGro" in data.keys():
                profit = data["proGro"]
                if_profit = int(data["proGroSign"])
            else:
                profit = ''
                if_profit = 0
            if "maiBusInc" in data.keys():
                main_income = data["maiBusInc"]
                if_main = int(data["maiBusIncSign"])
            else:
                main_income = ''
                if_main = 0
            if "netInc" in data.keys():
                net_income = data["netInc"]
                if_net = int(data["netIncSign"])
            else:
                net_income = ''
                if_net = 0
            if "ratGro" in data.keys():
                tax = data["ratGro"]
                if_tax = int(data["ratGroSign"])
            else:
                tax = ''
                if_tax = 0
            if "liaGro" in data.keys():
                debt = data["liaGro"]
                if_debt = int(data["liaGroSign"])
            else:
                debt = ''
                if_debt = 0

            if "priYeaLoan" in data.keys():
                loan = data["priYeaLoan"]
                if_loan = int(data["priYeaLoanSign"])
            else:
                loan = ''
                if_loan = 0
            if "priYeaSub" in data.keys():
                subsidy = data["priYeaSub"]
                if_subsidy = int(data["priYeaSubSign"])
            else:
                subsidy = ''
                if_subsidy = 0
            info = [asset, if_asset, benifit, if_benifit, income, if_income, profit, if_profit, main_income, if_main,
                    net_income, if_net,
                    tax, if_tax, debt, if_debt, loan, if_loan, subsidy, if_subsidy]
        return info

    def update_base(self, gs_basic_id, baseinfo, year, cursor, connect):
        name, uuid, tel, address = baseinfo[0][0], baseinfo[0][1], baseinfo[0][2], baseinfo[0][3]
        email, postcode, status, employee = baseinfo[0][4], baseinfo[0][5], baseinfo[0][6], baseinfo[0][7]
        if_empnum, womennum, if_womennum, holding = baseinfo[0][8], baseinfo[0][9], baseinfo[0][10], baseinfo[0][11]
        if_holding, mainbus, code, ccode = baseinfo[0][12], baseinfo[0][13], baseinfo[0][14], baseinfo[0][15]
        pripid, refuuid, if_invest, if_sharetrans = baseinfo[0][16], baseinfo[0][17], baseinfo[0][18], baseinfo[0][19]
        if_fwarnnt, if_website, if_net, report_mode = baseinfo[0][20], baseinfo[0][21], baseinfo[0][22], baseinfo[0][23]
        types, runner, amount, province = baseinfo[0][24], baseinfo[0][25], baseinfo[0][26], baseinfo[0][27]
        fill_date = baseinfo[0][28]
        m = hashlib.md5()
        m.update(str(gs_basic_id) + str(year))
        uuid = m.hexdigest()
        remark = 0
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        cursor.execute(update_address, (gs_basic_id, tel, address, email, updated_time, gs_basic_id))
        connect.commit()
        try:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            count = cursor.execute(basic_string, (
                gs_basic_id, year, province, name, uuid, tel, address, email, postcode, status, employee, if_empnum,
                womennum, \
                holding, if_holding, mainbus, code, ccode, pripid, refuuid, if_invest, if_sharetrans, if_fwarnnt,
                if_website, if_net, report_mode, types, runner, amount, fill_date, updated_time, updated_time))
            gs_report_id = connect.insert_id()
            connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error('report basic error:%s' % e)
        finally:
            if remark < 100000001:
                remark = count

            # print 'update report basic %s'%count
            return gs_report_id

    def update_run_info(self, year, gs_report_id, gs_basic_id, cursor, connect, province, runinfo):
        asset, if_asset, benifit, if_benifit = runinfo[0], runinfo[1], runinfo[2], runinfo[3]
        income, if_income, profit, if_profit = runinfo[4], runinfo[5], runinfo[6], runinfo[7]
        main_income, if_main, net_income, if_net = runinfo[8], runinfo[9], runinfo[10], runinfo[11]
        tax, if_tax, debt, if_debt = runinfo[12], runinfo[13], runinfo[14], runinfo[15]
        loan, if_loan, subsidy, if_subsidy = runinfo[16], runinfo[17], runinfo[18], runinfo[19]
        m = hashlib.md5()
        m.update(str(gs_basic_id) + str(year))
        uuid = m.hexdigest()
        remark = 0
        try:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            count = cursor.execute(run_string, (
                gs_report_id, gs_basic_id, province, asset, if_asset, benifit, if_benifit, income, if_income, profit,
                if_profit, main_income, if_main, net_income, if_net, tax, if_tax, debt, if_debt, loan, if_loan, subsidy,
                if_subsidy, uuid, updated_time, updated_time))
            connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error('%s run error:%s' % (year, e))
        finally:
            if remark < 100000001:
                remark = count
            return remark


#更新一年的年报数据
def update_report_main(gs_basic_id, year, cursor, connect,url,province):
    reportobject = Report()
    count = cursor.execute(select_report, (gs_basic_id, year))
    if int(count) > 0:
        flag = 0
    else:
        flag = reportobject.update_all_info(gs_basic_id, year, url, cursor, connect,province)
    return flag

#主函数入口
def main(url,year,gs_basic_id,province):
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        flag = update_report_main(gs_basic_id,  year, cursor, connect,url,province)
        string = '%s:' % year + str(flag)
        logging.info(string)
        print string
    except Exception, e:
        logging.error('report error:%s' % e)
    finally:
        cursor.close()
        connect.close()
