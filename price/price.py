import requests
from time import sleep
import threading
from collections import namedtuple
import redis

BASE_URL = 'http://hq.sinajs.cn/list={0}'
CODE_FILE = 'E:\price\code.txt'

SHARES = namedtuple('SHARES', ['name', 'today_open', 'last_day_close',
    'current_price', 'today_high', 'today_low',
    'un1', 'un2', 'un3', 'un4', 'un5', 'un6', 'un7', 'un8', 'un9', 'un10', 'un11', 'un12', 'un13',
    'un14', 'un15', 'un16', 'un17', 'un18', 'un19', 'un20', 'un21', 'un22', 'un23', 'un24', 'date',
    'time', 'un27'])


def read_codes():
    """读取股票代码 返回set 用于和url拼接"""
    code_set = []
    with open(CODE_FILE) as fd:
        for line in fd:
            code_set.append(line.strip())

    return ','.join(sorted(list(set(code_set))))


def get_price_detail(url):
    """根据URL返回请求内容"""
    try:
        content = requests.get(url).text
        return content
    except:
        sleep(3)
    return ''


def parse_line_data(line):
    """解析获取结果"""
    if not line:
        return {}
    info = line.split('="')[1].replace('";', '')
    if info.endswith(','):
        info = info.rstrip(',')
    details = info.split(',')
    share = SHARES._make(details)
    price_dict = share._asdict()
    for key in price_dict:
        if not key.startswith('un') and key not in ('time', 'date', 'name'):
            price_dict[key] = float(price_dict[key])
    change_pct = round(((price_dict['current_price'] - price_dict['last_day_close']) / price_dict['last_day_close']) * 100, 2)
    price_dict['change_pct'] = change_pct
    return price_dict


def format_line_info(dict_info):

    """格式化为可读信息"""
    name = dict_info.get('name')
    current_price = dict_info.get('current_price')
    today_high, today_low, change_pct = dict_info.get('today_high'), dict_info.get('today_low'), dict_info.get('change_pct')
    time = dict_info.get('time')

    msg = F"{name} 现价：{current_price} 浮动：{change_pct}%"
    if change_pct < 0:
        msg = F'<font color="green">{msg}</font>'
    else:
        msg = F'<font color="red">{msg}</font>'
    return msg


def send_text(msg):
    token = 'DEpg60blgoH81Q4XW5EbhKl6tK7yfFUXE36ODRVhzY7s8MiQptofQOaXUI-nBkimJV7CSxAkhLqHpIsKYW-L2cNslkAVn4JEdPHWsPFFlbFKRvekawOe6j_JxqFTak3sXvWdl4vPkQedeCwZWEewlr-J6PrJgNlH1YDZy3aO0T0vQwkV5CZH8weMinwWE7x0WzCNBgEW61HUpxwufTyb5w'
    url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}'.format(token)
    data = {
        "touser": "LiuYang|jessicachow",
        "msgtype": "text",
        "agentid": 1000002,
        "msgtype": "markdown",
        "markdown": {
            "content": msg
        },
    }
    res = requests.post(url, json=data)
    print(res.json())


class Token(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run():
        while 1:
            try:
                url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=ww19217f4ee611592e&corpsecret=tHLkUc8x_BGMuxOvB64sUiQYd8AkS5h25eTE4SJXy6Y'
                token = requests.get(url).json().get('access_token')
                client = redis.Redis()
                client.set('token', token)
                sleep(7100)
            except:
                continue


if __name__ == '__main__':
    t1 = Token()
    t1.start()
    while 1:
        try:
            a = read_codes()
            url = BASE_URL.format(a)
            content = get_price_detail(url).split('\n')
            dict_list = []
            for i in content:
                if not i.strip():
                    continue
                dict_list.append(parse_line_data(i))

            dict_list.sort(key=lambda a: a.get('change_pct'), reverse=True)
            msg_list = []
            for i in dict_list:
                msg_list.append((format_line_info(i)))

            msg = '\n'.join(msg_list)
            send_text(msg)
            sleep(180)
        except:
            sleep(300)