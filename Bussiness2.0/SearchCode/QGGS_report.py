#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_report.py
# @Author: Lmm
# @Date  : 2017-08-08
# @Desc  :

import json
import logging
import re
import sys
import time
import hashlib
import QGGS_report_invest
import QGGS_report_lab
import QGGS_report_permit
import QGGS_report_schange
import QGGS_report_shareholder
import QGGS_report_web
from SPublicCode import config
from SPublicCode.Bulid_Log import Log
from SPublicCode.Public_code import Connect_to_DB
from SPublicCode.Public_code import Get_BranchInfo as Get_BranchInfo
from SPublicCode.Public_code import Send_Request as Send_Request

url = sys.argv[1]
gs_basic_id = sys.argv[2]
gs_search_id = sys.argv[3]

# url = 'http://www.gsxt.gov.cn/%7BTgfN2Py4EG9HUlLktZwmxCk-4rmCBGlrdZMvL3HIFmGwPTDm4fkFZ6omhNo6w_M5Y6ZPYMLowLrV1VsqDK3o4ci6MtlkeAP69sidm5jcXNPIgsSWwnQwUsCLlYRWNEl9-1502173426358%7D'
# gs_basic_id = 229422000
# gs_search_id = 837


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


host = config.host

select_report = 'select gs_report_id from gs_report where gs_basic_id = %s and year = %s'
basic_string = 'insert into gs_report(gs_basic_id,year,province,name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum,\
 if_womennum, holding, if_holding,mainbus,code,ccode,pripid,source,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_report1 = 'select gs_report_id from gs_report where gs_basic_id = %s and year = %s and source = 0'
run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
frun_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,uuid,income,if_income,profit,if_profit,tax,if_tax,loan, if_loan, subsidy, if_subsidy,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_run = 'select gs_report_run_id,gs_report_id from gs_report_run where gs_basic_id = %s and uuid = %s'
update_run = 'update gs_report_run set asset = %s,if_asset = %s,benifit= %s,if_benifit = %s,income = %s,if_income = %s,profit = %s,if_profit = %s,main_income =%s,if_main= %s,net_income = %s,if_net = %s,tax= %s,if_tax= %s,debt = %s,if_debt = %s,updated = %s where gs_report_run_id= %s'
update_frun = 'update gs_report_run set income = %s,if_income = %s,profit = %s,if_profit = %s,tax = %s,if_tax = %s,loan = %s, if_loan = %s, subsidy = %s, if_subsidy = %s,updated = %s where gs_report_run_id = %s '

update_address = 'update gs_basic set gs_basic_id = %s,tel = %s,address = %s,email = %s,updated = %s where gs_basic_id = %s'
select_year = 'select year from gs_report where gs_basic_id = %s '
select_basic_year = 'select reg_date from gs_basic where gs_basic_id = %s'
update_pbreport = 'insert into gs_report(gs_basic_id,year,province,name,uuid,code,ccode,source,report_mode,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Report:
    def __init__(self, url, cursor, connect, gs_basic_id):
        self.url = url
        self.cursor = cursor
        self.connect = connect
        self.gs_basic_id = gs_basic_id
    #用于获取各年份的链接
    def get_year_href(self):
        information = {}
        result, status_code = Send_Request().send_requests(self.url)
        pattern = re.compile('.*/index/invalidLink.*|.*页面不存在.*')
        fail = re.findall(pattern, result)
        flag = 1
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
                annRepFrom = singledata["annRepFrom"]
                province = anCheId[15:17]
                province = config.province[province]
                information[i] = [anCheId, anCheYear, province,entType,annRepFrom]
        else:
            flag = 100000004
            logging.info("report url fail")
        return information,flag
    #获取一般银行，有限责任公司的全部信息
    def get_report_info(self, year,anCheId,province):
        flag = -1
        try:
            url_list = self.get_report_url(anCheId)
            baseurl = url_list["baseinfo"]
            baseinfo, runinfo = self.get_baseinfo(baseurl)
            report_id = self.update_base(self.gs_basic_id, baseinfo, year, self.cursor, self.connect, province)
            self.update_run(year, report_id, self.gs_basic_id, self.cursor, self.connect, province, runinfo)
            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                                                   QGGS_report_web.Web, "reportweb%s" % year)


            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["invest"],
                                          QGGS_report_invest.Invest, "reportinvest%s" % year)

            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["share"],
                                          QGGS_report_shareholder.Share, "reportshare%s" % year)

            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["schange"],
                                          QGGS_report_schange.Schange, "reportschange%s" % year)

            info = QGGS_report_lab.name(url_list["society"])
            if len(info)>0:
                QGGS_report_lab.update_to_db(report_id, self.gs_basic_id, self.cursor, self.connect, info,province)
            flag = 1
        except Exception,e:
            logging.info('report error %s'%e)
            flag = 100000006
        finally:
             return flag
    #用于更新年报股份银行等一般性企业的资产状况信息
    def get_report_runinfo(self, year,anCheId,province):

        url_list = self.get_report_url(anCheId)
        baseurl = url_list["baseinfo"]
        baseinfo, runinfo = self.get_baseinfo(baseurl)
        asset, if_asset, benifit, if_benifit = runinfo[0][0], runinfo[0][1], runinfo[0][2], runinfo[0][3]
        income, if_income, profit, if_profit = runinfo[0][4], runinfo[0][5], runinfo[0][6], runinfo[0][7]
        main_income, if_main, net_income, if_net = runinfo[0][8], runinfo[0][9], runinfo[0][10], runinfo[0][11]
        tax, if_tax, debt, if_debt = runinfo[0][12],runinfo[0][13],runinfo[0][14],runinfo[0][15]
        m = hashlib.md5()
        m.update(str(self.gs_basic_id) + str(year))
        uuid = m.hexdigest()
        remark = 0
        row_count = 0
        try:
            count = self.cursor.execute(select_report1, (self.gs_basic_id, year))
            if count == 0:
               pass
            elif int(count)== 1:
                gs_report_id = self.cursor.fetchall()[0][0]
                counts = self.cursor.execute(select_run,(gs_basic_id,uuid))
                if counts ==0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    row_count = self.cursor.execute(run_string, (
                        gs_report_id, self.gs_basic_id, province, asset, if_asset, benifit, if_benifit, income, if_income,
                        profit,
                        if_profit, main_income, if_main, net_income, if_net, tax, if_tax, debt, if_debt, uuid, updated_time,
                        updated_time))
                    self.connect.commit()
                elif int(counts) ==1:

                    for gs_report_run_id,gs_report_id in self.cursor.fetchall():
                        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        row_count = self.cursor.execute(update_run,(asset, if_asset, benifit, if_benifit,income, if_income, profit, if_profit,main_income, if_main, net_income, if_net,tax, if_tax, debt, if_debt,updated_time,gs_report_run_id))
                        self.connect.commit()
        except Exception,e:
            remark = 100000006
            logging("update report error: %s"%e)
        finally:
            if remark < 100000001:
                remark = row_count
            logging.info('execute report %s frun:%s' % (year, row_count))
            return remark
    #用于更新年报个体户等个别企业的年报的资产状况信息
    def get_freport_fruninfo(self,year,anCheId,province,type):
        if type == 'sfc':
            url_list = self.get_freport_url(anCheId)
        elif type == 'pb':
            url_list = self.get_preport_url(anCheId)
        baseurl = url_list["base"]
        baseinfo, fruninfo = self.get_fbaseinfo(baseurl)
        uuid, loan, if_loan, subsidy, if_subsidy = fruninfo[0][0], fruninfo[0][1], fruninfo[0][2], fruninfo[0][3], \
                                                   fruninfo[0][4]
        income, if_income, tax, if_tax = fruninfo[0][5], fruninfo[0][6], fruninfo[0][7], fruninfo[0][8]
        profit, if_profit = fruninfo[0][9], fruninfo[0][10]
        m = hashlib.md5()
        m.update(str(self.gs_basic_id) + str(year))
        uuid = m.hexdigest()
        remark = 0
        row_count = 0
        try:
            count = self.cursor.execute(select_report1, (self.gs_basic_id, year))
            if count ==0:
                pass
            elif int(count)==1:
                gs_report_id = self.cursor.fetchall()[0][0]
                counts = self.cursor.execute(select_run, (self.gs_basic_id, uuid))
                if counts ==0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                    row_count = self.cursor.execute(update_frun, (
                        gs_report_id, gs_basic_id, province, uuid, income, if_income, profit, if_profit, tax, if_tax, loan,
                        if_loan, subsidy, if_subsidy, updated_time, updated_time))
                    self.connect.commit()
                elif int(counts)==1:
                    for gs_report_run_id, gs_report_id in self.cursor.fetchall():
                        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        row_count = self.cursor.execute(update_frun, (
                            income, if_income, profit, if_profit, tax, if_tax, loan,if_loan,
                            subsidy, if_subsidy, updated_time, gs_report_run_id))
                        self.connect.commit()
        except Exception,e:
            remark = 100000006
            logging.info('frun error:%s'%e)
        finally:
            if remark <10000001:
                remark = row_count
            return remark


    #获取合作社家庭的个人用户的基本信息
    def get_freport_info(self,year,anCheId,province):
        flag = -1
        try:
            url_list = self.get_freport_url(anCheId)
            baseurl = url_list["base"]
            baseinfo, runinfo = self.get_fbaseinfo(baseurl)
            report_id = self.update_base(self.gs_basic_id, baseinfo, year, self.cursor, self.connect, province)
            self.update_frun(year, report_id, self.gs_basic_id, self.cursor, self.connect, province, runinfo)
            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                                                   QGGS_report_web.Web, "reportweb%s" % year)

            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                      QGGS_report_permit.Permit, "reportpermit%s" % year)

            info = QGGS_report_lab.name(url_list["society"])
            if len(info) > 0:
                QGGS_report_lab.update_to_db(report_id, self.gs_basic_id,self.cursor, self.connect, info,province)
            flag = 1
        except Exception,e:
            flag = 100000006
            logging.error('report error %s'%e)
        finally:
            return flag
    def get_pbreport_info(self,year,anCheId,province):
        flag = -1
        try:
            url_list = self.get_preport_url(anCheId)
            baseurl = url_list["base"]
            baseinfo, runinfo = self.get_pbaseinfo(baseurl)
            report_id = self.update_base(self.gs_basic_id, baseinfo, year, self.cursor, self.connect, province)
            self.update_frun(year, report_id, self.gs_basic_id, self.cursor, self.connect, province, runinfo)
            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                                                   QGGS_report_web.Web, "reportweb%s" % year)

            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                      QGGS_report_permit.Permit, "reportpermit%s" % year)
            flag = 1
        except Exception,e:
            flag = 100000006
            logging.error('report error %s'%e)
        finally:
            return flag
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
    def get_preport_url(self,anCheId):
        info = {}
        url = host +'/corp-query-entprise-info-vAnnualPbReportBaseInfoForJs-%s.html'%anCheId
        result, status_code = Send_Request().send_requests(url)
        if status_code ==200:
            data = json.loads(result)
            vannualSfcAssertUrl = host+data["vAnnPbAssetUrl"]
            webSiteInfoUrl = host+data["webSiteInfoUrl"]+"?entType=17"
            # annSfcSocsecinfoUrl = host+data["annSfcSocsecinfoUrl"]
            annulLicenceUrl = host +data["annulLicenceUrl"]+"?entType=17"
            info["permit"] = annulLicenceUrl
            info["web"] = webSiteInfoUrl
            # info["society"] = annSfcSocsecinfoUrl
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
            postcode = ''
            status = ''
            employee = data["memNum"]
            if_empnum = data["empNumDis"]

            if if_empnum != u""and if_empnum != '':
                if_empnum = int(if_empnum)
                if if_empnum == 2:
                    if_empnum = 0
            else:
                if_empnum = 0

            womennum = data["womEmpNum"]
            if_womennum = data["womEmpNumDis"]
            if womennum != '' and str(womennum) != '':
                if_womennum = int(if_womennum)
                if if_womennum == 2:
                    if_womennum = 0
            else:
                if_womennum = 0
            holding = ''
            if_holding = 0

            mainbus = data["mainBusiAct"]
            code = data["regNo"]
            ccode = data["uniscId"]
            information[0] = [name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum, holding, if_holding,mainbus,code,ccode]
            loan = data["priYeaLoan"]
            if_loan = data["priYeaLoanDis"]
            if if_loan!=u"" and if_loan!='':
                if_loan = int(if_loan)
                if if_loan ==2:
                    if_loan = 0
            else:
                if_loan = 0
            subsidy = data["priYeaSub"]
            if_subsidy = data["priYeaSubDis"]
            if if_subsidy!=u"" and if_subsidy!='':
                if_subsidy = int(if_subsidy)
                if if_subsidy ==2:
                    if_subsidy = 0
            else:
                if_subsidy = 0
            income = data["priYeaSales"]
            if_income = data["priYeaSalesDis"]
            if if_income!=u"" and if_income!='':
                if_income = int(if_income)
                if if_income ==2:
                    if_income = 0
            else:
                if_income = 0
            tax = data["ratGro"]
            if_tax = data["ratGroDis"]
            if if_tax!=u"" and if_tax!= '':
                if_tax = int(if_tax)
                if if_tax == 2:
                    if_tax = 0
            else:
                if_tax = 0
            profit = data["priYeaProfit"]
            if_profit = data["priYeaProfitDis"]
            if if_profit!=u"" and if_profit!= '':
                if_profit = int(if_profit)
                if if_profit == 2:
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
            if if_empnum!=u'' and if_empnum!='':
                if_empnum = int(if_empnum)
                if if_empnum ==2:
                    if_empnum =0
            else:
                if_empnum = 0
            womennum = data["womemPNum"]
            if_womennum = data["womemPNumDis"]
            if womennum!='' and str(womennum)!= '':
                if_womennum = int(if_womennum)
                if if_empnum ==2:
                    if_empnum =0
            else:
                if_womennum = 0
            holding = data["holdingSmsg"]
            if_holding = data["holdingSmsgDis"]
            if holding!='' and str(holding)!='':
                if_holding = int(if_holding)
                if if_holding == 2:
                    if_holding =0
            else:
                if_holding = 0
            mainbus = data["mainBusiAct"]
            pripid = data["pripId"]
            information[0] = [name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum, holding, if_holding,mainbus,code,ccode,pripid]
            asset = data["assGro"]
            if_asset = data["assGroDis"]
            if asset!='' and str(if_asset)!='':
                if_asset = int(data["assGroDis"])
                if if_asset ==2:
                    if_asset =0
            else:
                if_asset = 0
            benifit = data["totEqu"]
            if_benifit = data["totEquDis"]
            if if_benifit!='' and str(if_benifit)!='':
                if_benifit = int(data["totEquDis"])
                if if_benifit ==2:
                    if_benifit =0
            else:
                if_benifit = 0
            income = data["vendInc"]
            if_income = data["vendIncDis"]
            if if_income != '' and str(if_income) != '':
                if_income = int(data["vendIncDis"])
                if if_income == 2:
                    if_income = 0
            else:
                if_income = 0
            profit = data["proGro"]
            if_profit = data["proGroDis"]
            if if_profit!= '' and str(if_profit)!='':
                if_profit = int(data["proGroDis"])
                if if_profit ==2:
                    if_profit = 0
            else:
                if_profit = 0
            main_income = data["maiBusInc"]
            if_main = data["maiBusIncDis"]
            if if_main !='' and str(if_main)!='':
                if_main = int(data["maiBusIncDis"])
                if if_main ==2:
                    if_main = 0
            else:
                if_main = 0
            net_income = data["netInc"]
            if_net = data["netIncDis"]
            if if_net!='' and str(if_net)!='':
                if_net = int(data["netIncDis"])
                if if_net ==2:
                    if_net = 0
            else:
                if_net = 0
            tax = data["ratGro"]
            if_tax = data["ratGroDis"]
            if if_tax!='' and str(if_tax)!="":
                if_tax = int(data["ratGroDis"])
                if if_tax ==2:
                    if_tax= 0
            else:
                if_tax = 0
            debt = data["liaGro"]
            if debt!='' and str(debt)!='':
                if_debt = int(data["liaGroDis"])
                if if_debt == 2:
                    if_debt =0
            else:
                if_debt = 0
            runinfo[0] = [asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid]
        return information,runinfo
    #用于获取商店等个体户信息
    def get_pbaseinfo(self,baseinfourl):
        url = baseinfourl
        # print url
        information, fruninfo = {}, {}
        result, status_code = Send_Request().send_requests(url)

        if status_code == 200:
            data = json.loads(result)["data"][0]
            uuid = data["anCheId"]
            name = data["traName"]
            tel = data["tel"]

            address = ''
            email = ''
            postcode = ''
            status = ''
            employee = data["empNum"]
            if_empnum = data["empNumDis"]

            if if_empnum != u"" and if_empnum != '':
                if_empnum = int(if_empnum)
                if if_empnum == 2:
                    if_empnum = 0
            else:
                if_empnum = 0

            womennum = ''
            if_womennum = 0

            holding = ''
            if_holding = 0
            mainbus = ''
            code = data["regNo"]
            ccode = data["uniscId"]
            information[0] = [name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum,
                              if_womennum, holding, if_holding, mainbus, code, ccode]
            loan = ''
            if_loan = 0

            subsidy = ''
            if_subsidy = 0
            income = data["vendInc"]
            if_income = data["vendIncDis"]
            if if_income != u"" and if_income != '':
                if_income = int(if_income)
                if if_income == 2:
                    if_income = 0
            else:
                if_income = 0
            tax = data["ratGro"]
            if_tax = data["ratGroDis"]
            if if_tax != u"" and if_tax != '':
                if_tax = int(if_tax)
                if if_tax == 2:
                    if_tax = 0
            else:
                if_tax = 0
            profit = ''
            if_profit = 0

            fruninfo[0] = [uuid, loan, if_loan, subsidy, if_subsidy, income, if_income, tax, if_tax, profit, if_profit]
        return information, fruninfo

    # 用于更新年报基本信息
    def update_base(self, gs_basic_id, baseinfo, year, cursor, connect,province):
        name, uuid, tel, address = baseinfo[0][0], baseinfo[0][1], baseinfo[0][2], baseinfo[0][3]

        email, postcode, status, employee = baseinfo[0][4],baseinfo[0][5],baseinfo[0][6],baseinfo[0][7]
        pripid = baseinfo[0][8]
        if_empnum, womennum, if_womennum, holding = baseinfo[0][8],baseinfo[0][9],baseinfo[0][10],baseinfo[0][11]
        if_holding, mainbus = baseinfo[0][12],baseinfo[0][13]
        code,ccode= baseinfo[0][14],baseinfo[0][15]
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        if email =='无':
            email = ''
        if tel == '无':
            tel = ''
        if address == '无':
            address = ''
        cursor.execute(update_address, (gs_basic_id, tel, address, email, updated_time, gs_basic_id))
        connect.commit()
        remark = 0
        source = 1
        try:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            row_count = cursor.execute(basic_string, (gs_basic_id, year, province,
                    name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum,
                    holding, if_holding, mainbus,code,ccode,pripid,source,updated_time,updated_time))
            gs_report_id = connect.insert_id()
            connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error('report basic error %s' % e)
        finally:
            return gs_report_id
    #对于个体户的家庭经营状况信息
    def update_frun (self,year,gs_report_id,gs_basic_id,cursor,connect,province,fruninfo):

        uuid, loan, if_loan, subsidy, if_subsidy = fruninfo[0][0],fruninfo[0][1],fruninfo[0][2],fruninfo[0][3],fruninfo[0][4]
        income, if_income, tax, if_tax = fruninfo[0][5],fruninfo[0][6],fruninfo[0][7],fruninfo[0][8]
        profit, if_profit = fruninfo[0][9],fruninfo[0][10]
        try:

            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

            row_count = cursor.execute(frun_string, (gs_report_id,gs_basic_id,province,uuid,income,if_income,profit,if_profit,tax,if_tax,loan, if_loan, subsidy, if_subsidy,updated_time,updated_time))
            connect.commit()

        except Exception, e:
            logging.error('report %sfrun error %s' %(year,e))
        finally:
            logging.info('execute report %s frun:%s' % (year, row_count))



    #对于股份有限公司等的资产状况信息
    def update_run(self,year,gs_report_id,gs_basic_id,cursor,connect,province,runinfo):
        asset, if_asset, benifit, if_benifit = runinfo[0][0],runinfo[0][1],runinfo[0][2],runinfo[0][3]
        income, if_income, profit, if_profit = runinfo[0][4],runinfo[0][5],runinfo[0][6],runinfo[0][7]
        main_income, if_main, net_income, if_net = runinfo[0][8],runinfo[0][9],runinfo[0][10],runinfo[0][11]
        tax, if_tax, debt, if_debt = runinfo[0][12],runinfo[0][13],runinfo[0][14],runinfo[0][15]
        uuid = runinfo[0][16]
        try:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            row_count = cursor.execute(run_string, (gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,updated_time,updated_time))
            connect.commit()

        except Exception, e:
            logging.error('report run error %s' % e)
        finally:
            logging.info('execute report %s frun:%s' % (year, row_count))

    #用于更新纸质年报的信息
    def update_pbreport(self,year,gs_basic_id,cursor,connect,province):

        m = hashlib.md5()
        m.update(str(year)+str(gs_basic_id))
        uuid = m.hexdigest()
        name = '12'
        code = '12'
        ccode = '12'
        source = 1
        report_mode = '已上报纸质年报'
        try:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_pbreport,(gs_basic_id,year,province,name,uuid,code,ccode,source,report_mode,updated_time,updated_time))
            connect.commit()
            remark = 0
        except:
            remark = 100000006
        finally:
            return remark
#对年报中的各分项数据进行更新
def update_report_main(url, cursor, connect, gs_basic_id):
    total,insert_total = 0,0
    update_total = 0
    try:
        info = Report(url, cursor, connect, gs_basic_id)
        year_href,remark = info.get_year_href()
        if len(year_href) == 0:
            if remark == 1:
                flag = -1
            elif remark == 100000004:
                flag = 100000004
        elif len(year_href) != 0:
            total = len(year_href)
            for key in year_href.keys():
                year = year_href[key][1]
                count = cursor.execute(select_report, (gs_basic_id, year))
                if int(count) > 0:
                    anCheId = year_href[key][0]
                    province = year_href[key][2]
                    entType = year_href[key][3]
                    annRepFrom = year_href[key][4]
                    if entType == 'e':
                        flag = info.get_report_runinfo(year,anCheId,province)
                    elif entType == 'sfc':
                        flag = info.get_freport_fruninfo(year_href,anCheId,province,entType)
                    elif entType == 'pb' and annRepFrom!='2':
                        flag = info.get_pbreport_info(year,anCheId,province,entType)
                    elif entType == 'pb' and annRepFrom =='2':
                        flag = 0
                    update_total+= flag
                elif count == 0:
                    anCheId = year_href[key][0]
                    province = year_href[key][2]
                    entType = year_href[key][3]
                    annRepFrom = year_href[key][4]
                    if entType == 'e':
                        flag = info.get_report_info(year, anCheId, province)
                    elif entType == 'sfc':
                        flag = info.get_freport_info(year, anCheId, province)
                    elif entType == 'pb' and annRepFrom!='2':
                        flag = info.get_pbreport_info(year,anCheId,province)
                    elif entType == 'pb' and annRepFrom =='2':
                        flag = info.update_pbreport(year,gs_basic_id,cursor,connect,province)
                    insert_total+=flag
    except Exception, e:
        flag = 100000006
        logging.info('report error %s' % e)
    finally:
        return flag,total,insert_tupdate_totaloal,



def update_report(url,cursor, connect, gs_basic_id):
    total,insert_total = 0,0
    update_total = 0
    try:
        now_year = time.localtime(time.time())[0]
        select_string = select_basic_year % gs_basic_id
        cursor.execute(select_string)
        sign_date = str(cursor.fetchall()[0][0])[0:4]
        if now_year == int(sign_date):
            flag = -1
        elif now_year > int(sign_date):
            flag,total,insert_total,update_total = update_report_main(url, cursor, connect, gs_basic_id)
    except Exception, e:
        flag = 100000006
        logging.error('report error :%s' % e)
    finally:
        remark = flag
        return remark,total,insert_total,update_total


def main():
    Log().found_search_log(gs_search_id, gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    flag,total,insert_total,update_total = update_report(url, cursor, connect, gs_basic_id)
    cursor.close()
    connect.close()
    info = {
        "flag":0,
        "total":0,
        "insert":0,
        "update":0
    }
    info["flag"] = int(flag)
    info["total"] = int(total)
    info["insert"] = int(insert_total)
    info["update"] = int(update_total)
    print info

if __name__ == "__main__":
    main()
