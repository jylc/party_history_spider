## Party History Spider

---

该项目用于爬取所有高校党史成果信息

### 使用方法

#### 1. 安装pymysql库，具体配置环境详情见settings.py

#### 2. 运行partyhistoryspider.sql，创建数据库表

#### 3. 安装loguru库

#### 4. google部分的爬取需要安装ssr，设置代理

* 使用[ssr-command-client](https://github.com/TyrantLucifer/ssr-command-client)
* scrapy不支持socks5，因此安装python-proxy将socks5代理转为http代理，具体戳[这里](https://stackoverflow.com/questions/59085184/how-can-proxy-scrapy-requests-with-socks5)

#### 5. 安装scrapy-splash对动态网页解析
* 在解析外网的动态网页时，不能直接将代理设置为localhost本地代理，否者会转发到splash的容器端口，具体戳[这里](https://www.twblogs.net/a/5bfe243cbd9eee7aed333f2e)

#### 6. 运行main.py

### 待解决的问题
- [ ] 爬取动态网页
- [ ] 正常运行