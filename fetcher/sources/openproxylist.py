# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     openproxylist.py
   Description :   api.openproxylist.xyz 代理源（独立 API，量大，需过滤无效 IP）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

# openproxylist 返回里常含 0.0.0.0:80 这类占位符，必须过滤
_INVALID_HOSTS = {"0.0.0.0", "127.0.0.1", "localhost"}


class OpenProxyListFetcher(BaseFetcher):
    """api.openproxylist.xyz — 社区代理列表 API"""

    name = "openproxylist"
    url = "https://openproxylist.xyz"

    enabled = True

    _URLS = [
        ("http", "https://api.openproxylist.xyz/http.txt"),
        ("https", "https://api.openproxylist.xyz/https.txt"),
        ("socks4", "https://api.openproxylist.xyz/socks4.txt"),
        ("socks5", "https://api.openproxylist.xyz/socks5.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=10)
                for proxy in self.parseProxiesFromText(r.text):
                    host = proxy.split(":")[0]
                    if host not in _INVALID_HOSTS:
                        yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - openproxylist/{proto}: {e}")


if __name__ == '__main__':
    for proxy in OpenProxyListFetcher().fetch():
        print(proxy)
