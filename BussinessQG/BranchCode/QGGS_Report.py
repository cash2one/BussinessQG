#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import json
import logging
import re
import sys
import time

import QGGS_report_invest
import QGGS_report_schange
import QGGS_report_shareholder
import QGGS_report_web
from PublicCode import config
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
 if_womennum, holding, if_holding,mainbus,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_basic = 'update gs_report set name = %s,uuid = %s, tel = %s, address = %s, email = %s, postcode = %s, status = %s, employee = %s, if_empnum = %s, womennum = %s, if_womennum = %s, holding = %s, if_holding = %s,mainbus = %s,updated = %s where gs_report_id = %s'
select_run = 'select gs_report_run_id from gs_report_run where gs_basic_id = %s and gs_report_id = %s'
run_string = 'insert into gs_report_run(gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_run = 'update gs_report_run set asset = %s,if_asset= %s,benifit= %s,if_benifit= %s,income= %s,if_income= %s,profit= %s,if_profit= %s,main_income= %s,if_main= %s,net_income= %s,if_net= %s,tax= %s,if_tax= %s,debt= %s,if_debt= %s,uuid= %s,updated= %s where gs_report_run_id = %s'


# global gs_report_id

class Report:
    def __init__(self, url, cursor, connect, gs_basic_id):
        self.url = url
        self.cursor = cursor
        self.connect = connect
        self.gs_basic_id = gs_basic_id

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
                province = anCheId[15:17]
                province = config.province[province]
                # print province
                information[i] = [anCheId, anCheYear, province]
        else:
            logging.info("report url fail")
        return information

    def get_report_info(self, information):
        for key in information.keys():
            year = information[key][1]
            anCheId = information[key][0]
            province = information[key][2]
            url_list = self.get_report_url(anCheId)
            baseurl = url_list["baseinfo"]
            baseinfo, runinfo = self.get_baseinfo(baseurl)
            report_id = self.update_base(self.gs_basic_id, baseinfo, year, self.cursor, self.connect, province)
            self.update_run(year, report_id, self.gs_basic_id, self.cursor, self.connect, province, runinfo)
            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["web"],
                                      QGGS_report_web, "reportweb%s" % year)
            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["invest"],
                                      QGGS_report_invest, "reportinvest%s" % year)
            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["share"],
                                      QGGS_report_shareholder, "reportshare%s" % year)
            Get_BranchInfo().get_info(report_id, self.gs_basic_id, self.cursor, self.connect, url_list["schange"],
                                      QGGS_report_schange, "reportschange%s" % year)

    def get_report_url(self, anCheId):
        information = {}
        # print anCheId
        url = host + '/corp-query-entprise-info-vAnnualReportBaseInfoForJs-%s.html' % anCheId
        result, status_code = Send_Request().send_requests(url)
        data = json.loads(result)
        annSocsecinfoUrl = host + data["annSocsecinfoUrl"]
        webSiteInfoUrl = host + data["webSiteInfoUrl"]
        forInvestmentUrl = host + data["forInvestmentUrl"]
        sponsorUrl = host + data["sponsorUrl"]
        baseinfoUrl = host + data["baseinfoUrl"]
        schangeUrl = host + data["vAnnualReportAlterstockinfoUrl"]
        information["web"] = webSiteInfoUrl
        information["invest"] = forInvestmentUrl
        information["baseinfo"] = baseinfoUrl
        information["share"] = sponsorUrl
        information["schange"] = schangeUrl
        return information

    # 用于获取年报基本信息
    def get_baseinfo(self, baseinfourl):
        url = baseinfourl

        information,runinfo= {},{}
        result, status_code = Send_Request().send_requests(url)
        if status_code == 200:
            data = json.loads(result)["data"][0]
            uuid = data["anCheId"]
            name = data["entName"]
            tel = data["tel"]
            if tel !='':
                pattern = re.compile(
                    u'((\d{11})|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8})|(\d{4}|\d{3})-(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1})|(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1}))).*')
                tel = re.findall(pattern, tel)
                if len(tel)!= 0:
                     tel = tel[0][0]
            address = data["addr"]
            email = data["email"]
            postcode = data["postalCode"]
            status = data["busSt_CN"]
            employee = data["empNum"]
            if_empnum = data["empNumDis"]
            if if_empnum!='' or if_empnum!=None:
                if_empnum = int(if_empnum)
            else:
                if_empnum = 0
            womennum = data["womemPNum"]
            if_womennum = data["womemPNumDis"]
            if womennum!=None and str(womennum)!= '':
                if_womennum = int(if_womennum)
            else:
                if_womennum = 0
            holding = data["holdingSmsg"]
            if_holding = data["holdingSmsgDis"]
            if holding!=None and str(holding)!= '':
                if_holding = int(if_holding)
            else:
                if_holding = 0
            mainbus = data["mainBusiAct"]
            information[0] = [name,uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum, holding, if_holding,mainbus]
            asset = data["assGro"]
            if_asset = data["assGroDis"]
            if asset!=None and str(if_asset)!='':
                if_asset = int(data["assGroDis"])
            else:
                if_asset = 0
            benifit = data["totEqu"]
            if_benifit = data["totEquDis"]
            if benifit!=None and str(benifit)!='':
                if_benifit = int(data["totEquDis"])
            else:
                if_benifit = 0
            income = data["vendInc"]
            if_income = data["vendIncDis"]
            if income != None and str(income) != '':
                if_income = int(data["vendIncDis"])
            else:
                if_income = 0
            profit = data["proGro"]
            if_profit = data["proGroDis"]
            if profit!= None and str(profit)!='':
                if_profit = int(data["proGroDis"])
            else:
                if_profit = 0
            main_income = data["maiBusInc"]
            if_main = data["maiBusIncDis"]
            if main_income !=None and str(main_income)!='':
                if_main = int(data["maiBusIncDis"])
            else:
                if_main = 0
            net_income = data["netInc"]
            if_net = data["netIncDis"]
            if net_income!=None and str(net_income)!='':
                if_net = int(data["netIncDis"])
            else:
                if_net = 0
            tax = data["ratGro"]
            if_tax = data["ratGroDis"]
            if tax!=None and str(tax)!="":
                if_tax = int(data["ratGroDis"])
            else:
                if_tax = 0
            debt = data["liaGro"]
            if debt!=None and str(debt)!='':
                if_debt = int(data["liaGroDis"])
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

        count = cursor.execute(select_report, (gs_basic_id, year))
        try:
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                row_count = cursor.execute(basic_string, (gs_basic_id, year, province,
                    name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum,
                    holding, if_holding, mainbus,updated_time,updated_time))
                gs_report_id = connect.insert_id()
                connect.commit()
            elif int(count) == 1:
                gs_report_id = cursor.fetchall()[0][0]
                # print gs_report_id
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                row_count = cursor.execute(update_basic,(name, uuid, tel, address, email, postcode, status, employee, if_empnum, womennum, if_womennum,
                    holding, if_holding, mainbus,updated_time, gs_report_id))
                connect.commit()
        except Exception, e:
            # print e
            logging.error('report basic error %s' % e)
        print 'execute report %s basic:%s' % (year, row_count)
        return gs_report_id
    def update_run(self,year,gs_report_id,gs_basic_id,cursor,connect,province,runinfo):
        asset, if_asset, benifit, if_benifit = runinfo[0][0],runinfo[0][1],runinfo[0][2],runinfo[0][3]
        income, if_income, profit, if_profit = runinfo[0][4],runinfo[0][5],runinfo[0][6],runinfo[0][7]
        main_income, if_main, net_income, if_net = runinfo[0][8],runinfo[0][9],runinfo[0][10],runinfo[0][11]
        tax, if_tax, debt, if_debt = runinfo[0][12],runinfo[0][13],runinfo[0][14],runinfo[0][15]
        uuid = runinfo[0][16]
        count = cursor.execute(select_run, (gs_basic_id,gs_report_id))
        try:
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                # print run_string % (gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,updated_time,updated_time)
                row_count = cursor.execute(run_string, (gs_report_id,gs_basic_id,province,asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,updated_time,updated_time))
                connect.commit()
            elif int(count) == 1:
                gs_report_run_id = cursor.fetchall()[0][0]
                # print gs_report_run_id
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                print update_run % (asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,updated_time, gs_report_run_id)
                row_count = cursor.execute(update_run,(asset,if_asset,benifit,if_benifit,income,if_income,profit,if_profit,main_income,if_main,net_income,if_net,tax,if_tax,debt,if_debt,uuid,updated_time, gs_report_run_id))
                connect.commit()
        except Exception, e:
            # print e
            logging.error('report run error %s' % e)
        print 'execute report %s run:%s' % (year, row_count)

#对年报中的各分项数据进行更新
def update_report_main(url, cursor, connect, gs_basic_id):


    info = Report(url, cursor, connect, gs_basic_id)
    year_href = info.get_year_href()
    info.get_report_info(year_href)

