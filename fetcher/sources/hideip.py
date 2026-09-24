# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hideip.py
   Description :   zloi-user/hideip.me 代理源（每 10 分钟更新，带国家后缀，正则自动剥）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class HideipFetcher(BaseFetcher):
    """zloi-user/hideip.me https://github.com/zloi-user/hideip.me"""

    name = "hideip"
    url = "https://github.com/zloi-user/hideip.me"

    enabled = True

    _URLS = [
        ("http", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt"),
        ("https", "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=10)
                for proxy in self.parseProxiesFromText(r.text):
                    yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - hideip/{proto}: {e}")


if __name__ == '__main__':
    for proxy in HideipFetcher().fetch():
        print(proxy)
