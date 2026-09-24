# 项目结构 · Project Structure

```
proxy_pool/
├── api/                    # API 服务 · API server
│   └── proxyApi.py         #   Flask RESTful 接口 · RESTful endpoints
├── db/                     # 数据库层 · database layer
│   ├── dbClient.py         #   抽象接口 · abstract interface
│   ├── redisClient.py      #   Redis 实现 · Redis backend
│   └── ssdbClient.py       #   SSDB 实现 · SSDB backend
├── fetcher/                # 代理采集 · fetchers
│   ├── baseFetcher.py      #   BaseFetcher 基类 · base class
│   └── sources/            #   各代理源独立文件 · one file per source
│       ├── zdaye.py        #     站大爷
│       ├── kxdaili.py      #     开心代理
│       ├── monosans.py     #     Monosans (http/socks4/socks5)
│       ├── roosterkid.py   #     Roosterkid (HTTPS)
│       └── ...             #     其他源 · more
├── handler/                # 业务处理器 · handlers
│   ├── configHandler.py    #   配置读取 · config
│   ├── logHandler.py       #   日志处理 · logging
│   └── proxyHandler.py     #   代理 CRUD · proxy CRUD
├── helper/                 # 核心辅助模块 · core helpers
│   ├── scheduler.py        #   APScheduler 定时调度 · scheduler
│   ├── validator.py        #   代理校验 · validators
│   ├── proxy.py            #   代理数据模型 · proxy model
│   ├── fetch.py            #   采集任务执行 · fetch runner
│   └── check.py            #   校验任务执行 · check runner
├── util/                   # 工具库 · utilities
│   ├── singleton.py        #   单例元类 · singleton metaclass
│   ├── lazyProperty.py     #   惰性属性 · lazy property
│   ├── six.py              #   Python 2/3 兼容层 · compat shim
│   └── webRequest.py       #   HTTP 请求封装 · HTTP request wrapper
├── web/                    # 自包含前端页面 · self-contained frontend
│   ├── index.html          #   代理面板 /dashboard · dashboard page
│   └── api-docs.html       #   API 文档 /api-docs · API docs page
├── tests/                  # 测试 · tests
│   ├── conftest.py         #   共享 fixtures
│   ├── unit/               #   单元测试 · unit
│   ├── api/                #   API 路由测试 · API routes
│   └── integration/        #   集成测试 · integration
├── docs/                   # MkDocs 文档源 · docs source
├── proxyPool.py            # CLI 入口（click）
├── proxy_pool.sh           # 服务管理脚本 · service script
├── setting.py              # 全局配置文件 · config
├── requirements.txt        # 运行时依赖 · runtime deps
├── requirements-test.txt   # 测试依赖 · test deps
└── pyproject.toml          # pytest 配置 · pytest config
```

## 核心模块说明 · Core Modules

### `proxyPool.py` — 入口 · Entrypoint

基于 click 的 CLI，提供 `schedule`（调度采集+验证）、`server`（API 服务）、`fetcher`（查看启用源）三个子命令。
Click-based CLI with `schedule` / `server` / `fetcher` subcommands.

### `api/proxyApi.py` — API 服务

Flask 应用，提供 `/get`、`/pop`、`/all`、`/count`、`/delete`、`/stats`、`/dashboard`、`/api-docs` 等接口，运行在 `HOST:PORT`（默认 `0.0.0.0:5010`）。

### `web/` — 前端页面 · Frontend

两个自包含单文件（HTML+CSS+JS，无需构建）· Two self-contained single-file pages (no build step)：

- `index.html`：`/dashboard` 代理面板（统计卡片、来源/地域分布、获取代理、日志、最近代理表）
- `api-docs.html`：`/api-docs` API 文档（接口/参数/样例，样例带一键复制）

### `db/` — 数据库层

`dbClient.py` 定义统一接口，`redisClient.py` / `ssdbClient.py` 分别实现 Redis / SSDB。SOCKS 代理存独立 hash（`use_socks5_proxy` / `use_socks4_proxy`）。

### `fetcher/` — 代理采集

插件架构：`baseFetcher.py` 定义 `BaseFetcher` 基类，每个源在 `sources/` 下独立文件，继承 `BaseFetcher` 并实现 `fetch()`。支持 `default_proto` 声明协议（socks5 源需覆盖）。

### `helper/scheduler.py` — 定时调度

APScheduler 驱动采集与校验；内含 `STABLE_RECHECK_MINUTES` 健康代理降频复验。

### `helper/validator.py` — 代理校验

按 `proxy.proto` 分支走不同校验链路（HTTP/HTTPS 走隧道校验，SOCKS 走 requests+PySocks）。

### `handler/` — 业务处理

`configHandler.py`（配置）、`logHandler.py`（日志）、`proxyHandler.py`（代理 CRUD，含 protocol/region 过滤）。

### `setting.py` — 配置中心

所有运行时配置集中于此，见 [配置参考](configuration.md)。