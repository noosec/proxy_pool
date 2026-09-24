---
hide:
  - navigation
  - toc
---

<div class="tx-hero" markdown>

# ProxyPool

**Python 爬虫代理 IP 池** — 定时采集、验证、存储免费代理，通过 RESTful API 提供服务。
**Free proxy IP pool for Python** — crawls, validates and stores free proxies, served via RESTful API.

支持 HTTP / HTTPS / SOCKS4 / SOCKS5 四种协议。

[:octicons-mark-github-16: GitHub](https://github.com/noosec/proxy_pool){ .md-button }
[:octicons-rocket-16: 快速开始](getting-started.md){ .md-button .md-button--primary }

</div>

<div class="tx-features" markdown>

<div class="tx-feature" markdown>

### :material-access-point-network: 多源采集 · Multi-source

内置 25+ 免费代理源，插件式扩展，定时自动采集。

</div>

<div class="tx-feature" markdown>

### :material-shield-check: 自动验证 · Auto-validation

HTTP/HTTPS/SOCKS4/SOCKS5 按协议分链路校验，剔除失效代理。

</div>

<div class="tx-feature" markdown>

### :material-flash: 现场拨测 · Live dial

`GET /get/?check=1` 返回前即时验证，失败当场剔除，拿到即用。

</div>

<div class="tx-feature" markdown>

### :material-database: 持久存储 · Persistence

Redis/SSDB 持久化存储，代理按协议分 hash。

</div>

<div class="tx-feature" markdown>

### :material-api: RESTful API

提供 `/get`、`/pop`、`/all`、`/count`、`/delete`、`/stats` 等接口。

</div>

<div class="tx-feature" markdown>

### :material-monitor-dashboard: 图形化面板 · Dashboard

内置 `/dashboard` 面板与 `/api-docs` 文档页，开箱即用。

</div>

</div>

---

## 快速开始 · Quick Start

```bash
# 克隆项目 · clone
git clone https://github.com/noosec/proxy_pool.git
cd proxy_pool

# 安装依赖 · install
pip install -r requirements.txt

# 启动调度程序（采集和验证代理）· start scheduler (crawl + validate)
python proxyPool.py schedule

# 启动 API 服务 · start API server
python proxyPool.py server
```



启动后访问 `http://127.0.0.1:5010/get` 获取一个代理，`http://127.0.0.1:5010/dashboard` 查看面板，`http://127.0.0.1:5010/api-docs` 查看 API 文档。

## API 示例 · API Example

```python
import requests

# 获取代理 · get one proxy
proxy = requests.get("http://127.0.0.1:5010/get/").json()

# 使用代理 · use it
html = requests.get(
    "http://www.example.com",
    proxies={"http": f"http://{proxy['proxy']}", "https": f"http://{proxy['proxy']}"},
)
```

## 文档导航 · Documentation

| 章节 · Section | 说明 · Description |
|------|------|
| [快速开始](getting-started.md) | 安装、配置、启动项目 · Install & run |
| [项目结构](project-structure.md) | 目录结构与核心模块 · Structure & modules |
| [配置参考](configuration.md) | `setting.py` 全部配置项 · Config reference |
| [API 使用](api.md) | RESTful API 端点与示例 · API reference |
| [扩展代理源](extending/fetcher.md) | 自定义代理采集 · Extend fetchers |
| [扩展校验器](extending/validator.md) | 自定义代理校验 · Extend validators |
| [变更日志](changelog.md) | 版本发布记录 · Changelog |