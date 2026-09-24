# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyspace.py
   Description :   proxyspace.pro 代理源（独立站，HTTP + HTTPS + SOCKS5）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxySpaceFetcher(BaseFetcher):
    """proxyspace.pro — 独立代理列表站，无需 GitHub"""

    name = "proxyspace"
    url = "https://proxyspace.pro"

    enabled = True

    _URLS = [
        ("http", "https://proxyspace.pro/http.txt"),
        ("https", "https://proxyspace.pro/https.txt"),
        ("socks4", "https://proxyspace.pro/socks4.txt"),
        ("socks5", "https://proxyspace.pro/socks5.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=10)
                for proxy in self.parseProxiesFromText(r.text):
                    yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - proxyspace/{proto}: {e}")


if __name__ == '__main__':
    for proxy in ProxySpaceFetcher().fetch():
        print(proxy)
