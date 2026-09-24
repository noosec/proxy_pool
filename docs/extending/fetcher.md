# 扩展代理源 · Extending Proxy Sources

项目默认包含多个免费的代理获取源，但免费源的质量毕竟有限，直接运行可能拿到的代理质量不理想。因此提供用户自定义扩展代理获取的方法。

This project ships several free proxy sources, but free sources are limited in quality. You can add your own fetchers to pull higher-quality proxies.

## 添加新的代理源 · Adding a New Source

### 第一步：创建代理源文件 · Step 1: Create the fetcher file

在 `fetcher/sources/` 目录下新建一个 `.py` 文件，继承 `BaseFetcher` 基类，实现 `fetch()` 方法：

Create a `.py` file under `fetcher/sources/`, subclass `BaseFetcher`, and implement `fetch()`:

```python
# fetcher/sources/mySource.py

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class MySourceFetcher(BaseFetcher):
    """我的代理源 https://example.com/proxy"""

    name = "mysource"                   # 唯一标识，用于日志 · unique id, used in logs
    url = "https://example.com/proxy"   # 源网站首页 · source homepage
    enabled = True                      # 设为 False 可禁用 · set False to disable

    def fetch(self):
        """yield "host:port" 格式的代理字符串 · yield "host:port" proxies"""
        r = WebRequest().get(self.url, timeout=10)
        for proxy in self.parseProxiesFromText(r.text):
            yield proxy


if __name__ == '__main__':
    for proxy in MySourceFetcher().fetch():
        print(proxy)
```

添加完成后，调度器下一轮采集（默认 5 分钟）会自动发现并启用新源，**无需修改任何配置文件**。

The scheduler auto-discovers and enables the new source on the next fetch cycle (default 5 minutes), with **no config file changes required**.

### 第二步：验证 · Step 2: Verify

独立调试代理源 · Debug a single source:

```bash
python -m fetcher.sources.mySource
```

查看当前启用的代理源 · List enabled sources:

```bash
python proxyPool.py fetcher
```

## 禁用代理源 · Disabling a Source

有两种方式禁用某个代理源 · Two ways to disable a source:

**方式一：修改源文件（推荐）· Option 1: edit the source file (recommended)**

在对应 py 文件中将 `enabled` 设为 `False` · Set `enabled` to `False`:

```python
class MySourceFetcher(BaseFetcher):
    enabled = False  # 禁用该源 · disable this source
```

**方式二：黑名单配置 · Option 2: exclusion list**

在 `setting.py` 的 `PROXY_FETCHER_EXCLUDE` 列表中添加类名，无需修改源文件 · Add the class name to `PROXY_FETCHER_EXCLUDE` in `setting.py`:

```python
PROXY_FETCHER_EXCLUDE = ["MySourceFetcher"]
```

## BaseFetcher 基类 · The BaseFetcher Base Class

所有代理源必须继承 `BaseFetcher`，基类提供以下约定和工具 · All sources must subclass `BaseFetcher`:

### 必须声明的属性 · Required attributes

| 属性 · Attribute | 类型 · Type | 说明 · Description |
|------|------|------|
| `name` | str | 唯一标识，用于日志和代理来源标记 · unique id for logs and proxy origin |
| `url` | str | 源网站首页 URL · source homepage URL |

### 可选属性 · Optional attributes

| 属性 · Attribute | 类型 · Type | 默认值 · Default | 说明 · Description |
|------|------|--------|------|
| `enabled` | bool | `True` | 是否启用 · whether enabled |
| `default_proto` | str | `"http"` | 代理协议类型（`http`/`socks4`/`socks5`）。SOCKS 源必须覆盖为对应值，采集的代理才会走 SOCKS 校验链路并存入独立 hash 表 · proxy protocol. SOCKS sources must override it so proxies go through the SOCKS validation chain and are stored in the dedicated hash |

```python
class MySocksFetcher(BaseFetcher):
    name = "mysocks"
    url = "https://example.com/socks5"
    default_proto = "socks5"   # 声明该源产出 SOCKS5 代理 · declare SOCKS5 output
```

### 必须实现的方法 · Required method

| 方法 · Method | 说明 · Description |
|------|------|
| `fetch(self)` | 生成器，yield `"host:port"` 格式字符串 · generator yielding `"host:port"` |

### 共享解析工具 · Shared parsing helpers

| 方法 · Method | 说明 · Description |
|------|------|
| `parseProxiesFromText(text)` | 从纯文本中用正则提取 ip:port · regex-extract ip:port from text |
| `yieldUniqueProxies(proxies)` | 去重 yield · yield with dedup |

## 运行时热更新 · Runtime Hot-Reload

调度器每轮采集时会重新扫描 `fetcher/sources/` 目录并 reload 模块，因此 · The scheduler rescans and reloads `fetcher/sources/` every cycle, so:

- 新增文件 → 下一轮自动启用 · new file → auto-enabled next cycle
- 修改文件内容 → 下一轮自动加载新版本 · modified file → new version auto-loaded
- 删除文件 → 下一轮自动移除（建议先从 `PROXY_FETCHER_EXCLUDE` 或 `enabled` 中禁用）· deleted file → auto-removed (disable via `PROXY_FETCHER_EXCLUDE` or `enabled` first)

## 命名规范 · Naming Conventions

| 元素 · Element | 风格 · Style | 示例 · Example |
|------|------|------|
| 文件名 · filename | 小写 · lowercase | `mysource.py` |
| 类名 · class name | PascalCase | `MySourceFetcher` |
| `name` 属性 · name attr | 小写 · lowercase | `"mysource"` |