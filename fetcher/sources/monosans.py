# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     monosans.py
   Description :   monosans/proxy-list 代理源（每 30 分钟更新，带协议验证）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
   Change Activity:
                   2026/09/24:
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class MonosansFetcher(BaseFetcher):
    """monosans/proxy-list https://github.com/monosans/proxy-list"""

    name = "monosans"
    url = "https://github.com/monosans/proxy-list"

    enabled = True

    _URLS = [
        ("http", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"),
        ("socks4", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt"),
        ("socks5", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=10)
                for proxy in self.parseProxiesFromText(r.text):
                    yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - monosans/{proto}: {e}")


if __name__ == '__main__':
    for proxy in MonosansFetcher().fetch():
        print(proxy)
