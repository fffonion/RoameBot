#!/usr/bin/env python
# -*- coding:utf-8 -*-
# A multitask downloader for roame.net
# Contributor:
#      fffonion		<fffonion@gmail.com>

__version__ = '2.0'

import urllib2,re,os,os.path as opath,time,ConfigParser,sys,traceback,socket,threading,Queue,random
PICQUEUE=Queue.Queue()
REPORTQUEUE=Queue.Queue()
FILTER={}
INDEXLIST=[]
#INITURL='http://www.roame.net/index/hakuouki-shinsengumi-kitan'
HOMEURL='http://www.roame.net'
LASTUPDATE=0
#常量
RATIO_SUFFIX=['','-wall','-16x10','-16x9','-4x3','-5x4','-oall','-wgth','-wlth','-weqh']
BUILT_IN_SUFFIX=['','-pic-16x9','-pic-16x10','-pic-4x3','-pic-5x4','-pic-wgth','-pic-wlth','-pic-weqh','','',\
				'-hotest-down','-hotest-weeklydown','-hotest-monthlydown','-hotest-score',\
				'-hotest-monthlyscore','-others-latest','-others-random']
THREAD_NAME=['Almond','Banana','Cherry','Damson','Emblic']
GET_INTERVAL=0.1
THREADS=5

THREAD_PROGRESS=[[0,0,0,0,0]]*THREADS#已下载，总大小，开始时间，总下载量，总下载大小
LOGPATH='roamebot.log'
COOKIE=['uid=149448; upw=a3119b10b8cb23e19053e99b82bb4ea4; cmd=CY%408Tl8Z9GjXgp6p2UhqvJTHo3D7sVFpC;',\
	'uid=149449; upw=a3119b10b8cb23e19053e99b82bb4ea4; cmd=JP2SkSeeeb3hsrk7CST3XxmhpuY4Gszt9;',\
	'uid=149458; upw=a3119b10b8cb23e19053e99b82bb4ea4; cmd=JxKBgjlypSuBk4zkhJ3BtNrjdDUDq6yTb;',\
	'uid=149459; upw=a3119b10b8cb23e19053e99b82bb4ea4; cmd=JuYHdgPPyJQsh59JjaIUWFfkiWPmvBepi;',\
	'uid=149460; upw=a3119b10b8cb23e19053e99b82bb4ea4; cmd=JwGe6d%4022UwKg2sYCjUsvzdrZZIp9oFDH;']
def chunk_report(bytes_got, chunk_size, total_size,init_time):
	'''
	A hook for progress callback
	'''
	percent = float(bytes_got) / total_size
	percent = round(percent*100, 2)
	eta=time.strftime('%M:%S', time.localtime((time.time()-init_time)*(100-percent)/percent))#剩余时间
	proglength=30#进度条长度
	progressbar='#'*(proglength*int(percent)/100)+' '*(proglength-proglength*int(percent)/100)#计算进度条
	backspace='\b'*140#同一行打印的退格
	print "%4.1f%% [%s]     %5d/%5dKB   %s ETA%s" % (percent,progressbar,bytes_got/1024,total_size/1024, eta,backspace),
	if bytes_got >= total_size:#完成时
		print backspace,	
def urlget(src,getimage=False,retries=3,chunk_size=8,downloaded=-1,referer='',cookieid=-1):
	'''
	urllib2 download module
	'''
	#print src
	global REPORTQUEUE
	prompt=THREAD_NAME[cookieid]+': '
	try:
		#构造request
		req = urllib2.Request(src)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4')
		#req.add_header('Referer', referer)
		if cookieid!=-1:
			req.add_header('Cookie', COOKIE[cookieid])
		#打开回复
		resp = urllib2.urlopen(req)
		#resp.info()
		content=''
		total_size=None
		sleep_retry=1
		#处理内容
		#urlget会下载网页或者图片
		#网页抓得快不会挂掉；图片抓得快会返回text/html，url错误会返回text/html，内容为oops(2)，url过期会返回8843字节的防盗链图
		if getimage:#下载图片的话（或者在线更新
			while total_size==None:
				total_size=resp.info().getheader('Content-Length')
				time.sleep(GET_INTERVAL*sleep_retry)#服务器太捉鸡……睡一觉
				if resp.info().getheader('Content-Type').strip()=='text/html':
					if sleep_retry>27:#最多睡三次
						total_size='-1'#链接错误flag
					else:
						REPORTQUEUE.put(fmttime()+prompt+'Got plain content. Retrying in '+str(GET_INTERVAL*sleep_retry)+'s.')
						sleep_retry*=3
			total_size = int(total_size.strip())
			if total_size<=8843:#链接错误=-1或过期=8843
				REPORTQUEUE.put(fmttime()+prompt+'Url expired or broken. Reparsing from referer page.')
				content=urlget(parse_fullsize(referer),getimage,retries,chunk_size,downloaded,referer,cookieid)
			else:#正常下载
				#用头信息直接判断是否已下载
				if downloaded!=-1:
					if total_size==downloaded:
						return 'SAME'
					else:
						return 'NOT-SAME'
				#初始化变量
				bytes_got = 0
				init_time=time.time()
				#开始chunk read
				while 1:
					chunkrand=chunk_size*random.randint(800,1248)
					chunk = resp.read(chunkrand)
					content+=chunk
					bytes_got += len(chunk)
					if not chunk:#完成
						break
					if cookieid!=-1:
						global THREAD_PROGRESS
						THREAD_PROGRESS[cookieid-1][0]=bytes_got
						THREAD_PROGRESS[cookieid-1][1]=total_size
						THREAD_PROGRESS[cookieid-1][4]+=chunkrand
					else:#m不指定则是在在线更新
						chunk_report(bytes_got, chunk_size, total_size,init_time)
				#content=chunk_read(resp, chunk*1024,chunk_report)
		else:#直接读取
			content = resp.read()#.decode('utf-8')
		#返回上级
		return content
	except (urllib2.URLError,urllib2.HTTPError),e:#错误处理 
 		print e.code
 		if retries>0:#重试处理
	 		#if isinstance(e.reason, socket.timeout):
	 		print fmttime()+prompt+'Error['+str(e.code)+']',
	 		if e.code==10060:#超时
				print 'Connection timed out. Retrying '+str(retries)+' times.'
			elif  e.code>=400:#客户端错误或服务器错误
				print 'URL broken. Re-parsing from referer page.'
				src=parse_fullsize(referer)
			return urlget(src,getimage,retries-1,chunk_size,downloaded,referer,cookieid)
		else:
				print 'Failed on '+src
				return None
		
       
def print_c(str):
	'''
	UTF-8 print module
	'''
	print(normstr(str.decode('utf-8')))

def normstr(str,errors='ignore'):
	if sys.platform=='win32':
		return str.encode('gbk',errors)
	else:
		return str.encode('utf-8',errors)
def fmttime():
	'''
	Return time like [2013-02-13 16:23:21]
	'''
	return '['+time.strftime('%Y-%m-%d %X',time.localtime())+'] '

class getimgthread(threading.Thread):
	def __init__(self,threadname,workingdir,skip_exist,retries=3,chunk_size=8,downloaded=-1):
		threading.Thread.__init__(self, name=threadname)
		self.id=int(self.getName())
		self.workingdir=workingdir
		self.skip_exist=skip_exist
		self.retries=retries
		self.chunk_size=chunk_size
		self.downloaded=downloaded
		self.propmt=THREAD_NAME[self.id-1]+': '
		global THREAD_PROGRESS
		THREAD_PROGRESS[self.id-1]=[0]*5
		
	def tprint(self,str):
		global REPORTQUEUE
		if THREADS==1:
			REPORTQUEUE.put(str)
		else:
			print(str)
			
	def run(self):
		global THREAD_PROGRESS
		REPORTQUEUE.put(fmttime()+self.propmt+'Started.')
		while not PICQUEUE.empty():
			self.src=PICQUEUE.get()
			basename=re.findall('/([A-Za-z0-9._]+)$',self.src['full'])[0]#切割文件名
			filename=self.workingdir+opath.sep+basename
			#urlget(src,getimage=False,retries=3,chunk_size=8,downloaded=-1,referer='',cookieid=-1):
			if opath.exists(filename) and self.skip_exist=='1':#存在则跳过
					self.tprint(fmttime()+self.propmt+'Skip '+basename+': Exists.'+' '*10)
			elif opath.exists(filename) and self.skip_exist=='2' and \
			urlget(self.src['full'],True,self.retries,self.chunk_size,opath.getsize(filename),\
				self.src['referpage'],self.id-1)=='SAME':
					self.tprint(fmttime()+self.propmt+'Skip '+basename+': Same size.'+' '*5)
					THREAD_PROGRESS[self.id-1][3]+=1
			else:#不存在 或 2&&大小不符
				self.tprint(fmttime()+self.propmt+'Start '+basename+'.')
				#print '\b%sDownloading %3d/%3d images: %s ->' % (fmttime(),i+1,PICQUEUE.qsize(),basename)
				#       |不知道为什么会空一格…所以加上退格…
				#设置监视起始点
				THREAD_PROGRESS[self.id-1][2]=time.time()
				#保存到文件
				fileHandle=open(filename,'wb')
				fileHandle.write(urlget(self.src['full'],True,self.retries,self.chunk_size,-1,\
									self.src['referpage'],THREADS==1 and -1 or self.id-1))
				fileHandle.close()
				self.tprint(fmttime()+self.propmt+'Finish '+basename+'.')
				THREAD_PROGRESS[self.id-1][3]+=1
		THREAD_PROGRESS[self.id-1][2]=-1#退出标识
		self.tprint(fmttime()+self.propmt+'Exit~')
		
class reportthread(threading.Thread):
	def __init__(self,threadname='Reportter'):
		threading.Thread.__init__(self, name=threadname)
	def run(self):
		#THREAD_PROGRESS=[[0,0,0,0]]*THREADS#已下载，总大小，开始时间
		init_time=time.time()
		backspace='\b'*140
		flush=' '*67
		livethread=THREADS
		global REPORTQUEUE
		lastdownsize=0
		sleeptime=0.2
		while livethread>0:
			downcount=0
			queuesize=0
			downloadsize=0
			while not REPORTQUEUE.empty():
				print(flush+backspace+REPORTQUEUE.get())
			livethread=THREADS
			for i in range(THREADS):
				downcount+=THREAD_PROGRESS[i][3]
				queuesize+=THREAD_PROGRESS[i][1]
				downloadsize+=THREAD_PROGRESS[i][4]
				if THREAD_PROGRESS[i][2]==-1:
					livethread-=1
			#eta=time.strftime('%M:%S', time.localtime((time.time()-init_time)*(100-percent)/percent))
			elapse=time.strftime('%M:%S',time.localtime(time.time()-init_time))
			print "\bThread %d/%d  Remain %3d/%3d  Queued %3d/%3d   %3.1fKB/s    %s  %s" % (livethread,THREADS,\
				PICQUEUE.qsize(),downcount+PICQUEUE.qsize()+livethread,downloadsize/1024,queuesize/1024,\
				(downloadsize-lastdownsize)/sleeptime/1024,elapse,backspace),
			lastdownsize=downloadsize
			time.sleep(sleeptime)
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
	albumname_legal=[]
	for i in range(len(albumname[0])):
		albumname_legal.append(albumname[0][i].replace('/',' ').replace('\\',' ').replace(':',' '))
	return albumname_legal

def parse_entry(url):
	'''
	Return entry list
	'''
	content=urlget(url)
	entries=[]
	#exp <strong style="margin:0px;padding:0px">中二病也要谈恋爱 BD VOL.1</strong>
	allentries=re.findall('<h2>(.*?)</strong>',content,re.DOTALL)
	for i in range(len(allentries)):
		entries.append([re.findall('href="(.+)">',allentries[i])[0],\
					re.findall('2px">(\d+)</span',allentries[i])[0],
					re.findall('0px">(.+)$',allentries[i])[0]])
		print_c('入口'+str(i+1)+': '+entries[-1][2].decode('utf-8')+' ('+str(entries[-1][1])+'p)')
	return entries

def parse_pagelist(url,pagenum,mode=0):
	'''
	Return pic list, elem is dict
	'''
	global PICQUEUE
	up_to_date=False
	today_mode=False
	#pic_structure={'index':0,'thumb':'','full':'','width':0,'height':0,'length':0}
	content=urlget(url)
	singlepic=re.findall('/h[23]>(.*?)<div',content,re.DOTALL)#singlepic 包含 thumb and full-size page url
	#<div style="color:#456"><span style="color:#abc;font-size:10px">by</span> <u>EUREKASEVEN</u></div>
	picupload=re.findall('font-size:10px">by</span> <u>(.+)</u>',content)
	#<div style="color:#456">3天前（2013-02-16 22:30）</div>
	picdate=re.findall('前（(.+)）</div>',content)
	picinfo=re.findall('font-size:12px;font-weight:bold.*\">(.+) - ([0-9.]+)([A-Z]+)</div',content)#格式和大小
	if picinfo==[]:#有两种情况，以下对today模式
		picinfo=re.findall('r:#789">([0-9.]+)([A-Z]+)</span',content)
		today_mode=True
	picsize=re.findall('<strong>(\d+)×(\d+)</strong>',content)
	#具体处理
	for i in range(len(singlepic)):	
		if not today_mode:
			if LASTUPDATE>time.mktime(time.strptime(picdate[i],'%Y-%m-%d %H:%M')):#已到时间分割点
				up_to_date=True
				break
		#图片文件长度
		if(picinfo[i][-1]=='MB'):
			piclength=float(picinfo[i][-2])*1024#float化防止变int
		else:
			piclength=picinfo[i][-2]
		#测试filter
		if FILTER['min_width']<=float(picsize[i][0])<=FILTER['max_width'] and \
		FILTER['min_length']<=float(picsize[i][1])<=FILTER['max_length'] and \
		FILTER['min_size']<=float(piclength)<=FILTER['max_size'] and (not picupload[i] in FILTER['banned_uploader']):
			picelem={'index':0,'thumb':'','referpage':'','full':'','height':0,'width':0,'length':0,'format':''}
			picelem['index']=i+(pagenum-1)*8
			fullsizepageurl=re.findall('href=\"(.+)\"><img',singlepic[i])[0]#原图url
			picelem['referpage']=HOMEURL+fullsizepageurl.replace(HOMEURL,'')
			picelem['full']=parse_fullsize(picelem['referpage'])
			picelem['thumb']=re.findall('src=\"(.+)\"\/>',singlepic[i])[0]#缩略图url
			picelem['width']=picsize[i][0]#图宽
			picelem['height']=picsize[i][1]#图高
			picelem['length']=piclength
			picelem['format']=len(picinfo[i])==2 and 'UNKNOWN' or picinfo[i][0]#today模式没有文件格式
			PICQUEUE.put(picelem)
	nextpage=re.findall('title="下一页" href="(.+)" style=',content)#下一页
	if nextpage==[] or up_to_date:#最后一页或已把更加新的处理完
		return None
	else:
		return HOMEURL+nextpage[0]
	
def parse_fullsize(url):
	'''
	Return image url
	'''
	content=urlget(url)
	deeperpage=re.findall('darlnks">.+index.html.+href="(.*?)" style.+display:block',content,re.DOTALL)#goto download page
	content=urlget(deeperpage[0])
	picurl=re.findall('src="(.+)" style="background',content)
	return picurl[0]

#def down_callback(saved,blocksize,total):
#	x = 100.0 * saved * blocksize / total  
#	if x > 100:  
#	 	x = 100 
#	print '%.2f%%' % x

def read_config(sec,key):
	'''
	Read config from file
	'''
	cf=ConfigParser.ConfigParser()
	cf.read(os.getcwdu()+opath.sep+'config.ini')
	val=cf.get(sec, key)
	if val=='':
		return ''
	else:
		return val

def write_config(sec,key,val):
	'''
	Write config to file
	'''
	cf=ConfigParser.ConfigParser()
	cf.read(os.getcwdu()+opath.sep+'config.ini')
	cf.set(sec, key,val)
	cf.write(open(os.getcwdu()+opath.sep+'config.ini', "w"))

def read_timestamp(workingdir,ratio):
	'''
	Found earlist updated ratio
	'''
	global LASTUPDATE
	LASTUPDATE=0
	filename = workingdir+opath.sep+'.roamepast'
	if opath.exists(filename):
		f=open(filename,'r')
		for line in f:
			lst=line.split(',')
			if lst[0] == str(ratio):
				LASTUPDATE=long((lst[1][-1]=='\n' and lst[1][:-1] or lst[1]).strip())#这个ratio的更新时间
		f.close()
		return True
	else:
		return False
	
		
def write_timestamp(working_dir,ratio,projname):	
	filename = working_dir+opath.sep+'.roamepast'
	f=open(filename,'w')#覆盖写入
	f.write(projname+',0\n')
	for i in range(len(ratio)):
		f.write(ratio[i]+','+str(long(time.time()))+'\n')
	f.flush()
	f.close()

def load_filter(filtername):
	global FILTER
	cf=ConfigParser.ConfigParser()
	cf.read(os.getcwdu()+opath.sep+'config.ini')
	FILTER={'max_length':2147483647,'max_width':2147483647,'min_length':0,'min_width':0,\
		'max_size':2147483647,'min_size':0,'banned_uploader':[]}
	for o in FILTER:
		if cf.has_option(filtername, o):
			val=cf.get(filtername, o)
			if val!='':
				if o=='banned_uploader':
					FILTER[o]=val.decode('gbk').encode('utf-8').split('|')
				else:
					FILTER[o]=float(val)
	
def first_run():
	'''
	First run, initialize config.ini, show readme
	'''
	filename = os.getcwdu()+opath.sep+'config.ini'
	f=file(filename,'w')
	f.write('[download]\nskip_exist = 2\ndownload_when_parse = 1\ntimeout = 10\nchunksize = 8\nretries = 3\
	\ndir_name = 2\ndir_path = \nname = hyouka\nthreads = 3\ndir_pref = \ndir_suff = \nbuilt_in = 21\nfilter = filter_0\
	\nfirst_page_num = \nproxy = \nproxy_name = \nproxy_pswd = \n\n[filter_0]\nratio = 1|7\
	\nmax_length = 	\nmax_width = \nmin_length = \nmin_width = \nmax_size = \nmin_size = \nbanned_uploader = \n')
	f.flush()
	f.close()
	print_c('''【首次运行】
直接按照菜单项输入数字即可。
“继续上次任务”选项，可以用来：
1.恢复上次已中断的任务（直接输入3即可）
2.检查以前下载的番组有无新壁纸发布，并下载新壁纸（这需要读取上次目录下的.roamepast文件，须确保保存目录dir_path未变化）。

默认仅会下载壁纸尺寸和长尺寸的图片。如要下载其他尺寸，请编辑config.ini中的ratio为0或其他值。
可以用 | 分割指定多个值。

- 默认下载线程为3，可自行修改threads项，最大为5
- 根据官方帖子，普通用户下载凌晨5点最快，晚间21点最慢(http://www.roame.net/forum/office/policy)
- 完整说明请见：https://github.com/fffonion/RoameBot/blob/master/Readme.md
- 图文说明在这里：http://www.gn00.com/thread-220277-1-1.html

·ω·）ノ	fffonion@gmail.com
2013-2-25

按任意键继续……
	''')
	input=raw_input('')
	
def init_proxy():
	'''
	Install proxy opener
	'''
	if read_config('download','proxy')!='':
		proxy_support = urllib2.ProxyHandler({'http':'http://['+read_config('download','proxy_name')\
											+']:['+read_config('download','proxy_pswd')+']@['\
											+read_config('download','proxy')+']'})
		opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
		urllib2.install_opener(opener)
		
def load_remote_picqueue(nextpage,firstpagenum,workingdir,ratiolist):
	'''
	Remote PICQUEUE parsing
	'''
	#global PICQUEUE
	#页面处理并得到所有图片URL，位于全局变量PICQUEUE中
	pagenum=1
	for j in range(len(nextpage)):#nextpage列表个数等于比例个数
		if read_timestamp(workingdir,ratiolist[j])==True:
			print fmttime()+'Read time-stamp info from file.'
		while(nextpage[j]!=None and pagenum<=firstpagenum):
			print '%sPage parsing started at %s' % (fmttime(),nextpage[j])
			nextpage[j]=parse_pagelist(nextpage[j],pagenum)
			pagenum+=1
	#保存到文件
	file=open(workingdir+opath.sep+'.roameproject','w')
	queindex=1
	while queindex <= PICQUEUE.qsize():
		#print queindex,PICQUEUE.qsize()
		picelem=PICQUEUE.get()
		PICQUEUE.put(picelem)
		file.write(str(picelem['index'])+','+picelem['thumb']+','+picelem['referpage']+','+picelem['full']+','\
				+str(picelem['height'])+','+str(picelem['width'])+','+str(picelem['length'])+','\
				+picelem['format']+'\n')
		queindex+=1
	file.close()
	
def load_local_picqueue(projfile_path):
	'''
	read PICQUEUE from .roameproject
	'''
	global PICQUEUE
	file=open(projfile_path,'r')
	for line in file:
		list=(line[-1]=='\n' and line[:-1] or line).split(',')
		PICQUEUE.put({'index':int(list[0]),'thumb':list[1],'referpage':list[2],'full':list[3],'height':int(list[4]),\
					'width':int(list[5]),'length':float(list[6]),'format':list[7]})
	file.close()
	return PICQUEUE.qsize()
	
#main entry
def main():
	#读取并设置变量
	timeout=read_config('download','timeout')
	socket.setdefaulttimeout(int(timeout))
	chunk=int(read_config('download','chunksize'))
	retries=int(read_config('download','retries'))
	skip_exist=read_config('download','skip_exist')
	dir_name=read_config('download','dir_name')
	dir_path=read_config('download','dir_path')=='' and opath.abspath(os.curdir)	or read_config('download','dir_path')
	dir_pref=read_config('download','dir_pref')
	dir_suff=read_config('download','dir_suff')
	#LOGPATH=read_config('download','logpath')
	global THREADS
	THREADS=int(read_config('download','threads'))
	firstpagenum=read_config('download','first_page_num')
	if firstpagenum=='':#未指定默认为无限制
		firstpagenum=2147483647
	else:
		firstpagenum=int(firstpagenum)
	projname=read_config('download','name')
	filtername=read_config('download','filter')
	load_filter(filtername)
	ratiolist=read_config(filtername,'ratio').split('|')
	global PICQUEUE,FILTER,LASTUPDATE
	PICQUEUE=Queue.Queue()
	nextpage=[]
	
	###################开始预处理
	#决定首页
	if projname=='' or 0<projname<20:#today模式
		print_c('没有指定名称,按照快速筛选(built_in)选项下载')
		nextpage.append(HOMEURL+'/today/index'+BUILT_IN_SUFFIX[int(read_config('download','built_in'))]+'.html')
		namelist=[time.strftime('%Y-%m-%d %H-%M',time.localtime()),'','']
		dir_name=0#only this one
	else:#正常模式OR散图模式
		if projname=='misc':#散图模式
			print_c('输入散图的年月，如201301，最早为200604:')
			yyyymm=raw_input()
			namelist=[(yyyymm[:4]+'年'+yyyymm[4:6]+'月 散图').decode('utf-8'),yyyymm,'']
			print namelist[0]
			projname='/misc/'+yyyymm
			entry='/index'+projname+'/images'
		else:#正常模式
			namelist=parse_albumname(HOMEURL+'/index/'+projname)
			entry=parse_entry(HOMEURL+'/index/'+projname)
			if len(entry)>1:
				entry=entry[int(raw_input('> '))-1][0]
			else:
				entry=entry[0][0]
		print_c(fmttime()+'Collecting info for : '+namelist[0]+'/'+namelist[1]+'/'+namelist[2])
		#处理比例过滤器,依次构造
		for r in range(len(ratiolist)):
			nextpage.append(HOMEURL+entry+'/index'+RATIO_SUFFIX[int(ratiolist[r].strip())]+'.html')
	if namelist[2]==''and dir_name=='2':#选日文而日文不存在则改选中文
		dir_name='0'
	for i in range(3):
		working_dir=(dir_path+opath.sep+dir_pref+namelist[i]+dir_suff).decode('utf-8')
		if opath.exists(working_dir) and namelist[i]!='':#目录已存在
			print_c(fmttime()+'Former folder exists. Use that one.')
			break#使用之前已使用过的目录
		else:#目录不存在或没有日文名（而且未被选择，否则2已=0） 
			if int(dir_name)==i:#第一次任务
				os.mkdir(working_dir)
				break
	#working_dir=(dir_path+opath.sep+dir_pref+namelist[int(dir_name)]+dir_suff).decode('utf-8')#保存目录
	print_c(fmttime()+'Working directory is: '+working_dir)
	###################开始主处理
	projfile_path=(working_dir+opath.sep+'.roameproject').decode('utf-8')
	if opath.exists(projfile_path) and opath.getsize(projfile_path)!=0:
		load_local_picqueue(projfile_path)
		print fmttime()+'Load download progress from file. (Got '+str(PICQUEUE.qsize())+'p)'
	else:
		load_remote_picqueue(nextpage,firstpagenum,working_dir,ratiolist)
		print fmttime()+'Parse finished. (Got '+str(PICQUEUE.qsize())+'p)'
	print fmttime()+'Download started.'+(THREADS==1 and '(Single Thread)' or '('+str(THREADS)+' Threads)')
	#图片下载
	#time.sleep(GET_INTERVAL)#f*ck!!!
	#(self,threadname,workingdir,skip_exist,retries=3,chunk_size=8,downloaded=-1):
	threadlist=[getimgthread('1',working_dir,skip_exist,retries,chunk,-1),\
			getimgthread('2',working_dir,skip_exist,retries,chunk,-1),\
			getimgthread('3',working_dir,skip_exist,retries,chunk,-1),\
			getimgthread('4',working_dir,skip_exist,retries,chunk,-1),\
			getimgthread('5',working_dir,skip_exist,retries,chunk,-1)]
	for i in range(THREADS):
		threadlist[i].start()
	if THREADS>1:
		report=reportthread()
		report.start()
	for i in range(THREADS):
		threadlist[i].join()
	if THREADS>1:
		report.join()
	print '\n'+fmttime()+'Download finished.\n'+str(PICQUEUE.qsize())+' pictures saved under \"'+working_dir
	os.remove(working_dir+opath.sep+'.roameproject')
	write_timestamp(working_dir,ratiolist,projname)
	
def search():
	'''
	Search module
	'''
	urllist=[]
	global INDEXLIST
	if INDEXLIST==[]:
		#从索引页处理所有名称
		content=urlget('http://www.roame.net/index')
		#exp:<div class="l2"><a href="/index/kikis-delivery-service">魔女宅急便 - Kiki's Delivery Service</a></div>
		#另三种：Vividred Operation - ，TYPE-MOON，GOSICK(6 pcs) 尼玛老子就为了这六个想了好久正则！！
		#list=re.findall('<a href="/index/([0-9a-z-]+)">(.+)[ -]+(.*)</a>',content):[ -]+无法匹配那6个，[ -]*无法分割字符串
		#难道只能匹配好之后再分割么www好没劲我放弃了QAQ
		#原来list=re.findall('<a href="/index/([0-9a-z-]+)">(.+)</a>',content)
		#不！我不会向不讲规范的站长低头的！！
		#只要使用预处理大法并且第二、三个匹配变成非贪婪即可！这样>GOSICK</a>变成>GOSICK - </a啦~我怎么就那么笨呢wwwww
		content=content.replace('</a',' - </a')
		INDEXLIST=re.findall('<a href="/index/([0-9a-z-]+)">(.*?) - (.*?)( - )?</a',content)
		#debug用
		'''list2=re.findall('<a href="/index/([0-9a-z-]+)">(.+)[ -]*(.*)</a>',content)
		print len(INDEXLIST),len(list2)
		offset=0
		for i in range(1225):
			if INDEXLIST[i-offset][0]!=list2[i][0]:
				print list2[i]
				offset+=1
		return'''
	#询问输入
	input=raw_input(normstr('输入关键字: '))
	if sys.platform=='win32':
		input=input.decode('gb2312')
	else:
		input=input.decode('utf-8')
	count=0
	#顺序查找并分割打印
	for i in range(len(INDEXLIST)):
		if re.search(input.encode('utf-8'), INDEXLIST[i][1], re.IGNORECASE) or \
		re.search(input, INDEXLIST[i][2], re.IGNORECASE):
			urllist.append(INDEXLIST[i][0])
			count+=1
			if INDEXLIST[i][2]!='':
				print normstr((str(count)+'.'+INDEXLIST[i][1]+'('+INDEXLIST[i][2]+')').decode('utf-8','ignore'))
			else:
				print normstr((str(count)+'.'+INDEXLIST[i][1]).decode('utf-8','ignore'))
	print_c('找到'+str(count)+'个结果 ㄟ( ▔, ▔ )ㄏ')
	if count > 0:
		#try:
		input=int(raw_input('> '))
		if 0<input<count+1:
			write_config('download','name',urllist[int(input)-1])
			main()
		else:
			print_c('别乱按，熊孩子o(￣ヘ￣o＃) \n')
	
def quick_filter():
	'''
	Today mode/Quick filter/Unsorted
	'''
	print_c('显示快速过滤选项：')
	print_c('0.所有最新\t10.今日下载排行\t15.大家刚下载的\n1.最新16:9\t11.一周下载排行\t16.随机八张图片\n2.最新16:10\t12.30天下载排行\n3.最新4:3\t13.一周评分排行\t17.未分类画集\n4.最新5:4\t14.30天评分排行\t18.未分类散图\n5.最新其他横向\n6.最新竖向\n7.最新等宽')
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
	except ValueError:#熊孩子没有输入数字
		print_c('[なに？]σ(· ·?) \n')

def update():
	'''
	Online update
	'''
	newver=urlget("https://raw.github.com/fffonion/RoameBot/master/version.txt")
	notification=urlget("https://raw.github.com/fffonion/RoameBot/master/notification.txt")
	if newver!=__version__:
		print_c('花现新版本Σ( ° △ °|||):'+newver)
		if opath.split(sys.argv[0])[1].find('py')==-1:#is exe
			ext='.exe'
			print_c('二进制文件较大，你也可以直接从这里下载：http://t.cn/zYcYyQc')
			filename=os.getcwdu()+opath.sep+'RoameBot.'+newver+ext
		else:
			ext='.py'
			#filename=os.getcwdu()+opath.sep+'RoameBot.py'
			filename=sys.argv[0]
		fileHandle=open(filename,'wb')
		fileHandle.write(urlget("https://github.com/fffonion/RoameBot/raw/master/RoameBot"+ext,True,3,8))
		fileHandle.close()
		print_c('\n更新到了版本：'+newver+'\n[注意事项]\n'+notification)
	else:
		print_c('已经是最新版本啦更新控：'+__version__)
		
if __name__ == '__main__':  
	try:
		if not opath.exists(os.getcwdu()+opath.sep+'config.ini'):#first time
			first_run()
		init_proxy()
		#重设默认编码
		reload(sys)
		sys.setdefaultencoding('utf-8')
		print_c('「ロアメボット。」'+__version__+'  ·ω·）ノ')
		#if len(sys.argv)==1:
		#菜单
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
				print_c('按错了吧亲∑(っ °Д °;)\n')
			
	except Exception,ex:
		print_c('啊咧，出错了_(:з」∠)_ ('+str(ex)+')\n错误已经记载在'+LOGPATH+'中')
		f=open(os.getcwdu()+opath.sep+LOGPATH,'a')
		f.write(fmttime()+'Stopped.\n')
		traceback.print_exc(file=f)
		traceback.print_exc()
		f.flush()
		f.close()
if sys.platform=='win32':
	print_c("按任意键退出亲~")
	os.system('pause>nul'.decode('utf-8'))