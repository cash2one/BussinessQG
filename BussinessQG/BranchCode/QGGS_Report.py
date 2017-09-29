#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
import logging
import re
import sys
import time

import QGGS_report_invest
import QGGS_report_schange
import QGGS_report_shareholder
import QGGS_report_web
import QGGS_report_permit
import QGGS_report_lab
from PublicCode.Public_code import Get_BranchInfo as Get_BranchInfo
from PublicCode.Public_code import Send_Request as Send_Request
from PublicCode import config
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# url = 'http://www.gsxt.gov.cn/%7BaH8LOjM0uhosG-gipUJT2XnRkWxkN2fUhoeCXWnB0dEohV1W4JB2TP9Js48bcXTCBwbc854D3GLGvj740V402Zms6ow2nQQTH7hAtvfkeVmPcbWI22POI8lHFSDw46LN3phU41_sU_wAlHa78WsKBg-1498705562212%7D'
host = config.host

select_report = 'select gs_report_id from gs_report where gs_basic_id = %s and year = %s'
basic_string = 'insert into gs_report(gs_basic_id,year,province,name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum,\
 if_womennum, holding, if_holding,mainbus,code,ccode,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
frun_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,uuid,income,if_income,profit,if_profit,tax,if_tax,loan, if_loan, subsidy, if_subsidy,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

update_report_py ='update gs_py set gs_py_id = %s ,report = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
update_run_py = 'update gs_py set gs_py_id = %s ,report_run = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
assure_py = 'update gs_py set gs_py_id = %s ,report_assure = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s '
invest_py = 'update gs_py set gs_py_id = %s ,report_invest = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
permit_py = 'update gs_py set gs_py_id = %s ,report_permit = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
schange_py = 'update gs_py set gs_py_id = %s ,report_schange = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
share_py = 'update gs_py set gs_py_id = %s,report_share = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
web_py = 'update gs_py set gs_py_id = %s,report_web = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
class Report:
    def __init__(self, url, cursor, connect, gs_basic_id,gs_py_id):
        self.url = url
        self.cursor = cursor
        self.connect = connect
        self.gs_basic_id = gs_basic_id
        self.gs_py_id = gs_py_id
    def judge_status(self,update_sql,records,total):

        if records == 0:
            flag = None
        elif records > 0 and total >= 0 and total < 100000001:
            flag = total
        elif records > 0 and total > 100000001:
                flag = 100000001
        if flag ==None:
            pass
        else:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            self.cursor.execute(update_sql,(self.gs_py_id,flag,updated_time,self.gs_basic_id,self.gs_py_id))
            self.connect.commit()




    #用于获取各年份的链接
    def get_year_href(self):
        information = {}
        result, status_code = Send_Request().send_requests(self.url)
        # print result
        pattern = re.compile('.*/index/invalidLink.*|.*页面不存在.*')
        fail = re.findall(pattern, result)
        if status_code == 200 and len(fail) == 0:
            pattern = re.compile(r'\[(.*?)\]')
            result = re.findall(pattern, result)[0]
            pattern = re.compile(u'{.*?}')
            result = re.findall(pattern, result)
            for i in xrange(len(result)):
                singledata = json.loads(result[i])
                anCheId = singledata["anCheId"]
                anCheYear = singledata["anCheYear"]
                entType = singledata["entType"]
                province = anCheId[15:17]
                province = config.province[province]
                information[i] = [anCheId, anCheYear, province,entType]
        else:
            logging.info("report url fail")
        return information
    #获取一般银行，有限责任公司的全部信息
    def get_report_info(self, year,anCheId,province):
        url_list = self.get_report_url(anCheId)
        baseurl = url_list["baseinfo"]
        baseinfo, runinfo = self.get_baseinfo(baseurl)
        report_id = self.update_base(self.gs_basic_id, baseinfo, year, self.cursor, self.connect, province)
        self.update_run(year, report_id, self.gs_basic_id, self.cursor, self.connect, province, runinfo)
        records,total = Get_BranchInfo(self.gs_py_id).get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                      QGGS_report_web, "reportweb%s" % year)
        self.judge_status(web_py,records,total)
        records,total = Get_BranchInfo(self.gs_py_id).get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["invest"],
                                      QGGS_report_invest, "reportinvest%s" % year)
        self.judge_status(invest_py,records,total)
        records,total = Get_BranchInfo(self.gs_py_id).get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["share"],
                                      QGGS_report_shareholder, "reportshare%s" % year)
        self.judge_status(share_py,records,total)
        records,total = Get_BranchInfo(self.gs_py_id).get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["schange"],
                                      QGGS_report_schange, "reportschange%s" % year)
        self.judge_status(schange_py,records,total)
        info = QGGS_report_lab.name(url_list["society"])
        if len(info)>0:
            QGGS_report_lab.update_to_db(report_id, self.gs_basic_id, self.cursor, self.connect, info,province)
    #获取合作社家庭的个人用户的基本信息
    def get_freport_info(self,year,anCheId,province):
        url_list = self.get_freport_url(anCheId)
        baseurl = url_list["base"]
        baseinfo, runinfo = self.get_fbaseinfo(baseurl)
        report_id = self.update_base(self.gs_basic_id, baseinfo, year, self.cursor, self.connect, province)
        self.update_frun(year, report_id, self.gs_basic_id, self.cursor, self.connect, province, runinfo)
        records,total = Get_BranchInfo(self.gs_py_id).get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                  QGGS_report_web, "reportweb%s" % year)
        self.judge_status(web_py,records,total)
        records,total = Get_BranchInfo(self.gs_py_id).get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                  QGGS_report_permit, "reportpermit%s" % year)
        self.judge_status(permit_py,records,total)
        info = QGGS_report_lab.name(url_list["society"])
        if len(info) > 0:
            QGGS_report_lab.update_to_db(report_id, self.gs_basic_id,self.gs_py_id, self.cursor, self.connect, info,province)

    def get_report_url(self, anCheId):
        information = {}
        url = host + '/corp-query-entprise-info-vAnnualReportBaseInfoForJs-%s.html' % anCheId
        result, status_code = Send_Request().send_requests(url)
        data = json.loads(result)
        annSocsecinfoUrl = host + data["annSocsecinfoUrl"]
        information["society"] = annSocsecinfoUrl

        webSiteInfoUrl = host + data["webSiteInfoUrl"]
        information["web"] = webSiteInfoUrl

        forInvestmentUrl = host + data["forInvestmentUrl"]
        information["invest"] = forInvestmentUrl

        sponsorUrl = host + data["sponsorUrl"]
        information["share"] = sponsorUrl

        baseinfoUrl = host + data["baseinfoUrl"]
        information["baseinfo"] = baseinfoUrl

        schangeUrl = host + data["vAnnualReportAlterstockinfoUrl"]
        information["schange"] = schangeUrl
        return information
    def get_freport_url(self,anCheId):
        info = {}
        #http://www.gsxt.gov.cn/corp-query-entprise-info-vAnnualSfcReportBaseInfoForJs-PROVINCENODENUM53000000c868f3492a41db8f5aecac83084053.html
        url = host +'/corp-query-entprise-info-vAnnualSfcReportBaseInfoForJs-%s.html'%anCheId
        result,status_code = Send_Request().send_requests(url)
        if status_code ==200:
            data = json.loads(result)
            vannualSfcAssertUrl = host+data["vannualSfcAssertUrl"]
            webSiteInfoUrl = host+data["webSiteInfoUrl"]+"?entType=17"
            annSfcSocsecinfoUrl = host+data["annSfcSocsecinfoUrl"]
            annulLicenceUrl = host +data["annulLicenceUrl"]+"?entType=17"
        info["permit"] = annulLicenceUrl
        info["web"] = webSiteInfoUrl
        info["society"] = annSfcSocsecinfoUrl
        info["base"] = vannualSfcAssertUrl
        return info

    #用于获取家庭、合作社的个人用户的基本信息
    def get_fbaseinfo(self,baseinfourl):

        url = baseinfourl
        # print url
        information, fruninfo = {}, {}
        result, status_code = Send_Request().send_requests(url)

        if status_code == 200:
            data = json.loads(result)["data"][0]
            uuid = data["anCheId"]
            name = data["farSpeArtName"]
            tel = data["tel"]

            address = data["addr"]
            email = data["email"]
            postcode = None
            status = None
            employee = data["memNum"]
            if_empnum = data["empNumDis"]

            if if_empnum != u""and if_empnum != None:
                if_empnum = int(if_empnum)
                if if_empnum == 2:
                    if_empnum = 0
            else:
                if_empnum = 0

            womennum = data["womEmpNum"]
            if_womennum = data["womEmpNumDis"]
            if womennum != None and str(womennum) != '':
                if_womennum = int(if_womennum)
                if if_womennum ==2:
                    if_womennum = 0
            else:
                if_womennum = 0
            holding = None
            if_holding = 0

            mainbus = data["mainBusiAct"]
            code = data["regNo"]
            ccode = data["uniscId"]
            information[0] = [name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum, holding, if_holding,mainbus,code,ccode]
            loan = data["priYeaLoan"]
            if_loan = data["priYeaLoanDis"]
            if if_loan!=u"" and if_loan!=None:
                if_loan = int(if_loan)
                if if_loan ==2:
                    if_loan = 0
            else:
                if_loan = 0
            subsidy = data["priYeaSub"]
            if_subsidy = data["priYeaSubDis"]
            if if_subsidy!=u"" and if_subsidy!=None:
                if_subsidy = int(if_subsidy)
                if if_subsidy ==2:
                    if_subsidy = 0
            else:
                if_subsidy = 0
            income = data["priYeaSales"]
            if_income = data["priYeaSalesDis"]
            if if_income!=u"" and if_income!=None:
                if_income = int(if_income)
                if if_income ==2:
                    if_income = 0
            else:
                if_income = 0
            tax = data["ratGro"]
            if_tax = data["ratGroDis"]
            if if_tax!=u"" and if_tax!= None:
                if_tax = int(if_tax)
                if if_tax == 2:
                    if_tax = 0
            else:
                if_tax = 0
            profit = data["priYeaProfit"]
            if_profit = data["priYeaProfitDis"]
            if if_profit!=u"" and if_profit!= None:
                if_profit = int(if_profit)
                if if_profit ==2:
                    if_profit = 0
            fruninfo[0] = [uuid,loan,if_loan,subsidy,if_subsidy,income,if_income,tax,if_tax,profit,if_profit]
        return information,fruninfo

    # 用于获取年报一般公司的基本信息
    def get_baseinfo(self, baseinfourl):
        url = baseinfourl

        information,runinfo= {},{}
        result, status_code = Send_Request().send_requests(url)
        if status_code == 200:
            data = json.loads(result)["data"][0]
            code = data["regNo"]
            ccode = data["uniscId"]
            uuid = data["anCheId"]
            name = data["entName"]
            tel = data["tel"]
            address = data["addr"]
            email = data["email"]
            postcode = data["postalCode"]
            status = data["busSt_CN"]
            employee = data["empNum"]
            if_empnum = data["empNumDis"]
            if if_empnum!=u'' and if_empnum!=None:
                if_empnum = int(if_empnum)
                if if_empnum ==2:
                    if_empnum ==0
            else:
                if_empnum = 0
            womennum = data["womemPNum"]
            if_womennum = data["womemPNumDis"]
            if womennum!=None and str(womennum)!= '':
                if_womennum = int(if_womennum)
                if if_empnum ==2:
                    if_empnum ==0
            else:
                if_womennum = 0
            holding = data["holdingSmsg"]
            if_holding = data["holdingSmsgDis"]
            if holding!=None and str(holding)!='':
                if_holding = int(if_holding)
                if if_holding ==2:
                    if_holding ==0
            else:
                if_holding = 0
            mainbus = data["mainBusiAct"]
            information[0] = [name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum, holding, if_holding,mainbus,code,ccode]
            asset = data["assGro"]
            if_asset = data["assGroDis"]
            if asset!=None and str(if_asset)!='':
                if_asset = int(data["assGroDis"])
                print 1
                print if_asset
                if if_asset ==2:
                    if_asset =0
                    print 2
                print if_asset
            else:
                if_asset = 0
            benifit = data["totEqu"]
            if_benifit = data["totEquDis"]
            if if_benifit!=None and str(if_benifit)!='':
                if_benifit = int(data["totEquDis"])
                if if_benifit ==2:
                    if_benifit =0
            else:
                if_benifit = 0
            income = data["vendInc"]
            if_income = data["vendIncDis"]
            if if_income != None and str(if_income) != '':
                if_income = int(data["vendIncDis"])
                if if_income == 2:
                    if_income = 0
            else:
                if_income = 0
            profit = data["proGro"]
            if_profit = data["proGroDis"]
            if if_profit!= None and str(if_profit)!='':
                if_profit = int(data["proGroDis"])
                if if_profit ==2:
                    if_profit = 0
            else:
                if_profit = 0
            main_income = data["maiBusInc"]
            if_main = data["maiBusIncDis"]
            if if_main !=None and str(if_main)!='':
                if_main = int(data["maiBusIncDis"])
                if if_main ==2:
                    if_main = 0
            else:
                if_main = 0
            net_income = data["netInc"]
            if_net = data["netIncDis"]
            if net_income!=None and str(net_income)!='':
                if_net = int(data["netIncDis"])
                if if_net ==2:
                    if_net = 0
            else:
                if_net = 0
            tax = data["ratGro"]
            if_tax = data["ratGroDis"]
            if if_tax!=None and str(if_tax)!="":
                if_tax = int(data["ratGroDis"])
                if if_tax ==2:
                    if_tax= 0
            else:
                if_tax = 0
            debt = data["liaGro"]
            if debt!=None and str(debt)!='':
                if_debt = int(data["liaGroDis"])
                if if_debt == 2:
                    if_debt =0
            else:
                if_debt = 0
            runinfo[0] = [asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid]
        return information,runinfo

    # 用于更新年报基本信息
    def update_base(self, gs_basic_id, baseinfo, year, cursor, connect,province):
        name, uuid, tel, address = baseinfo[0][0], baseinfo[0][1], baseinfo[0][2], baseinfo[0][3]

        email, postcode, status, employee = baseinfo[0][4],baseinfo[0][5],baseinfo[0][6],baseinfo[0][7]

        if_empnum, womennum, if_womennum, holding = baseinfo[0][8],baseinfo[0][9],baseinfo[0][10],baseinfo[0][11]
        if_holding, mainbus = baseinfo[0][12],baseinfo[0][13]
        code,ccode= baseinfo[0][14],baseinfo[0][15]

        remark = 0
        try:

            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            row_count = cursor.execute(basic_string, (gs_basic_id, year, province,
                    name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum,
                    holding, if_holding, mainbus,code,ccode,updated_time,updated_time))
            gs_report_id = connect.insert_id()
            connect.commit()
        except Exception, e:
            remark = 100000001
            logging.error('report basic error %s' % e)
        finally:
            if remark < 100000001:
                remark = row_count
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_report_py,(self.gs_py_id,remark,updated_time,gs_basic_id,self.gs_py_id))
            connect.commit()
        return gs_report_id
    #对于个体户的家庭经营状况信息
    def update_frun (self,year,gs_report_id,gs_basic_id,cursor,connect,province,fruninfo):

        uuid, loan, if_loan, subsidy, if_subsidy = fruninfo[0][0],fruninfo[0][1],fruninfo[0][2],fruninfo[0][3],fruninfo[0][4]
        income, if_income, tax, if_tax = fruninfo[0][5],fruninfo[0][6],fruninfo[0][7],fruninfo[0][8]
        profit, if_profit = fruninfo[0][9],fruninfo[0][10]
        remark = 0
        try:
            frun_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,uuid,income,if_income,profit,if_profit,tax,if_tax,loan, if_loan, subsidy, if_subsidy,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

            row_count = cursor.execute(frun_string, (gs_report_id,gs_basic_id,province,uuid,income,if_income,profit,if_profit,tax,if_tax,loan, if_loan, subsidy, if_subsidy,updated_time,updated_time))
            connect.commit()

        except Exception, e:
            remark = 100000001
            logging.error('report %sfrun error %s' %(year,e))
        finally:
            if remark <10000001:
                remark = row_count
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_run_py,(self.gs_py_id,remark,updated_time,gs_basic_id,self.gs_py_id))
            connect.commit()


        # print 'execute report %s frun:%s' % (year, row_count)

    #对于股份有限公司等的资产状况信息
    def update_run(self,year,gs_report_id,gs_basic_id,cursor,connect,province,runinfo):
        asset, if_asset, benifit, if_benifit = runinfo[0][0],runinfo[0][1],runinfo[0][2],runinfo[0][3]
        income, if_income, profit, if_profit = runinfo[0][4],runinfo[0][5],runinfo[0][6],runinfo[0][7]
        main_income, if_main, net_income, if_net = runinfo[0][8],runinfo[0][9],runinfo[0][10],runinfo[0][11]
        tax, if_tax, debt, if_debt = runinfo[0][12],runinfo[0][13],runinfo[0][14],runinfo[0][15]
        uuid = runinfo[0][16]
        remark = 0
        try:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            row_count = cursor.execute(run_string, (gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,updated_time,updated_time))
            connect.commit()

        except Exception, e:
            remark = 100000001
            logging.error('report run error %s' % e)

        finally:
            if remark < 100000001:
                remark = row_count
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_run_py, (self.gs_py_id,remark, updated_time,gs_basic_id,self.gs_py_id))
            connect.commit()

#对年报中的各分项数据进行更新
def update_report_main(url, cursor, connect, gs_basic_id,gs_py_id):

    try:
        info = Report(url, cursor, connect, gs_basic_id,gs_py_id)
        year_href = info.get_year_href()
        if len(year_href) == 0:
            pass
        elif len(year_href) != 0:
            for key in year_href.keys():
                year = year_href[key][1]
                count = cursor.execute(select_report, (gs_basic_id, year))
                if int(count) > 0:
                    pass
                elif count == 0:
                    anCheId = year_href[key][0]
                    province = year_href[key][2]
                    entType = year_href[key][3]
                    if entType == 'e':
                        info.get_report_info(year, anCheId, province)
                    elif entType == 'sfc':
                        info.get_freport_info(year, anCheId, province)
    except Exception, e:
        flag = 100000005
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        cursor.execute(update_report_py, (gs_py_id, flag, updated_time, gs_basic_id, gs_py_id))
        connect.commit()
        logging.info('report error %s' % e)




