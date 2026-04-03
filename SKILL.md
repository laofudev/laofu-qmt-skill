---
name: laofuqmt
description: "QMT（迅投）行情数据本地接口。通过调用本地安装的 xtquant 库获取 A 股实时行情、历史K线、财务数据、板块成分股等。使用场景：查行情、量化策略数据获取、公众号文章数据图表。仅支持行情数据，不涉及交易。依赖本地 PC 端运行的 QMT 客户端。"
---

# laofuqmt - QMT 行情数据本地接口

通过本地安装的 QMT 客户端中的 xtquant 库，获取 A 股行情数据的 Skill。

> **运行依赖**：需要本机运行 QMT 客户端并登录，xtquant 库通过进程通信获取数据。此 Skill 为 WorkBuddy 本地 PC 端专用。

## 前置条件

1. **已安装 QMT 客户端**（支持国金证券、中信证券等提供 QMT 的券商版本）
2. **QMT 客户端已登录**并保持运行（xtquant 依赖客户端进程通信）
3. **已配置 config.json**（见下方配置说明）
4. **系统已安装 Python 3.6+**（任意版本均可，脚本内部自动加载 xtquant）

## 开源配置指南

开源后，其他用户**必须修改** `scripts/config.json` 中的以下两个参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `qmt_root` | QMT 客户端的安装根目录 | `"D:/国金证券QMT交易端"` |
| `xtquant_path` | xtquant 库所在的 site-packages 路径 | `"D:/国金证券QMT交易端/bin.x64/Lib/site-packages"` |

其他参数说明：

| 参数 | 是否必改 | 说明 |
|------|----------|------|
| `python_path` | 否 | 留空 `""` 或设为 `"python"` 即可，使用系统 Python |
| `output_dir` | 否 | 数据输出目录，留空则输出到当前工作目录 |

> 如何找到自己的 xtquant_path：打开 QMT 安装目录，找到 `bin.x64/Lib/site-packages/xtquant` 文件夹，其父目录即为 `xtquant_path` 的值。部分券商版本可能是 `bin/Lib/site-packages`。

## 配置文件

配置文件路径：`scripts/config.json`（与 laofuqmt.py 同目录）

```json
{
  "python_path": "python",
  "qmt_root": "D:/国金证券QMT交易端",
  "xtquant_path": "D:/国金证券QMT交易端/bin.x64/Lib/site-packages",
  "output_dir": ""
}
```

> **安全提示**：此配置文件不包含任何账户密码或交易相关敏感信息。仅记录 QMT 安装路径。

## 工作原理

```
用户自然语言请求 → AI 解析意图 → 调用 laofuqmt.py
→ 脚本自动注入 xtquant 路径到 sys.path → import xtquant → 返回 JSON 结果
```

核心脚本 `scripts/laofuqmt.py` 封装了 xtquant 的行情 API，通过命令行子命令调用，输出 JSON 格式数据。

> **为什么不直接用 QMT 自带的 Python？** QMT 目录下通常只有 `pythonw.exe`（无控制台输出），脚本通过将 xtquant 的 site-packages 注入 sys.path，可以用系统 Python 正常运行。

## 可用接口一览

共 **9 个命令**，覆盖行情查询的主要场景：

### 基础行情

| # | 命令 | 功能 | 底层 xtdata API |
|---|------|------|----------------|
| 1 | `quote` | 实时行情快照（最新价、开高低、成交量额） | `get_market_data_ex` |
| 2 | `subscribe` | 实时订阅（含五档买卖盘口） | `subscribe_quote` + `get_full_tick` |
| 3 | `tick` | 逐笔成交明细 | `get_market_data_ex(period='tick')` |

### K线与历史

| # | 命令 | 功能 | 底层 xtdata API |
|---|------|------|----------------|
| 4 | `kline` | K线数据（多周期：1m/5m/15m/30m/1h/1d/1w/1mon） | `get_market_data_ex` + `download_history_data2` |

### 市场与板块

| # | 命令 | 功能 | 底层 xtdata API |
|---|------|------|----------------|
| 5 | `market_overview` | 大盘概览（上证/深证/创业板/科创50/沪深300） | `get_market_data_ex` |
| 6 | `blocks` | 板块列表（概念板块 / 行业板块） | `get_plate_list` |
| 7 | `block_stocks` | 板块成分股查询 | `get_plate_stock` |

### 财务与搜索

| # | 命令 | 功能 | 底层 xtdata API |
|---|------|------|----------------|
| 8 | `finance` | 个股财务数据 | `get_financial_data2` |
| 9 | `search` | 股票/板块搜索（支持中文名称模糊匹配） | `get_plate_list` + 本地映射表 |

> **不包含**：交易功能（下单、撤单、持仓查询等）、资金流向专用接口。如需交易功能，直接调用 xtquant 的 xttrader 模块。

## 使用方式

### 直接调用

```powershell
# 使用系统 Python（脚本内部自动加载 xtquant）
python scripts/laofuqmt.py <command> [options]
```

### 常用命令速查

```powershell
# 实时行情（支持中文名称）
python laofuqmt.py quote --codes 000001.SZ,600036.SH
python laofuqmt.py quote --codes 平安银行,贵州茅台

# K线数据（支持多周期）
python laofuqmt.py kline --code 000001.SZ --period 1d --count 30
python laofuqmt.py kline --code 000001.SZ --period 5m --count 60
python laofuqmt.py kline --code 000001.SZ --start 20260101 --end 20260331

# 实时订阅（含五档盘口）
python laofuqmt.py subscribe --codes 000001.SZ,600519.SH

# 逐笔成交
python laofuqmt.py tick --code 000001.SZ --count 200

# 大盘概览
python laofuqmt.py market_overview

# 财务数据
python laofuqmt.py finance --code 002594.SZ

# 板块列表
python laofuqmt.py blocks --type concept
python laofuqmt.py blocks --keyword 芯片

# 板块成分股
python laofuqmt.py block_stocks --block 锂电池

# 搜索
python laofuqmt.py search --keyword 茅台

# 通用选项
python laofuqmt.py quote --codes 000001.SZ --format table
python laofuqmt.py kline --code 000001.SZ --count 30 --output kline.json
```

### 命令行参数汇总

```
--code, -c     股票代码（如 000001.SZ，支持中文名称如"茅台"）
--codes        多个股票代码，逗号分隔
--period, -p   K线周期：1m/5m/15m/30m/1h/1d/1w/1mon（默认 1d）
--count, -n    数据条数（默认 100）
--start        起始时间（格式 YYYYMMDD）
--end          结束时间（格式 YYYYMMDD）
--type, -t     板块类型：concept（概念）/ industry（行业）
--block, -b    板块名称（支持模糊匹配）
--keyword, -k  搜索关键词
--output, -o   输出文件路径（默认输出到 stdout）
--format, -f   输出格式：json（默认）/ table
```

### 股票代码格式

标准格式：`代码.市场后缀`

| 后缀 | 市场 | 示例 |
|------|------|------|
| `.SZ` | 深圳（主板/创业板/北交所） | 000001.SZ, 300750.SZ |
| `.SH` | 上海（主板/科创板/指数） | 600519.SH, 000001.SH |

> **智能识别**：输入纯数字自动判断市场（6开头→SH，其他→SZ）；输入中文名称自动查找本地映射表。

## 返回数据结构

所有命令返回统一 JSON 格式：

```json
{
  "success": true,
  "timestamp": "2026-04-03 19:00:00",
  "data": { ... },
  "message": "获取 2 只股票的行情数据"
}
```

### 各命令返回的 data 字段

详细字段说明见 `references/api-reference.md`。

| 命令 | data 类型 | 关键字段 |
|------|-----------|----------|
| `quote` | `array` | code, name, lastPrice, open, high, low, volume, amount |
| `kline` | `object` | code, name, period, count, kline[{time,open,high,low,close,volume,amount}] |
| `tick` | `object` | code, count, ticks[{time,lastPrice,volume,amount}] |
| `market_overview` | `array` | name, code, close, open, high, low, prevClose, change, changePct, volume, amount |
| `subscribe` | `array` | code, lastPrice, open, high, low, lastClose, volume, amount, bidPrice[0-4], askPrice[0-4], bidVol[0-4], askVol[0-4] |
| `finance` | `object` | code, name, finance{...} |
| `blocks` | `object` | type, count, blocks[] |
| `block_stocks` | `array` | blockName, blockType, stockCount, stocks[{code,name}] |
| `search` | `object` | keyword, count, results[{code,name,source}] |

## 自然语言映射

用户使用自然语言描述需求时，AI 自动转换为对应命令：

| 用户说 | 转换为 |
|--------|--------|
| "帮我查一下平安银行最近5天的K线" | `kline --code 000001.SZ --period 1d --count 5` |
| "看一下茅台和宁德时代的实时行情" | `quote --codes 600519.SH,300750.SZ` |
| "锂电池板块有哪些股票" | `block_stocks --block 锂电池` |
| "查一下比亚迪的财务数据" | `finance --code 002594.SZ` |
| "今天大盘怎么样" | `market_overview` |
| "帮我找一下芯片相关的板块" | `blocks --keyword 芯片` |
| "平安银行五档盘口" | `subscribe --codes 000001.SZ` |

## 注意事项

1. **QMT 客户端必须运行** — xtquant 依赖客户端进程通信，未登录时无法获取数据
2. **数据延迟** — 行情数据来自客户端中转，非实时直连交易所
3. **任意 Python 均可** — 脚本自动将 xtquant 路径注入 sys.path，无需使用 QMT 自带的 pythonw.exe
4. **数据频率限制** — 频繁请求可能触发限速，建议合理控制请求频率
5. **首次请求较慢** — 首次请求需要下载历史数据到本地缓存，后续请求会快很多
6. **日K数据最可靠** — 分钟级数据在非交易时间可能不可用
7. **逐笔数据仅当日** — tick 数据只在当日交易时段有效
8. **开源安全** — 不包含任何账户、密码、资金等敏感信息

## 文件结构

```
~/.workbuddy/skills/laofuqmt/
├── SKILL.md                  # 本文件 - Skill 说明与使用指南
├── scripts/
│   ├── laofuqmt.py           # 核心脚本 - 封装所有行情 API（9个命令）
│   └── config.json           # 配置文件 - 路径设置（开源用户需修改）
└── references/
    └── api-reference.md      # API 详细参考文档（字段、参数、示例）
```
