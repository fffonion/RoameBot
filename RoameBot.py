# -*- coding:utf-8 -*-
import urllib2,re,os,threading,time,ConfigParser,sys,socket
PICLIST=[]
INITURL='http://www.roame.net/index/hakuouki-shinsengumi-kitan'
HOMEURL='http://www.roame.net'
RATIO_SUFFIX=['','-wall','-16x10','-16x9','-4x3','-5x4','-oall','-wgth','-wlth','-weqh']
BUILT_IN_SUFFIX=['','-pic-16x9','-pic-16x10','-pic-4:3','-5:4','-wgth','-pic-wlth','-pic-wegh','','',\
				'-hotest-down','-hotest-weeklydown','-hotest-monthlydown','-hotest-score',\
				'-hotest-monthlyscore','','','','','',\
				'-others-latest','-others-random']
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
def chunk_read(response, chunk_size=8192, report_hook=None):
	buffer=''
	total_size = int(response.info().getheader('Content-Length').strip())
	bytes_got = 0
	init_time=time.time()
	while 1:
		chunk = response.read(chunk_size)
		buffer+=chunk
		bytes_got += len(chunk)
		if not chunk:
			break
		if report_hook:
			report_hook(bytes_got, chunk_size, total_size,init_time)
	return buffer

def urlget(src,showprogress=False,retries=3,chunk=8):
	#try:
		req = urllib2.Request(src)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4')
		#req.add_header('Referer', 'http://www.google.com/xxxx')
		resp = urllib2.urlopen(req)
		if showprogress:
			#savedPICBUFFER
			content=chunk_read(resp, chunk*1024,chunk_report)
		else:
			content = resp.read()#.decode('utf-8')
		return content
	#except Exception, what:
	#	print Exception.message
	#	if retries>0:
	#		return urlget(src,showprogress,retries-1)
	#	else:
	#		print 'Failed on '+src
	#	return None
	
#NOT USING CURRENTLY	
class multiget(threading.Thread):
	def __init__(self,url):
		threading.Thread.__init__(self)
		self.thread_stop = False
		self.geturl=url
 
	def run(self):
		print len(urlget(self.geturl))
		self.stop()
	def stop(self):
		self.thread_stop = True
  
def decutf(lst):
	lstnew=[i for i in range(len(lst))]
	for i in range(len(lst)):
		lstnew[i]=lst[i].decode('utf-8')
	return lstnew

def parse_albumname(str):
	'''
	Return albumname TUPLE: 0=CHN, 1=ENG, 2=JPN
	'''
	#exp :<title>夏目友人帐 - 英文名:Natsume Yuujinchou, 日文名:夏目友人帳 - 路游动漫图片壁纸网</title>
	albumname=re.findall('title>(.+) -.+:(.+),.+:(.+) -',urlget(str))
	#no jp exp :<title>阿倍野挢魔法商店街 - 英文名:Magical Shopping Arcade Abenobashi - 路游动漫图片壁纸网</title>
	if albumname==[]:
		albumname=re.findall('title>(.+) -.+:(.+)(.*) -',urlget(str))
	return decutf(albumname[0])
	
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
	cf.read(os.path.abspath(os.curdir)+'/'+'config.ini')
	val=cf.get(sec, key)
	if val=='':
		return ''
	else:
		return val

def write_config(sec,key,val):
	cf=ConfigParser.ConfigParser()
	cf.read(os.path.abspath(os.curdir)+'/'+'config.ini')
	cf.set(sec, key,val)
	cf.write(open(os.path.abspath(os.curdir)+'/'+'config.ini', "w"))

def init_config():
	filename = os.path.abspath(os.curdir)+'/'+'config.ini'
	f=file(filename,'w')
	f.write('[download]\nskip_exist = 1\ndownload_when_parse = 1\ntimeout = 10\nbuffersize = 8\nretries = 3\ndir_name = 2\ndir_path = \nlogpath = log.txt\nname = hyouka\nbuilt_in = 21\nfilter = filter_0\nfirst_page_num = \nproxy = http://proxy.com/\n[filter_0]\nratio = 1\nmax_length = \nmax_width = \nmin_length = \nmin_width = \nmax_size = \nmin_size = ')
	f.close() 
#main entry
def main():
	global INITURL,PICLIST
	PICLIST=[]
	#read and set config vals
	timeout=read_config('download','timeout')
	socket.setdefaulttimeout(int(timeout))
	chunk=int(read_config('download','buffersize'))
	retries=int(read_config('download','retries'))
	SKIP_EXIST=read_config('download','skip_exist')
	DIR_NAME=read_config('download','dir_name')
	dir_path=read_config('download','dir_path')=='' and os.path.abspath(os.curdir)	or read_config('download','dir_path')
	LOGPATH=read_config('download','logpath')
	firstpagenum=read_config('download','first_page_num')
	if firstpagenum=='':
		firstpagenum=2147483647
	projname=read_config('download','name')
	#determine first page
	if projname=='' or 0<projname<20:
		print 'No banngumi name specified.Downloading latest images.'
		INITURL=HOMEURL+'/today/index'+BUILT_IN_SUFFIX[int(read_config('download','built_in'))]+'.html'
		nextpage=INITURL
		namelist=[time.strftime('%Y-%m-%d %H-%M-%S',time.localtime()),'','']
		DIR_NAME=0#only this one
	else:
		INITURL=HOMEURL+'/index/'+projname
		filtername=read_config('download','filter')
		nextpage=INITURL+'/images/index'+RATIO_SUFFIX[int(read_config(filtername,'ratio'))]+'.html'
		#print INITURL
		namelist=parse_albumname(INITURL)
		print fmttime()+'Collecting info for : '+namelist[0]+'/'+namelist[1]+'/'+namelist[2]
	WORKINGDIR=dir_path+'/'+((namelist[2]=='' and DIR_NAME=='2')and namelist[0] or namelist[int(DIR_NAME)])
	if not os.path.exists(WORKINGDIR):
		os.mkdir(WORKINGDIR)
	pagenum=1
	while(nextpage!=None and pagenum<firstpagenum):
		print '%sPage parsing started at %s' % (fmttime(),nextpage)
		nextpage=parse_pagelist(nextpage,pagenum)
		pagenum+=1
		#print PICLIST
	print fmttime()+'Parse finished.'
	print fmttime()+'Download started.'
	for i in range(len(PICLIST)):
		basename=re.findall('/([A-Za-z0-9._]+)$',PICLIST[i]['full'])[0]
		filename=WORKINGDIR+'/'+basename
		#urllib.urlretrieve(PICLIST[i]['full'], filename,down_callback)  
		if os.path.exists(filename) and SKIP_EXIST=='1':#存在且跳过
			print 'Skip '+basename+': Exists.'
		else:
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
	count=0
	#print list
	reload(sys)
	sys.setdefaultencoding('utf-8')
	for i in range(len(list)):
		if re.search(input.decode('gb2312').encode('utf-8'), list[i][1], re.IGNORECASE) or \
		re.search(input, list[i][2], re.IGNORECASE):
			reslist.append((list[i][0],list[i][1],list[i][2]))
			count+=1
			try:
				print str(count)+'.'+list[i][1].encode('utf-8').decode('utf-8')+'('+list[i][2]+')'
			except:
				print str(count)+'.'+list[i][1].replace('〜','~').encode('utf-8').decode('utf-8')+\
				'('+list[i][2]+')'
	print str(count)+' result(s) found.'
	if count > 0:
		input=raw_input('Choice:')
		if 0<int(input)<count+1:
			write_config('download','name',reslist[int(input)-1][0])
			main()
		else:
			print 'Nani?!'
	#print reslist
	
if __name__ == '__main__':  
	if not os.path.exists(os.path.abspath(os.curdir)+'/'+'config.ini'):#first time
		init_config()
	while input !=4:
		print '[Menu]\n1.Search\t2.Use \'config.ini\'\t3.About\t\t4.Exit'
		input=raw_input('Choice:')
		if input=='2':
			main()
		elif input=='1':
			search()
		else:
			print 'Not implemented.'
print 'done'
