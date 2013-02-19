#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Contributor:
#      fffonion		<fffonion@gmail.com>

__version__ = '1.5'

import urllib2,re,os,os.path as opath,time,ConfigParser,sys,traceback,socket
PICLIST=[]
#INITURL='http://www.roame.net/index/hakuouki-shinsengumi-kitan'
HOMEURL='http://www.roame.net'
RATIO_SUFFIX=['','-wall','-16x10','-16x9','-4x3','-5x4','-oall','-wgth','-wlth','-weqh']
BUILT_IN_SUFFIX=['','-pic-16x9','-pic-16x10','-pic-4x3','-pic-5x4','-pic-wgth','-pic-wlth','-pic-weqh','','',\
				'-hotest-down','-hotest-weeklydown','-hotest-monthlydown','-hotest-score',\
				'-hotest-monthlyscore','-others-latest','-others-random']
GET_INTERVAL=0.1
LOGPATH='roamebot.log'
#urllib2 HOOk 基于 http://stackoverflow.com/questions/2028517/python-urllib2-progress-hook
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

def urlget(src,getimage=False,retries=3,chunk_size=8,downloaded=-1,referer=''):
	'''
	urllib2 download module
	'''
	#print src
	try:
		#构造request
		req = urllib2.Request(src)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4')
		#req.add_header('Referer', referer)
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
					if sleep_retry>8:#最多睡三次
						total_size='-1'#链接错误flag
					else:
						print(fmttime()+'Got plain content. Retrying in '+str(GET_INTERVAL*sleep_retry)+'s.')
						sleep_retry*=3
			total_size = int(total_size.strip())
			if total_size<=8843:#链接错误=-1或过期=8843
				print fmttime()+'Url expired or broken. Reparsing from referer page.'
				content=urlget(parse_fullsize(referer),getimage,retries,chunk_size,downloaded,referer)
			else:#正常下载
				#用头信息直接判断是否已下载
				if total_size==downloaded:
					return 'SAME'
				#初始化变量
				chunk_size*=1024
				bytes_got = 0
				init_time=time.time()
				#开始chunk read
				while 1:
					chunk = resp.read(chunk_size)
					content+=chunk
					bytes_got += len(chunk)
					if not chunk:#完成
						break
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
	 		print fmttime()+'Error['+str(e.code)+']',
	 		if e.code==10060:#超时
				print 'Connection timed out. Retrying '+str(retries)+' times.'
			elif  e.code>=400:#客户端错误或服务器错误
				print 'URL broken. Re-parsing from referer page.'
				src=parse_fullsize(referer)
			return urlget(src,getimage,retries-1,chunk_size,downloaded,referer)
		else:
				print 'Failed on '+src
				return None
		
		
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
	'''
	UTF-8 print module
	'''
	print normstr(str.decode('utf-8'))

def normstr(str,errors='ignore'):
	if sys.platform=='win32':
		return str.encode('gbk',errors)
	else:
		return str.encode('utf-8',errors)
	
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
	global PICLIST
	#pic_structure={'index':0,'thumb':'','full':'','width':0,'height':0,'length':0}
	content=urlget(url)
	singlepic=re.findall('/h[23]>(.*?)<div',content,re.DOTALL)#singlepic 包含 thumb and full-size page url
	picinfo=re.findall('font-size:12px;font-weight:bold.*\">(.+) - ([0-9.]+)([A-Z]+)</div',content)
	if picinfo==[]:#有两种情况，以下对today模式
		picinfo=re.findall('r:#789">([0-9.]+)([A-Z]+)</span',content)
	picsize=re.findall('<strong>(\d+)×(\d+)</strong>',content)
	#具体处理
	for i in range(len(singlepic)):	
		PICLIST.append({'index':0,'thumb':'','referpage':'','full':'','height':0,'width':0,'length':0,'format':''})
		PICLIST[-1]['index']=i+(pagenum-1)*8
		fullsizepageurl=re.findall('href=\"(.+)\"><img',singlepic[i])[0]#原图url
		PICLIST[-1]['referpage']=HOMEURL+fullsizepageurl.replace(HOMEURL,'')
		PICLIST[-1]['full']=parse_fullsize(PICLIST[-1]['referpage'])
		PICLIST[-1]['thumb']=re.findall('src=\"(.+)\"\/>',singlepic[i])[0]#缩略图url
		PICLIST[-1]['width']=picsize[i][0]#图宽
		PICLIST[-1]['height']=picsize[i][1]#图高
		#图片文件长度
		if(picinfo[i][-1]=='MB'):
			PICLIST[-1]['length']=float(picinfo[i][-2])*1024#float化防止变int
		else:
			PICLIST[-1]['length']=picinfo[i][-2]
		PICLIST[-1]['format']=len(picinfo[i])==2 and 'UNKNOWN' or picinfo[i][0]#today模式没有文件格式
	nextpage=re.findall('title="下一页" href="(.+)" style=',content)#下一页
	if (nextpage==[]):#最后一页
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

def fmttime():
	'''
	Return time like [2013-02-13 16:23:21]
	'''
	return '['+time.strftime('%Y-%m-%d %X',time.localtime())+'] '
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

def init_config():
	'''
	First run, initialize config.ini
	'''
	filename = os.getcwdu()+opath.sep+'config.ini'
	f=file(filename,'w')
	f.write('[download]\nskip_exist = 2\ndownload_when_parse = 1\ntimeout = 10\nchunksize = 8\nretries = 3\ndir_name = 2\ndir_path = \nname = hyouka\ndir_pref = \ndir_suff = \nbuilt_in = 21\nfilter = filter_0\nfirst_page_num = \nproxy = \nproxy_name = \nproxy_pswd = \n[filter_0]\nratio = 1|7\nmax_length = \nmax_width = \nmin_length = \nmin_width = \nmax_size = \nmin_size = ')
	f.flush()
	f.close() 

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
		
def load_remote_piclist(nextpage,firstpagenum,projfile_path):
	'''
	Remote PICLIST parsing
	'''
	#global PICLIST
	#页面处理并得到所有图片URL，位于全局变量PICLIST中
	pagenum=1
	for j in range(len(nextpage)):
		while(nextpage[j]!=None and pagenum<=firstpagenum):
			print '%sPage parsing started at %s' % (fmttime(),nextpage[j])
			nextpage[j]=parse_pagelist(nextpage[j],pagenum)
			pagenum+=1
			#print PICLIST
	#保存到文件
	file=open(projfile_path,'w')
	for i in range(len(PICLIST)):
		file.write(str(PICLIST[i]['index'])+','+PICLIST[i]['thumb']+','+PICLIST[i]['referpage']+','+PICLIST[i]['full']+','\
				+str(PICLIST[i]['height'])+','+str(PICLIST[i]['width'])+','+str(PICLIST[i]['length'])+','\
				+PICLIST[i]['format']+'\n')
	file.close()
	
def load_local_piclist(projfile_path):
	'''
	read PICLIST from .roameproject
	'''
	global PICLIST
	file=open(projfile_path,'r')
	for line in file:
		list=line.split(',')
		PICLIST.append({'index':int(list[0]),'thumb':list[1],'referpage':list[2],'full':list[3],'height':int(list[4]),\
					'width':int(list[5]),'length':float(list[6]),'format':list[7]})
	file.close()
	return len(PICLIST)
	
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
	firstpagenum=read_config('download','first_page_num')
	if firstpagenum=='':#未指定默认为无限制
		firstpagenum=2147483647
	else:
		firstpagenum=int(firstpagenum)
	projname=read_config('download','name')
	global PICLIST
	PICLIST=[]
	nextpage=[]
	###################开始预处理
	#决定首页
	if projname=='' or 0<projname<20:#today模式
		print_c('没有指定名称,按照快速筛选(built_in)选项下载')
		nextpage.append(HOMEURL+'/today/index'+BUILT_IN_SUFFIX[int(read_config('download','built_in'))]+'.html')
		namelist=[time.strftime('%Y-%m-%d %H-%M-%S',time.localtime()),'','']
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
		filtername=read_config('download','filter')
		#处理比例过滤器
		ratiolist=read_config(filtername,'ratio').split('|')
		for r in range(len(ratiolist)):#依次构造
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
		load_local_piclist(projfile_path)
		print fmttime()+'Load download progress from file. (Got '+str(len(PICLIST))+'p)'
	else:
		load_remote_piclist(nextpage,firstpagenum,projfile_path)
		print fmttime()+'Parse finished. (Got '+str(len(PICLIST))+'p)'
	print fmttime()+'Download started.'
	#图片下载
	for i in range(len(PICLIST)):
		#time.sleep(GET_INTERVAL)#f*ck!!!
		basename=re.findall('/([A-Za-z0-9._]+)$',PICLIST[i]['full'])[0]#切割文件名
		filename=working_dir+opath.sep+basename
		#urllib.urlretrieve(PICLIST[i]['full'], filename,down_callback)
		if opath.exists(filename) and skip_exist=='1':#存在则跳过
				print fmttime()+'Skip '+basename+': Exists.'+' '*10
		elif opath.exists(filename) and skip_exist=='2' and \
		urlget(PICLIST[i]['full'],True,retries,chunk,opath.getsize(filename),PICLIST[i]['referpage'])=='SAME':
				print fmttime()+'Skip '+basename+': Same size exists.'+' '*5
		else:#不存在 或 2&&大小不符
			print '\b%sDownloading %3d/%3d images: %s ->' % (fmttime(),i+1,len(PICLIST),basename)
			#       |不知道为什么会空一格…所以加上退格…
			#保存到文件
			fileHandle=open(filename,'wb')
			fileHandle.write(urlget(PICLIST[i]['full'],True,retries,chunk,-1,PICLIST[i]['referpage']))
			fileHandle.close()
	print '\n'+fmttime()+'Download finished.\n'+str(len(PICLIST))+' pictures saved under \"'+working_dir
	os.remove(working_dir+opath.sep+'.roameproject')
	
def search():
	'''
	Search module
	'''
	urllist=[]
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
	list=re.findall('<a href="/index/([0-9a-z-]+)">(.*?) - (.*?)( - )?</a',content)
	#debug用
	'''list2=re.findall('<a href="/index/([0-9a-z-]+)">(.+)[ -]*(.*)</a>',content)
	print len(list),len(list2)
	offset=0
	for i in range(1225):
		if list[i-offset][0]!=list2[i][0]:
			print list2[i]
			offset+=1
	return'''
	#询问输入
	input=raw_input('Input your keyword:')
	if sys.platform=='win32':
		input=input.decode('gb2312')
	else:
		input=input.decode('utf-8')
	count=0
	#顺序查找并分割打印
	for i in range(len(list)):
		if re.search(input.encode('utf-8'), list[i][1], re.IGNORECASE) or \
		re.search(input, list[i][2], re.IGNORECASE):
			urllist.append(list[i][0])
			count+=1
			if list[i][2]!='':
				print normstr((str(count)+'.'+list[i][1]+'('+list[i][2]+')').decode('utf-8','ignore'))
			else:
				print normstr((str(count)+'.'+list[i][1]).decode('utf-8','ignore'))
	print str(count)+' result(s) found.'
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
	except ValueError:#熊孩子没有输入数字
		print_c('[なに？]σ(· ·?) \n')

def update():
	'''
	Online update
	'''
	newver=urlget("https://raw.github.com/fffonion/RoameBot/master/version.txt")
	if newver!=__version__:
		print_c('花现新版本：'+newver)
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
		print_c('\n更新到了版本：'+newver)
	else:
		print_c('已经是最新版本啦更新控：'+__version__)
		
if __name__ == '__main__':  
	try:
		if not opath.exists(os.getcwdu()+opath.sep+'config.ini'):#first time
			init_config()
		init_proxy()
		#重设默认编码
		reload(sys)
		sys.setdefaultencoding('utf-8')
		#菜单
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
		f=open(os.getcwdu()+opath.sep+'romaebot.log','a')
		f.write(fmttime()+'Stopped.\n')
		traceback.print_exc(file=f)
		#traceback.print_exc()
		f.flush()
		f.close()
if sys.platform=='win32':
	print_c("按任意键退出亲~")
	os.system('pause>nul'.decode('utf-8'))