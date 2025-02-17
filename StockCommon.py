#coding=utf-8
import re
try:
    # py3
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
except ImportError:
    # py2
    from urllib2 import Request, urlopen
    from urllib import urlencode

from StockDB import Symbols
from Stock import Stock


ChinaStockIndexList = [
    "sh000001", # sh000001 上证指数
    "399001", # sz399001 深证成指
    "000300", # sh000300 沪深300
    "399005", # sz399005 中小板指
    "399006", # sz399006 创业板指
    "000003",  # sh000003 B股指数
]
WorldStockIndexList = [
    "000001.SS", #"中国上证指数"
    "399001.SZ", #"中国深证成指"
    "399006.SZ", #"创业板指"
    "^DJI", #"美国道琼斯工业平均指数"
    "^IXIC",#"美国纳斯达克综合指数"
    "^GSPC", #"美国标准普尔500指数"
    "^N225", #"日本日经225指数"
    "^TWII", #"台湾台北加权指数"
    "^HSI", #"香港恒生指数"
    "^FCHI", #"法国CAC40指数"
    "^FTSE", #"英国富时100指数"
    "^GDAXI", #"德国法兰克福DAX指数"
]

stocks_sh = range(600000,603999) #603999.SS
stocks_sz = range(2,2787)  #002787.SZ
stocks_cyb = range(300001,300497) #300497.SZ

def symbolFormat(symbol_number):
    symbol = str(symbol_number)
    symbol = symbol.rjust(6,'0')
    symbol_yahoo = ''
    if(symbol == '000001'):
        symbol_yahoo = symbol + '.SZ'
    elif(symbol == '399001'):
        symbol_yahoo =  symbol + 'SZ'
    elif(symbol == '399006'):
        symbol_yahoo = symbol + '.SZ'
    elif(symbol == 'sh000001'):
        symbol_yahoo = '000001.SS'
    elif(re.search('^60',symbol) != None):
        symbol_yahoo = symbol + '.SS'
    elif(re.search('^30',symbol) != None):
        symbol_yahoo =  symbol + '.SZ'
    elif(re.search('^00',symbol) != None):
        symbol_yahoo =  symbol + '.SZ'
    else:
        symbol_yahoo =  symbol + '.SZ'
    return symbol,symbol_yahoo

def testing():
    s,sy = symbolFormat('600547')
    s,sy = symbolFormat('300386')
    s,sy = symbolFormat('555')
    s,sy = symbolFormat('1')
    s,sy = symbolFormat('399006')
    print(s + ' ' + sy)

#testing()

def getAllSymbols():
    allSymbols = []
    for symbol_number in stocks_sh:
        symbol,symbol_y = symbolFormat(str(symbol_number))
        allSymbols.append(symbol)
    for symbol_number in stocks_sz:
        symbol,symbol_y = symbolFormat(str(symbol_number))
        allSymbols.append(symbol)
    for symbol_number in stocks_cyb:
        symbol,symbol_y = symbolFormat(str(symbol_number))
        allSymbols.append(symbol)

    allSymbols.extend(ChinaStockIndexList)
    return allSymbols

def getAllSymbols2():
    return Symbols().getSymbols()

#getAllSymbols2()

def getStock(stockCode, todayStr):
    try:
        exchange = "sz"
        if stockCode =='sh000001':
            exchange =''
        elif(int(stockCode) // 100000 != 6) :
            exchange ='sz'
        else:
            exchange = 'sh'
        dataUrl = "http://hq.sinajs.cn/list=" + exchange + stockCode
        stdout = urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312')
        re_result = re.search('''(")(.+)(")''', stdoutInfo)
        if re_result is None:
            print("the stock %s is not actived" % stockCode)
            return None,1
        tempData = re_result.group(2)
        stockInfo = tempData.split(",")
        #stockCode = stockCode,
        stockName   = stockInfo[0]  #名称
        stockStart  = stockInfo[1]  #开盘
        stockLastEnd= stockInfo[2]  #昨收盘
        stockCur    = stockInfo[3]  #当前
        stockMax    = stockInfo[4]  #最高
        stockMin    = stockInfo[5]  #最低
        stockUp     = round(float(stockCur) - float(stockLastEnd), 2)
        stockRange  = round(float(stockUp) / float(stockLastEnd), 4) * 100
        stockVolume = round(float(stockInfo[8]) / (100 * 10000), 2)
        stockMoney  = round(float(stockInfo[9]) / (100000000), 2)
        stockDate = stockInfo[30]
        stockTime   = stockInfo[31]

        is_close_price = 1
        if stockTime < '15:00:00' and todayStr <= stockDate:
            print("The stock market still is openning, this is not the close price")
            is_close_price = 0
        else:
            is_close_price = 1

        if float(stockStart) < 0.0001:
            print("the stock %s is stopped" % stockCode)
            return None,is_close_price


        content = "#" + stockName + "#(" + stockCode + ")" + " 开盘:" + stockStart \
        + ",最新:" + stockCur + ",最高:" + stockMax + ",最低:" + stockMin \
        + ",涨跌:" + str(stockUp) + ",幅度:" + str(stockRange) + "%" \
        + ",总手:" + str(stockVolume) + "万" + ",金额:" + str(stockMoney) \
        + "亿" + ",更新时间:" + stockTime + "  "

        #imgUrl = "http://image.sinajs.cn/newchart/" + period + "/n/" + exchange + str(stockCode) + ".gif"
        #print(content)
        open_to_close = round((float(stockCur) - float(stockStart))/float(stockStart)*100,4)
        low_to_high =  round((float(stockMax) - float(stockMin))/float(stockMin)*100,4)
        s = Stock(stockCode,stockDate,stockStart,stockCur,stockCur,stockMax,stockMin,stockVolume,stockRange,open_to_close,low_to_high)

    except Exception as e:
        print(">>>>>> Exception: " + str(e))
        return None,1

    return s, is_close_price

def getStockName(stockCode):
    try:
        exchange = "sh" if (int(stockCode) // 100000 == 6) else "sz"
        dataUrl = "http://hq.sinajs.cn/list=" + exchange + stockCode
        stdout = urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312')
        tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
        stockInfo = tempData.split(",")
        stockName   = stockInfo[0]  #名称
        return stockName
    except Exception as e:
        print(e)

    return ''
