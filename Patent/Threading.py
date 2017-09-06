#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Threading.py
# @Author: Lmm
# @Date  : 2017-09-03
# @Desc  : 多线程爬虫小模板
import threading
import time
import Queue
SHARE_Q = Queue.Queue()  #构造一个不限制大小的的队列
_WORKER_THREAD_NUM = 3  #设置线程的个数

class MyThread(threading.Thread):
	'''线程函数逻辑'''
	def __init__(self,func):
		super(MyThread,self).__init__()#调用父类函数的构造对象
		self.func = func
	def run(self):
		'''重写基类的run方法'''
		self.func()
		
def do_something(item):
	'''运行逻辑，比如获取所需要的信息'''
	print item
def worker():
	'''主要用来写工作逻辑，主要队列不空持续处理
	对列为空时，检查对列，有Queue 中已经包含了wait
	notity锁，所以不需要在去任务或者放任务的时候加锁，解锁'''
	global SHARE_Q
	while True:
		if not SHARE_Q.empty():
			item = SHARE_Q.get()#获得任务
			do_something(item)
			time.sleep(1)
			SHARE_Q.task_done()
def main():
	global SHARE_Q
	threads = []
	#向队列中放入任务，真正使用时，应该设置为可持续的放入任务
	for task in xrange(5):
		SHARE_Q.put(task)
	#开启_WORKER_THREAD_NUM个线程
	for i in xrange(_WORKER_THREAD_NUM):
		thread = MyThread(worker)
		thread.start()
		threads.append(thread)
	for thread in threads:
		thread.join()
	SHARE_Q.join()
	
if __name__ == '__main__':
	main()