# laofuqmt - QMT 行情数据本地接口

> 通过 QMT 客户端的 xtquant 库获取 A 股行情数据，支持 WorkBuddy AI Skill 和命令行独立使用。

## 它是什么

laofuqmt 是一个 [WorkBuddy](https://www.codebuddy.cn) Skill，封装了 QMT（迅投）量化交易终端的 xtdata 行情 API，提供 **9 个命令**覆盖 A 股行情查询的主要场景：

- **基础行情**：实时行情快照、五档盘口订阅、实时逐笔
- **K 线历史**：多周期 K 线数据（1m / 5m / 15m / 30m / 1h / 日 / 周 / 月）
- **市场板块**：大盘指数概览、板块列表、板块成分股
- **财务搜索**：个股财务数据、股票/板块关键词搜索

**仅支持行情数据，不涉及交易。**

## 快速开始

### 1. 环境要求

- 已安装 QMT 客户端（国金证券、中信证券等提供 QMT 的券商）并登录运行
- 系统 Python 3.6+

### 2. 安装

```bash
# 克隆到 WorkBuddy skills 目录
git clone https://github.com/laofudev/laofu-qmt-skill.git ~/.workbuddy/skills/laofuqmt
```

### 3. 配置

修改 `scripts/config.json`，将路径改为你自己的 QMT 安装目录：

```json
{
  "python_path": "python",
  "qmt_root": "D:/你的券商QMT交易端",
  "xtquant_path": "D:/你的券商QMT交易端/bin.x64/Lib/site-packages",
  "output_dir": ""
}
```

> 如何找到 xtquant_path：打开 QMT 安装目录，找到 `bin.x64/Lib/site-packages/xtquant` 文件夹，其父目录即为 xtquant_path。部分券商可能是 `bin/Lib/site-packages`。

### 4. 运行

```powershell
# 确保 QMT 客户端已登录
python scripts/laofuqmt.py <command> [options]
```

## 使用示例

```powershell
# 查看大盘概览
python scripts/laofuqmt.py market_overview

# 实时行情（支持中文名称）
python scripts/laofuqmt.py quote --codes 平安银行,贵州茅台

# 日K线
python scripts/laofuqmt.py kline --code 000001.SZ --period 1d --count 30

# 5分钟K线
python scripts/laofuqmt.py kline --code 600519.SH --period 5m --count 60

# 实时五档盘口
python scripts/laofuqmt.py subscribe --codes 000001.SZ,600519.SH

# 财务数据
python scripts/laofuqmt.py finance --code 002594.SZ

# 板块成分股
python scripts/laofuqmt.py block_stocks --block 锂电池

# 搜索股票
python scripts/laofuqmt.py search --keyword 茅台
```

## 命令一览

| 命令 | 功能 | 说明 |
|------|------|------|
| `market_overview` | 大盘概览 | 上证/深证/创业板/科创50/沪深300 |
| `quote` | 实时行情 | 最新价、开高低、成交量额 |
| `kline` | K 线数据 | 支持多周期，指定条数或时间范围 |
| `tick` | 实时盘口 | 五档买卖价量快照 |
| `subscribe` | 实时订阅 | 含五档盘口的详细行情 |
| `finance` | 财务数据 | 利润表/资产负债表/现金流等 |
| `blocks` | 板块列表 | 概念板块 / 行业板块 |
| `block_stocks` | 板块成分股 | 查询某板块的所有股票 |
| `search` | 搜索 | 按关键词搜索股票和板块 |

## 命令行参数

```
--code, -c     股票代码（如 000001.SZ，支持中文名称）
--codes        多个股票代码，逗号分隔
--period, -p   K线周期：1m/5m/15m/30m/1h/1d/1w/1mon（默认 1d）
--count, -n    数据条数（默认 100）
--start        起始时间（YYYYMMDD）
--end          结束时间（YYYYMMDD）
--type, -t     板块类型：concept / industry
--block, -b    板块名称（支持模糊匹配）
--keyword, -k  搜索关键词
--output, -o   输出文件路径（默认 stdout）
--format, -f   输出格式：json（默认）/ table
```

## 股票代码格式

标准格式：`代码.市场后缀`

| 后缀 | 市场 | 示例 |
|------|------|------|
| `.SZ` | 深圳（主板/创业板/北交所） | 000001.SZ, 300750.SZ |
| `.SH` | 上海（主板/科创板/指数） | 600519.SH, 000001.SH |

也支持纯数字（自动识别市场）和中文名称（模糊匹配）。

## 返回数据格式

所有命令返回统一 JSON：

```json
{
  "success": true,
  "timestamp": "2026-04-03 21:00:00",
  "data": { ... },
  "message": "获取 2 只股票的行情数据"
}
```

## 在 WorkBuddy 中使用

安装到 `~/.workbuddy/skills/laofuqmt/` 后，WorkBuddy 会自动识别。你可以用自然语言查询行情：

- "帮我查一下平安银行最近5天的K线"
- "看一下茅台和宁德时代的实时行情"
- "今天大盘怎么样"
- "锂电池板块有哪些股票"

AI 会自动转换为对应的命令调用。

## 工作原理

```
自然语言请求 → AI 解析意图 → 调用 laofuqmt.py
→ 脚本注入 xtquant 路径到 sys.path → import xtdata → 返回 JSON
```

xtquant 依赖 QMT 客户端进程通信获取数据。脚本通过将 xtquant 的 site-packages 注入 sys.path，可以用系统 Python 运行，无需使用 QMT 自带的 pythonw.exe。

## 底层 API 对照

| 命令 | xtdata API |
|------|-----------|
| quote | `get_market_data_ex` + `get_instrument_detail` |
| kline | `get_market_data_ex` |
| tick | `get_full_tick` |
| subscribe | `subscribe_quote` + `get_full_tick` + `unsubscribe_quote` |
| market_overview | `get_market_data_ex` |
| finance | `download_financial_data` + `get_financial_data` |
| blocks | `get_sector_list` |
| block_stocks | `get_sector_list` + `get_stock_list_in_sector` |
| search | `get_sector_list` + 本地映射 |

> **注意**：API 名称以本地 xtdata.py 源码为准，不同券商版本的线上文档可能存在 API 名称差异。

## 文件结构

```
laofuqmt/
├── README.md                 # 本文件
├── SKILL.md                  # WorkBuddy Skill 定义文件
├── scripts/
│   ├── laofuqmt.py           # 核心脚本（9 个命令）
│   └── config.json           # 路径配置（用户需修改）
└── references/
    └── api-reference.md      # API 详细参考文档
```

## 注意事项

1. **QMT 客户端必须登录运行** — xtquant 通过客户端进程通信获取数据
2. **首次请求可能较慢** — 需要下载历史数据到本地缓存
3. **日 K 数据最可靠** — 分钟级数据在非交易时间可能不可用
4. **各券商路径不同** — 需根据实际安装路径修改 config.json
5. **不包含敏感信息** — 配置文件仅记录路径，无账户密码

## 未封装的 API

以下 xtdata API 未封装，有需求可直接 import xtdata 调用：

`get_trading_dates` · `get_divid_factors` · `get_index_weight` · `get_etf_info` · `get_industry` · `get_l2_quote` · `get_l2_order` · `get_l2_transaction` 等

详见 [references/api-reference.md](references/api-reference.md)。

## License

MIT

## 作者

[资源老夫](https://github.com/laofudev) — 公众号「资源老夫」

<div align="center">
  <img src="images/感谢关注.png" alt="感谢关注" width="400"/>
</div>
