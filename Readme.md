#路游动漫社区爬虫
python脚本跨平台。windows用户可[直接下载.exe](https://github.com/fffonion/RoameBot/raw/master/RoameBot.exe)
 - BUG提交请在issues中附带日志（roamebot.log）
 - 更新日志[在这里~](https://github.com/fffonion/RoameBot/blob/master/History.md)
 - 更新后出现no option错误的请删除原来的config.ini
 
##PS
路游社区对图片下载会话作了限制，因此下载是单线程单任务进行的。

##使用说明
你也可以参见快速入门Readme.txt
###1.使用内置搜索
在界面选择1即可，支持中英文搜索，并按默认设置下载
###2.配置文件config.ini说明
####[download]块
***
####skip_exist
是否跳过已存在的文件，2-是，且比较文件大小[默认]，1-是，0-否
####download_when_parse 
是否边分析页面边下载，1-是[默认]，0-否，
####timeout
设置超时时间，单位为秒,默认为10
####chunksize
设置chunk值，单位为KB，默认为8，可能对下载速度有影响
####retries
设置重试次数，默认为3
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
根据<http://www.roame.net/today>页的快速筛选选项。
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
####proxy_name
代理用户名
####proxy_pswd
代理密码
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

以下过滤器不可用
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

##授权
[GPLv2授权](http://opensource.org/licenses/gpl-2.0.php)
***
![@fffonion](http://img.t.sinajs.cn/t5/style/images/register/logo.png)[@fffonion](http://weibo.com/376463435)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![Blog](http://zmingcx.com/wp-content/themes/HotNewspro/images/caticon/wordpress.gif)[博客](http://yooooo.us)
