# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
-------------------------------------------------
"""
__author__ = 'JHao'

from random import choice

from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    def _table_for_proto(self, proto):
        """根据协议类型返回对应的 Redis hash 名。
        socks5/socks4 存独立 hash，http/multi 存主 hash。"""
        main = self.conf.tableName
        if proto in ("socks5", "socks4"):
            suffix = proto  # e.g. "use_proxy" -> "use_socks5_proxy"
            if "socks" not in suffix:
                return main.replace("proxy", f"socks{proto}_proxy")
            return f"use_{proto}_proxy"
        return main

    def get(self, https=False, proto=None, region=None):
        """返回一个代理。proto 可选过滤（http/socks5/multi），region 可选过滤（国家码，大小写不敏感）。"""
        if region:
            candidates = self.getAll(https, proto=proto, region=region)
            return choice(candidates) if candidates else None
        target_tables = [self._table_for_proto(proto)] if proto else [self.conf.tableName]
        for table in target_tables:
            self.db.changeTable(table)
            proxy = self.db.get(https)
            if proxy:
                p = Proxy.createFromJson(proxy)
                # proto 精确过滤：旧数据 proto=None 时按 http 处理
                actual_proto = getattr(p, "proto", None) or "http"
                if proto and actual_proto not in (proto, "multi"):
                    continue
                return p
        self.db.changeTable(self.conf.tableName)
        return None

    def pop(self, https, proto=None):
        """return and delete a useful proxy"""
        target_tables = [self._table_for_proto(proto)] if proto else [self.conf.tableName]
        for table in target_tables:
            self.db.changeTable(table)
            proxy = self.db.pop(https)
            if proxy:
                self.db.changeTable(self.conf.tableName)
                return Proxy.createFromJson(proxy)
        self.db.changeTable(self.conf.tableName)
        return None

    def put(self, proxy):
        """put proxy into use proxy（按 proto 自动选 hash）"""
        table = self._table_for_proto(getattr(proxy, "proto", "http"))
        self.db.changeTable(table)
        self.db.put(proxy)
        self.db.changeTable(self.conf.tableName)

    def delete(self, proxy):
        """delete useful proxy"""
        # 可能在任一 hash 里，挨个查
        for table in (self.conf.tableName, "use_socks5_proxy", "use_socks4_proxy"):
            self.db.changeTable(table)
            if self.db.exists(proxy.proxy):
                self.db.delete(proxy.proxy)
        self.db.changeTable(self.conf.tableName)

    def getAll(self, https=False, proto=None, region=None):
        """get all proxy from pool as Proxy list"""
        all_proxies = []
        tables = [self.conf.tableName]
        for extra in ("use_socks5_proxy", "use_socks4_proxy"):
            if extra not in tables:
                tables.append(extra)
        for table in tables:
            self.db.changeTable(table)
            proxies = self.db.getAll(https)
            for _ in proxies:
                p = Proxy.createFromJson(_)
                # proto 精确过滤：旧数据 proto=None 时按 http 处理
                actual_proto = getattr(p, "proto", None) or "http"
                if proto and actual_proto not in (proto, "multi"):
                    continue
                if region and (getattr(p, "region", "") or "").upper() != region.upper():
                    continue
                all_proxies.append(p)
        self.db.changeTable(self.conf.tableName)
        return all_proxies

    def exists(self, proxy):
        """check proxy exists"""
        for table in (self.conf.tableName, "use_socks5_proxy", "use_socks4_proxy"):
            self.db.changeTable(table)
            if self.db.exists(proxy.proxy):
                self.db.changeTable(self.conf.tableName)
                return True
        self.db.changeTable(self.conf.tableName)
        return False

    def getCount(self):
        """return raw_proxy and use_proxy count"""
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}
