#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
laofuqmt.py - QMT 行情数据本地接口

封装 xtquant/xtdata 的常用行情 API，提供命令行调用接口。
通过 JSON 输出数据，方便其他程序解析。

使用方式：
    python laofuqmt.py <command> [options]

安全说明：
    - 本脚本仅涉及行情数据读取，不包含任何交易功能
    - 不存储或传输任何账户密码信息
    - 配置文件仅包含路径信息
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

# ============================================================
# 配置加载
# ============================================================

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    default_config = {
        "python_path": "python",  # 使用系统 Python，脚本内部自动加载 xtquant
        "qmt_root": "D:/国金证券QMT交易端",
        "xtquant_path": "D:/国金证券QMT交易端/bin.x64/Lib/site-packages",
        "output_dir": ""
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception:
            pass  # 使用默认配置
    return default_config

CONFIG = load_config()

# ============================================================
# 将 xtquant 的 site-packages 加入 sys.path
# 这样可以使用任意版本的 Python 来运行此脚本
# ============================================================

_xtquant_path = CONFIG.get('xtquant_path', '')
if _xtquant_path and os.path.exists(_xtquant_path):
    if _xtquant_path not in sys.path:
        sys.path.insert(0, _xtquant_path)
else:
    # 尝试从 qmt_root 推断路径
    qmt_root = CONFIG.get('qmt_root', '')
    if qmt_root:
        for candidate in [
            os.path.join(qmt_root, 'bin.x64', 'Lib', 'site-packages'),
            os.path.join(qmt_root, 'bin', 'Lib', 'site-packages'),
        ]:
            if os.path.exists(candidate) and candidate not in sys.path:
                sys.path.insert(0, candidate)
                _xtquant_path = candidate
                break

# ============================================================
# xtquant 导入（延迟导入，方便错误处理）
# ============================================================

_xtdata = None
_xtconstant = None

def ensure_xtdata():
    """确保 xtdata 已导入"""
    global _xtdata, _xtconstant
    if _xtdata is not None:
        return _xtdata, _xtconstant
    try:
        from xtquant import xtdata
        from xtquant import xtconstant
        _xtdata = xtdata
        _xtconstant = xtconstant
        return _xtdata, _xtconstant
    except ImportError as e:
        print(json.dumps({
            "success": False,
            "error": f"无法导入 xtquant 模块: {e}",
            "hint": "请检查 config.json 中 xtquant_path 是否正确指向 QMT 的 site-packages 目录，且 QMT 客户端已安装。"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

# ============================================================
# 工具函数
# ============================================================

PERIOD_MAP = {
    '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
    '1h': '1h', '1d': '1d', 'daily': '1d', '1w': '1w', '1mon': '1mon',
    'week': '1w', 'month': '1mon',
    '1M': '1m', '5M': '5m', '15M': '15m', '30M': '30m',
    '1H': '1h', '1D': '1d', '1W': '1w',
}

# 常用股票名称 → 代码映射
NAME_CODE_MAP = {
    '平安银行': '000001.SZ',
    '万科A': '000002.SZ',
    '国信证券': '002736.SZ',
    '宁波银行': '002142.SZ',
    '洋河股份': '002304.SZ',
    '海康威视': '002415.SZ',
    '比亚迪': '002594.SZ',
    '东方财富': '300059.SZ',
    '宁德时代': '300750.SZ',
    '迈瑞医疗': '300760.SZ',
    '中信证券': '600030.SH',
    '宝钢股份': '600019.SH',
    '中国石化': '600028.SH',
    '招商银行': '600036.SH',
    '保利发展': '600048.SH',
    '中国联通': '600050.SH',
    '三一重工': '600031.SH',
    '恒瑞医药': '600276.SH',
    '中国平安': '601318.SH',
    '工商银行': '601398.SH',
    '建设银行': '601939.SH',
    '农业银行': '601288.SH',
    '中国银行': '601988.SH',
    '贵州茅台': '600519.SH',
    '中国中免': '601888.SH',
    '长江电力': '600900.SH',
    '紫金矿业': '601899.SH',
    '上汽集团': '600104.SH',
    '中国太保': '601601.SH',
    '新华保险': '601336.SH',
    '国泰君安': '601211.SH',
    '海螺水泥': '600585.SH',
    '片仔癀': '600436.SH',
    '云南白药': '000538.SZ',
    '美的集团': '000333.SZ',
    '格力电器': '000651.SZ',
    '泸州老窖': '000568.SZ',
    '五粮液': '000858.SZ',
    '中兴通讯': '000063.SZ',
    '科大讯飞': '002230.SZ',
    '立讯精密': '002475.SZ',
    '长城汽车': '601633.SH',
    '药明康德': '603259.SH',
    '隆基绿能': '601012.SH',
    '北方稀土': '600111.SH',
    '比亚迪电子': None,  # 港股
    '上证指数': '000001.SH',
    '深证成指': '399001.SZ',
    '创业板指': '399006.SZ',
    '科创50': '000688.SH',
    '沪深300': '000300.SH',
    '上证50': '000016.SH',
    '中证500': '000905.SH',
    '中证1000': '000852.SH',
}

def resolve_code(code_or_name):
    """将股票名称或代码解析为标准代码格式"""
    if not code_or_name:
        return None
    
    code = code_or_name.strip().upper()
    
    # 如果是纯名称（无点号），尝试从映射表查找
    if '.' not in code and code not in NAME_CODE_MAP:
        # 尝试模糊匹配名称
        for name, std_code in NAME_CODE_MAP.items():
            if code in name or name.startswith(code):
                return std_code
        return None
    
    # 直接在映射表中
    if code in NAME_CODE_MAP:
        return NAME_CODE_MAP[code]
    
    # 尝试原始输入作为名称
    original = code_or_name.strip()
    if original in NAME_CODE_MAP:
        return NAME_CODE_MAP[original]
    
    # 已是标准代码格式
    if '.' in code:
        return code
    
    # 纯数字，尝试自动加后缀
    if code.isdigit():
        if code.startswith('6'):
            return f"{code}.SH"
        else:
            return f"{code}.SZ"
    
    return None


def resolve_codes(codes_str):
    """解析多个代码，支持逗号分隔"""
    if not codes_str:
        return []
    codes = [c.strip() for c in codes_str.split(',')]
    result = []
    for c in codes:
        resolved = resolve_code(c)
        if resolved:
            result.append(resolved)
    return result


def make_response(data, success=True, message=""):
    """构造标准 JSON 响应"""
    resp = {
        "success": success,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": data
    }
    if message:
        resp["message"] = message
    return resp


def format_table(data, columns=None):
    """将数据格式化为表格字符串"""
    if not data or not isinstance(data, list):
        return str(data)
    
    if columns:
        # 只取指定列
        rows = [[str(item.get(col, '')) for col in columns] for item in data]
        headers = columns
    else:
        # 取所有 key 作为列
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
            rows = [[str(item.get(h, '')) for h in headers] for item in data]
        else:
            headers = [f"col_{i}" for i in range(len(data[0]))]
            rows = [[str(v) for v in row] for row in data]
    
    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))
    
    # 构建表格
    def make_line(values):
        return " | ".join(v.ljust(col_widths[i]) for i, v in enumerate(values))
    
    def make_sep():
        return "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    
    lines = []
    lines.append(make_line(headers))
    lines.append(make_sep())
    for row in rows:
        lines.append(make_line(row))
    
    return "\n".join(lines)

# ============================================================
# 行情数据命令实现
# ============================================================

def get_stock_name(xtdata, code):
    """获取股票名称"""
    try:
        detail = xtdata.get_instrument_detail(code)
        if detail:
            return detail.get('InstrumentName', '')
    except Exception:
        pass
    return ''


def cmd_quote(args):
    """获取实时行情快照"""
    xtdata, _ = ensure_xtdata()
    
    codes = resolve_codes(args.codes)
    if not codes:
        return make_response([], False, "请提供有效的股票代码")
    
    # quote 直接读本地缓存，不调用 download（避免阻塞）
    # 如果缓存没有数据，返回空即可
    
    results = []
    for code in codes:
        try:
            # 获取最新K线作为快照
            kline = xtdata.get_market_data_ex(
                field_list=[],
                stock_list=[code],
                period='1d',
                count=1
            )
            
            if code in kline and len(kline[code]) > 0:
                data = kline[code]
                if 'close' in data:
                    close_arr = data['close']
                    if len(close_arr) > 0:
                        last = float(close_arr.iloc[-1]) if hasattr(close_arr, 'iloc') else float(close_arr[-1])
                    else:
                        last = 0
                else:
                    last = 0
                
                # 构造行情快照
                snapshot = {
                    "code": code,
                    "name": get_stock_name(xtdata, code),
                    "lastPrice": round(last, 2),
                }
                
                # 添加其他字段
                field_map = {
                    'open': 'open', 'high': 'high', 'low': 'low',
                    'volume': 'volume', 'amount': 'amount'
                }
                for api_field, out_field in field_map.items():
                    if api_field in data and len(data[api_field]) > 0:
                        arr = data[api_field]
                        val = float(arr.iloc[-1]) if hasattr(arr, 'iloc') else float(arr[-1])
                        if out_field in ('volume', 'amount'):
                            snapshot[out_field] = round(val, 2)
                        else:
                            snapshot[out_field] = round(val, 2)
                
                results.append(snapshot)
        except Exception as e:
            results.append({"code": code, "error": str(e)})
    
    return make_response(results, message=f"获取 {len(results)} 只股票的行情数据")


def cmd_kline(args):
    """获取K线数据"""
    xtdata, _ = ensure_xtdata()
    
    code = resolve_code(args.code)
    if not code:
        return make_response(None, False, f"无法识别的股票代码: {args.code}")
    
    period = PERIOD_MAP.get(args.period, args.period)
    count = args.count
    start_time = args.start if hasattr(args, 'start') and args.start else ''
    end_time = args.end if hasattr(args, 'end') and args.end else ''
    
    # 直接读取本地缓存数据（download_history_data2 会阻塞等待服务端，
    # 非交易时间可能导致无限等待，改为按需下载或直接读已有缓存）
    try:
        kline = xtdata.get_market_data_ex(
            field_list=[],
            stock_list=[code],
            period=period,
            count=count,
            start_time=start_time,
            end_time=end_time
        )
        
        if code in kline:
            data = kline[code]
            if data is None or len(data) == 0:
                return make_response([], message=f"{code} 无数据")
            
            # 转换为列表格式
            records = []
            length = len(data.get('close', []))
            
            for i in range(length):
                record = {}
                # 时间
                if 'time' in data:
                    t = data['time'].iloc[i] if hasattr(data['time'], 'iloc') else data['time'][i]
                    record['time'] = str(t)
                
                # OHLCV
                for field in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                    if field in data:
                        arr = data[field]
                        val = arr.iloc[i] if hasattr(arr, 'iloc') else arr[i]
                        record[field] = round(float(val), 2)
                
                records.append(record)
            
            # 获取股票名称
            name = get_stock_name(xtdata, code)
            
            return make_response({
                "code": code,
                "name": name,
                "period": period,
                "count": len(records),
                "kline": records
            }, message=f"获取 {code} {len(records)} 条{period}K线数据")
        else:
            return make_response(None, False, f"{code} 无数据返回")
    
    except Exception as e:
        return make_response(None, False, f"获取K线数据失败: {e}")


def cmd_tick(args):
    """获取逐笔成交数据"""
    xtdata, _ = ensure_xtdata()
    
    code = resolve_code(args.code)
    if not code:
        return make_response(None, False, f"无法识别的股票代码: {args.code}")
    
    count = args.count if hasattr(args, 'count') else 100
    
    try:
        # tick 数据只在当日有效，直接读缓存即可
        # 使用 get_full_tick 获取实时盘口数据（含五档买卖价）
        tick_raw = xtdata.get_full_tick([code])
        
        if tick_raw and code in tick_raw:
            tick = tick_raw[code]
            return make_response({
                "code": code,
                "lastPrice": tick.get('lastPrice', 0),
                "open": tick.get('open', 0),
                "high": tick.get('high', 0),
                "low": tick.get('low', 0),
                "lastClose": tick.get('lastClose', 0),
                "volume": tick.get('volume', 0),
                "amount": tick.get('amount', 0),
                "bidPrice": tick.get('bidPrice', []),
                "askPrice": tick.get('askPrice', []),
                "bidVol": tick.get('bidVol', []),
                "askVol": tick.get('askVol', []),
                "time": tick.get('timetag', '')
            }, message=f"获取 {code} 实时tick数据")
        else:
            return make_response([], message=f"{code} 无tick数据")
    
    except Exception as e:
        return make_response(None, False, f"获取逐笔数据失败: {e}")


def cmd_market_overview(args):
    """大盘概览"""
    xtdata, _ = ensure_xtdata()
    
    index_codes = ['000001.SH', '399001.SZ', '399006.SZ', '000688.SH', '000300.SH']
    index_names = ['上证指数', '深证成指', '创业板指', '科创50', '沪深300']
    
    # 大盘指数数据通常已缓存，直接读取
    # 如果缓存为空，首次调用可能需要 QMT 客户端在线
    
    results = []
    for code, name in zip(index_codes, index_names):
        try:
            kline = xtdata.get_market_data_ex(
                field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
                stock_list=[code],
                period='1d',
                count=2
            )
            if code in kline and len(kline[code].get('close', [])) >= 2:
                data = kline[code]
                close = float(data['close'].iloc[-1]) if hasattr(data['close'], 'iloc') else float(data['close'][-1])
                prev_close = float(data['close'].iloc[-2]) if hasattr(data['close'], 'iloc') else float(data['close'][-2])
                open_price = float(data['open'].iloc[-1]) if hasattr(data['open'], 'iloc') else float(data['open'][-1])
                high = float(data['high'].iloc[-1]) if hasattr(data['high'], 'iloc') else float(data['high'][-1])
                low = float(data['low'].iloc[-1]) if hasattr(data['low'], 'iloc') else float(data['low'][-1])
                
                change_pct = round((close - prev_close) / prev_close * 100, 2) if prev_close else 0
                change_amt = round(close - prev_close, 2) if prev_close else 0
                
                volume = float(data['volume'].iloc[-1]) if hasattr(data['volume'], 'iloc') else float(data['volume'][-1])
                amount = float(data['amount'].iloc[-1]) if hasattr(data['amount'], 'iloc') else float(data['amount'][-1])
                
                results.append({
                    "name": name,
                    "code": code,
                    "close": round(close, 2),
                    "open": round(open_price, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "prevClose": round(prev_close, 2),
                    "change": change_amt,
                    "changePct": change_pct,
                    "volume": round(volume, 2),
                    "amount": round(amount, 2)
                })
        except Exception as e:
            results.append({"name": name, "code": code, "error": str(e)})
    
    return make_response(results, message="大盘概览数据")


def cmd_finance(args):
    """获取财务数据"""
    xtdata, _ = ensure_xtdata()
    
    code = resolve_code(args.code)
    if not code:
        return make_response(None, False, f"无法识别的股票代码: {args.code}")
    
    try:
        # 先下载财务数据（首次需要，后续走缓存很快）
        tables = ['Income', 'Balance', 'CashFlow', 'Capital', 'PershareIndex']
        xtdata.download_financial_data([code], table_list=tables)
        
        # get_financial_data 返回: {stock_code: {table_name: DataFrame}}
        fin_data = xtdata.get_financial_data([code], table_list=tables, report_type='report_time')
        
        if fin_data and code in fin_data:
            stock_tables = fin_data[code]
            results = {}
            for table_name, df in stock_tables.items():
                if hasattr(df, 'to_dict'):
                    records = df.to_dict(orient='records')
                    # 只取最近4期
                    results[table_name] = records[-4:] if len(records) > 4 else records
                elif isinstance(df, list):
                    results[table_name] = df[-4:] if len(df) > 4 else df
                else:
                    results[table_name] = str(df)
            
            name = get_stock_name(xtdata, code)
            return make_response({
                "code": code,
                "name": name,
                "tables": results
            }, message=f"获取 {code} 财务数据 ({list(results.keys())})")
        else:
            return make_response({"code": code, "tables": {}}, message=f"{code} 暂无财务数据")
    
    except Exception as e:
        return make_response(None, False, f"获取财务数据失败: {e}")


def cmd_blocks(args):
    """获取板块列表"""
    xtdata, _ = ensure_xtdata()
    
    try:
        # get_sector_list() 返回客户端左侧板块列表中的所有板块名
        block_list = xtdata.get_sector_list()
        
        if hasattr(block_list, 'to_list'):
            block_list = block_list.to_list()
        elif not isinstance(block_list, list):
            block_list = list(block_list)
        
        # 如果有搜索关键词则过滤
        keyword = args.keyword if hasattr(args, 'keyword') else ''
        if keyword:
            block_list = [b for b in block_list if keyword.lower() in str(b).lower()]
        
        return make_response({
            "count": len(block_list),
            "blocks": block_list[:200]  # 限制返回数量
        }, message=f"获取板块列表，共 {len(block_list)} 个")
    
    except Exception as e:
        return make_response(None, False, f"获取板块列表失败: {e}")


def cmd_block_stocks(args):
    """获取板块成分股"""
    xtdata, _ = ensure_xtdata()
    
    block_name = args.block if hasattr(args, 'block') else ''
    if not block_name:
        return make_response(None, False, "请提供板块名称")
    
    try:
        # 从板块列表中找到匹配的板块名
        all_blocks = xtdata.get_sector_list()
        if hasattr(all_blocks, 'to_list'):
            all_blocks = all_blocks.to_list()
        
        matched = [b for b in all_blocks if block_name in str(b)]
        
        if not matched:
            return make_response(None, False, f"未找到包含 '{block_name}' 的板块")
        
        results = []
        for block in matched[:5]:  # 最多返回5个匹配板块
            stocks = xtdata.get_stock_list_in_sector(block)
            if hasattr(stocks, 'to_list'):
                stocks = stocks.to_list()
            elif not isinstance(stocks, list):
                stocks = list(stocks)
            
            stock_info = []
            for s in stocks[:50]:  # 每个板块最多50只
                code = str(s)
                name = get_stock_name(xtdata, code)
                stock_info.append({"code": code, "name": name})
            
            results.append({
                "blockName": block,
                "stockCount": len(stock_info),
                "stocks": stock_info
            })
        
        return make_response(results, message=f"找到 {len(results)} 个匹配板块")
    
    except Exception as e:
        return make_response(None, False, f"获取板块成分股失败: {e}")


def cmd_search(args):
    """搜索股票（通过板块和名称匹配）"""
    xtdata, _ = ensure_xtdata()
    
    keyword = args.keyword if hasattr(args, 'keyword') else ''
    if not keyword:
        return make_response(None, False, "请提供搜索关键词")
    
    results = []
    
    # 1. 先从本地映射表搜索
    for name, code in NAME_CODE_MAP.items():
        if keyword in name:
            results.append({"code": code, "name": name, "source": "local"})
    
    # 2. 通过板块列表搜索
    try:
        all_blocks = xtdata.get_sector_list()
        if hasattr(all_blocks, 'to_list'):
            all_blocks = all_blocks.to_list()
        for b in all_blocks:
            if keyword.lower() in str(b).lower() and str(b) not in [r.get('name', '') for r in results]:
                results.append({"code": str(b), "name": str(b), "source": "block"})
    except Exception:
        pass
    
    return make_response({
        "keyword": keyword,
        "count": len(results),
        "results": results[:20]
    }, message=f"搜索 '{keyword}'，找到 {len(results)} 个结果")


def cmd_subscribe(args):
    """订阅实时行情（简版，获取最新报价）"""
    xtdata, _ = ensure_xtdata()
    
    codes = resolve_codes(args.codes)
    if not codes:
        return make_response(None, False, "请提供有效的股票代码")
    
    try:
        # 订阅
        for code in codes:
            xtdata.subscribe_quote(code, period='tick', count=1)
        
        time.sleep(1)
        
        # 获取最新数据
        results = []
        for code in codes:
            try:
                data = xtdata.get_full_tick([code])
                if data and code in data:
                    tick = data[code]
                    results.append({
                        "code": code,
                        "name": get_stock_name(xtdata, code),
                        "lastPrice": tick.get('lastPrice', 0),
                        "open": tick.get('open', 0),
                        "high": tick.get('high', 0),
                        "low": tick.get('low', 0),
                        "lastClose": tick.get('lastClose', 0),
                        "volume": tick.get('volume', 0),
                        "amount": tick.get('amount', 0),
                        "bidPrice": tick.get('bidPrice', []),
                        "askPrice": tick.get('askPrice', []),
                        "bidVol": tick.get('bidVol', []),
                        "askVol": tick.get('askVol', []),
                    })
            except Exception as e:
                results.append({"code": code, "error": str(e)})
        
        # 取消订阅
        for code in codes:
            try:
                xtdata.unsubscribe_quote(code)
            except Exception:
                pass
        
        return make_response(results, message=f"实时行情订阅数据 ({len(results)} 只)")
    
    except Exception as e:
        return make_response(None, False, f"订阅行情失败: {e}")


# ============================================================
# 命令行接口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='laofuqmt - QMT 行情数据本地接口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python laofuqmt.py quote --codes 000001.SZ,600036.SH
  python laofuqmt.py kline --code 000001.SZ --period 1d --count 30
  python laofuqmt.py tick --code 000001.SZ --count 100
  python laofuqmt.py market_overview
  python laofuqmt.py finance --code 000001.SZ
  python laofuqmt.py blocks --type concept
  python laofuqmt.py block_stocks --block 锂电池
  python laofuqmt.py search --keyword 茅台
  python laofuqmt.py subscribe --codes 000001.SZ
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # quote - 实时行情
    p_quote = subparsers.add_parser('quote', help='获取实时行情快照')
    p_quote.add_argument('--codes', '-c', required=True, help='股票代码，逗号分隔（如 000001.SZ,600036.SH）')
    
    # kline - K线数据
    p_kline = subparsers.add_parser('kline', help='获取K线数据')
    p_kline.add_argument('--code', '-c', required=True, help='股票代码')
    p_kline.add_argument('--period', '-p', default='1d', help='K线周期（1m/5m/15m/30m/1h/1d/1w/1mon，默认 1d）')
    p_kline.add_argument('--count', '-n', type=int, default=100, help='数据条数（默认 100）')
    p_kline.add_argument('--start', default='', help='起始时间（YYYYMMDD）')
    p_kline.add_argument('--end', default='', help='结束时间（YYYYMMDD）')
    
    # tick - 逐笔成交
    p_tick = subparsers.add_parser('tick', help='获取逐笔成交数据')
    p_tick.add_argument('--code', '-c', required=True, help='股票代码')
    p_tick.add_argument('--count', '-n', type=int, default=100, help='数据条数（默认 100）')
    
    # market_overview - 大盘概览
    subparsers.add_parser('market_overview', help='大盘概览')
    
    # finance - 财务数据
    p_finance = subparsers.add_parser('finance', help='获取财务数据')
    p_finance.add_argument('--code', '-c', required=True, help='股票代码')
    
    # blocks - 板块列表
    p_blocks = subparsers.add_parser('blocks', help='获取板块列表')
    p_blocks.add_argument('--type', '-t', default='concept', help='板块类型：concept（概念）/ industry（行业）')
    p_blocks.add_argument('--keyword', '-k', default='', help='搜索关键词（可选）')
    
    # block_stocks - 板块成分股
    p_bs = subparsers.add_parser('block_stocks', help='获取板块成分股')
    p_bs.add_argument('--block', '-b', required=True, help='板块名称')
    
    # search - 搜索
    p_search = subparsers.add_parser('search', help='搜索股票/板块')
    p_search.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    
    # subscribe - 实时订阅
    p_sub = subparsers.add_parser('subscribe', help='订阅实时行情')
    p_sub.add_argument('--codes', '-c', required=True, help='股票代码，逗号分隔')
    
    # 通用选项
    parser.add_argument('--output', '-o', default='', help='输出到文件')
    parser.add_argument('--format', '-f', default='json', choices=['json', 'table'], help='输出格式（默认 json）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # 命令映射
    cmd_map = {
        'quote': cmd_quote,
        'kline': cmd_kline,
        'tick': cmd_tick,
        'market_overview': cmd_market_overview,
        'finance': cmd_finance,
        'blocks': cmd_blocks,
        'block_stocks': cmd_block_stocks,
        'search': cmd_search,
        'subscribe': cmd_subscribe,
    }
    
    handler = cmd_map.get(args.command)
    if not handler:
        print(json.dumps({"success": False, "error": f"未知命令: {args.command}"}, ensure_ascii=False))
        sys.exit(1)
    
    # 执行命令
    result = handler(args)
    
    # 输出
    output_format = args.format if hasattr(args, 'format') else 'json'
    output_path = args.output if hasattr(args, 'output') else ''
    
    if output_format == 'table':
        output_str = format_table(result.get('data'))
    else:
        output_str = json.dumps(result, ensure_ascii=False, indent=2)
    
    if output_path:
        output_dir = CONFIG.get('output_dir', '')
        if output_dir and not os.path.isabs(output_path):
            output_path = os.path.join(output_dir, output_path)
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_str)
        print(f"数据已保存到: {output_path}")
    else:
        print(output_str)


if __name__ == '__main__':
    main()
