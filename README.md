# ProxyPool 代理 IP 池 · Proxy IP Pool

> 基于 [jhao104/proxy_pool](https://github.com/jhao104/proxy_pool)（2.x）二次开发（二开）的免费代理 IP 池。
> A free proxy IP pool, forked and extended from [jhao104/proxy_pool](https://github.com/jhao104/proxy_pool).
>
> 定时采集公开免费代理、验证入库并持续复验，通过 HTTP API 对外提供可用代理，支持 HTTP / HTTPS / SOCKS4 / SOCKS5 四种协议。
> Periodically crawls free public proxies, validates and stores them, keeps re-checking, and serves usable proxies via an HTTP API — supporting HTTP / HTTPS / SOCKS4 / SOCKS5.

---

## ✨ 特性 · Features

- **多源采集** · Multi-source crawling — 内置 25+ 免费代理源，插件式扩展，定时自动采集。
- **自动验证** · Auto validation — HTTP/HTTPS/SOCKS4/SOCKS5 按协议分链路校验，剔除失效代理。
- **HTTPS 隧道校验** · HTTPS tunnel validation — 双目标（baidu / cn.bing.com）任一 200 即认定隧道可用，修复历史上 https 代理近乎为零的问题。
- **现场拨测** · Live dial — `GET /get/?check=1` 返回前即时验证，失败当场剔除，拿到即用。
- **图形化面板** · Web dashboard — `/dashboard` 实时统计、来源/地域分布、获取代理、采集/校验日志。
- **API 文档页** · API docs page — `/api-docs` 内置接口说明、参数、调用样例（含一键复制）。
- **地域过滤** · Region filter — `?region=CN` 按国家码过滤；`/stats` 提供地域分布统计。
- **持久存储** · Persistent storage — Redis / SSDB，代理按协议分 hash 存储。

---

## 🚀 快速开始 · Quick Start

### 环境要求 · Requirements

- Python 3.8+
- Redis（或 SSDB）

### 安装 · Install

```bash
git clone https://github.com/noosec/proxy_pool.git
cd proxy_pool
pip install -r requirements.txt
```



### 配置 · Configure

编辑 `setting.py`，主要是数据库连接（默认 Redis）：

```python
DB_CONN = 'redis://:pwdstring@127.0.0.1:6379/0'
```

### 启动 · Run

```bash
# 启动调度程序（采集 + 验证代理）
python proxyPool.py schedule

# 启动 API 服务（默认 0.0.0.0:5010）
python proxyPool.py server
```

启动后在浏览器打开 `http://127.0.0.1:5010/api-docs` 查看 API 文档，或 `http://127.0.0.1:5010/dashboard` 查看图形化面板。

---

## 📖 API 接口 · API Reference

| 接口 · Endpoint | 方法 · Method | 说明 · Description | 参数 · Params |
|------|:---:|------|------|
| `/` | GET | API 列表 · API list | 无 · — |
| `/get` | GET | 随机返回一个代理 · Get one proxy | `?type=http/https/socks4/socks5`；`?region=CN`；`?check=1` |
| `/pop` | GET | 返回并删除一个代理 · Pop (get & delete) | `?type=http/https/socks4/socks5` |
| `/all` | GET | 返回所有代理 · List all proxies | `?type=http/https/socks4/socks5` |
| `/count` | GET | 代理数量统计 · Count | 无 · — |
| `/delete` | GET | 删除指定代理 · Delete one proxy | `?proxy=host:port` |
| `/stats` | GET | 聚合统计（协议/来源/地域、最近代理、日志） · Aggregated stats | 无 · — |
| `/dashboard` | GET | 图形化代理面板 · Web dashboard (HTML) | 无 · — |
| `/api-docs` | GET | API 调用说明文档 · API docs page (HTML) | 无 · — |

### 常用命令 · Common Examples

```bash
# API 列表 · API list
curl http://127.0.0.1:5010/

# 随机获取一个代理 · Get one proxy
curl http://127.0.0.1:5010/get/

# 获取 HTTPS 代理 · Get an HTTPS proxy
curl 'http://127.0.0.1:5010/get/?type=https'

# 获取 SOCKS5 代理 · Get a SOCKS5 proxy
curl 'http://127.0.0.1:5010/get/?type=socks5'

# 获取 CN 地域代理 · Get a CN proxy
curl 'http://127.0.0.1:5010/get/?region=CN'

# 现场拨测后返回（拿到即用）· Live-dial before returning
curl 'http://127.0.0.1:5010/get/?type=https&check=1'

# 删除指定代理 · Delete a proxy
curl 'http://127.0.0.1:5010/delete/?proxy=1.2.3.4:8080'
```

### 爬虫中调用 · Use in Python

```python
import requests

def get_proxy():
    # 现场拨测后返回的 HTTPS 代理，拿到即用 · live-checked, ready to use
    return requests.get("http://127.0.0.1:5010/get/?type=https&check=1").json()

proxy = get_proxy()
html = requests.get(
    "http://www.example.com",
    proxies={"http": f"http://{proxy['proxy']}", "https": f"http://{proxy['proxy']}"},
)
```

> ⚠️ 免费代理漂移快、不可信，不要通过它们传输密码 / Cookie / Token / 个人资料等敏感数据。
> Free proxies are volatile and untrusted — never send passwords, cookies, tokens or personal data through them.

---

## 🔌 协议与字段 · Protocols & Fields

代理返回 JSON 中的关键字段 · Key fields in the proxy JSON:

| 字段 · Field | 含义 · Meaning | 取值 · Values |
|------|------|------|
| `proxy` | 代理地址 · proxy address | `ip:port` |
| `proto` | 代理底层协议 · underlying protocol | `http` / `socks4` / `socks5` / `multi` |
| `https` | 是否支持 https · supports https | `true` / `false` |

**`type` 过滤语义 · `type` filter semantics：**

- `type=http` → 协议为 `http` 的代理（`https` 可为 true 或 false）
- `type=https` → **http 协议 + 支持 https**（`proto=http` 且 `https=true`，不含 socks）
- `type=socks4` / `type=socks5` → 对应 `proto` 的代理

> 代理协议中不存在 `https` 这个 `proto` 值；`https` 是布尔标志，表示这个 http 代理能否通过 CONNECT 隧道访问 https 目标。
> There is no `https` protocol value — `https` is a boolean flag indicating whether an http proxy can tunnel to https targets via CONNECT.

SOCKS4/SOCKS5 代理存储于独立的 Redis hash（`use_socks5_proxy` / `use_socks4_proxy`），与 HTTP 池互不干扰。

---

## 🌐 图形化页面 · Web Pages

- **`/dashboard`**：代理面板 —— 实时统计卡片、来源/地域分布条形图、获取代理（协议/地域/拨测）、采集/校验日志、最近代理表。
- **`/api-docs`**：API 文档 —— 全部接口的方法、参数、curl 样例、响应样例，样例代码带一键复制。

两个页面均为自包含单文件（`web/index.html`、`web/api-docs.html`），无需额外前端构建。

---

## 📁 项目结构 · Project Structure

```
proxy_pool/
├── api/                  # Flask API（proxyApi.py）
├── db/                   # 数据库层（Redis / SSDB）
├── fetcher/              # 代理采集（插件式，sources/ 下每个源一个文件）
├── handler/              # 配置/日志/代理 CRUD
├── helper/               # 调度、校验、模型、采集/检查执行
├── util/                 # 工具库（单例、web 请求、兼容层）
├── web/                  # 自包含前端页面（dashboard + api-docs）
├── docs/                 # MkDocs 文档源
├── setting.py            # 全局配置
└── proxyPool.py          # CLI 入口（schedule / server / fetcher）
```

---

## 📚 文档 · Documentation

完整文档见 [`docs/`](docs/)（MkDocs）：

- [快速开始](docs/getting-started.md) · Getting started
- [项目结构](docs/project-structure.md) · Project structure
- [配置参考](docs/configuration.md) · Configuration
- [API 使用](docs/api.md) · API reference
- [扩展代理源](docs/extending/fetcher.md) · Extend fetchers
- [扩展校验器](docs/extending/validator.md) · Extend validators
- [变更日志](docs/changelog.md) · Changelog

---

## 📝 变更日志 · Changelog

本二开版本相对上游 `jhao104/proxy_pool` 2.x 的主要改动：

- 新增 SOCKS4/SOCKS5 协议支持（`proto` 字段 + 独立分池 + 按协议校验）
- SOCKS5 校验由 curl 子进程改为 requests + PySocks
- HTTPS 校验重写为隧道校验（`httpsTunnelValidator`，双目标 OR），修复 https 代理近乎为零的历史问题
- 校验目标由 httpbin/qq 改为 baidu
- 新增 `GET /get/?check=1` 现场拨测端点
- 健康代理降频复验（`STABLE_RECHECK_MINUTES=10`）
- 新增代理源 monosans / roosterkid / hookzof / proxifly（扩展 https 子集）
- 新增 `/stats` 聚合统计、`/dashboard` 图形面板、`/api-docs` API 文档页、`?region` 地域过滤

完整明细见 [docs/changelog.md](docs/changelog.md)。

---

## 📄 许可证 · License

[LICENSE](LICENSE) — MIT License。

本项目基于开源项目 [jhao104/proxy_pool](https://github.com/jhao104/proxy_pool) 二次开发，感谢原作者 [@jhao104](https://github.com/jhao104)。
This project is a fork of [jhao104/proxy_pool](https://github.com/jhao104/proxy_pool). Thanks to the original author [@jhao104](https://github.com/jhao104).