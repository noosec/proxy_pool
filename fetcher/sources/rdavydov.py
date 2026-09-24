# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     rdavydov.py
   Description :   rdavydov/proxy-list 代理源（554 个）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class RdavydovFetcher(BaseFetcher):
    """rdavydov/proxy-list https://github.com/rdavydov/proxy-list"""

    name = "rdavydov"
    url = "https://github.com/rdavydov/proxy-list"

    enabled = True

    _URLS = [
        ("http", "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt"),
        ("socks5", "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=15)
                for proxy in self.parseProxiesFromText(r.text):
                    yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - rdavydov/{proto}: {e}")


if __name__ == '__main__':
    for proxy in RdavydovFetcher().fetch():
        print(proxy)
