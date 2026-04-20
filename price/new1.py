import requests
from time import sleep

BASE_URL = 'https://hq.sinajs.cn/list={}'
CODE_FILE = r'code.txt'

HEADERS = {
    "User-Agent": "PostmanRuntime/7.26.8",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/javascript; charset=GB18030",
    "Referer": "https://finance.sina.com.cn"
}


def read_codes():
    """读取股票代码，返回逗号拼接字符串"""
    codes = set()
    with open(CODE_FILE, encoding='utf-8') as f:
        for line in f:
            code = line.strip()
            if code:
                codes.add(code)
    return ','.join(sorted(codes))


def get_price_detail(codes: str) -> str:
    """等价 C# RestClient + Encoding.Convert"""
    try:
        url = BASE_URL.format(codes)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        return resp.content.decode('gb18030', errors='ignore')
    except Exception as e:
        print('[ERROR]', e)
        sleep(3)
        return ''


def parse_line_data(line: str):
    """
    自适应解析新浪行情行
    只取稳定字段，不依赖字段总数
    """
    if not line or '="' not in line:
        return None

    try:
        info = line.split('="')[1].rstrip('";')
        if info.endswith(','):
            info = info[:-1]

        f = info.split(',')

        # 基础字段（所有 A 股都有）
        name = f[0]
        today_open = float(f[1])
        last_close = float(f[2])
        current_price = float(f[3])
        high = float(f[4])
        low = float(f[5])
        volume = float(f[8])      # 成交股数
        amount = float(f[9])      # 成交金额
        date = f[-3]
        time = f[-2]

        change_pct = round(
            (current_price - last_close) / last_close * 100, 2
        )

        return {
            "name": name,
            "today_open": today_open,
            "last_close": last_close,
            "current_price": current_price,
            "high": high,
            "low": low,
            "volume": volume,
            "amount": amount,
            "date": date,
            "time": time,
            "change_pct": change_pct
        }

    except Exception as e:
        print('[PARSE ERROR]', e, line)
        return None


def format_line_info(d):
    sign = '+' if d['change_pct'] >= 0 else ''
    return (
        f"{d['name']} | "
        f"现价 {d['current_price']} | "
        f"涨跌 {sign}{d['change_pct']}%"
    )


def main():
        try:
            codes = read_codes()
            raw = get_price_detail(codes)

            lines = raw.split('\n')
            stocks = []

            for line in lines:
                data = parse_line_data(line)
                if data:
                    stocks.append(data)

            stocks.sort(key=lambda x: x['change_pct'], reverse=True)

            print('=' * 60)
            for s in stocks:
                print(format_line_info(s))
            print('=' * 60)


        except Exception as e:
            print('[MAIN ERROR]', e)


if __name__ == '__main__':
    main()

