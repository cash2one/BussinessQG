#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import time

from PublicCode import deal_html_code
from PublicCode.deal_html_code import judge_province
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
brand_string = 'insert into ia_brand(gs_basic_id,ia_zch, ia_flh, ia_zcgg,ia_servicelist, ia_zyqqx, ia_zcdate,ia_img,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_brand = 'select ia_brand_id from ia_brand where ia_zch ="%s"'
update_brand = 'update ia_brand set ia_brand_id = %s,gs_basic_id = %s,ia_flh = %s , ia_zcgg = %s ,ia_servicelist = %s, ia_zyqqx = %s,ia_zcdate = %s,img_url = %s,updated = %s where ia_brand_id = %s'
update_brand_py = 'update gs_py set gs_py_id = %s ,gs_brand = %s,updated = %s where gs_py_id = %s'
img_list = {
    "SHH": 'http://sh.gsxt.gov.cn/notice/download/downloadImage?fileName={0}',
    'HEB': "http://he.gsxt.gov.cn/notice/download/downloadImage?fileName={0}",
    'SCH': 'http://sc.gsxt.gov.cn/notice/download/downloadImage?fileName={0}',
    'YUN': 'http://yn.gsxt.gov.cn/notice/download/downloadImage?fileName={0}'

}
class Brand:
    def name(self,data):
        information = {}
        for i,singledata in enumerate(data):
            # nodeNum = singledata["nodeNum"]
            ia_zch = singledata["regNum"]
            if "intCls" in singledata.keys():
                ia_flh = singledata["intCls"]
            else:
                ia_flh = ''
            if "regAnncIssue" in singledata.keys():
                ia_zcgg = singledata["regAnncIssue"]
            else:
                ia_zcgg = None
            if "goodsCnName" in singledata.keys():
                ia_servicelist = deal_html_code.remove_symbol(singledata["goodsCnName"])
            else:
                ia_servicelist = ''
            if "propertyBgnDate" in singledata.keys():
                begin = singledata["propertyBgnDate"]
                begin = deal_html_code.change_chinese_date(begin)
            else:
                begin = None
            if "propertyEndDate" in singledata.keys():
                end = singledata["propertyEndDate"]
                end = deal_html_code.change_chinese_date(end)
            else:
                end = None
            if "uniScid" in singledata.keys():
                regNo = singledata["uniScid"]
            else:
                regNo = singledata["regNo"]
            province = judge_province(regNo)
            if begin== None and end ==None:
                ia_zyqqx = ''
            else:
                ia_zyqqx = begin + '至' + end
            if "regAnncDate" in singledata.keys():
                ia_zcdate = singledata["regAnncDate"]
                ia_zcdate = deal_html_code.change_chinese_date(ia_zcdate)
            else:
                ia_zcdate = None
            if "tmImage" in singledata.keys():
                tmImage = singledata["tmImage"]
            else:
                tmImage = ''
            information[i] = [ia_zch, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate,province,tmImage]
        return information


    def update_to_db(self,cursor, connect,gs_basic_id ,information):
        insert_flag, update_flag = 0, 0
        flag = 0
        total = len(information)
        logging.info('brand total:%s'%total)
        try:
            for key in information.keys():
                ia_zch, ia_flh, ia_zcgg = information[key][0], information[key][1], information[key][2]
                ia_servicelist, ia_zyqqx, ia_zcdate = information[key][3], information[key][4], information[key][5]
                province ,tmImage= information[key][6], information[key][7]

                if tmImage!= '' or tmImage!= None:
                    ia_img_url = img_list[province].format(tmImage)
                else:
                    ia_img_url = None

                select_string = select_brand % ia_zch
                # print select_string
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
                logging.info('execute brand:%s'%flag)
            return flag,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    Judge_status().update_py(gs_py_id,gs_basic_id,Brand,"brand",data,update_brand_py)





