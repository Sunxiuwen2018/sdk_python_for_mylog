# sdk_python_for_mylog
我的开源小脚本-愉快的记录日志
# 人生苦短，我用python

### 一、怎么获取源码？
[GitHub地址](https://github.com/Sunxiuwen2018/sdk_python_for_mylog.git)

### 二、怎么使用？
1. 安装
```shell
pip  install python_for_mylog
```
2. 构建日志对象
```python
from python_for_my_log import LogMiddleware
# 在项目全局的地方实例化
logger = LogMiddleware(log_dir_path="自定义日志存放的目录路径名，默认为/app/logs/服务名/",
                 app_name="自定义服务的名称",
                 hostname="自定义实例的主机名，默认获取实例机器的hostname",
                 log_level="定义日志最低输出的级别，默认DEBUG",
                 log_format_model="日志记录的格式，默认执行给出的elk样式，也提供default模式，也可自定义",
                 log_when="定义日志分割的模式：H 小时，M 分钟，S 秒，默认小时",
                 log_interval=1, # 日志分割的维度，仅支持天D、小时H，分钟M，秒S
                 log_backup_count=30 * 24) # 日志最多保留的个数，默认按小时分割，保留30天的日志
# 记录日志
logger.debug("人生苦短，我用孙氏牌日志记录器")
```
3. 范例调用参考sdk中的test.py文件

### 三、日志存放路径说明
**建议传入你当前服务的根目录且建议通过os模块获取或者通过os.sep代替`/`或`\`**
1. 默认windows系统，在您传入的路径后新建一个log的目录，存放记录的日志，如/log_dir_path/log/debug.*.log
2. linux系统，在您传入的路径最后一层目录名前拼接/app/logs/log_dir_path.split("/")[-1]
```
# 示例: 如您传入的是当前服务的基目录：/project/my_app_name
# windows：那么您存放日志的路径就是：/project/my_app_name/log
# linux: 那么您存放日志的路径就是：/app/logs/my_app_name
```

### 四、后期待优化的问题
```shell
# 分割文件,文件名会出现两个.log，如：debug.log.2020-09-12_16.log
# 那么采集就必须是获取文件名，如果文件时.log【结尾】的才行
```

### 五、更多交流请关注微信公众号`Python小白成长记`
![](https://raw.githubusercontent.com/Sunxiuwen2018/MyPicGoDir/main/Picture/%E6%88%91%E7%9A%84%E5%85%AC%E4%BC%97%E5%8F%B7.jpg)
