#ROAME.NET Crawler
由于编码问题还没有在*nix下测试。windows用户可直接下载.exe
##PS
路游网对图片下载会话作了限制，因此下载是单线程单任务进行的。

##使用说明
###1.使用内置搜索
在界面选择1即可，支持中英文搜索，并按默认设置下载
###2.配置文件config.ini说明
####[download]块
***
####skip_exist
是否跳过已存在的文件，1-是[默认]，0-否
####download_when_parse 
是否边分析页面边下载，1-是[默认]，0-否，
####timeout
设置超时时间，单位为秒,默认为10
####buffersize
设置chunk值，单位为KB，默认为8，可能对下载速度有影响
####retries
设置重试次数，默认为3
####dir_name
设置下载目录名称 0-中文[默认]，1-英文，2-日文
####dir_path
设置下载目录所在位置，默认为当前目录
####logpath
[未实现]输出日志路径
####name
<<<<<<< HEAD
抓取url，对于形如http://www.roame.net/index/little-busters/images只需输入little-busters；留空则使用built_in选项
####built_in
根据<http://www.roame.net/today>页的快速筛选选项。

=======
抓取url，对于形如<http://www.roame.net/index/little-busters/images>只需输入little-busters；留空则使用built_in选项
####built_in
根据<http://www.roame.net/today>页的快速筛选选项。
>>>>>>> 39b59c02b802deb238fd7b8f408d5a87861dbfc5
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
[未实现]设置代理路径，留空则跟随IE代理
####[filter]过滤器块
***1
默认的过滤器名称为filter_0
####ratio
比例过滤器

* 0：所有尺寸
* 1：壁纸尺寸
* 1：所有16:10
* 2：所有16:9
* 3：所有4:3
* 4：所有5:4
* 5：所有其他横向
* 6：所有竖向
* 7：所有等宽

以下过滤器尚未实现
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
