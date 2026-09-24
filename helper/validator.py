# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     _validators
   Description :   定义proxy验证方法
   Author :        JHao
   date：          2021/5/25
-------------------------------------------------
   Change Activity:
                   2023/03/10: 支持带用户认证的代理格式 username:password@ip:port
                   2026/09/24: 新增 socks5_validator（curl --socks5h），独立于 http 链路
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from requests import head
from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler

conf = ConfigHandler()

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []
    socks5_validator = []

    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func

    @classmethod
    def addSocks5Validator(cls, func):
        cls.socks5_validator.append(func)
        return func


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(proxy) else False


@ProxyValidator.addHttpValidator
def httpTimeOutValidator(proxy):
    """ http检测超时 """

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}

    try:
        r = head(conf.httpUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False


# 2026/09/24 移除原 httpsTimeOutValidator：其 proxies 字典写 "https://{proxy}"
# 会让 requests 先与代理做 TLS 握手（普通免费代理必败），且多 validator 链是
# AND 语义，一个 False 全部否决——这是历史上池内 https 代理近乎为零的根因。
# https 检测统一由下方 httpsTunnelValidator 承担（修正 scheme + 双目标 OR）。


@ProxyValidator.addHttpsValidator
def httpsTunnelValidator(proxy):
    """https隧道检测（双目标 OR 逻辑）。

    实测教训（2026-09-24）：单目标校验会被目标站的代理策略误导——qq.com 对
    部分代理间歇 501/302（漏报），jd.com 对境外数据中心 IP 常拒 HEAD
    （双目标 AND 时同样漏报：池内实测 20% 代理可隧道 baidu 却全被标 false）。
    改为「任一目标 200 即认定隧道可用」：目标多样性对冲单站策略，
    剩余误差由调用方 /get/?check=1 现场拨测兜底。
    """
    # 关键修正：代理本身一律用 http:// 连接（普通免费代理不支持 TLS-in，
    # 原版写 "https://{proxy}" 会让 requests 先跟代理做 TLS 握手导致必败）；
    # 目标 URL 的 https scheme 由 requests 自动升级为 CONNECT 隧道。
    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "http://{proxy}".format(proxy=proxy)}
    for url in (conf.httpsUrl, "https://cn.bing.com"):
        try:
            r = head(url, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
            if r.status_code == 200:
                return True
        except Exception:
            continue
    return False


@ProxyValidator.addHttpValidator
def customValidatorExample(proxy):
    """自定义validator函数，校验代理是否可用, 返回True/False"""
    return True


@ProxyValidator.addSocks5Validator
def socks5TimeOutValidator(proxy):
    """socks5 / socks5h 检测（requests + PySocks，进程内完成）。

    socks5h:// scheme 让 SOCKS5 代理自己做 DNS 解析，避免 Pi 本地 DNS 劫持
    导致「代理好但域名解析不通」的假阴性（与原 curl --socks5h 等价）。
    2026/09/24 由 subprocess curl 改为 requests：省去每次校验 fork 进程的
    开销（20 线程并发下收益明显），异常处理与 http 链路统一。
    需要 PySocks 依赖（requirements.txt 已登记，venv 已安装）。
    """
    # 尝试 3 个目标：HTTP(baidu) + HTTPS(baidu) + HTTPS(bing)
    # 任一 200 即认定 socks5 可用（socks5 天然支持 CONNECT 隧道到 HTTPS 目标）
    proxies = {"http": "socks5h://{proxy}".format(proxy=proxy),
               "https": "socks5h://{proxy}".format(proxy=proxy)}
    for target in ("http://www.baidu.com", "https://www.baidu.com", "https://cn.bing.com"):
        try:
            r = head(target, headers=HEADER, proxies=proxies,
                     timeout=conf.verifyTimeout, verify=False, allow_redirects=False)
            if r.status_code == 200:
                return True
        except Exception:
            continue
    return False
