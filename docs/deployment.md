# 部署手册（面向 AI 编码助手） · Deployment Guide (for AI Coding Assistants)

本文档是**面向 AI 编码助手 / 智能体**的可执行部署手册：所有命令均可逐字复制执行，并在关键步骤后给出「校验点」判断是否成功。目标环境为 Linux（含 Raspberry Pi / Debian 系），生产运行采用 **Redis + gunicorn + APScheduler + systemd**。

This is an **executable deployment guide for AI coding assistants**: every command can be copied verbatim, and each key step is followed by a **verification point**. Target environment is Linux (incl. Raspberry Pi / Debian), production runs on **Redis + gunicorn + APScheduler + systemd**.

## 0. 前置条件 · Prerequisites

| 组件 · Component | 版本要求 · Requirement | 用途 · Purpose |
|------|------|------|
| Python | ≥ 3.10（推荐）· ≥ 3.10 recommended | 运行服务 · runtime |
| Redis | ≥ 5.0 | 代理存储 · proxy storage |
| systemd | 任意 · any | 常驻进程 · daemonize |
| pip / venv | 任意 · any | 依赖安装 · deps |

> 本项目仅支持 Redis / SSDB 两种存储后端（见 `setting.py` 的 `DB_CONN`）。以下以 Redis 为例。
> Only Redis and SSDB backends are supported. Redis is used below.

## 1. 获取代码 · Get the Code

```bash
git clone https://github.com/noosec/proxy_pool.git /opt/proxy_pool
cd /opt/proxy_pool
```

> 校验点 · Verify：`ls proxyPool.py setting.py` 两个文件均存在。
> Verify: both `proxyPool.py` and `setting.py` exist.

## 2. 创建虚拟环境并安装依赖 · Create venv & Install Deps

```bash
cd /opt/proxy_pool
python3 -m venv venv
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt
```

> 校验点 · Verify：`./venv/bin/python -c "import flask, redis, apscheduler, gunicorn, lxml, socks"` 无报错。
> Verify: the import check exits without error.

## 3. 准备 Redis · Provision Redis

Debian 系安装并启动 · Install & start on Debian:

```bash
sudo apt-get update && sudo apt-get install -y redis-server
sudo systemctl enable --now redis-server
```

模式一：无密码（本机开发/内网）· Mode 1: no password (local/LAN):

```bash
redis-cli ping   # 期望输出 PONG · expect PONG
```

模式二：设置密码 · Mode 2: with password（编辑 `/etc/redis/redis.conf` 设置 `requirepass`）:

```bash
redis-cli -a '<password>' ping
```

> 校验点 · Verify：`redis-cli ping` 返回 `PONG`。
> Verify: `redis-cli ping` returns `PONG`.

## 4. 配置 · Configure

所有运行时配置集中在 `setting.py`，且支持**环境变量覆盖**（优先级高于文件）· All runtime config lives in `setting.py` and can be overridden by **env vars** (higher priority).

**必须修改 · Required** 的只有一项：`DB_CONN`（Redis 连接串，格式 `redis://:密码@host:port/db`；无密码用 `redis://@host:port/db`）。

Only one item is **required**: `DB_CONN` (Redis URI, format `redis://:password@host:port/db`; omit password as `redis://@host:port/db`).

两种写法，二选一 · Pick one:

```bash
# 方式一：直接改 setting.py · Option 1: edit setting.py
# DB_CONN = 'redis://@127.0.0.1:6379/0'

# 方式二：systemd 单元里注入环境变量（更推荐，见第 6 节）
# Option 2 (recommended): inject via systemd Environment= (see step 6)
```

其他常用配置（均可环境变量覆盖）· Other common configs (all env-overridable):

| 配置项 · Config | 环境变量 · Env Var | 默认 · Default | 说明 · Description |
|------|------|------|------|
| `HOST` / `PORT` | `HOST` / `PORT` | `0.0.0.0` / `5010` | API 监听地址 · bind |
| `TIMEZONE` | `TIMEZONE` | `Asia/Shanghai` | 调度器时区 · scheduler TZ |
| `HTTP_URL` / `HTTPS_URL` | `HTTP_URL` / `HTTPS_URL` | `baidu` | 校验目标 · validation target |
| `VERIFY_TIMEOUT` | `VERIFY_TIMEOUT` | `10` | 校验超时（秒）· timeout |
| `POOL_SIZE_MIN` | `POOL_SIZE_MIN` | `20` | 触发抓取阈值 · fetch trigger |
| `PROXY_REGION` | `PROXY_REGION` | `True` | 是否采集地域 · region attr |

## 5. 冒烟启动（先不常驻，确认能跑通）· Smoke Test (foreground, before daemonizing)

分别开两个终端跑，观察日志 · Run in two terminals and watch logs:

```bash
# 终端 1：API 服务 · Terminal 1: API server
./venv/bin/python proxyPool.py server

# 终端 2：调度器 · Terminal 2: scheduler
./venv/bin/python proxyPool.py schedule
```

> 校验点 · Verify：
> - 终端 1 无 `Traceback`，且 `curl http://127.0.0.1:5010/count` 返回 JSON。
> - 终端 2 打印 `ProxyPool Version`、`DB_TYPE: REDIS` 后进入定时循环。
> - Terminal 1 has no traceback and `curl http://127.0.0.1:5010/count` returns JSON; Terminal 2 prints version + `DB_TYPE: REDIS` then loops.

确认无误后 `Ctrl+C` 停掉两个进程，进入常驻化。· Once confirmed, kill both and proceed to daemonize.

## 6. systemd 常驻化（推荐）· Daemonize with systemd (recommended)

创建专用运行用户并授权 · Create a dedicated run user:

```bash
sudo useradd --system --home /opt/proxy_pool --shell /usr/sbin/nologin proxy
sudo chown -R proxy:proxy /opt/proxy_pool
```

写入两个单元文件 · Write two unit files:

**`/etc/systemd/system/proxy-pool-api.service`**:

```ini
[Unit]
Description=ProxyPool API server (gunicorn)
After=network.target redis-server.service

[Service]
Type=simple
User=proxy
WorkingDirectory=/opt/proxy_pool
Environment=DB_CONN=redis://@127.0.0.1:6379/0
Environment=PORT=5010
ExecStart=/opt/proxy_pool/venv/bin/python proxyPool.py server
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/proxy-pool-scheduler.service`**:

```ini
[Unit]
Description=ProxyPool scheduler (APScheduler fetch + check)
After=network.target redis-server.service

[Service]
Type=simple
User=proxy
WorkingDirectory=/opt/proxy_pool
Environment=DB_CONN=redis://@127.0.0.1:6379/0
Environment=TIMEZONE=Asia/Shanghai
ExecStart=/opt/proxy_pool/venv/bin/python proxyPool.py schedule
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

> 若 Redis 设了密码，把 `Environment=DB_CONN=...` 改成 `redis://:你的密码@127.0.0.1:6379/0`。
> If Redis has a password, change `DB_CONN` to `redis://:PASSWORD@127.0.0.1:6379/0`.

启用并启动 · Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now proxy-pool-api proxy-pool-scheduler
```

> 校验点 · Verify：`sudo systemctl status proxy-pool-api proxy-pool-scheduler --no-pager` 均为 `active (running)`。
> Verify: both units are `active (running)`.

## 7. （可选）轻量脚本管理 · (Optional) Lightweight Script Manager

项目自带 `proxy_pool.sh`，用 PID 文件管理（不依赖 systemd）· Ships a `proxy_pool.sh` manager using PID files:

```bash
./proxy_pool.sh start     # 后台启动 · background start
./proxy_pool.sh status    # 查看状态 · status
./proxy_pool.sh stop      # 停止 · stop
./proxy_pool.sh restart   # 重启 · restart
```

## 8. 最终校验清单 · Final Verification Checklist

部署完成后，逐条执行并确认 · Run each and confirm:

```bash
# 1) 服务健康 · health
curl -s http://127.0.0.1:5010/count
# 期望 JSON 含 total 字段 · expect JSON with "total"

# 2) 随机取一个 http 代理 · fetch an http proxy
curl -s "http://127.0.0.1:5010/get"

# 3) 池内统计 · pool stats
curl -s http://127.0.0.1:5010/stats

# 4) 面板可访问 · dashboard reachable
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5010/dashboard   # 期望 200

# 5) API 文档可访问 · api-docs reachable
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5010/api-docs   # 期望 200
```

日志排障 · Logs for troubleshooting:

```bash
sudo journalctl -u proxy-pool-api -f        # API 日志 · API logs
sudo journalctl -u proxy-pool-scheduler -f  # 调度日志 · scheduler logs
```

## 9. 关键坑与注意事项 · Gotchas

1. **gunicorn `timeout=60`**：`/get/?check=1` 现场拨测最坏 24s，若把 gunicorn 超时压到默认 30s 会把 worker abort（`SystemExit` 是 `BaseException`，`except Exception` 接不住 → 500）。勿改小 `runFlask()` 里的 `timeout`。
   The `/get/?check=1` live-check takes up to 24s worst-case; a gunicorn timeout ≤ 30s aborts the worker → 500. Do not lower `timeout` in `runFlask()`.

2. **SOCKS5 校验依赖 PySocks**：`socks5h://` 链路需要 `PySocks`（已登记在 `requirements.txt`）。若报 `socks` 相关错误，先 `pip install -r requirements.txt` 重装。
   SOCKS5 validation needs `PySocks` (already in `requirements.txt`).

3. **时区**：`TIMEZONE` 影响 APScheduler 的 cron/interval 与日志时间戳，同步目标机时区需与 `Setting.py` 一致，否则报 `Timezone offset does not match system offset`。
   `TIMEZONE` must match the host timezone or APScheduler raises a timezone-offset error.

4. **`PROXY_FETCHER_EXCLUDE` 是黑名单**：源是自动扫描加载的，若要禁用某源，把类名加入 `setting.py` 的 `PROXY_FETCHER_EXCLUDE`，而非删除文件。
   Fetchers are auto-discovered; disable via `PROXY_FETCHER_EXCLUDE`, not by deleting files.

5. **免费代理漂移快**：池内代理存活时间短是正常现象；可用性兜底依赖调用方的 `?check=1` 现场拨测（见 API 文档）。
   Free proxies churn quickly; availability is ultimately guaranteed by the caller-side `?check=1` live-check.

## 10. 升级 / 回滚 · Upgrade / Rollback

```bash
cd /opt/proxy_pool
git pull
./venv/bin/pip install -r requirements.txt
sudo systemctl restart proxy-pool-api proxy-pool-scheduler
```

> 回滚：`git checkout <tag-or-commit>` 后重启两个单元即回退到旧版本。
> Rollback: `git checkout <tag-or-commit>` then restart both units.