# ChromeDriver 管理工具

这是一个用于自动检测和下载与本地 Chrome 浏览器匹配的 ChromeDriver 的工具，适用于 Windows 系统。

方便办公使用，全部国内源和代理源下载，无需翻墙。

## 功能介绍

该工具主要提供以下功能：



1.  自动检测系统架构（32 位 / 64 位）

2.  扫描本地 Chrome 浏览器的安装路径

3.  提取已安装 Chrome 浏览器的版本号

4.  根据 Chrome 版本号和系统架构提供合适的 ChromeDriver 下载源

5.  支持从多个下载源下载 ChromeDriver

6.  自动解压并安装 ChromeDriver 到当前目录

7.  当未检测到 Chrome 时，提供推荐版本的 Chrome 及对应驱动的下载地址

## 所需模块

运行该工具需要以下 Python 模块：



*   标准库：`os`、`re`、`sys`、`platform`、`shutil`、`zipfile`

*   第三方库：`requests`、`progressbar`

## 安装依赖

使用 pip 安装所需第三方库：



```
pip install requests progressbar2
```

## 使用方法



1.  确保已安装 Python 环境 3.8+

2.  安装上述依赖库

3.  运行脚本：



```
python driver.py
```



1.  按照程序提示进行操作，工具会自动完成环境检测和驱动下载安装

## 注意事项



*   本工具仅支持 Windows 系统

*   对于 Chrome 114 及以下版本，仅支持 32 位驱动

*   若自动下载失败，工具会提供下载地址供手动下载

## 工作流程



1.  检测系统信息（工作目录、系统架构）

2.  查找本地 Chrome 浏览器安装
   
3.  未检测到或未按照，推荐安装默认版本（可选自动下载自动安装）

4.  获取 Chrome 版本号（自动检测或手动输入）

5.  提供对应版本的 ChromeDriver 下载源

6.  下载并解压 ChromeDriver 到当前目录

7.  可选是否保留下载的压缩包
   
