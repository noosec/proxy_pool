# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     shiftytr.py
   Description :   ShiftyTR/Proxy-List 代理源（小而稳，40 个）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ShiftyTRFetcher(BaseFetcher):
    """ShiftyTR/Proxy-List https://github.com/ShiftyTR/Proxy-List"""

    name = "shiftytr"
    url = "https://github.com/ShiftyTR/Proxy-List"

    enabled = True

    _URLS = [
        ("http", "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"),
        ("https", "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=10)
                for proxy in self.parseProxiesFromText(r.text):
                    yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - shiftytr/{proto}: {e}")


if __name__ == '__main__':
    for proxy in ShiftyTRFetcher().fetch():
        print(proxy)
