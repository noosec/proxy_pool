# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hookzof.py
   Description :   hookzof/socks5_list 代理源（socks5 大户，19798 个）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class HookzofFetcher(BaseFetcher):
    """hookzof/socks5_list https://github.com/hookzof/socks5_list"""

    name = "hookzof"
    url = "https://github.com/hookzof/socks5_list"

    enabled = True
    default_proto = "socks5"

    _URLS = [
        ("socks5", "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=15)
                for proxy in self.parseProxiesFromText(r.text):
                    yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - hookzof/{proto}: {e}")


if __name__ == '__main__':
    for proxy in HookzofFetcher().fetch():
        print(proxy)
