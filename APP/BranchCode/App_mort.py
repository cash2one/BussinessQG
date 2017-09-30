#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import logging
import sys
import time
import json
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Judge_status
import requests
from PublicCode.Public_code import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_mort = 'select gs_mort_id from gs_mort where gs_basic_id = %s and code = %s'
mort_string = 'insert into gs_mort(gs_basic_id,id,code, dates, dept, amount, status,cates,period, ranges, remark,updated)' \
              'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_mort = 'update gs_mort set gs_mort_id = %s ,dates = %s, dept = %s, amount = %s, status = %s,cates = %s,period = %s, ranges = %s, remark = %s,updated = %s ' \
              'where gs_mort_id = %s'

select_goods = 'select gs_mort_goods_id from gs_mort_goods where gs_mort_id = %s and name = %s and ownership = %s'
goods_string = 'insert into gs_mort_goods(gs_mort_id,id,gs_basic_id,name,ownership,situation,remark,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
update_goods_sql = 'update gs_mort_goods set gs_mort_goods_id = %s,situation = %s,remark = %s,updated = %s where gs_mort_goods_id = %s'

select_person = 'select gs_mort_person_id from gs_mort_person where gs_mort_id = %s and name = %s'
person_string = 'insert into gs_mort_person(gs_mort_id,id,gs_basic_id,name,cert,number,updated) values (%s,%s,%s,%s,%s,%s,%s)'
update_mort_person = 'update gs_mort_person set gs_mort_person_id = %s,name = %s,cert = %s,updated = %s where gs_mort_person_id = %s'

person_py = 'update gs_py set gs_py_id = %s,gs_mort_goods = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
goods_py = 'update gs_py set gs_py_id = %s, gs_mort_person = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
update_mort_py = 'update gs_py set gs_py_id = %s,gs_mort = %s,updated = %s where gs_py_id = %s'
mort_url = {
    "SHH":'http://sh.gsxt.gov.cn/notice/ws/data/ent_mortgage/{0}',
    'HEB':"http://he.gsxt.gov.cn/notice/ws/data/ent_mortgage/{0}",
    'SCH':'http://sc.gsxt.gov.cn/notice/ws/data/ent_mortgage/{0}',
    'YUN':'http://yn.gsxt.gov.cn/notice/ws/data/ent_mortgage/{0}'
}
class Mort:
    def name(self,data,province):
        informaiton = {}
        for i ,singledata  in enumerate(data):
            code = singledata["morRegCno"]
            if "regDate" in singledata.keys():
                dates = singledata["regDate"]
                dates = deal_html_code.change_chinese_date(dates)
            else:
                dates = '0000-00-00'
            if "regOrgInterpreted" in singledata.keys():
                dept = singledata["regOrgInterpreted"]
            else:
                dept = ''
            if "priclasecAm" in singledata.keys():
                amount = singledata["priclasecAm"]
            else:
                amount = ''
            if "typeInterpreted" in singledata.keys():
                status = singledata["typeInterpreted"]
            else:
                status = ''
            uuid = singledata["uuid"]
            if "priclasecKind" in singledata.keys():
                cates = singledata["priclasecKind"]
            else:
                cates = ''
            if "pefperForm" in singledata.keys():
                begin = deal_html_code.change_chinese_date(singledata["pefperForm"])
                end = deal_html_code.change_chinese_date(singledata["pefperTo"])
                if begin == '0000-00-00' and end == '0000-00-00':
                    period = ''
                else:
                    period = begin+'至'+end
            else:
                period = ''
            if "warCov" in singledata.keys():
                ranges = singledata["warCov"]
            else:
                ranges = ''
            if "remark" in singledata.keys():
                remark = singledata["remark"]
            else:
                remark = ''
            url = mort_url[province].format(uuid)

            info = requests.get(url).content
            info = json.loads(info)
            if "entMortgageMorSet" in info.keys():
                person_info = self.get_single_person(info["entMortgageMorSet"])
            else:
                person_info = {}
            if "entMortgageGuaSet" in info.keys():
                goods_info = self.get_single_goods(info["entMortgageGuaSet"])
            else:
                goods_info = {}
            # print person_info
            informaiton[i] = [code, dates, dept, amount, status, cates, period, ranges, remark, goods_info, person_info]
        return informaiton


    def update_to_db(self,gs_py_id , cursor, connect,gs_basic_id, info):
        update_flag, insert_flag = 0, 0
        mort_flag = 0
        recordstotal = len(info)
        logging.info("mort total:%s"%recordstotal)
        persontotal, personexecute = 0,0
        goodstotal, goodsexecute = 0,0
        try:
            for key in info.keys():
                code, dates, dept, amount = info[key][0], info[key][1], info[key][2], info[key][3]
                status, cates, period, ranges, remark = info[key][4], info[key][5], info[key][6], info[key][7], info[key][8]
                goods_info = info[key][9]
                person_info = info[key][10]

                count = cursor.execute(select_mort, (gs_basic_id, code))
                if count == 0:
                    m = hashlib.md5()
                    m.update(code)
                    id = m.hexdigest()
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    flag = cursor.execute(mort_string, (
                    gs_basic_id, id, code, dates, dept, amount, status, cates, period, ranges, remark, updated_time))
                    gs_mort_id = connect.insert_id()
                    insert_flag += flag
                    connect.commit()
                    person_total, person_execute = self.update_person(gs_mort_id, gs_basic_id, cursor, connect,
                                                                      person_info)
                    goods_total, goods_execute = self.update_goods(gs_mort_id, gs_basic_id, cursor, connect, goods_info)
                elif int(count) == 1:
                    gs_mort_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    flag = cursor.execute(update_mort, (gs_mort_id,
                    dates, dept, amount, status, cates, period, ranges, remark, updated_time, gs_mort_id))
                    update_flag += flag
                    connect.commit()
                    person_total, person_execute = self.update_person(gs_mort_id, gs_basic_id, cursor, connect, person_info)
                    goods_total,goods_execute = self.update_goods(gs_mort_id, gs_basic_id, cursor, connect, goods_info)
                persontotal+= person_total
                personexecute+= person_execute
                goodstotal +=goods_total
                goodsexecute+=goods_execute

        except Exception, e:
            logging.info('mort error :%s' % e)
            mort_flag = 100000006
        finally:

            self.update_goods_py(gs_py_id, gs_basic_id, cursor, connect, goodstotal,goodsexecute)
            self.update_person_py(gs_py_id, gs_basic_id, cursor, connect, persontotal,personexecute)
            total = insert_flag + update_flag
            if mort_flag < 100000001:
                mort_flag = total
                logging.info("execute mort:%s"%mort_flag)
            return mort_flag,recordstotal,update_flag,insert_flag


    def update_goods_py(self,gs_py_id, gs_basic_id, cursor, connect, total,execute):
        try:
            if total == 0:
                flag = ''
            elif total > 0 and execute>=0 and execute< 100000001:
                flag = execute
            elif total > 0 and execute > 100000001:
                flag = 100000001

        except Exception, e:
            flag = 100000005
            logging.error("mort goods error %s" % e)
        finally:
            if flag == '':
                pass
            else:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(goods_py, (gs_py_id,flag, updated_time,gs_basic_id,gs_py_id))
                connect.commit()

    def update_person_py(self,gs_py_id,gs_basic_id, cursor, connect, total,execute):
        try:
            if total == 0:
                flag = ''
            elif total > 0 and execute>=0 and execute< 100000001:
                flag = execute
            elif total > 0 and execute > 100000001:
                flag = 100000006

        except Exception, e:
            flag = 100000005
            logging.error("mort goods error %s" % e)
        finally:
            if flag == '':
                pass
            else:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(person_py, (gs_py_id,flag, updated_time ,gs_basic_id,gs_py_id))
                connect.commit()
    # 更新抵押物品信息
    def update_goods(self,gs_mort_id, gs_basic_id, cursor, connect, info):
        total = len(info)
        #print 'mort_goods :%s' % total
        goods_flag = 0
        insert_flag, update_flag = 0, 0
        try:
            for key in info.keys():
                name, ownership, situation, remark = info[key][0], info[key][1], info[key][2], info[key][3]

                count = cursor.execute(select_goods, (gs_mort_id, name, ownership))
                if count == 0:
                    m = hashlib.md5()
                    m.update(name + ownership)
                    id = m.hexdigest()
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    flag = cursor.execute(goods_string, (
                            gs_mort_id, id, gs_basic_id, name, ownership, situation, remark, updated_time))
                    insert_flag += flag
                    connect.commit()
                elif int(count) == 1:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    gs_mort_goods_id = cursor.fetchall()[0][0]
                    flag = cursor.execute(update_goods_sql, (gs_mort_goods_id,situation, remark, updated_time, gs_mort_goods_id))
                    update_flag += flag
        except Exception, e:
            goods_flag = 100000006
            logging.info('mort_goods error:%s' % e)
        finally:
            executetotal = insert_flag + update_flag
            if goods_flag < 100000001:
                goods_flag = executetotal
            #print 'execute mort_goods :%s' % executetotal
            return total,goods_flag




    # 更新抵押人信息
    def update_person(self,gs_mort_id, gs_basic_id, cursor, connect, info):
        total = len(info)
        #print 'person_info :%s' % total
        insert_flag, update_flag = 0, 0
        person_flag = 0
        try:
            for key in info.keys():
                name, cert, number = info[key][0], info[key][1], info[key][2]

                count = cursor.execute(select_person, (gs_mort_id, name))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    m = hashlib.md5()
                    m.update(number)
                    id = m.hexdigest()
                    flag = cursor.execute(person_string, (gs_mort_id, id, gs_basic_id, name, cert, number, updated_time))
                    insert_flag += flag
                    connect.commit()
                elif int(count) == 1:
                    gs_mort_person_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    flag = cursor.execute(update_mort_person, (gs_mort_person_id,name, cert, updated_time, gs_mort_person_id))
                    update_flag += flag
                    connect.commit()
        except Exception, e:
            person_flag = 100000001
            logging.info('mort_person error:%s' % e)
        finally:
            executetotal = insert_flag + update_flag
            if person_flag < 100000001:
                person_flag = executetotal
                #print 'execute mort_person:%s' % executetotal
            return total, person_flag



    # 获取单页的动产抵押信息
    def get_single_goods(self,data):
        information = {}
        if data != '':
            for i,singledata in enumerate(data):
                name = singledata["guaName"]
                if "own" in singledata.keys():
                    ownership = singledata["own"]
                else:
                    ownership = ''
                situation = singledata["guaDesc"]
                situation = deal_html_code.remove_symbol(situation)
                if "remark" in singledata.keys():
                    remark = singledata["remark"]
                else:
                    remark = ''
                information[i] = [name, ownership, situation, remark]
        return information


    # 获取单页的抵押人信息
    # http://www.gsxt.gov.cn/corp-query-entprise-info-mortregpersoninfo-PROVINCENODENUM4300002c9902d558baa3de015a36605e6a0961.html
    def get_single_person(self,data):
        information = {}
        if data != '':
            for i ,singledata in enumerate(data):
                name = singledata["more"]
                if "blicType" in singledata.keys():
                    cert = singledata["blicType"]
                    number = singledata["blicNo"]
                elif 'certType'in singledata.keys():
                    cert = singledata["certType"]
                    number = singledata["certNo"]
                information[i] = [name, cert, number]
        return information

def main(gs_py_id, gs_basic_id, data, province):
    Log().found_log(gs_py_id, gs_basic_id)
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        info = Mort().name(data,province)
        flag, total, insert_flag, update_flag = Mort().update_to_db(gs_py_id,cursor,connect,gs_basic_id,info)
        flag = Judge_status().judge(flag,total)
        string = 'mort:' + str(flag) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(update_flag)
        print string
        if flag == -1:
            pass
        else:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_mort_py, (gs_py_id, flag, updated_time, gs_py_id))
            connect.commit()
    except Exception,e:
        logging.error("mort error :%s"%e)
    finally:
        cursor.close()
        connect.close()
