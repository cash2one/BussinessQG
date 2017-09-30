import hashlib
import logging
import sys
import time
from PublicCode.Public_code import Judge_status
from PublicCode import deal_html_code
from PublicCode.Public_code import Log
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

pdf_path = {
    'SHH':"http://sh.gsxt.gov.cn/notice/download/viewPdf?pdfName=%s",
    'HEB':"http://he.gsxt.gov.cn/notice/download/viewPdf?pdfName=%s",
    'SCH':'http://sc.gsxt.gov.cn/notice/download/viewPdf?pdfName=%s',
    'YUN':'http://yn.gsxt.gov.cn/notice/download/viewPdf?pdfName=%s'

}
punish_string = 'insert into gs_punish(gs_basic_id,id,number, types, content,date, pub_date, gov_dept,name,pdfurl,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'
update_punish_py = 'update gs_py set gs_py_id = %s, gs_punish = %s ,updated = %s where gs_py_id = %s'
class Punish:
    #entPunishSet
    def name(self,data):
        information = {}
        if len(data)>0:
            for i,singledata in enumerate(data):
                number = singledata["penDecNo"]
                if "illegActType" in singledata.keys():
                    types = singledata["illegActType"]
                elif "illegAct" in singledata.keys():
                    types = singledata["illegAct"]
                content = singledata["penPunishCon"]
                date = singledata["penDecissDate"]
                date = deal_html_code.change_chinese_date(date)
                # updateDate = singledata["updateDate"]
                pub_date = '0000-00-00'
                pdfurl = singledata["penFilePath"]
                name = singledata["illegPt"]
                gov_dept = singledata["penOrgan"]
                regNo = singledata["regNo"]
                if "uniScid" in singledata.keys():
                    uniScid = singledata["uniScid"]
                    provin = deal_html_code.judge_province(uniScid)
                else:
                    provin = deal_html_code.judge_province(regNo)
                pdfurl = pdf_path[provin]%pdfurl
                information[i] = [number, types, content, date, name, gov_dept,pdfurl,pub_date]
        return information


    def update_to_db(self, cursor, connect,gs_basic_id, information):
        insert_flag,update_flag = 0,0
        remark = 0
        total = len(information)
        logging.info("punish total:%s"%total)
        try:
            for key in information.keys():
                number, types, content = information[key][0], information[key][1], information[key][2]
                date, name, gov_dept = information[key][3], information[key][4], information[key][5]
                pdfurl,pub_date = information[key][6],information[key][7]
                count = cursor.execute(select_punish, (gs_basic_id, number))
                if count == 0:
                    m = hashlib.md5()
                    m.update(str(number))
                    id = m.hexdigest()
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(punish_string, (
                    gs_basic_id, id,number, types, content, date, pub_date, gov_dept,name,pdfurl, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("punish error:%s" % e)
        finally:
            if remark<100000001:
                remark = insert_flag
                logging.info("execute punish:%s"%remark)
            # print remark
            return remark,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    Judge_status().update_py(gs_py_id,gs_basic_id,Punish,"punish",data,update_punish_py)

