
import os
import time
import http.client

from urllib import request,error
from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, abort

class Quote(object):

    def __init__(self):
        self.name = None
        self.trade_time = None
        self.trade_price = None
        self.change = None
        self.open = None
        self.high = None
        self.low = None

    def __str__(self):
        res = list()

        res.append(self.name)
        res.append(self.trade_time.strftime("%H:%M:%S"))
        res.append(self.trade_price)
        res.append(self.change)
        res.append(self.open)
        res.append(self.high)
        res.append(self.low)
        return str(res)

TXF_NAME = u'臺指現貨'

targets= [TXF_NAME]

quotes = dict()

if __name__ == "__main__":
    def downWeb(url):
        headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

        while 1:
            try:
                req = request.Request(url, headers=headers)
                html_data = urlopen(url).read().decode()
            except error.HTTPError as e:
                print("get url Fail")
                print(e.reason, e.code, e.headers)
                return
            except error.URLError as e:
                print(e.reason)
                time.sleep(1)   # resolve [Errno 111] Connection refused or Network is unreachable
            except  http.client.HTTPException as e:
                print("HTTPException retry!!")
                time.sleep(1)
            else:
                # print('Request Successfully')
                soup = BeautifulSoup(html_data, 'html.parser')
                return soup.find_all('tr', {"class": "custDataGridRow", "bgcolor": "White"})

    def combineMsg(name,qtime,price,updown):
        msg = """\n%s
        ==========
        Time quotes     :%s
        Current price   :%0.2f
        Up and down     :%0.2f
        """%(name,qtime,price,updown)
        # msg = """\n%s
        # ==========
        # 報價時間:%s
        # 現價       :%0.2f
        # 漲跌       :%0.2f
        # """%(name,qtime,price,updown)

        return msg

    while 1:
        msg = ""
        url = 'http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx'
        rows = downWeb(url)

        for row in rows:
            items = row.find_all('td')
            name = items[0].a.text.strip()
            if name in targets:
                quote = Quote()
                quote.name = name

                try:
                    quote.trade_price = float(items[6].font.text.replace(',', ''))
                except:
                    print("Not open yet")
                    break
                else:
                    quote.change = float(items[7].font.text)
                    quote.trade_time = datetime.strptime(items[14].font.text, "%H:%M:%S")
                    quote.open = float(items[10].font.text.replace(',', ''))
                    quote.high = float(items[11].font.text.replace(',', ''))
                    quote.low = float(items[12].font.text.replace(',', ''))

                    quotes[name] = quote
                    # msg += combineMsg(quote.name, items[14].font.text, quote.trade_price, quote.change)
                    msg += combineMsg("Taiwan Index Spot", items[14].font.text, quote.trade_price, quote.change)
        
                url = 'https://info512.taifex.com.tw/Future/VIXQuote_Norl.aspx'
                rows = downWeb(url)

                for row in rows:
                    items = row.find_all('td')
                    delta = float(items[1].font.text) - float(items[2].font.text)

                    # msg += combineMsg(items[0].a.text.strip(), items[6].font.text.strip(), float(items[1].font.text.strip()), delta)
                    msg += combineMsg("IVX", items[6].font.text.strip(), float(items[1].font.text.strip()), delta)

                print(msg)
        time.sleep(5)