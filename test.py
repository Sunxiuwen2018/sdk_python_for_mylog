#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:SunXiuWen
# datetime:2021/1/12 0012 17:07
import os
import time
import datetime

import python_for_my_log

# 手动指定目录
# log_dir_path = f"{os.sep}app{os.sep}app_name"
# 手动在调用文件位置获取基目录
log_dir_path = os.path.dirname(os.path.abspath(__file__))
print(log_dir_path)
logger = python_for_my_log.LogMiddleware(log_dir_path=log_dir_path,
                                         app_name="test_app",
                                         log_when="S",
                                         log_format_model="default")

# 测试在3s内创建文件多个日志文件
print(datetime.datetime.now())
count = 0
for i in range(0, 3):
    logger.debug("测试debug日志")
    logger.info("测试info日志")
    logger.warning("测试warning日志")
    logger.error("测试error日志")
    count += 1
    time.sleep(1)
print(count)
