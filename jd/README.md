爬取京东试用商品信息

requests访问页面获取基本数据，ajax获取动态数据（商品价格，申请人数），beautifulsoup解析数据，然后存储到mongo数据库。图片是celery异步下载的。

查看requirements.txt, 安装依赖需要的包
pip install -r requirements.txt
其中celery在windows下时使用的是3.*版本， 最新版本已不支持windows
