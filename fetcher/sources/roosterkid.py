# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     roosterkid.py
   Description :   roosterkid/openproxylist 代理源（每小时更新，HTTPS 密度高）
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


class RoosterKidFetcher(BaseFetcher):
    """roosterkid/openproxylist https://github.com/roosterkid/openproxylist"""

    name = "roosterkid"
    url = "https://github.com/roosterkid/openproxylist"

    enabled = True  # 是否启用

    def fetch(self):
        try:
            r = WebRequest().get(
                "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
                timeout=10)
            for proxy in self.parseProxiesFromText(r.text):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - roosterkid: %s" % e)


if __name__ == '__main__':
    for proxy in RoosterKidFetcher().fetch():
        print(proxy)
