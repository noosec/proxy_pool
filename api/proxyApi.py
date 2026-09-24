# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :   WebApi
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/04: WebApi
                   2019/08/14: 集成Gunicorn启动方式
                   2020/06/23: 新增pop接口
                   2022/07/21: 更新count接口
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import platform

import requests
import urllib3
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

from util.six import iteritems
from helper.proxy import Proxy
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler

# 现场拨测走 verify=False（与 validator.py 的 https 校验一致），关掉告警噪音
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
conf = ConfigHandler()
proxy_handler = ProxyHandler()

# /get/?check=1 现场拨测：最多尝试的代理个数
LIVE_CHECK_MAX_TRIES = 6
# 现场拨测单次超时（秒）：收紧到 4s，最坏 6×4=24s，须低于 gunicorn timeout(60s)，
# 否则请求会被 gunicorn abort（SystemExit 是 BaseException，except Exception 接不住 → 500）
LIVE_CHECK_TIMEOUT = 4

_CHECK_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
    "Accept": "*/*",
    "Connection": "keep-alive",
}


def _quickCheck(proxy_str, https):
    """现场拨测（HTTP/HTTPS 代理）。"""
    proxies = {"http": "http://{0}".format(proxy_str), "https": "http://{0}".format(proxy_str)}
    url = conf.httpsUrl if https else conf.httpUrl
    try:
        r = requests.head(url, headers=_CHECK_HEADER, proxies=proxies,
                          timeout=LIVE_CHECK_TIMEOUT, verify=False, allow_redirects=False)
        return r.status_code == 200
    except Exception:
        return False


def _socks5Check(proxy_str):
    """现场拨测（SOCKS5 代理，requests + PySocks）。

    socks5h:// 让代理自己做 DNS 解析（等价 curl --socks5h）。
    2026/09/24 由 subprocess curl 改为 requests，省 fork 开销。
    """
    proxies = {"http": "socks5h://{0}".format(proxy_str),
               "https": "socks5h://{0}".format(proxy_str)}
    try:
        r = requests.head("http://www.baidu.com", headers=_CHECK_HEADER,
                          proxies=proxies, timeout=LIVE_CHECK_TIMEOUT,
                          verify=False, allow_redirects=False)
        return r.status_code == 200
    except Exception:
        return False


def _liveCheck(proxy):
    """统一现场拨测入口，按 proxy.proto 选合适的验证方式。"""
    proto = getattr(proxy, "proto", "http")
    if proto in ("socks5", "socks4"):
        return _socks5Check(proxy.proxy)
    return _quickCheck(proxy.proxy, getattr(proxy, "https", False))


def _parse_type(type_param):
    """归一化 type 参数，返回 (https, proto)。

    type=https 语义收敛为「http 协议且支持 https 的代理」：把 proto 定为 http，
    从而排除 socks5/socks4 这类 https=true 但非 http 协议的代理。
    """
    type_param = (type_param or "").lower()
    https = type_param == 'https'
    proto = type_param if type_param in ("socks5", "socks4", "http") else None
    if https:
        proto = "http"
    return https, proto


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = [
    {"url": "/get", "params": "type: 'http|https|socks4|socks5'; check: '1' 现场拨测通过才返回（最多试6个，失败即剔除）", "desc": "get a proxy"},
    {"url": "/pop", "params": "type: 'http|https|socks4|socks5'", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: 'http|https|socks4|socks5'", "desc": "get all proxy from proxy pool"},
    {"url": "/count", "params": "", "desc": "return proxy count"},
    {"url": "/stats", "params": "", "desc": "聚合统计（协议/来源分布、最近代理、日志尾部）"},
    {"url": "/dashboard", "params": "", "desc": "图形化代理面板（HTML）"},
    {"url": "/api-docs", "params": "", "desc": "API 调用说明文档（HTML）"},
    # 'refresh': 'refresh proxy pool',
]


@app.route('/')
def index():
    return {'url': api_list}


@app.route('/get/')
def get():
    https, proto = _parse_type(request.args.get("type", ""))
    region = request.args.get("region", "").strip()
    need_check = request.args.get("check", "").lower() in ("1", "true", "yes")
    if not need_check:
        proxy = proxy_handler.get(https, proto=proto, region=region)
        return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}
    # 现场拨测模式
    tried = set()
    for _ in range(LIVE_CHECK_MAX_TRIES):
        proxy = proxy_handler.get(https, proto=proto, region=region)
        if not proxy or proxy.proxy in tried:
            break
        tried.add(proxy.proxy)
        if _liveCheck(proxy):
            return proxy.to_dict
        proxy_handler.delete(proxy)
    return {"code": 0, "src": "no usable proxy after live check", "tried": len(tried)}


@app.route('/pop/')
def pop():
    https, proto = _parse_type(request.args.get("type", ""))
    proxy = proxy_handler.pop(https, proto=proto)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    return 'success'


@app.route('/all/')
def getAll():
    https, proto = _parse_type(request.args.get("type", ""))
    proxies = proxy_handler.getAll(https, proto=proto)
    return jsonify([_.to_dict for _ in proxies])


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    status = proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}


@app.route('/count/')
def getCount():
    proxies = proxy_handler.getAll()
    http_type_dict = {}
    source_dict = {}
    for proxy in proxies:
        http_type = 'https' if proxy.https else 'http'
        http_type_dict[http_type] = http_type_dict.get(http_type, 0) + 1
        for source in proxy.source.split('/'):
            source_dict[source] = source_dict.get(source, 0) + 1
    return {"http_type": http_type_dict, "source": source_dict, "count": len(proxies)}


# ---------------------------------------------------------------------------
# 统计与图形化面板
# ---------------------------------------------------------------------------

def _web_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')


def _log_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')


def _tail_log(name, n=60):
    """读取 log/ 下指定日志文件的末尾 n 行（供面板展示来源/校验动态）。"""
    path = os.path.join(_log_dir(), name)
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        return [line.rstrip('\n') for line in lines[-n:]]
    except Exception:
        return []


@app.route('/stats')
def stats():
    """聚合统计：按协议/来源分布、HTTPS 数、最近代理、采集/校验日志尾部。"""
    proxies = proxy_handler.getAll()
    by_proto = {}
    by_source = {}
    by_region = {}
    https_count = 0
    for proxy in proxies:
        proto = getattr(proxy, "proto", None) or "http"
        by_proto[proto] = by_proto.get(proto, 0) + 1
        if proxy.https:
            https_count += 1
        for src in proxy.source.split('/'):
            if src:
                by_source[src] = by_source.get(src, 0) + 1
        r = (getattr(proxy, "region", "") or "").strip().upper()
        by_region[r or "未知"] = by_region.get(r or "未知", 0) + 1
    return {
        "total": len(proxies),
        "https": https_count,
        "by_proto": by_proto,
        "by_source": sorted(by_source.items(), key=lambda x: -x[1]),
        "by_region": sorted(by_region.items(), key=lambda x: -x[1]),
        "recent": [p.to_dict for p in proxies[:20]],
        "fetch_log": _tail_log('fetcher.log'),
        "check_log": _tail_log('checker.log'),
    }


@app.route('/dashboard')
def dashboard():
    """代理面板（自包含 HTML）：统计、来源分布、获取代理、最近日志。"""
    with open(os.path.join(_web_dir(), 'index.html'), encoding='utf-8') as f:
        html = f.read()
    # app.response_class 是 JsonResponse，返回裸字符串会被标成 text/plain，
    # 这里显式指定 text/html 让浏览器按页面渲染
    return Response(html, mimetype='text/html')


@app.route('/api-docs')
def api_docs():
    """API 调用说明文档（自包含 HTML）：接口、参数、样例。"""
    with open(os.path.join(_web_dir(), 'api-docs.html'), encoding='utf-8') as f:
        html = f.read()
    return Response(html, mimetype='text/html')


def runFlask():
    if platform.system() == "Windows":
        app.run(host=conf.serverHost, port=conf.serverPort)
    else:
        import gunicorn.app.base

        class StandaloneApplication(gunicorn.app.base.BaseApplication):

            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super(StandaloneApplication, self).__init__()

            def load_config(self):
                _config = dict([(key, value) for key, value in iteritems(self.options)
                                if key in self.cfg.settings and value is not None])
                for key, value in iteritems(_config):
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        _options = {
            'bind': '%s:%s' % (conf.serverHost, conf.serverPort),
            'workers': 4,
            'timeout': 60,  # 现场拨测(check=1)最坏 24s，须高于此值避免 worker 被 abort
            'accesslog': '-',  # log to stdout
            'access_log_format': '%(h)s %(l)s %(t)s "%(r)s" %(s)s "%(a)s"'
        }
        StandaloneApplication(app, _options).run()


if __name__ == '__main__':
    runFlask()
