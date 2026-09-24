# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     thespeedx.py
   Description :   TheSpeedX/PROXY-List 代理源（每 30 分钟更新，含 HTTP + SOCKS5）
   Author：        JHao
   date：          2026/09/24
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class TheSpeedXFetcher(BaseFetcher):
    """TheSpeedX/PROXY-List https://github.com/TheSpeedX/PROXY-List"""

    name = "thespeedx"
    url = "https://github.com/TheSpeedX/PROXY-List"

    enabled = True

    _URLS = [
        ("http", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"),
        ("https", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt"),
        ("socks4", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt"),
        ("socks5", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"),
    ]

    def fetch(self):
        for proto, url in self._URLS:
            try:
                r = WebRequest().get(url, timeout=10)
                for proxy in self.parseProxiesFromText(r.text):
                    yield proxy
            except Exception as e:
                logger.error(f"ProxyFetch - thespeedx/{proto}: {e}")


if __name__ == '__main__':
    for proxy in TheSpeedXFetcher().fetch():
        print(proxy)
