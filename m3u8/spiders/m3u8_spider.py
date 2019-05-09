#问题1：指定page而非m3u8时，page源代码需包含http... .m3u8链接
#问题2：IV给定的情况还未测试
import hashlib
import os
import re
from urllib.parse import urljoin

import requests
import scrapy
from Crypto.Cipher import AES

from m3u8.settings import USER_AGENT
from m3u8.merge_ts import merge


class m3u8_Spider(scrapy.Spider):
	name='m3u8'
	
	def start_requests(self):
		m3u8=getattr(self,'m3u8',None)
		page=getattr(self,'page',None)
		self.merge=getattr(self,'merge',True)
		#根据参数类型决定爬取内容
		if m3u8:
			yield scrapy.Request(url=m3u8,callback=self.parse_m3u8)
		elif page:
			yield scrapy.Request(url=page,callback=self.parse_page)
		else:
			self.logger.error('no source provided')
	def parse_page(self,response):
		#解析页面获取m3u8的url
		try:
			m3u8=re.search(r'http\S+\.m3u8',response.text).group()
			yield scrapy.Request(url=m3u8,callback=self.parse_m3u8)
		except:
			self.logger.error('no m3u8 found in the page')
	def parse_m3u8(self,response:scrapy.http.Response):
		current_url=response.url#m3u8的url，用于生成目录名和拼接后续请求的url
		another_m3u8=re.search(r'\S+\.m3u8',response.text)
		#如果指定了另一m3u8文件
		if another_m3u8:
			yield response.follow(another_m3u8.group(0),callback=self.parse_m3u8)
			return
		#判断是否加密
		match=re.search(r'#EXT-X-KEY:METHOD=AES-128(\S+)',response.text)
		if match:
			#获取AES加密的key
			info=match.group(1)
			key=urljoin(current_url,re.search(r'URI="([^"]+)"',info).group(1))
			self.key=requests.get(url=key,headers={'USER_AGENT':USER_AGENT}).content
			#是否提供了IV
			match=re.search(r'IV=0x([0-9A-Fa-f]{32})',info)
			self.iv=bytes.fromhex(match.group(1)) if match else None
		else:
			self.key=None
		self.file_names=re.findall(r'\S+\.ts\S*',response.text)#m3u8包含的ts片段名
		self.directory=hashlib.md5(current_url.encode('utf-8')).hexdigest()#ts片段存储目录
		if not os.path.exists(self.directory):
			os.mkdir(self.directory)
		for i,file_name in enumerate(self.file_names):
			file_path=os.path.join(self.directory,f'{i}.ts')#存储位置，按序命名
			#忽略已下载的片段
			if os.path.exists(file_path):
				self.logger.info(f'{i}.ts already crawled')
				continue
			yield response.follow(file_name,callback=self.parse_ts,meta={'file_path':file_path})
	def parse_ts(self,response):
		data=response.body
		#是否需要解密
		if self.key:
			#是否提供了IV
			if self.iv:
				iv=self.iv
			else:
				iv=data[:16]
				data=data[16:]
			data=AES.new(self.key, AES.MODE_CBC, iv).decrypt(data)
		#ts片段持久化
		with open(response.meta['file_path'],'wb') as f:
			f.write(data)
	def closed(self,reason):
		pattern=re.compile(r'\d+\.ts')
		crawled=len([1 for file_name in os.listdir(self.directory) if pattern.match(file_name)])#爬取的片段数
		target=len(self.file_names)#应该爬取的片段数
		if crawled<target:
			self.logger.error(f'{target-crawled} of {target} failed to download')
		else:
			self.logger.info('all successfully downloaded')
			#合并片段
			if self.merge is True:
				merge(self.directory)
				self.logger.info(f'all merged into {self.directory}.ts')
