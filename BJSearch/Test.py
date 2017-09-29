#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Test.py.py
# @Author: Lmm
# @Date  : 2017-09-19
# @Desc  :
from selenium import webdriver
#实例化出一个Firefox浏览器
driver = webdriver.Chrome()

# #设置浏览器窗口的位置和大小
# driver.set_window_position(20, 40)
# driver.set_window_size(1100,700)

#打开一个页面（QQ空间登录页）
driver.get("http://qzone.qq.com")
#登录表单在页面的框架中，所以要切换到该框架

driver.switch_to.frame("login_frame")
#通过使用选择器选择到表单元素进行模拟输入和点击按钮提交
driver.find_element_by_id("switcher_plogin").click()
driver.find_element_by_id("u").clear()
driver.find_element_by_id("u").send_keys("2016593039")
driver.find_element_by_id("p").clear()
driver.find_element_by_id("p").send_keys("lmm@qq.com123/")
driver.find_element_by_id("login_button").click()