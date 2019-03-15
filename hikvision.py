#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"获取到的accessToken有效期是7天，在即将过期时重新获取，请勿频繁调用，频繁调用将会被拉入限制黑名单"
"东西不多，就不用多线程了"

_author_="wrysunny"

import os
import time
import json
import requests
import configparser
from pathlib import Path
import urllib3
urllib3.disable_warnings()


Get_accessToken_url = "https://open.ys7.com/api/lapp/token/get"
Header = {"Content-Type": "application/x-www-form-urlencoded"}
#Get_accessToken_data = f"appKey={AppKey}&appSecret={Secret}"

def Get_accessToken(AppKey,Secret):
	s = requests.post(url = Get_accessToken_url, headers = Header, data = f"appKey={AppKey}&appSecret={Secret}", timeout = 10, verify = False).content
	#json.dumps(s) 将内容编码为json格式
	r = json.loads(s) # 加载已编码的json
	if r["code"] == "200" : # 判断状态码是否为200，否则不执行
		accessToken = r["data"]["accessToken"] # 获取accessToken
		expireTime = r["data"]["expireTime"]# accessToken具体过期时间
		return accessToken,expireTime
	else:
		exit(1)

Get_capture_url = "https://open.ys7.com/api/lapp/device/capture"

# 建议调用的间隔为4s左右
def Get_picUrl(accessToken,Serial):
	s = requests.post(url = Get_capture_url, headers = Header, data = f"accessToken={accessToken}&deviceSerial={Serial}&channelNo=1", timeout = 10, verify = False).content
	r = json.loads(s) 
	if r["code"] == "200" : 
		picUrl = r["data"]["picUrl"] # 图片有效期2小时
		return Serial,picUrl
	else:
		print("Pic Url Get Fail ! ",r["code"])
		print("See :","https://open.ys7.com/doc/zh/book/index/device_option.html") # 状态码参考
		exit(1)

def Get_capture(Serial,picUrl):
	ymd = time.strftime("%Y%m%d", time.localtime())
	h = time.strftime("%H", time.localtime())
	if os.path.exists(ymd) is True: # 判断上级目录是否存在
		if os.path.exists(f"{ymd}/{h}") is True:
			s = requests.get(url = picUrl, headers = Header, timeout = 10, verify = False).content
			with open(f'{ymd}/{h}/{time.strftime("%H-%M-%S", time.localtime())}_{Serial}.png','wb') as f:
				f.write(s)
			print(f"Done! : {Serial}")
		else:
			os.makedirs(f"{ymd}/{h}")
			Get_capture(Serial,picUrl)
	else:
		os.makedirs(f"{ymd}")
		Get_capture(Serial,picUrl)

		
def Get_config():
	if Path("config.ini").exists() is True : # 内建函数判断配置文件是否存在
		cf = configparser.ConfigParser()
		cf.read("config.ini")  # 读取配置文件
		accessToken = cf.get("Auth-info", "accessToken")
		expireTime = cf.get("Auth-info", "expireTime")
		AppKey = cf.get("Cam-info", "AppKey")
		Secret = cf.get("Cam-info", "Secret")
		Serial1 = cf.get("Cam-info", "Serial1")
		Serial2 = cf.get("Cam-info", "Serial2")
		Serial3 = cf.get("Cam-info", "Serial3")
		if len(accessToken) > 0 : # 判断是否存在accessToken
			if int(expireTime) > int(str(int(time.time())) + "000") : # 判断是否过期
				return accessToken,Serial1,Serial2,Serial3 # 没过期返回accessToken
			else:
				accessToken,expireTime = Get_accessToken(AppKey,Secret) # 更新accessToken并写入配置文件中，并返回
				cf.set("Auth-info","accessToken",f"{accessToken}")
				cf.set("Auth-info","expireTime",f"{expireTime}")
				cf.write(open('config.ini','w'))
				return accessToken,Serial1,Serial2,Serial3
		else:
			accessToken,expireTime = Get_accessToken(AppKey,Secret)# 获取accessToken并写入配置文件中，并返回
			cf.set("Auth-info","accessToken",f"{accessToken}")
			cf.set("Auth-info","expireTime",f"{expireTime}")
			cf.write(open('config.ini','w'))
			return accessToken,Serial1,Serial2,Serial3
	else:
		print("Config File Not Found !!!")

if __name__ == '__main__':
	accessToken,Serial1,Serial2,Serial3 = Get_config()
	for Serial in Serial1,Serial2,Serial3 :
		print(Serial)
		Serial,picUrl = Get_picUrl(accessToken,Serial)
		#print(picUrl)
		Get_capture(Serial,picUrl)
		# crontab 
		# */1 * * * HOME=/home/xx/xx/  xx.py 
		# 指定执行目录位置