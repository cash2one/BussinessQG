#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup

from BranchCode import QGGS_basic
from BranchCode import QGGS_branch
from BranchCode import QGGS_brand
from BranchCode import QGGS_change
from BranchCode import QGGS_check
from BranchCode import QGGS_except
from BranchCode import QGGS_freeze
from BranchCode import QGGS_gtshareholder
from BranchCode import QGGS_mort
from BranchCode import QGGS_permit
from BranchCode import QGGS_person
from BranchCode import QGGS_punish
from BranchCode import QGGS_shareholder
from BranchCode import QGGS_stock
from BranchCode.QGGS_Report import *
from PublicCode.Public_code import Get_BranchInfo as Get_BranchInfo
from PublicCode.deal_html_code import caculate_time
import time

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

host = 'http://www.gsxt.gov.cn'

update_basic_py = 'update gs_py set gs_basic = %s where gs_basic_id = %s'
update_branch_py = 'update gs_py set gs_branch = %s where gs_basic_id = %s'
update_brand_py = 'update gs_py set gs_brand = %s where gs_basic_id = %s'
delete_change = 'delete from gs_change where gs_basic_id = %s'
update_change_py = 'update gs_py set gs_change = %s where gs_basic_id = %s'
select_check = 'select  updated from gs_check where gs_basic_id = %s order by updated desc  LIMIT 1'
update_check_py = 'update gs_py set gs_check = %s where gs_basic_id = %s'
select_except = 'select  updated from gs_except where gs_basic_id = %s order by updated desc  LIMIT 1'
update_except_py = 'update gs_py set gs_except = %s where gs_basic_id = %s'
update_freeze_py = 'update gs_py set gs_freeze = %s where gs_basic_id = %s '
update_permit_py = 'update gs_py set gs_permit = %s where gs_basic_id = %s'
update_punish_py = 'update gs_py set gs_punish = %s where gs_basic_id = %s'
update_stock_py = 'update gs_py set gs_stock = %s where gs_basic_id = %s'
delete_share = 'delete from gs_shareholder where  gs_basic_id = %s and cate = 0'
delete_gtshare = 'delete from gs_shareholder where gs_basic_id = %s and cate = 2'
update_share_py = 'update gs_py set gs_shareholder = %s where gs_basic_id = %s'

update_person_py = 'update gs_py set gs_person = %s where gs_basic_id = %s '
update_person_sql = 'update gs_person set quit = 1 where gs_basic_id = %s and updated < %s'

url = {}

#匹配url
def get_url(pattern, url_content):
    url = re.findall(pattern, str(url_content))
    real_url = host + url[0]
    return real_url

#用于获取各分支的url
def get_singleinfo_url(result):

    url_content = BeautifulSoup(result, 'lxml').find("div", {"id": "url"}).find("script")
    #print url_content
    shareholder_url = get_url(config.shareholder_pattern, url_content)
    person_url = get_url(config.person_pattern, url_content)
    branch_url = get_url(config.branch_pattern, url_content)
    change_url = get_url(config.change_pattern, url_content)
    gtchange_url = get_url(config.gtchange_pattern, url_content)
    check_url = get_url(config.check_pattern, url_content)
    permit_url = get_url(config.permit_pattern, url_content)
    punish_url = get_url(config.punish_pattern, url_content)
    gt_punish_url = get_url(config.gtpunish_pattern, url_content)
    except_url = get_url(config.except_pattern, url_content)
    freeze_url = get_url(config.freeze_pattern, url_content)
    stock_url = get_url(config.stock_pattern, url_content)
    gt_permit_url = get_url(config.gt_permit, url_content)
    brand_url = get_url(config.brand_pattern, url_content)
    mort_url = get_url(config.mort_pattern, url_content)
    report_url = get_url(config.report_pattern, url_content)
    gt_share_url = get_url(config.gtshare_pattern, url_content)

    # print brand_url
    url["branch"] = branch_url
    url["shareholder"] = shareholder_url
    url["person"] = person_url
    url["change"] = change_url
    url["gtchange"] = gtchange_url
    url["check"] = check_url
    url["permit"] = permit_url
    url["except"] = except_url
    url["punish"] = punish_url
    url["freeze"] = freeze_url
    url["stock"] = stock_url
    url["gt_permit"] = gt_permit_url
    url["brand"] = brand_url
    url["report"] = report_url
    url["mort"] = mort_url
    url["gtshare"] = gt_share_url
    url["gtpunish"] = gt_punish_url

    return url


#对branch,permit punish,freeze,stock,brand表的更新情况做判断
def update_branch1(cursor, connect, gs_basic_id,update_sql,QGGS,name):
    try:
        recordstotal, total = Get_BranchInfo().get_info(None, gs_basic_id, cursor, connect, url[name], QGGS, name)
        if recordstotal ==0:
            flag = None
        if recordstotal > 0 and total >= 0 and total<100000001:
            flag = total
        elif recordstotal >0 and total >=100000001:
            flag = 100000001
    except Exception, e:
        logging.info('%s error :%s' %(name, e))
        flag = 100000005
    finally:
        if flag == None:
            pass
        else:
            cursor.execute(update_sql, (flag, gs_basic_id))
            connect.commit()


#对change,shareholder表的更新情况做判断
def update_branch2(cursor, connect, gs_basic_id, delete_sql, update_sql, name, QGGS):
    try:
        cursor.execute(delete_sql,gs_basic_id)
        connect.commit()
        recordstotal, total = Get_BranchInfo().get_info(None, gs_basic_id, cursor, connect, url[name], QGGS, name)
        if recordstotal == 0:
            flag = None
        elif recordstotal> 0 and total >=0 and total < 100000001:
            flag = total
        elif recordstotal > 0 and total >100000001:
            flag = 100000001
    except Exception, e:
        flag = 100000005
        logging.error('%s error:%s' % (name, e))
    finally:
        if flag == None:
            pass
        else:
            # print update_sql %(flag, gs_basic_id)
            cursor.execute(update_sql, (flag, gs_basic_id))
            connect.commit()

#对check和except表的更新情况做判断
def update_branch3(cursor,connect,gs_basic_id,select_sql,update_sql,QGGS,name):
    try:
        now_time = time.time()
        last_time = cursor.execute(select_sql,gs_basic_id)
        if last_time == 0:
            recordstotal, total = Get_BranchInfo().get_info(None, gs_basic_id, cursor, connect, url[name], QGGS, name)
            if recordstotal == 0:
                flag = None
            elif recordstotal > 0 and total >= 0 and total < 100000001:
                flag = total
            elif recordstotal > 0 and total > 100000001:
                flag = 100000001
        elif int(last_time) == 1:
            last_time = cursor.fetchall()[0][0]
            interval = caculate_time(str(now_time), str(last_time))
            if interval > 2592000:
                flag = None
            else:
                recordstotal, total = Get_BranchInfo().get_info(None, gs_basic_id, cursor, connect, url[name], QGGS, name)
                if recordstotal == 0:
                    flag = None
                elif recordstotal > 0 and total >= 0 and total < 100000001:
                    flag = total
                elif recordstotal > 0 and total > 100000001:
                    flag = 100000001
    except Exception, e:
        flag = 100000005
        logging.error('%s error %s' % (name, e))
    finally:
        if flag == None:
            pass
        else:
            cursor.execute(update_sql, (flag, gs_basic_id))
            connect.commit()

# 对person表的更新情况做判断
def update_person(cursor,connect,gs_basic_id,update_py,update_sql,QGGS,name):
    #用于获取最新的执行时间
    execute_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    try:
        recordstotal, total = Get_BranchInfo().get_info(None, gs_basic_id, cursor, connect, url[name], QGGS, name)
        if recordstotal == 0:
            flag = None
        elif recordstotal > 0 and total >= 0 and total < 100000001:
            flag = total
        elif recordstotal > 0 and total > 100000001:
            flag = 100000001
    except Exception,e:
        flag = 100000005
        logging('person errror:%s ' % e)
    else:
        if flag!=None and flag <100000001:
            cursor.execute(update_sql, (gs_basic_id, execute_time))
            connect.commit()
    finally:
        if flag == None:
            pass
        else:
            cursor.execute(update_py, (flag, gs_basic_id))
            connect.commit()






def update_info_main(cursor, connect, url, flag, gs_basic_id):

    result, status_code = Send_Request().send_requests(url)

    pattern = re.compile(".*返回首页.*")
    fail = re.findall(pattern, result)

    if status_code == 200 and len(fail) == 0:
        information,flag = QGGS_basic.get_basic_info(result, status_code)
        # print information,flag
        if len(information) > 0:
            row_count = QGGS_basic.update_basic(information, connect, cursor, gs_basic_id)
            if row_count == 0:
                flag = 100000001
            elif row_count == 1:
                flag = 1
            cursor.execute(update_basic_py, (flag, gs_basic_id))
            connect.commit()
            url = get_singleinfo_url(result)
            # update_branch1(cursor, connect, gs_basic_id,update_branch_py, QGGS_branch, "branch")
            # update_branch1(cursor, connect, gs_basic_id, update_brand_py, QGGS_brand, "brand")
            # update_branch1(cursor, connect, gs_basic_id, update_permit_py, QGGS_permit, "permit")
            # update_branch1(cursor, connect, gs_basic_id, update_permit_py, QGGQ_permit,"gt_permit")
            # update_branch1(cursor, connect, gs_basic_id, update_punish_py, QGGS_punish, "punish")
            # update_branch1(cursor, connect, gs_basic_id, update_punish_py, QGGS_punish, "gtpunish")
            # update_branch1(cursor, connect, gs_basic_id, update_freeze_py, QGGS_freeze, "freeze")
            # update_branch1(cursor, connect, gs_basic_id, update_stock_py, QGGS_stock, "stock")

            # update_branch2(cursor, connect, gs_basic_id, delete_change, update_change_py,"change", QGGS_change)
            # update_branch2(cursor,connect,gs_basic_id,delete_change,update_change_py,"gtchange",QGGS_change)
            # update_branch2(cursor, connect, gs_basic_id, delete_share, update_share_py, "shareholder", QGGS_shareholder)

            # update_branch2(cursor, connect, gs_basic_id, delete_gtshare, update_share_py, "gtshare", QGGS_gtshareholder)

            # update_branch3(cursor, connect, gs_basic_id, select_check, update_check_py, QGGS_check, "check")
            # update_branch3(cursor, connect, gs_basic_id, select_except, update_except_py, QGGS_except, "except")
            # update_person(cursor, connect, gs_basic_id, update_person_py, update_person_sql, QGGS_person, "person")

            # update_report_main(url["report"], cursor, connect, gs_basic_id)
        else:
            logging.error('首页访问失败！！！')
            flag = 100000005
            cursor.execute(update_basic_py, (flag, gs_basic_id))
            connect.commit()
    else:
        logging.error('网页打开出错！！!')
        flag = 100000005
        cursor.execute(update_basic_py, (gs_basic_id, flag,gs_basic_id))
        connect.commit()

