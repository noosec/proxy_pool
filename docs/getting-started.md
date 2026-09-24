# 快速开始 · Getting Started

## 下载代码 · Get the Code

```console
git clone https://github.com/noosec/proxy_pool.git
```



## 安装依赖 · Install Dependencies

```console
pip install -r requirements.txt
```

## 更新配置 · Configure

编辑项目主目录下的 `setting.py`。常用的配置项 · common options：

```python
# API 服务 · server
HOST = "0.0.0.0"               # 监听 IP · bind address
PORT = 5010                    # 监听端口 · port

# 数据库 · database
DB_CONN = 'redis://:pwdstring@127.0.0.1:6379/0'
```

代理源采用插件式自动扫描：调度器会加载 `fetcher/sources/` 下所有 `enabled=True` 的源，无需在此配置列表；临时禁用某源请在 `PROXY_FETCHER_EXCLUDE` 中添加其类名。

Fetchers are pluggable and auto-discovered from `fetcher/sources/` (all sources with `enabled=True`); no list is needed here. Use `PROXY_FETCHER_EXCLUDE` to temporarily disable one.

更多配置见 [配置参考](configuration.md)。

## 启动项目 · Run

完整程序包含两部分：`schedule` 调度程序（采集+验证）和 `server` API 服务。
The complete program has two parts: `schedule` (crawl + validate) and `server` (API).

### 方式一 · via `proxy_pool.sh`（推荐 · recommended）

```console
./proxy_pool.sh start           # 后台启动 · start in background
./proxy_pool.sh start --fg      # 前台启动 · run in foreground
./proxy_pool.sh stop            # 停止 · stop
./proxy_pool.sh restart         # 重启 · restart
./proxy_pool.sh status          # 状态 · status
```

### 方式二 · via `proxyPool.py`

```console
python proxyPool.py schedule    # 调度程序 · scheduler
python proxyPool.py server      # API 服务 · API server
```

启动后访问 · after startup：

- API 文档 · API docs：`http://127.0.0.1:5010/api-docs`
- 图形面板 · dashboard：`http://127.0.0.1:5010/dashboard`
- 获取代理 · get a proxy：`http://127.0.0.1:5010/get`

## 运行测试 · Run Tests

```console
pip install -r requirements-test.txt

pytest                            # 全部 · all
pytest tests/unit/                # 单元测试 · unit (no external deps)
pytest tests/api/                 # API 路由测试 · API routes
pytest tests/integration/         # 集成测试 · integration (Redis/SsdbClient)
pytest --cov=. --cov-report=term-missing   # 覆盖率 · coverage
```