#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import time

from PublicCode.Public_code import Send_Request
from PublicCode.deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
brand_string = 'insert into ia_brand(gs_basic_id,ia_zch, ia_flh, ia_zcgg,ia_servicelist, ia_zyqqx, ia_zcdate,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_brand = 'select ia_brand_id from ia_brand where gs_basic_id = %s and ia_zch = %s'
update_brand = 'update ia_brand set gs_basic_id = %s,ia_flh = %s , ia_zcgg = %s ,ia_servicelist = %s, ia_zyqqx = %s , ia_zcdate = %s,updated = %s where ia_brand_id = %s'


def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        nodeNum = singledata["nodeNum"]
        ia_zch = singledata["regNum"]
        ia_flh = singledata["intCls"]
        ia_zcgg = singledata["regAnncIssue"]
        ia_servicelist = singledata["goodsCnName"]
        begin = singledata["propertyBgnDate"]
        begin = change_date_style(begin)
        end = singledata["propertyEndDate"]
        end = change_date_style(end)
        if begin== None and end ==None:
            ia_zyqqx = None
        else:
            ia_zyqqx = begin + '至' + end
        ia_zcdate = singledata["regAnncDate"]
        ia_zcdate = change_date_style(ia_zcdate)
        tmImage = singledata["tmImage"]
        information[i] = [ia_zch, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate,nodeNum,tmImage]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        ia_zch, ia_flh, ia_zcgg = information[key][0], information[key][1], information[key][2]
        ia_servicelist, ia_zyqqx, ia_zcdate = information[key][3], information[key][4], information[key][5]
        nodeNum ,tmImage= information[key][6],information[key][7]

        try:
            count = cursor.execute(select_brand, (gs_basic_id, ia_zch))
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                brand_string = 'insert into ia_brand(gs_basic_id,ia_zch, ia_flh, ia_zcgg,ia_servicelist, ia_zyqqx, ia_zcdate,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
                rows_count = cursor.execute(brand_string, (
                    gs_basic_id, ia_zch, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate, updated_time))
                insert_flag += rows_count
                gs_brand_id = connect.insert_id()
                connect.commit()

            elif count == 1:
                gs_brand_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(update_brand,
                                            (gs_basic_id, ia_flh, ia_zcgg, ia_servicelist, ia_zyqqx, ia_zcdate,
                                             updated_time, gs_brand_id))
                update_flag += rows_count
                connect.commit()
            if tmImage != '':
                ia_img_url = 'http://www.gsxt.gov.cn' + '/doc/%s/tmfiles/' % nodeNum + str(tmImage)
                img_result, status_code = Send_Request().send_requests(ia_img_url)
                if img_result!= None:
                    with open('./brandimages/' + str(gs_brand_id).decode("utf8") + "_" + str(ia_zch).decode("utf8") + ".jpg","wb") as f:
                        f.write(img_result)
        except Exception, e:
            logging.error("brand error: %s" % e)
    flag = insert_flag + update_flag
    return flag
