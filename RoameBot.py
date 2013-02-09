﻿#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Contributor:
#      fffonion		<fffonion@gmail.com>

__version__ = '1.33'

import urllib2,re,os,time,ConfigParser,sys,traceback,socket
PICLIST=[]
#INITURL='http://www.roame.net/index/hakuouki-shinsengumi-kitan'
HOMEURL='http://www.roame.net'
RATIO_SUFFIX=['','-wall','-16x10','-16x9','-4x3','-5x4','-oall','-wgth','-wlth','-weqh']
BUILT_IN_SUFFIX=['','-pic-16x9','-pic-16x10','-pic-4:3','-5:4','-wgth','-pic-wlth','-pic-wegh','','',\
				'-hotest-down','-hotest-weeklydown','-hotest-monthlydown','-hotest-score',\
				'-hotest-monthlyscore','-others-latest','-others-random']
GET_INTERVAL=0.2
LOGPATH='roamebot.log'
#urllib2 HOOk was based on:http://stackoverflow.com/questions/2028517/python-urllib2-progress-hook
def chunk_report(bytes_got, chunk_size, total_size,init_time):
	percent = float(bytes_got) / total_size
	percent = round(percent*100, 2)
	eta=time.strftime('%M:%S', time.localtime((time.time()-init_time)*(100-percent)/percent))
	proglength=30
	progressbar='#'*(proglength*int(percent)/100)+' '*(proglength-proglength*int(percent)/100)
	backspace='\b'*140
	print "%4.1f%% [%s]     %5d/%5dKB   %s ETA%s" % (percent,progressbar,bytes_got/1024,total_size/1024, eta,backspace),
	if bytes_got >= total_size:
		print backspace,

def urlget(src,getimage=False,retries=3,chunk_size=8,downloaded=-1):
	try:
		req = urllib2.Request(src)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4')
		#req.add_header('Referer', 'http://www.google.com/xxxx')
		resp = urllib2.urlopen(req)
		resp.info()
		content=''
		total_size=None
		if getimage:
			while total_size==None:
				total_size=resp.info().getheader('Content-Length')
				time.sleep(GET_INTERVAL)#F*CK!!!!!!!
			total_size = int(total_size.strip())#html has no content-length
			if total_size==downloaded:
				return 'SAME'
			chunk_size*=1024
			bytes_got = 0
			init_time=time.time()
			while 1:
				chunk = resp.read(chunk_size)
				content+=chunk
				bytes_got += len(chunk)
				if not chunk:
					break
				if getimage:
					chunk_report(bytes_got, chunk_size, total_size,init_time)
			#content=chunk_read(resp, chunk*1024,chunk_report)
		else:
			content = resp.read()#.decode('utf-8')
		return content
	except urllib2.URLError, e:  
 		if isinstance(e.reason, socket.timeout):  
			if retries>0:
				return urlget(src,getimage,retries-1)
			else:
				print 'Failed on '+src
				return None
		else:
			raise
	
#NOT USING CURRENTLY	
#class multiget(threading.Thread):
#	def __init__(self,url):
#		threading.Thread.__init__(self)
#		self.thread_stop = False
#		self.geturl=url
#
#	def run(self):
#		print len(urlget(self.geturl))
#		self.stop()
#	def stop(self):
#		self.thread_stop = True
  
#def decutf(lst):
#	lstnew=[i for i in range(len(lst))]
#	for i in range(len(lst)):
#		lstnew[i]=lst[i].decode('utf-8')
#	return lstnew
def print_c(str):
	print str.decode('utf-8')
def parse_albumname(url):
	'''
	Return albumname TUPLE: 0=CHN, 1=ENG, 2=JPN
	'''
	content=urlget(url)
	#exp :<title>夏目友人帐 - 英文名:Natsume Yuujinchou, 日文名:夏目友人帳 - 路游动漫图片壁纸网</title>
	albumname=re.findall('title>(.+) -.+:(.+),.+:(.+) -',content)
	#no jp exp :<title>阿倍野挢魔法商店街 - 英文名:Magical Shopping Arcade Abenobashi - 路游动漫图片壁纸网</title>
	if albumname==[]:
		albumname=re.findall('title>(.+) -.+:(.+)(.*) -',content)
	return albumname[0]

def parse_entry(url):
	print url
	content=urlget(url)
	entries=[]
	#exp <strong style="margin:0px;padding:0px">中二病也要谈恋爱 BD VOL.1</strong>
	allentries=re.findall('<h2>(.*?)</strong>',content,re.DOTALL)
	for i in range(len(allentries)):#link num name
		entries.append([re.findall('href="(.+)">',allentries[i])[0],\
					re.findall('2px">(\d+)</span',allentries[i])[0],
					re.findall('0px">(.+)$',allentries[i])[0]])
		print_c('入口'+str(i+1)+': '+entries[-1][2].decode('utf-8')+' ('+str(entries[-1][1])+'p)')
	return entries

def parse_pagelist(url,pagenum,mode=0):
	global PICLIST
	#pic_structure={'index':0,'thumb':'','full':'','width':0,'height':0,'length':0}
	content=urlget(url)
	singlepic=re.findall('/h[23]>(.*?)<div',content,re.DOTALL)#singlepic contains thumb and full-size page url
	picinfo=re.findall('font-size:12px;font-weight:bold.*\">(.+) - ([0-9.]+)([A-Z]+)</div',content)
	if picinfo==[]:
		picinfo=re.findall('r:#789">([0-9.]+)([A-Z]+)</span',content)#today mode
	picsize=re.findall('<strong>(\d+)×(\d+)</strong>',content)
	for i in range(len(singlepic)):	#len(singlepic)#pic num added
		PICLIST.append({'index':0,'thumb':'','full':'','height':0,'width':0,'length':0,'format':''})
		PICLIST[-1]['index']=i+(pagenum-1)*8
		fullsizepageurl=re.findall('href=\"(.+)\"><img',singlepic[i])[0]#full-size
		PICLIST[-1]['full']=parse_fullsize(HOMEURL+fullsizepageurl.replace(HOMEURL,''))
		PICLIST[-1]['thumb']=re.findall('src=\"(.+)\/>',singlepic[i])[0]#thumbnail
		PICLIST[-1]['width']=picsize[i][0]
		PICLIST[-1]['height']=picsize[i][1]
		if(picinfo[i][-1]=='MB'):
			PICLIST[-1]['length']=float(picinfo[i][-2])*1024#wrap with float()
		else:
			PICLIST[-1]['length']=picinfo[i][-2]
		PICLIST[-1]['format']=len(picinfo[i])==2 and 'UNKNOWN' or picinfo[i][0]#today mode no format
	nextpage=re.findall('title="下一页" href="(.+)" style=',content)
	if (nextpage==[]):
		return None
	else:
		return HOMEURL+nextpage[0]
	
def parse_fullsize(url):
	content=urlget(url)
	deeperpage=re.findall('darlnks">.+index.html.+href="(.*?)" style.+display:block',content,re.DOTALL)#goto download page
	content=urlget(deeperpage[0])
	picurl=re.findall('src="(.+)" style="background',content)
	return picurl[0]

def fmttime():
	return '['+time.strftime('%Y-%m-%d %X',time.localtime())+'] '
#def down_callback(saved,blocksize,total):
#	x = 100.0 * saved * blocksize / total  
#	if x > 100:  
#	 	x = 100 
#	print '%.2f%%' % x

def read_config(sec,key):
	cf=ConfigParser.ConfigParser()
	cf.read(os.getcwdu()+os.path.sep+'config.ini')
	val=cf.get(sec, key)
	if val=='':
		return ''
	else:
		return val

def write_config(sec,key,val):
	cf=ConfigParser.ConfigParser()
	cf.read(os.getcwdu()+os.path.sep+'config.ini')
	cf.set(sec, key,val)
	cf.write(open(os.getcwdu()+os.path.sep+'config.ini', "w"))

def init_config():
	filename = os.getcwdu()+os.path.sep+'config.ini'
	f=file(filename,'w')
	f.write('[download]\nskip_exist = 2\ndownload_when_parse = 1\ntimeout = 10\nchunksize = 8\nretries = 3\ndir_name = 2\ndir_path = \nname = hyouka\nbuilt_in = 21\nfilter = filter_0\nfirst_page_num = \nproxy = \nproxy_name = \nproxy_pswd = \n[filter_0]\nratio = 1\nmax_length = \nmax_width = \nmin_length = \nmin_width = \nmax_size = \nmin_size = ')
	f.flush()
	f.close() 

def init_proxy():
	if read_config('download','proxy')!='':
		proxy_support = urllib2.ProxyHandler({'http':'http://['+read_config('download','proxy_name')\
											+']:['+read_config('download','proxy_pswd')+']@['\
											+read_config('download','proxy')+']'})
		opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
		urllib2.install_opener(opener)
#main entry
def main():
	global PICLIST
	PICLIST=[]
	#read and set config vals
	timeout=read_config('download','timeout')
	socket.setdefaulttimeout(int(timeout))
	chunk=int(read_config('download','chunksize'))
	retries=int(read_config('download','retries'))
	SKIP_EXIST=read_config('download','skip_exist')
	DIR_NAME=read_config('download','dir_name')
	dir_path=read_config('download','dir_path')=='' and os.path.abspath(os.curdir)	or read_config('download','dir_path')
	#LOGPATH=read_config('download','logpath')
	firstpagenum=read_config('download','first_page_num')
	if firstpagenum=='':
		firstpagenum=2147483647
	else:
		firstpagenum=int(firstpagenum)
	projname=read_config('download','name')
	#determine first page
	if projname=='' or 0<projname<20:
		print_c('没有指定名称,按照快速筛选(built_in)选项下载')
		nextpage=HOMEURL+'/today/index'+BUILT_IN_SUFFIX[int(read_config('download','built_in'))]+'.html'
		namelist=[time.strftime('%Y-%m-%d %H-%M-%S',time.localtime()),'','']
		DIR_NAME=0#only this one
	else:
		if projname=='misc':#散图模式
			print_c('输入散图的年月，如201301，最早为200604:')
			yyyymm=raw_input()
			namelist=[(yyyymm[:4]+'年'+yyyymm[4:6]+'月 散图').decode('utf-8'),yyyymm,'']
			print namelist[0]
			projname='/misc/'+yyyymm
			entry='/index'+projname+'/images'
		else:
			namelist=parse_albumname(HOMEURL+'/index/'+projname)
			entry=parse_entry(HOMEURL+'/index/'+projname)
			if len(entry)>1:
				entry=entry[int(raw_input('> '))-1][0]
			else:
				entry=entry[0][0]
		print_c(fmttime()+'Collecting info for : '+namelist[0]+'/'+namelist[1]+'/'+namelist[2])
		filtername=read_config('download','filter')
		nextpage=HOMEURL+entry+'/index'+RATIO_SUFFIX[int(read_config(filtername,'ratio'))]+'.html'
	WORKINGDIR=(dir_path+'/'+((namelist[2]=='' and DIR_NAME=='2')and namelist[0] or namelist[int(DIR_NAME)]))\
	.decode('utf-8')
	if not os.path.exists(WORKINGDIR):
		os.mkdir(WORKINGDIR)
	pagenum=1
	while(nextpage!=None and pagenum<=firstpagenum):
		print '%sPage parsing started at %s' % (fmttime(),nextpage)
		nextpage=parse_pagelist(nextpage,pagenum)
		pagenum+=1
		#print PICLIST
	print fmttime()+'Parse finished.'
	print fmttime()+'Download started.'
	for i in range(len(PICLIST)):
		#time.sleep(GET_INTERVAL)#f*ck!!!
		basename=re.findall('/([A-Za-z0-9._]+)$',PICLIST[i]['full'])[0]
		filename=WORKINGDIR+'/'+basename
		#urllib.urlretrieve(PICLIST[i]['full'], filename,down_callback)  
		if os.path.exists(filename) and SKIP_EXIST=='1':#存在则跳过
				print '\bSkip '+basename+': Exists.'+' '*35
		elif os.path.exists(filename) and SKIP_EXIST=='2' and \
		urlget(PICLIST[i]['full'],True,retries,chunk,os.path.getsize(filename))=='SAME':
				print '\bSkip '+basename+': Same size exists.'+' '*25
		else:#不存在 或 2&&大小不符
			print '\b%sDownloading %3d/%3d images: %s ->' % (fmttime(),i+1,len(PICLIST),basename)
			#       |不知道为什么会空一格…所以加上退格…
			fileHandle=open(filename,'wb')
			fileHandle.write(urlget(PICLIST[i]['full'],True,retries,chunk))
			fileHandle.close()
	print '\n'+fmttime()+'Download finished.\n'+str(len(PICLIST))+' pictures saved under \"'+WORKINGDIR
	
def search():
	reslist=[]
	content=urlget('http://www.roame.net/index')
	#exp:<div class="l2"><a href="/index/kikis-delivery-service">魔女宅急便 - Kiki's Delivery Service</a></div>
	list=re.findall('<a href="/index/([a-z-]+)">(.+) - (.+)</a>',content)
	input=raw_input('Input your keyword:')
	if sys.platform=='win32':
		input=input.decode('gb2312')
	else:
		input=input.decode('utf-8')
	count=0
	#print list
	for i in range(len(list)):
		if re.search(input.encode('utf-8'), list[i][1], re.IGNORECASE) or \
		re.search(input, list[i][2], re.IGNORECASE):
			reslist.append((list[i][0],list[i][1],list[i][2]))
			count+=1
			try:
				print str(count)+'.'+list[i][1].encode('utf-8').decode('utf-8')+'('+list[i][2]+')'
			except UnicodeEncodeError:
				print str(count)+'.'+list[i][1].replace('〜','~').encode('utf-8').decode('utf-8')+\
				'('+list[i][2]+')'
	print str(count)+' result(s) found.'
	if count > 0:
		#try:
		input=int(raw_input('> '))
		if 0<input<count+1:
			write_config('download','name',reslist[int(input)-1][0])
			main()
		else:
			print_c('别乱按，熊孩子o(￣ヘ￣o＃) \n')
	#print reslist
def quick_filter():
	print_c('显示快速过滤选项：')
	print_c('0.所有最新\t10.今日下载排行\t15.大家刚下载的\n1.最新16:9\t11.一周下载排行\t16.随机八张图片\n2.最新16:10\t12.30天下载排行\t17.未分类画集\n3.最新4:3\t13.一周评分排行\t18.未分类散图\n4.最新5:4\t14.30天评分排行\n5.最新其他横向\n6.最新竖向\n7.最新等宽\t')
	try:
		input=int(raw_input('> '))
		if 0<=input<8 or 9<input<17:
			write_config('download','name','')
			write_config('download','built_in',input)
		elif input==17:
			write_config('download','name','misc-books')
		elif input==18:
			write_config('download','name','misc')
		else:
			raise Exception('', '')
		main()
	except ValueError:
		print_c('[なに？]σ(· ·?) \n')

def update():
	newver=urlget("https://raw.github.com/fffonion/RoameBot/master/version.txt")
	if newver!=__version__:
		print_c('花现新版本：'+newver)
		if os.path.split(sys.argv[0])[1].find('py')==-1:#is exe
			ext='.exe'
			print_c('二进制文件较大，你也可以直接从这里下载：http://t.cn/zYcYyQc')
			filename=os.getcwdu()+os.path.sep+'RoameBot.'+newver+ext
		else:
			ext='.py'
			filename=os.getcwdu()+os.path.sep+'RoameBot.py'
		fileHandle=open(filename,'wb')
		fileHandle.write(urlget("https://github.com/fffonion/RoameBot/raw/master/RoameBot"+ext,True,3,8))
		fileHandle.close()
		print_c('\n最新到了版本：'+newver)
	else:
		print_c('已经是最新版本啦更新控：'+__version__)
if __name__ == '__main__':  
	try:
		if not os.path.exists(os.getcwdu()+os.path.sep+'config.ini'):#first time
			init_config()
		init_proxy()
		reload(sys)
		sys.setdefaultencoding('utf-8')
		print_c('「ロアメボット。」'+__version__+'  ·ω·）ノ')
		while input !='5':
			print_c('1.搜索\n2.快速筛选\n3.继续上次任务\n4.更新\n5.退出\n')
			input=raw_input('> ')
			if input=='3':
				main()
			elif input=='1':
				search()
			elif input=='2':
				quick_filter()
			elif input=='4':
				update()
			elif input!='5':
				print_c('按错了吧亲╭(╯3╰)╮\n')
	except Exception,ex:
		print_c('啊咧，出错了( ⊙ o ⊙ )~ ('+str(ex)+')\n错误已经记载在roamebot.log中')
		f=open(os.getcwdu()+os.path.sep+'romaebot.log','a')
		f.write(fmttime()+'Stopped.\n')
		traceback.print_exc(file=f)
		#traceback.print_exc()
		f.flush()
		f.close()
print_c("按任意键退出亲~")
if sys.platform=='win32':
	os.system('pause>nul'.decode('utf-8'))