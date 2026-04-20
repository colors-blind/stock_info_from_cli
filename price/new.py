import requests
from time import sleep

BASE_URL = 'https://hq.sinajs.cn/list={}'

HEADERS = {
    "User-Agent": "PostmanRuntime/7.26.8",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/javascript; charset=GB18030",
    "Referer": "https://finance.sina.com.cn"
}


def get_price_detail(codes: str) -> str:
    """
    等价于 C# RestClient + Encoding.Convert
    """
    try:
        url = BASE_URL.format(codes)
        resp = requests.get(url, headers=HEADERS, timeout=10)

        # ❗关键：强制用 GB18030 解码
        text = resp.content.decode('gb18030', errors='ignore')
        return text

    except Exception as e:
        print("[ERROR]", e)
        sleep(3)
        return ""

code = 'sh601012'
a = get_price_detail(code)
print(a)
