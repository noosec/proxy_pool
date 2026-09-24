# 配置参考 · Configuration Reference

配置文件 `setting.py` 位于项目主目录，配置分为五类：服务、数据库、采集、校验、调度。
Configuration lives in `setting.py`, grouped into: server, database, fetcher, validator, scheduler.

## 服务配置 · Server

### `HOST`

API 服务监听的 IP。本机访问用 `127.0.0.1`，远程访问用 `0.0.0.0`。
Bind address of the API server. Use `127.0.0.1` for local-only, `0.0.0.0` for remote access.

- 默认 · Default：`"0.0.0.0"`

### `PORT`

API 服务监听端口 · API port.

- 默认 · Default：`5010`

## 数据库配置 · Database

### `DB_CONN`

代理存储的数据库 URI，格式 · format：

```
db_type://[[user]:[pwd]]@ip:port/[db]
```

支持的 `db_type`：`redis`、`ssdb`。

```python
# Redis
DB_CONN = 'redis://@127.0.0.1:6379'
DB_CONN = 'redis://:123456@127.0.0.1:6379'
DB_CONN = 'redis://:123456@127.0.0.1:6379/15'

# SSDB
DB_CONN = 'ssdb://@127.0.0.1:8888'
```

### `TABLE_NAME`

代理存储的载体名称（hash name）。HTTP 代理存主表；SOCKS 代理存独立 hash（`use_socks5_proxy` / `use_socks4_proxy`）。
Storage hash name. HTTP proxies use the main table; SOCKS proxies use separate hashes (`use_socks5_proxy` / `use_socks4_proxy`).

- 默认 · Default：`"use_proxy"`

## 采集配置 · Fetcher

代理采集采用插件架构，调度器自动扫描 `fetcher/sources/` 目录，加载所有 `enabled=True` 的源。新增源只需在 `sources/` 下新建文件。
Fetchers are pluggable: the scheduler auto-scans `fetcher/sources/` and loads every source with `enabled=True`. Add a new source by dropping a file into `sources/`.

```bash
python proxyPool.py fetcher
```

### `PROXY_FETCHER_EXCLUDE`

代理源黑名单，列表中的类名不会被加载（即使 `enabled=True`）。
Blacklist of fetcher class names to skip.

```python
PROXY_FETCHER_EXCLUDE = [
    # "SomeFetcher",
]
```

## 校验配置 · Validator

### `HTTP_URL`

检验代理可用性的地址 · URL used to check proxy availability.

- 默认 · Default：`"http://www.baidu.com"`

> 由 `http://httpbin.org` 改为 baidu：httpbin 常抽风，baidu 对代理友好且 HEAD 稳定 200。

### `HTTPS_URL`

检验代理是否支持 HTTPS 的地址 · URL used to check https support.

- 默认 · Default：`"https://www.baidu.com"`

> 隧道校验采用「`HTTPS_URL` + `cn.bing.com` 双目标任一 200 即认定」的口径，见 [扩展校验器](extending/validator.md)。

### `VERIFY_TIMEOUT`

校验超时（秒）· validation timeout (seconds).

- 默认 · Default：`10`

### `MAX_FAIL_COUNT`

允许的最大失败次数，超过则剔除 · max failures before removal.

- 默认 · Default：`0`（失败一次即删 · removed after one failure）

### `POOL_SIZE_MIN`

校验任务运行前若代理数低于该值，先触发采集 · fetch first when pool drops below this.

- 默认 · Default：`20`

## 代理属性 · Proxy Attributes

### `PROXY_REGION`

是否启用代理地域属性（解析 IP 地理位置）· enable region attribute (IP geolocation).

- 默认 · Default：`True`

## 调度配置 · Scheduler

### `TIMEZONE`

调度器时区 · scheduler timezone.

- 默认 · Default：`"Asia/Shanghai"`

### `STABLE_RECHECK_MINUTES`

> 该常量位于 `helper/scheduler.py`（非 `setting.py`）· This constant lives in `helper/scheduler.py`, not `setting.py`.

健康代理降频复验间隔（分钟）：最近一次校验通过且零失败的代理，距上次校验不足该间隔时本轮跳过。校验任务每 2 分钟一轮，即健康代理实际复验频率约 10 分钟，降低校验 CPU 开销。
Interval (minutes) to skip re-checking recently-passed, zero-failure proxies. Since the check job runs every 2 minutes, healthy proxies are effectively re-checked ~every 10 minutes.

- 默认 · Default：`10`