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
import config
from PublicCode.Public_code import Connect_to_DB as Connect_to_DB
from PublicCode.Public_code import Get_BranchInfo as Get_BranchInfo
from PublicCode.Public_code import Send_Request as Send_Request

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# url = 'http://www.gsxt.gov.cn/%7BaH8LOjM0uhosG-gipUJT2XnRkWxkN2fUhoeCXWnB0dEohV1W4JB2TP9Js48bcXTCBwbc854D3GLGvj740V402Zms6ow2nQQTH7hAtvfkeVmPcbWI22POI8lHFSDw46LN3phU41_sU_wAlHa78WsKBg-1498705562212%7D'
host = config.host
select_report = 'select gs_report_id from gs_report where gs_basic_id = %s and year = %s'
basic_string = 'insert into gs_report(gs_basic_id,id,year,name,tel,address,email,postcode,status,employee\
,assets,benifit,income,profit,income_main,net_profit,tax,debt,loan,subsidy,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
%s,%s,%s,%s,%s,%s,%s)'
update_basic = 'update gs_report set name = %s,tel = %s,address = %s,email = %s,postcode = %s,status = %s,employee = %s\
,assets = %s ,benifit = %s ,income = %s ,profit = %s ,income_main = %s ,net_profit = %s ,tax = %s ,debt = %s ,loan = %s,subsidy = %s,updated = %s where gs_report_id = %s'


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
                information[i] = [anCheId, anCheYear]
        else:
            logging.info("report url fail")
        return information

    def get_report_info(self, information):
        for key in information.keys():
            year = information[key][1]
            anCheId = information[key][0]
            url_list = self.get_report_url(anCheId)
            baseurl = url_list["baseinfo"]
            # print baseurl
            baseinfo = self.get_baseinfo(baseurl)
            report_id = self.update_base(self.gs_basic_id, baseinfo, year, self.cursor, self.connect)
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

        information = {}
        result, status_code = Send_Request().send_requests(url)
        if status_code == 200:
            data = json.loads(result)["data"][0]
            name = data["entName"]
            tel = data["tel"]
            # print tel
            pattern = re.compile(
                u'((\d{11})|^((\d{7,8})|(\d{4}|\d{3})-(\d{7,8})|(\d{4}|\d{3})-(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1})|(\d{7,8})-(\d{4}|\d{3}|\d{2}|\d{1}))).*')
            tel = re.findall(pattern, tel)[0][0]
            address = data["addr"]
            email = data["email"]
            postcode = data["postalCode"]
            status = data["busSt_CN"]
            # share_trans = None
            # if_invest = None
            # if_website = None
            assets = data["assGro"]
            benifit = data["totEqu"]
            income = data["vendInc"]
            employee = data["empNum"]
            profit = data["proGro"]
            income_main = data["maiBusInc"]
            net_profit = data["netInc"]
            tax = data["ratGro"]
            debt = data["liaGro"]
            loan = None
            subsidy = None
            information[0] = [name, tel, address, email, postcode, status, assets, benifit, income, employee, profit,
                              income_main, net_profit, tax, debt, loan, subsidy]
        return information

    # 用于更新年报基本信息
    def update_base(self, gs_basic_id, baseinfo, year, cursor, connect):
        name, tel, address, email = baseinfo[0][0], baseinfo[0][1], baseinfo[0][2], baseinfo[0][3]
        postcode, status, assets, benifit = baseinfo[0][4], baseinfo[0][5], baseinfo[0][6], baseinfo[0][7]
        income, employee, profit, income_main = baseinfo[0][8], baseinfo[0][9], baseinfo[0][10], baseinfo[0][11]
        net_profit, tax, debt = baseinfo[0][12], baseinfo[0][13], baseinfo[0][14]
        loan, subsidy = baseinfo[0][15], baseinfo[0][16]
        m = hashlib.md5()
        idstring = str(gs_basic_id) + str(year) + '1'
        m.update(idstring)
        id = m.hexdigest()
        # print tel
        count = cursor.execute(select_report, (gs_basic_id, year))
        try:
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                row_count = cursor.execute(basic_string, (
                    gs_basic_id, id, year, name, tel, address, email, postcode, status,
                    employee, assets, benifit, income, profit, income_main, net_profit, tax, debt, loan, subsidy,
                    updated_time))
                gs_report_id = connect.insert_id()
                connect.commit()
            elif int(count) == 1:
                gs_report_id = cursor.fetchall()[0][0]
                # print gs_report_id
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                row_count = cursor.execute(update_basic,
                                           (name, tel, address, email, postcode, status,
                                            employee, assets, benifit, income, profit, income_main, net_profit, tax,
                                            debt, loan,
                                            subsidy, updated_time, gs_report_id))
                connect.commit()
        except Exception, e:
            print e
            logging.error('report basic error %s' % e)
        print 'execute report %s basic:%s' % (year, row_count)
        return gs_report_id
        # 用于获取年报内的歌项目，分项目数据


def update_report_main(url, cursor, connect, gs_basic_id):
    # HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    # connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    # gs_basic_id = 2
    info = Report(url, cursor, connect, gs_basic_id)
    year_href = info.get_year_href()
    info.get_report_info(year_href)

# update_report_main()
# if __name__ == '__main__':
#     print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     start = time.time()
#     main()
#     print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
