#路游动漫社区爬虫
###这是一个批量多任务下载路游动漫壁纸的爬虫，并可按图片长宽、大小、上传者ID、上传时间进行过滤
python脚本跨平台。windows用户可[直接下载.exe](https://github.com/fffonion/RoameBot/raw/master/RoameBot.exe)
 - BUG提交请在issues中附带日志（roamebot.log）
 - 更新日志[在这里~](https://github.com/fffonion/RoameBot/blob/master/History.md)
 - 图文并茂的介绍www[在这里_(:зJ∠)_ ](http://www.gn00.com/thread-220277-1-1.html)
 - 更新后出现no option错误的请删除原来的config.ini
 
##小技巧
###1.关于多任务下载
路游社区对图片下载会话作了限制，因此无法实现多线程。但从2.0版本开始本爬虫具有了多任务下载的能力。
内置账号因为大家都在用所以可能会有问题，你可以[使用这个工具](https://raw.github.com/fffonion/RoameBot/master/addUserUtil.py)添加自己的账号
###2.关于增量更新已下载的壁纸
只要保证保存目录(dir_path)相同，RoameBot就会智能地选择下载未下载的壁纸，跳过已有的


旧版点这里[(﹁ ﹁ )σ](https://github.com/fffonion/RoameBot/tree/1.6)
##使用说明
你也可以参见快速入门[Readme.txt](https://github.com/fffonion/RoameBot/blob/master/Readme.txt)
###1.使用“搜索”
在界面选择1即可，支持中英文搜索，支持正则表达式，并按默认设置下载
###2.使用“快速筛选”
在界面选择4，按照根据<http://www.roame.net/today>页的快速筛选选项，以及“未分类画集”，“未分类散图”，“随机十个番组”进行快速选择
###3.使用’最新上传”
在界面选择3，从首页抓取最新上传的壁纸信息，可以直接下载/更新
###4.使用“继续上次任务”
在界面选择3；你可以
 - 恢复上次已中断的任务（直接输入3即可）
 - 检查以前下载的番组有无新壁纸发布，并下载新壁纸（这需要读取上次目录下的.roamepast文件，须确保保存目录dir_path未变化）

###5.配置文件config.ini说明
####[download]块
***
####skip_exist
是否跳过已存在的文件，2-是，且比较文件大小[默认]，1-是，0-否
####use_cache
是否使用缓存（保存在系统临时目录\.roame下），1-是[默认]，0-否，
####timeout
设置超时时间，单位为秒,默认为10
####chunksize
设置chunk值，单位为KB，默认为8，可能对下载速度有影响
####retries
设置重试次数，默认为3
####threads
设置下载线程数，最大为5，默认为3，设置1则进入顺序下载模式
####dir_name
设置下载目录名称 0-中文[默认]，1-英文，2-日文
若已存在中/英/日任何目录时，优先使用已存在的目录而不新建
####dir_path
设置下载目录所在位置，默认为当前目录
####dir_pref
设置下载目录名称固定前缀
####dir_suff
设置下载目录名称固定后缀
####name
抓取url，对于形如<http://www.roame.net/index/little-busters/images>只需输入little-busters；留空则使用built_in选项
####built_in
根据<http://www.roame.net/today>页的快速筛选选项；也可以通过主界面菜单的“4”选择
* 0：所有最新
* 1：最新16:9
* 2：最新16:10
* 3：最新4:3
* 4：最新5:4
* 5：最新其他横向
* 6：最新竖向
* 7：最新等宽
* 10：今日下载排行
* 11：本周下载排行
* 12：30天下载排行
* 13：本周评分排行
* 14：30天评分排行
* 15：大家刚下载的
* 16：随机八张图片

下载内容将保存在以时间命名的文件夹中
####filter
当前激活的过滤器名称
####first_page_num
仅下载前多少页，留空为不限
####proxy
设置代理路径，留空则跟随IE代理
####proxy_urlarg, proxy_arg
设置指南，如果一个在线代理在不开启url加密、启用cookie时的url为：http://a.co/b.php?u=baidu.com&b=4, 则proxy填入http://a.co/b.php, proxy_urlarg填入u, proxy_arg填入b=4
####[filter]过滤器块
***
默认的过滤器名称为filter_0
####ratio
比例过滤器

* 0：所有尺寸
* 1：仅壁纸尺寸
* 2：所有16:10
* 3：所有16:9
* 4：所有4:3
* 5：所有5:4
* 6：其他尺寸
* 7：其他横向尺寸
* 8：竖向图片
* 9：等宽图片
* 可以使用|分割多个比例，比如2|3匹配所有16:10和16:9

####max_length
指定最大长度
####max_width
指定最大宽度
####min_length
指定最小长度
####min_width
指定最小宽度
####max_size
指定最大文件大小
####min_size
指定最小文件大小
####banned_uploader
指定屏蔽上传者ID，| 分割

####[cookie]Cookie串块
***
####var
cookie的内容，用|分割，添加教程见(https://github.com/fffonion/RoameBot/wiki/Add-custom-cookie)

##授权
[CC BY-3.0授权](http://zh.wikipedia.org/wiki/Wikipedia:CC_BY-SA_3.0协议文本)
***
![@fffonion](http://img.t.sinajs.cn/t5/style/images/register/logo.png)[@fffonion](http://weibo.com/376463435)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![Blog](http://zmingcx.com/wp-content/themes/HotNewspro/images/caticon/wordpress.gif)[博客](http://www.yooooo.us)
