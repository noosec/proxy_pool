# API 使用 · API Reference

## 接口列表 · Endpoint Overview

启动 ProxyPool 的 `server` 后，提供如下 HTTP 接口（均为 GET，返回 JSON）· After starting `server`, the following HTTP endpoints are available (all GET, JSON responses)：

| 接口 · Endpoint | 方法 · Method | 说明 · Description | 参数 · Params |
|------|:---:|------|------|
| `/` | GET | 返回 API 列表 · API list | 无 · — |
| `/get` | GET | 随机返回一个代理 · Get one proxy | `?type=http/https/socks4/socks5`；`?region=CN`；`?check=1` |
| `/pop` | GET | 返回并删除一个代理 · Pop (get & delete) | `?type=http/https/socks4/socks5` |
| `/all` | GET | 返回所有代理 · List all proxies | `?type=http/https/socks4/socks5` |
| `/count` | GET | 返回代理数量统计 · Count | 无 · — |
| `/delete` | GET | 删除指定代理 · Delete one proxy | `?proxy=host:port` |
| `/stats` | GET | 聚合统计 · Aggregated stats | 无 · — |
| `/dashboard` | GET | 图形化代理面板 · Web dashboard (HTML) | 无 · — |
| `/api-docs` | GET | API 调用说明文档 · API docs page (HTML) | 无 · — |

在浏览器打开 `http://127.0.0.1:5010/dashboard` 查看图形化面板，`http://127.0.0.1:5010/api-docs` 查看带复制按钮的 API 文档页。

---

## 协议类型 · Protocol Types

代理返回 JSON 中包含 `proto` 字段，标识代理底层协议 · The `proto` field identifies the underlying protocol：

| `proto` | 含义 · Meaning |
|------|------|
| `http` | HTTP 代理 · HTTP proxy |
| `socks4` | SOCKS4 代理 · SOCKS4 proxy |
| `socks5` | SOCKS5 代理 · SOCKS5 proxy |
| `multi` | 多协议代理 · Multi-protocol proxy |

### `type` 过滤语义 · `type` Filter Semantics

- `type=http` → `proto=http` 的代理（`https` 可为 true 或 false）
- `type=https` → **http 协议 + 支持 https**：`proto=http` 且 `https=true`，**不含 socks5/socks4**（即使其 `https` 字段为 true）
- `type=socks4` / `type=socks5` → 对应 `proto` 的代理

> 代理协议中不存在 `https` 这个 `proto` 值；`https` 是布尔标志，表示该 http 代理能否通过 CONNECT 隧道访问 https 目标。
> There is no `https` protocol value — `https` is a boolean flag indicating whether an http proxy can tunnel to https targets.

SOCKS4/SOCKS5 代理存储于独立的 Redis hash（`use_socks5_proxy` / `use_socks4_proxy`），与 HTTP 池互不干扰。

### 地域过滤 · Region Filter

`/get` 支持 `?region=CN` 按国家码过滤（大小写不敏感）；`/stats` 的 `by_region` 字段返回按地域降序的分布数组（未知地域归「未知」）。

---

## 调用示例 · Examples

### 在爬虫中使用 · Use in Python

```python
import requests


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def get_html():
    retry_count = 5
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            html = requests.get(
                "http://www.example.com",
                proxies={
                    "http": "http://{}".format(proxy),
                    "https": "http://{}".format(proxy),
                },
            )
            return html
        except Exception:
            retry_count -= 1
            delete_proxy(proxy)
    return None
```

### 获取 HTTPS 代理 · Get an HTTPS Proxy

```python
# 只获取 http 协议且支持 https 的代理 · http proxies that support https
proxy = requests.get("http://127.0.0.1:5010/get/?type=https").json()
```

### 获取 SOCKS5 代理 · Get a SOCKS5 Proxy

```python
proxy = requests.get("http://127.0.0.1:5010/get/?type=socks5").json()
```

### 按地域获取 · Filter by Region

```python
proxy = requests.get("http://127.0.0.1:5010/get/?region=CN").json()
```

### 现场拨测后返回 · Live-dial Before Returning

`/get/?check=1` 会先从池中抽一个代理并现场拨测（最多试 6 个），拨测不通过即从池中剔除换下一个，返回的一定是当前可用的代理：

```python
# 返回的代理已经过现场验证 · verified on the fly
proxy = requests.get("http://127.0.0.1:5010/get/?check=1").json()
# 指定协议 + 现场拨测 · with protocol + live dial
proxy = requests.get("http://127.0.0.1:5010/get/?type=socks5&check=1").json()
```

### 获取代理统计 · Get Stats

```python
# /count 返回数量、http/https 分布、来源分布 · count + type/source breakdown
stats = requests.get("http://127.0.0.1:5010/count/").json()

# /stats 返回更完整的聚合统计 · richer aggregated stats
full = requests.get("http://127.0.0.1:5010/stats").json()
# full 包含: total / https / by_proto / by_source / by_region / recent / fetch_log / check_log
```

---

## 直接读取数据库 · Read Database Directly

除 API 外也可直接读库。当前支持 Redis 和 SSDB，存储结构均为 hash，hash name 为配置项 `TABLE_NAME`（默认 `use_proxy`；SOCKS 代理存于 `use_socks5_proxy` / `use_socks4_proxy` 独立 hash）。

Besides the API, you can read the database directly. Both Redis and SSDB use a hash structure; the hash name is the `TABLE_NAME` config (default `use_proxy`; SOCKS proxies are stored in separate `use_socks5_proxy` / `use_socks4_proxy` hashes).