# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     premiumproxy.py
   Description :   premiumproxy.net 独立代理源（HTML 页面，每小时更新）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class PremiumProxyFetcher(BaseFetcher):
    """premiumproxy.net — 独立代理列表站，返回 HTML 页面，正则自动提取 IP:PORT"""

    name = "premiumproxy"
    url = "https://premiumproxy.net"

    enabled = True

    def fetch(self):
        try:
            r = WebRequest().get(
                "https://premiumproxy.net/full-proxy-list",
                timeout=15)
            for proxy in self.parseProxiesFromText(r.text):
                yield proxy
        except Exception as e:
            logger.error(f"ProxyFetch - premiumproxy: {e}")


if __name__ == '__main__':
    for proxy in PremiumProxyFetcher().fetch():
        print(proxy)
