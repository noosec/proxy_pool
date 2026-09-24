# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     mmpx12.py
   Description :   mmpx12/proxy-list 代理源（440 个）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Mmpx12Fetcher(BaseFetcher):
    """mmpx12/proxy-list https://github.com/mmpx12/proxy-list"""

    name = "mmpx12"
    url = "https://github.com/mmpx12/proxy-list"

    enabled = True

    _URLS = [
        ("http", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt"),
        ("https", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt"),
        ("socks4", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt"),
        ("socks5", "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=15)
                for proxy in self.parseProxiesFromText(r.text):
                    yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - mmpx12/{proto}: {e}")


if __name__ == '__main__':
    for proxy in Mmpx12Fetcher().fetch():
        print(proxy)
