#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:SunXiuWen
# datetime:2021/1/12 0012 16:15
"""
setup.py 是 setuptools 的构建脚本，用于告知 setuptools
我们要上传到PYPI的库的信息（库名、版本信息、描述、环境需求等）。
"""

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="python_for_my_log",  # 库名,这里指定什么名字，安装时就写什么名字
    version="0.0.2",                   # 版本号
    author="SunXiuWen",             # 作者
    author_email="xiuwensun@163.com",   # 作者邮箱
    description="Record your diary happily",  # 包的简单说明
    long_description=long_description,        # 包的详细说明
    long_description_content_type="text/markdown",  # README.md中描述的语法（一般为markdown）
    url="https://github.com/Sunxiuwen2018/sdk_python_for_mylog.git",   # 项目地址
    packages=setuptools.find_packages(),  # 包列表,即包下的带有_init__文件的模块
    classifiers=[       # 包标签，便于搜索
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Logging"
    ],
)
