# laofuqmt API 参考文档

本文档详细说明 `laofuqmt.py` 封装的所有 API 及其用法。
完整的接口概述和配置说明见 `SKILL.md`。

---

## 快速开始

```powershell
# 1. 确保 QMT 客户端已登录运行
# 2. 修改 config.json 中的 qmt_root 和 xtquant_path 为自己的路径
# 3. 使用系统 Python 执行（脚本内部自动加载 xtquant）
python laofuqmt.py <command> [options]
```

---

## 命令列表

### 1. `quote` — 实时行情快照

获取一只或多只股票的最新行情数据（基于最近一根日K）。

**语法：**
```
python laofuqmt.py quote --codes <代码列表>
```

**参数：**

| 参数 | 缩写 | 必填 | 说明 |
|------|------|------|------|
| `--codes` | `-c` | 是 | 股票代码，逗号分隔 |

**示例：**
```powershell
# 单只股票
python laofuqmt.py quote --codes 000001.SZ

# 多只股票（支持中文名称）
python laofuqmt.py quote --codes 平安银行,贵州茅台

# 输出到文件
python laofuqmt.py quote --codes 000001.SZ,600519.SH --output quote.json
```

**返回字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 股票代码 |
| name | string | 股票名称 |
| lastPrice | float | 最新价 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| volume | float | 成交量（股） |
| amount | float | 成交额（元） |

---

### 2. `kline` — K线数据

获取指定周期的K线数据。

**语法：**
```
python laofuqmt.py kline --code <代码> [--period <周期>] [--count <条数>] [--start <起始>] [--end <结束>]
```

**参数：**

| 参数 | 缩写 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--code` | `-c` | 是 | - | 股票代码 |
| `--period` | `-p` | 否 | 1d | K线周期 |
| `--count` | `-n` | 否 | 100 | 数据条数 |
| `--start` | - | 否 | 空 | 起始时间 YYYYMMDD |
| `--end` | - | 否 | 空 | 结束时间 YYYYMMDD |

**K线周期选项：**

| 值 | 说明 |
|------|------|
| 1m | 1分钟线 |
| 5m | 5分钟线 |
| 15m | 15分钟线 |
| 30m | 30分钟线 |
| 1h | 1小时线 |
| 1d | 日K线 |
| 1w | 周K线 |
| 1mon | 月K线 |

**示例：**
```powershell
# 平安银行最近 30 天日K
python laofuqmt.py kline --code 000001.SZ --count 30

# 茅台最近 60 根分钟线
python laofuqmt.py kline --code 贵州茅台 --period 5m --count 60

# 指定时间范围
python laofuqmt.py kline --code 000001.SZ --start 20260101 --end 20260331

# 周K线
python laofuqmt.py kline --code 600519.SH --period 1w --count 12
```

**返回字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 股票代码 |
| name | string | 股票名称 |
| period | string | K线周期 |
| count | int | 数据条数 |
| kline | array | K线数据数组 |

kline 数组中每条记录：

| 字段 | 类型 | 说明 |
|------|------|------|
| time | string | 时间 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | float | 成交量 |
| amount | float | 成交额 |

---

### 3. `tick` — 逐笔成交

获取逐笔成交数据（仅当日有效）。

**语法：**
```
python laofuqmt.py tick --code <代码> [--count <条数>]
```

**参数：**

| 参数 | 缩写 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--code` | `-c` | 是 | - | 股票代码 |
| `--count` | `-n` | 否 | 100 | 数据条数 |

**示例：**
```powershell
python laofuqmt.py tick --code 000001.SZ --count 200
```

---

### 4. `market_overview` — 大盘概览

获取主要指数的行情概览。

**语法：**
```
python laofuqmt.py market_overview
```

**包含指数：** 上证指数、深证成指、创业板指、科创50、沪深300

**返回字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 指数名称 |
| code | string | 指数代码 |
| close | float | 最新点位 |
| open | float | 今开 |
| high | float | 最高 |
| low | float | 最低 |
| prevClose | float | 昨收 |
| change | float | 涨跌额 |
| changePct | float | 涨跌幅(%) |
| volume | float | 成交量 |
| amount | float | 成交额 |

---

### 5. `finance` — 财务数据

获取股票的财务数据。

**语法：**
```
python laofuqmt.py finance --code <代码>
```

**参数：**

| 参数 | 缩写 | 必填 | 说明 |
|------|------|------|------|
| `--code` | `-c` | 是 | 股票代码 |

**示例：**
```powershell
python laofuqmt.py finance --code 002594.SZ
```

---

### 6. `blocks` — 板块列表

获取概念板块或行业板块列表。

**语法：**
```
python laofuqmt.py blocks [--type <类型>] [--keyword <关键词>]
```

**参数：**

| 参数 | 缩写 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--type` | `-t` | 否 | concept | 板块类型：concept / industry |
| `--keyword` | `-k` | 否 | 空 | 搜索关键词 |

**示例：**
```powershell
# 所有概念板块
python laofuqmt.py blocks --type concept

# 搜索包含"芯片"的板块
python laofuqmt.py blocks --keyword 芯片

# 行业板块
python laofuqmt.py blocks --type industry
```

---

### 7. `block_stocks` — 板块成分股

获取某个板块的成分股列表。

**语法：**
```
python laofuqmt.py block_stocks --block <板块名称>
```

**参数：**

| 参数 | 缩写 | 必填 | 说明 |
|------|------|------|------|
| `--block` | `-b` | 是 | 板块名称（支持模糊匹配） |

**示例：**
```powershell
python laofuqmt.py block_stocks --block 锂电池
python laofuqmt.py block_stocks --block 人工智能
```

---

### 8. `search` — 搜索股票

通过关键词搜索股票或板块。

**语法：**
```
python laofuqmt.py search --keyword <关键词>
```

**示例：**
```powershell
python laofuqmt.py search --keyword 茅台
python laofuqmt.py search --keyword 银行
python laofuqmt.py search --keyword 新能源
```

---

### 9. `subscribe` — 实时订阅

订阅实时行情数据（包含五档盘口）。

**语法：**
```
python laofuqmt.py subscribe --codes <代码列表>
```

**参数：**

| 参数 | 缩写 | 必填 | 说明 |
|------|------|------|------|
| `--codes` | `-c` | 是 | 股票代码，逗号分隔 |

**返回字段（比 quote 更详细）：**

| 字段 | 说明 |
|------|------|
| lastPrice | 最新价 |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| lastClose | 昨收 |
| volume | 成交量 |
| amount | 成交额 |
| bidPrice[0-4] | 五档买价 |
| askPrice[0-4] | 五档卖价 |
| bidVol[0-4] | 五档买量 |
| askVol[0-4] | 五档卖量 |

---

## 通用选项

所有命令都支持以下通用选项：

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--output` | `-o` | 输出到文件路径 |
| `--format` | `-f` | 输出格式：json（默认）/ table |

**示例：**
```powershell
# 表格格式输出
python laofuqmt.py market_overview --format table

# JSON 输出到文件
python laofuqmt.py kline --code 000001.SZ --count 30 --output kline_000001.json
```

---

## 股票代码格式

标准格式为：`代码.市场后缀`

| 市场后缀 | 说明 | 代码范围 |
|----------|------|----------|
| `.SZ` | 深圳主板 | 000xxx, 001xxx, 002xxx, 003xxx |
| `.SH` | 上海主板 | 600xxx, 601xxx, 603xxx, 605xxx |
| `.SZ` | 创业板 | 300xxx, 301xxx |
| `.SH` | 科创板 | 688xxx, 689xxx |
| `.SZ` | 北交所 | 8xxxxx, 4xxxxx |
| `.SH` | 指数 | 000xxx, 899xxx |

**代码简写支持：** 输入纯数字时会自动识别市场（6开头→SH，其他→SZ）。

**名称转代码：** 支持常用股票的中文名称直接输入（如"茅台"→600519.SH）。

---

## 错误处理

所有命令返回的 JSON 都包含 `success` 字段：

- `success: true` — 请求成功
- `success: false` — 请求失败，`error` 字段包含错误信息

常见错误：

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 无法导入 xtquant 模块 | xtquant 路径未正确配置 | 检查 config.json 中的 xtquant_path 是否指向正确的 site-packages |
| 无数据 | 客户端未登录或股票代码错误 | 确保 QMT 已登录运行 |
| 获取数据失败 | 网络问题或请求频率过高 | 稍后重试 |

---

## 底层 API 对照表

laofuqmt 封装的 xtdata 原生 API：

| laofuqmt 命令 | xtdata 原生 API | 说明 |
|--------------|----------------|------|
| quote | `get_market_data_ex` + `get_instrument_detail` | 最新K线快照 + 股票名称 |
| kline | `get_market_data_ex` | 历史K线，支持多周期（不调用 download） |
| tick | `get_full_tick` | 实时五档盘口（非历史逐笔） |
| market_overview | `get_market_data_ex` (指数代码) | 5大指数行情（不调用 download） |
| finance | `download_financial_data` + `get_financial_data` | 5大财务报表（利润/资产负债/现金流/股本/每股） |
| blocks | `get_sector_list` | 客户端板块列表 |
| block_stocks | `get_sector_list` + `get_stock_list_in_sector` | 板块内成分股列表 |
| search | `get_sector_list` + 本地映射 | 关键词搜索股票和板块 |
| subscribe | `subscribe_quote` + `get_full_tick` + `unsubscribe_quote` | 实时五档盘口，用完自动取消订阅 |

### 未封装但有需求的 xtdata API

以下 API 未在 laofuqmt 中封装，如需使用可直接在脚本中 import xtdata 后调用：

| xtdata API | 功能 | 备注 |
|------------|------|------|
| `get_instrument_detail` (iscomplete=True) | 获取完整证券信息 | 包含上市日期、退市日等扩展字段 |
| `get_trading_dates` | 获取交易日历 | 按市场查询 |
| `get_divid_factors` | 获取复权因子 | 除权除息数据 |
| `get_index_weight` | 获取指数成分股权重 | 个股在某指数中的权重 |
| `get_etf_info` | 获取ETF信息 | ETF净值、份额等 |
| `get_industry` | 获取行业成份股 | 申万/证监会行业分类 |
| `download_history_data` | 下载历史数据（旧版） | 阻塞式，download_history_data2 为新版 |
| `get_l2_quote` | L2 行情数据 | 需要 L2 行情权限 |
| `get_l2_order` | L2 委托队列 | 需要 L2 行情权限 |
| `get_l2_transaction` | L2 逐笔成交 | 需要 L2 行情权限 |
| `subscribe_whole_quote` | 全推行情订阅 | 推送模式 |
| `subscribe_l2thousand` | L2 千档行情订阅 | 需要 L2 权限 |

---

## 注意事项

1. **QMT 客户端必须运行** — xtquant 通过与客户端进程通信获取数据
2. **首次请求较慢** — 需要先下载数据到本地缓存，后续请求会快很多
3. **合理控制频率** — 过于频繁的请求可能触发限速
4. **日K数据最可靠** — 分钟级数据在非交易时间可能不可用
5. **逐笔数据仅当日** — tick 数据只在当日交易时段有效
6. **subscribe 用完即退** — 订阅获取数据后会自动取消订阅，不会持续占用
7. **各券商 QMT 版本差异** — xtquant API 基本一致，但安装路径不同，需修改 config.json
