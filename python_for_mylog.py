#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# DevVersion: Python3.6.8
# Date: 2020-09-11 22:04
# Author: SunXiuWen
# Des: 构建日志文件记录通用中间件
# PyCharm|log_config
import os
import re
import time
import datetime
import inspect
import json
import socket
import logging
import platform
import threading
from logging.handlers import TimedRotatingFileHandler

"""
缺陷：
1. 分割文件,文件名会出现两个.log，如：debug.log.2020-09-12_16.log
那么采集就必须是获取文件名，如果文件时.log【结尾】的才行
"""
# TODO：项目日志结构的不同获取对应服务名称需要根据实际进行调整
# 项目基目录
SERVER_DIR_BASENAME = os.path.dirname(os.path.abspath(__file__))
# 本地项目日志路径
CURRENT_LOG_PATH = os.path.join(SERVER_DIR_BASENAME, 'log')
# 日志级别权重值
LOG_LEVEL = {
    "NOTSET": 0,
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "WARN": 30,
    "ERROR": 40,
    "FATAL": 50,
    "CRITICAL": 50,
    "EXTERNAL": 60,
    "INTERNAL": 60,
}


class LogMiddleware(object):
    _instance_lock = threading.Lock()
    log_dict = {}

    def __init__(self,
                 app_name="Test_app",
                 hostname=socket.gethostname(),
                 log_level="DEBUG",
                 log_format_model="elk",
                 log_when="H",
                 log_interval=1,
                 log_backup_count=30 * 24,
                 log_dir_path="/app/logs/{}".format(os.path.basename(SERVER_DIR_BASENAME))):
        """
        :param app_name:  标识日志归属与那个app
        :param hostname:  实例的主机名
        :param log_level: 日志最低输出的级别
        :param log_format_model: 日志记录的格式,可以选设置好的default或elk，也可以自定义
        :param log_when: 日志分割的模式：H 小时，M 分钟，S 秒
        :param log_interval: 日志分割的维度，仅支持天D、小时H，分钟M，秒S
        :param log_backup_count: 日志最多保留的个数，默认按小时分割，保留30天的日志
        :param log_dir_path: 日志存放的基目录
        """
        self.app_name = app_name
        self.hostname = hostname
        self.log_level = log_level
        self.log_dir_path = log_dir_path
        self.log_format_model = log_format_model
        self.log_when = log_when.upper()
        self.log_interval = log_interval
        self.log_backup_count = log_backup_count
        self.logger = self.__class__.__name__  # 类名

    def __new__(cls, *args, **kwargs):
        """单例模式，log对象多进程/线程实例化一次"""
        if not hasattr(LogMiddleware, "_instance"):
            with LogMiddleware._instance_lock:
                if not hasattr(LogMiddleware, "_instance"):
                    cls._instance = object.__new__(cls)
        return cls._instance

    def get_logger(self):
        """
        构建日志对象
        :return:
        """
        p_id = str(os.getpid())
        logger_ = self.log_dict.get("p" + p_id)
        if not logger_:
            # 日志记录的格式,默认提供两种方式
            log_format_dict = {
                "default": "[%(levelname)s]:[%(asctime)s]:(thread_id:%(thread)d):[%(filename)s:%(lineno)d]-%(message)s",
                "elk": "%(message)s"
            }
            def_format = logging.Formatter(
                log_format_dict[
                    self.log_format_model] if self.log_format_model in log_format_dict.keys() else self.log_format_model)

            # 配置日志文件输出目录及日志文件名
            log_path_prefix = CURRENT_LOG_PATH if platform.system() == 'Windows' else self.log_dir_path
            if not os.path.exists(log_path_prefix):
                os.makedirs(log_path_prefix)
            log_path_debug = "{}/{}-debug-{}.log".format(log_path_prefix, self.app_name, self.hostname)
            log_path_error = "{}/{}-error-{}.log".format(log_path_prefix, self.app_name, self.hostname)
            log_path_info = "{}/{}-info-{}.log".format(log_path_prefix, self.app_name, self.hostname)
            log_path_warn = "{}/{}-warn-{}.log".format(log_path_prefix, self.app_name, self.hostname)

            # 设置分割日志后文件名的后缀格式及不符合日志文件名规则的删除日志文件
            split_log_file_prefix_dict = {
                "D": {"suffix": "%Y-%m-%d.log", "extMatch": r"^\d{4}-\d{2}-\d{2}.log$"},
                "H": {"suffix": "%Y-%m-%d_%H.log", "extMatch": r"^\d{4}-\d{2}-\d{2}_\d{2}.log$"},
                "M": {"suffix": "%Y-%m-%d_%H-%M.log", "extMatch": r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$"},
                "S": {"suffix": "%Y-%m-%d_%H-%M-%S.log", "extMatch": r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.log$"}
            }

            # 配置日志各级别对象字典
            handler_map = {
                "DEBUG": {"file_name": log_path_debug, "record_filter": logging.INFO, "level": logging.DEBUG},
                "INFO": {"file_name": log_path_info, "record_filter": logging.WARN, "level": logging.INFO},
                "WARNING": {"file_name": log_path_warn, "record_filter": logging.ERROR, "level": logging.WARNING},
                "ERROR": {"file_name": log_path_error, "record_filter": logging.FATAL, "level": logging.ERROR}}
            handler_list = []
            for k, v in handler_map.items():
                # 构建各级别日志处理对象
                my_log_handler = logging.handlers.TimedRotatingFileHandler(
                    # 文件名
                    v["file_name"],
                    # 分割的维度
                    when=self.log_when,
                    # 如按秒分割，间隔5秒，从执行程序开始计时，如第1开始，分割就是第6
                    interval=self.log_interval,
                    # 保留日志个数，默认30天的日志
                    backupCount=self.log_backup_count,
                    # 日志编码，避免中文乱码
                    encoding='utf-8')
                # 文件分割后文件名及过期文件匹配设置
                my_log_handler.suffix = split_log_file_prefix_dict[self.log_when]["suffix"]
                my_log_handler.extMatch = re.compile(split_log_file_prefix_dict[self.log_when]["extMatch"])
                # 构建过滤器
                my_filter = logging.Filter()
                my_filter.filter = lambda record: record.levelno < v["record_filter"]
                my_log_handler.addFilter(my_filter)
                # 日志手柄关联的日志级别配置及日志记录格式配置
                my_log_handler.setLevel(v["level"])
                my_log_handler.setFormatter(def_format)
                handler_list.append(my_log_handler)

            # 构建日志对象
            logger_ = logging.getLogger(name=self.app_name)
            logger_.setLevel(self.log_level)
            for handler in handler_list:
                logger_.addHandler(handler)
            self.log_dict["p" + p_id] = logger_
        return logger_

    def base_model(self, log_type, levelno, level, message, path_name, lineno, func_name, extra=None, app_name=None):
        data = {
            "app_name": app_name,
            "logger": self.logger,
            "HOSTNAME": self.hostname,
            "log_type": log_type,
            "level_no": levelno,  # 日志的权重值
            "log_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "level": level,
            "thread": threading.currentThread().ident,
            "code_message": message,
            "pathName": path_name,
            "lineNo": lineno,  # 程序文件记录日志所在的行数
            "funcName": func_name,
        }
        if extra:
            data.update(extra)
        return json.dumps(data, ensure_ascii=False)

    def debug(self, msg, log_type="desc"):
        if LOG_LEVEL[self.log_level] <= LOG_LEVEL["DEBUG"]:
            path_name, lineno, func_name = self.make_path()

            self.get_logger().debug(self.base_model(log_type=log_type,
                                                    levelno=LOG_LEVEL["DEBUG"],
                                                    level="DEBUG",
                                                    app_name="{}_code".format(str(self.app_name)),
                                                    message=msg,
                                                    path_name=path_name,
                                                    lineno=lineno,
                                                    func_name=func_name))

    def info(self, msg, log_type="desc"):
        if LOG_LEVEL[self.log_level] <= LOG_LEVEL["INFO"]:
            path_name, lineno, func_name = self.make_path()

            self.get_logger().info(self.base_model(log_type=log_type,
                                                   levelno=LOG_LEVEL["INFO"],
                                                   level="INFO",
                                                   app_name="{}_code".format(str(self.app_name)),
                                                   message=msg,
                                                   path_name=path_name,
                                                   lineno=lineno,
                                                   func_name=func_name))

    def warning(self, msg, log_type="desc"):
        if LOG_LEVEL[self.log_level] <= LOG_LEVEL["WARNING"]:
            path_name, lineno, func_name = self.make_path()

            self.get_logger().warning(self.base_model(log_type=log_type,
                                                      levelno=LOG_LEVEL["WARNING"],
                                                      level="WARNING",
                                                      app_name="{}_code".format(str(self.app_name)),
                                                      message=msg,
                                                      path_name=path_name,
                                                      lineno=lineno,
                                                      func_name=func_name))

    def error(self, msg, log_type="desc"):
        if LOG_LEVEL[self.log_level] <= LOG_LEVEL["ERROR"]:
            path_name, lineno, func_name = self.make_path()

            self.get_logger().error(self.base_model(log_type=log_type,
                                                    levelno=LOG_LEVEL["ERROR"],
                                                    level="ERROR",
                                                    app_name="{}_code".format(str(self.app_name)),
                                                    message=msg,
                                                    path_name=path_name,
                                                    lineno=lineno,
                                                    func_name=func_name))

    def external(self, msg, extra, log_type="monitor"):
        path_name, lineno, func_name = self.make_path()

        self.get_logger().info(self.base_model(log_type=log_type,
                                               levelno=LOG_LEVEL["EXTERNAL"],
                                               level="EXTERNAL",
                                               app_name="{}_info".format(str(self.app_name)),
                                               message=msg,
                                               path_name=path_name,
                                               lineno=lineno,
                                               func_name=func_name,
                                               extra=extra))

    def internal(self, msg, extra, log_type="monitor"):
        path_name, lineno, func_name = self.make_path()

        self.get_logger().info(self.base_model(log_type=log_type,
                                               levelno=LOG_LEVEL["INTERNAL"],
                                               level="INTERNAL",
                                               app_name="{}_info".format(str(self.app_name)),
                                               message=msg,
                                               path_name=path_name,
                                               lineno=lineno,
                                               func_name=func_name,
                                               extra=extra))

    @staticmethod
    def make_path():
        d = inspect.stack()[2]  # 获取栈内调用行
        return d[1], d[2], d[3]


if __name__ == '__main__':
    logger = LogMiddleware(app_name="test_app", log_when="S", log_format_model="default")

    # 测试在10s内创建文件多个日志文件
    print(datetime.datetime.now())
    count = 0
    for i in range(0, 10):
        logger.debug("测试debug日志")
        count += 1
        # logger.info("测试info日志")
        # logger.warning("测试warning日志")
        # logger.error("测试error日志")
        time.sleep(1)
    print(count)
