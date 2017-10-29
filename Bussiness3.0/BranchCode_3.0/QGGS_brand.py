#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_brand.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取商标信息，并进行更新

import logging
import sys
import time
from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Bulid_Log import Log
from PublicCode.deal_html_code import remove_symbol




reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
brand_string = 'insert into ia_brand(gs_basic_id,ia_zch, ia_flh, ia_zcgg,ia_servicelist, ia_zyqqx, ia_zcdate,img_url,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_brand = 'select ia_brand_id from ia_brand where ia_zch = "%s"'
update_brand = 'update ia_brand set ia_brand_id = %s,gs_basic_id = %s,ia_flh = %s, ia_zcgg = %s ,ia_servicelist = %s, ia_zyqqx = %s,ia_zcdate = %s,img_url =%s,updated = %s where ia_brand_id = %s'
update_brand_py = 'update gs_py set gs_py_id = %s ,gs_brand = %s,updated = %s where gs_py_id = %s'

class Brand:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            nodeNum = singledata["nodeNum"]
            ia_zch = singledata["regNum"]
            ia_flh = singledata["intCls"]
            ia_zcgg = singledata["regAnncIssue"]
            ia_servicelist = singledata["goodsCnName"]
            ia_servicelist = remove_symbol(ia_servicelist)
            begin = singledata["propertyBgnDate"]
            begin = change_date_style(begin)
            end = singledata["propertyEndDate"]
            end = change_date_style(end)
            if begin== '0000-0000-00' and end =='0000-00-00':
                ia_zyqqx = ''
            else:
                ia_zyqqx = begin + '至' + end
            ia_zcdate = singledata["regAnncDate"]
            ia_zcdate = change_date_style(ia_zcdate)
            tmImage = singledata["tmImage"]
            information[i] = [ia_zch, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate,nodeNum,tmImage]
        return information


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag, update_flag = 0, 0
        flag = 0
        try:
            for key in information.keys():
                ia_zch, ia_flh, ia_zcgg = information[key][0], information[key][1], information[key][2]
                ia_servicelist, ia_zyqqx, ia_zcdate = information[key][3], information[key][4], information[key][5]
                nodeNum ,tmImage = information[key][6], information[key][7]
                if tmImage!= '' or tmImage!= None:
                    ia_img_url = 'http://www.gsxt.gov.cn' + '/doc/{0}/tmfiles/{1}'.format(nodeNum,str(tmImage))
                else:
                    ia_img_url = None
                select_string = select_brand % ia_zch
                count = cursor.execute(select_string)
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(brand_string, (
                            gs_basic_id, ia_zch, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate, ia_img_url,updated_time))
                    insert_flag += rows_count
                    connect.commit()
                elif count == 1:
                    gs_brand_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(update_brand,
                                                    (gs_brand_id,gs_basic_id, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate,
                                                     ia_img_url, updated_time, gs_brand_id))
                    update_flag += rows_count
                    connect.commit()
        except Exception,e:
            flag = 100000006
            logging.error("brand error: %s" % e)
        finally:
            if flag <100000001:
                flag = insert_flag + update_flag
            return flag,insert_flag,update_flag
def main():
    Log().found_log(gs_py_id,gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    Judge(gs_py_id, connect, cursor, gs_basic_id, url,pagenumber, perpage).update_branch(update_brand_py, Brand, "brand")
    cursor.close()
    connect.close()

if __name__ == '__main__':
    main()
