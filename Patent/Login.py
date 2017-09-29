#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Login.py
# @Author: Lmm
# @Date  : 2017-08-28
# @Desc  : 利用selenium+PhantomJS 获取cookie及验证码 利用图片包识别后再利用工具模拟登录专利首页
#          登录过程中需要保持登录状态及session会话，否则验证码识别会出现错误
from PublicCode import config
import pytesseract
from PIL import Image
import requests
from selenium import webdriver
import logging
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import random
import time


# 用于保持回话
session = requests.session()

dcap = dict(DesiredCapabilities.PHANTOMJS)  #设置userAgent
dcap["phantomjs.page.settings.userAgent"] = (random.choice(config.USER_AGENTS))
dcap["phantomjs.page.settings.loadImages"] = False #禁止加载图片，用于提升加载速度

headers = config.header
#用于创建浏览器对象
driver = webdriver.PhantomJS()
#driver = webdriver.Chrome()
driver.set_page_load_timeout(40) #设置页面最长加载时间为40s


class Patent_Login:
    
    # 用于获取cookies
    def get_cookies(self):
        flag = 1
        try:
            result = driver.get(config.firsturl)
            cookies = driver.get_cookies()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
        except Exception, e:
            logging.error("cookies error:%s"%e)
            flag = 100000001
        finally:
            return flag

    # 用于识别验证码
    def recognize_code(self):
        flag = 1
        try:
            codeurl = driver.find_element_by_xpath("//*[@id= 'codePic']").get_attribute("src")
            result = session.get(codeurl)
            with open('./Image/code.jpg', "wb") as f:
                f.write(result.content)
            result = Image.open("./Image/code.jpg")
            code = pytesseract.image_to_string(result, config=config.tessdata_dir_config)
        except Exception,e:
            flag = 100000003
            logging.error("recognise code error:%s"%e)
        finally:
            return code,flag

    # 用于模拟登录
    def analog_login(self, code):
        flag = 1
        try:
            elem = driver.find_element_by_xpath("//*[@id='j_username']")
            elem.send_keys(config.username)
            elem = driver.find_element_by_xpath("//*[@id= 'j_password_show']")
            elem.send_keys(config.password)
            elem = driver.find_element_by_xpath("//*[@id= 'j_validation_code']")
            elem.send_keys(code)
            elem = driver.find_element_by_class_name("btn")
            elem.send_keys(Keys.ENTER)
            url = 'http://www.pss-system.gov.cn/sipopublicsearch/portal/checkLoginTimes-check.shtml'
            string = 'username=79data'
            user_agent = random.choice(config.USER_AGENTS)
            headers["User-Agent"] = user_agent
            session.post(url, string, headers=headers)
            # cookies = session.cookies
            # print cookies
            #cookies = driver.get_cookies()
            # cookies = session.cookies
            # print cookies
            # for cookie in cookies:
            #     session.cookies.set(cookie['name'], cookie['value'])
			#cookies = session.cookies
            cookies = requests.utils.dict_from_cookiejar(session.cookies)
        except Exception, e:
            flag = 100000002
            cookies = {}
            print "analog error:%s" % e
        return cookies, flag


# 主函数
def main():
    try:
        object = Patent_Login()
        flag = object.get_cookies()
        if flag == 1:
            code,flag = object.recognize_code()
            if len(code) == 4 and flag !=100000003:
                cookies, flag = object.analog_login(code)
        else:
            cookies = {}
    except Exception, e:
        cookies = {}
        logging.error("Login error:%s"%e)
    finally:
        driver.quit() #退出浏览器
        for key in cookies:
            string = str(key)
            cookies[string] = str(cookies[key])
        print cookies
        print 'flag:%s' % flag


if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main()
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)