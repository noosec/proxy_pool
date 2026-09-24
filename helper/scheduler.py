# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
-------------------------------------------------
"""
__author__ = 'JHao'

from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler

# 健康代理降频复验间隔（分钟）：最近一次校验通过且零失败的代理，
# 距上次校验不足该间隔时本轮跳过。校验任务每 2 分钟跑一轮，
# 即健康代理实际复验频率从 2 分钟降到 10 分钟，校验 CPU 开销降一个量级。
STABLE_RECHECK_MINUTES = 10


def __runProxyFetch():
    proxy_queue = Queue()
    proxy_fetcher = Fetcher()

    for proxy in proxy_fetcher.run():
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)


def __runProxyCheck():
    proxy_handler = ProxyHandler()
    proxy_queue = Queue()
    if proxy_handler.db.getCount().get("total", 0) < proxy_handler.conf.poolSizeMin:
        __runProxyFetch()
    now = datetime.now()
    for proxy in proxy_handler.getAll():
        # 健康代理降频：上次校验通过且当前零失败的，间隔内跳过本轮复验
        if proxy.last_status and not proxy.fail_count and proxy.last_time:
            try:
                last = datetime.strptime(proxy.last_time, "%Y-%m-%d %H:%M:%S")
            except (TypeError, ValueError):
                last = None
            if last and now - last < timedelta(minutes=STABLE_RECHECK_MINUTES):
                continue
        proxy_queue.put(proxy)
    Checker("use", proxy_queue)


def runScheduler():
    __runProxyFetch()

    timezone = ConfigHandler().timezone
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    scheduler.add_job(__runProxyFetch, 'interval', minutes=5, id="proxy_fetch", name="proxy采集")
    scheduler.add_job(__runProxyCheck, 'interval', minutes=2, id="proxy_check", name="proxy检查")
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()
