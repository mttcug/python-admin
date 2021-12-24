from flask import Flask, request, url_for, render_template
from flask_cors import cross_origin
import matplotlib.pyplot as plt
import pandas as pd
import tushare as ts
import akshare as aks
import json
import time
from io import BytesIO
import base64
# import dbOperate
app = Flask(__name__)

url = 'api'
pro = ts.pro_api('79b02307d33ca733aeac643f8d1551a9794607ba8cc905f313815494')

def timeStamp(x):
    timeStamp = float(x)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    return otherStyleTime

# 东方财富网-数据中心-特色数据-机构调研-机构调研详细
# start_date="20210910"; 开始查询的时间
@app.route(f'/{url}/getNews', methods=['GET'])
@cross_origin()
def getNews():
    result = aks.stock_zh_a_alerts_cls()
    result['time'] = result['时间'].astype('str')
    result['news'] = result['快讯信息']
    df = result[['time', 'news']].head().to_json(orient='records', force_ascii=False)
    return df

#############################################################################
# 东方财富网-数据中心-特色数据-机构调研-机构调研统计
# start_date="20210910"; 开始查询的时间
@app.route(f'/{url}/organInvestigate', methods=['GET'])
@cross_origin()
def organInvestigate():
    date = request.args.to_dict().get('date')
    if (not date):
        date = '20211201'
    result = aks.stock_em_jgdy_tj(start_date=date)
    result['code'] = result['代码']
    result['name'] = result['名称']
    result['institute_count'] = result['接待机构数量']
    result['receive_date'] = result['接待日期'].astype('str')
    _result = result[result['institute_count'] > 10]
    _result.sort_values(by="institute_count",ascending=False)
    data = _result[['code', 'name', 'institute_count', 'receive_date']]
    df = data.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 东方财富网-数据中心-特色数据-机构调研-机构调研详细
# start_date="20210910"; 开始查询的时间
@app.route(f'/{url}/organInvestigateDetail', methods=['GET'])
@cross_origin()
def organInvestigateDetail():
    date = request.args.to_dict().get('date')
    result = aks.stock_em_jgdy_detail(start_date=date)
    df = result.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 乐咕乐股网-赚钱效应分析数据
@app.route(f'/{url}/marketActivity', methods=['GET'])
@cross_origin()
def marketActivity():
    result = aks.stock_market_activity_legu()
    df = result.to_json(orient='records', force_ascii=False)
    return df

##############################################################################

# 巨潮资讯-数据中心-新股数据-新股发行
@app.route(f'/{url}/getNewStocks', methods=['GET'])
@cross_origin()
def getNewStocks():
    stocks = aks.stock_new_ipo_cninfo()
    df = stocks.to_json(orient='records', force_ascii=False)
    return df

##############################################################################

# 巨潮资讯-数据中心-行业分析-行业市盈率
# symbol="证监会行业分类"; choice of {"证监会行业分类", "国证行业分类"}
# date="20210910"; 交易日
@app.route(f'/{url}/industryPERatio', methods=['GET'])
@cross_origin()
def industryPERatio():
    symbol = request.args.to_dict().get('symbol')
    date = request.args.to_dict().get('date')
    result = aks.stock_industry_pe_ratio_cninfo(symbol=symbol, date=date)
    df = result.to_json(orient='records', force_ascii=False)
    return df

##############################################################################

# 新浪财经-机构推荐池-股票评级记录
@app.route(f'/{url}/instituteRecommend', methods=['GET'])
@cross_origin()
def instituteRecommend():
    code = request.args.to_dict().get('code')
    result = aks.stock_institute_recommend_detail(stock=code)
    result['code'] = result['股票代码']
    result['name'] = result['股票名称']
    result['target_price'] = result['目标价']
    result['grade'] = result['最新评级']
    result['industry'] = result['行业']
    result['date'] = result['评级日期']
    data = result[['code', 'name', 'target_price', 'grade', 'industry', 'date']]
    df = data.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 获取新浪财经-机构持股-机构持股一览表
# quarter="20051"; 从 2005 年开始, {"一季报":1, "中报":2 "三季报":3 "年报":4}, e.g., "20191", 其中的 1 表示一季报; "20193", 其中的 3 表示三季报;
@app.route(f'/{url}/instituteHold', methods=['GET'])
@cross_origin()
def instituteHold():
    count = request.args.to_dict().get('count')
    quarter = request.args.to_dict().get('quarter')
    result = aks.stock_institute_hold(quarter=quarter)
    result['code'] = result['证券代码']
    result['name'] = result['证券简称']
    result['institute_count'] = result['机构数']
    result['institute_change'] = result['机构数变化']
    result['hold_change'] = result['持股比例增幅']
    result['institute_change_abs'] = result['机构数变化'].abs()
    _result = result[result['institute_count'] > int(count)]
    _result1 = _result.sort_values(by="institute_change_abs",ascending=False)
    data = _result1[['code', 'name', 'institute_count', 'institute_change', 'hold_change']]
    df = data.to_json(orient='records', force_ascii=False)
    return df

##############################################################################

# 北京证券交易所股票代码和简称数据
@app.route(f'/{url}/getAllBJStocks', methods=['GET'])
@cross_origin()
def getAllBJStocks():
    stocks = aks.stock_info_bj_name_code()
    df = stocks.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 深证证券交易所股票代码和股票简称数据
# indicator="A股列表"; choice of {"A股列表", "B股列表", "CDR列表", "AB股列表"}
@app.route(f'/{url}/getAllSZStocks', methods=['GET'])
@cross_origin()
def getAllSZStocks():
    indicator = request.args.to_dict().get('indicator')
    stocks = aks.stock_info_sz_name_code(indicator=indicator)
    stocks['code'] = stocks['A股代码']
    stocks['name'] = stocks['A股简称']
    data = stocks[['code', 'name']]
    df = data.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 上海证券交易所股票代码和简称数据
# indicator="主板A股"; choice of {"主板A股", "主板B股", "科创板"}
@app.route(f'/{url}/getAllSHStocks', methods=['GET'])
@cross_origin()
def getAllSHStocks():
    indicator = request.args.to_dict().get('indicator')
    stocks = aks.stock_info_sh_name_code(indicator=indicator)
    stocks['code'] = stocks['公司代码']
    stocks['name'] = stocks['公司简称']
    data = stocks[['code', 'name']]
    df = data.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 沪深京 A 股股票代码和股票简称数据
@app.route(f'/{url}/getAllStocks', methods=['GET'])
@cross_origin()
def getAllStocks():
    pageNum = int(request.args.to_dict().get('pageNum'))
    pageSize = int(request.args.to_dict().get('pageSize'))
    sql = f'select * from all_type_stocks_list limit {(pageNum-1)* pageSize},{pageSize}'
    stocks = pd.read_sql(sql, dbOperate.engine)
    df = stocks.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 获取东方财富-行情中心-盘口异动数据
# symbol="大笔买入"; choice of {'火箭发射', '快速反弹', '大笔买入', '封涨停板', '打开跌停板', '有大买盘', '竞价上涨', '高开5日线', '向上缺口', '60日新高', '60日大幅上涨', '加速下跌', '高台跳水', '大笔卖出', '封跌停板', '打开涨停板', '有大卖盘', '竞价下跌', '低开5日线', '向下缺口', '60日新低', '60日大幅下跌'}
@app.route(f'/{url}/unusualChange', methods=['GET'])
@cross_origin()
def unusualChange():
    symbol = request.args.to_dict().get('symbol')
    predit = aks.stock_changes_em(symbol=symbol)
    df = predit.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 获取东方财富网-数据中心-特色数据-高管持股
@app.route(f'/{url}/shareholdersChange', methods=['GET'])
@cross_origin()
def shareholdersChange():
    predit = aks.stock_em_ggcg()
    df = predit.to_json(orient='records', force_ascii=False)
    return df

##############################################################################
# 东方财富网-数据中心-研究报告-盈利预测
@app.route(f'/{url}/predictProfit', methods=['GET'])
@cross_origin()
def predictProfit():
    predit = aks.stock_profit_forecast()
    df = predit.to_json(orient='records', force_ascii=False)
    return df

#######################################################################################

#######################################################################################
# 同花顺-板块-概念板块-概念
# Concept
@app.route(f'/{url}/getTHConcept', methods=['GET'])
@cross_origin()
def getTHConcept():
    thc = aks.stock_board_concept_name_ths()
    thc['name'] = thc['概念名称']
    thc['code'] = thc['代码'].str.slice(38, 44, 1)
    thc['count'] = thc['成分股数量']
    data = thc[['code', 'name', 'count']]
    df = data.to_json(orient='records', force_ascii=False)
    return df

# 同花顺-板块-概念板块-成份股数据
# Concept 
# Name
@app.route(f'/{url}/getTHStocksByConceptName', methods=['GET'])
@cross_origin()
def getTHStocksByConceptName():
    symbol = request.args.to_dict().get('symbol')
    stocks = aks.stock_board_concept_cons_ths(symbol = symbol)
    df = stocks.to_json(orient='records', force_ascii=False)
    return df


# 同花顺-板块-概念板块-成份股数据
# Concept
# Code
@app.route(f'/{url}/getTHStocksByConceptCode', methods=['GET'])
@cross_origin()
def getTHStocksByConceptCode():
    symbol = request.args.to_dict().get('symbol')
    stocks = aks.stock_board_cons_ths(symbol = symbol)
    df = stocks.to_json(orient='records', force_ascii=False)
    return df

# 同花顺-板块-行业板块-行业
# Industry
@app.route(f'/{url}/getTHIndustry', methods=['GET'])
@cross_origin()
def getTHIndustry():
    keyWord = request.args.to_dict().get('keyWord')
    thi = aks.stock_board_industry_name_ths()
    if (keyWord):
        thi = thi[thi['name'].str.contains(keyWord)]
    data = thi[['code', 'name']]
    df = data.to_json(orient='records', force_ascii=False)
    return df


# 同花顺-板块-行业板块-成份股数据
# Industry
# Name
@app.route(f'/{url}/getTHIndustryByName', methods=['GET'])
@cross_origin()
def getTHIndustryByName():
    symbol = request.args.to_dict().get('symbol')
    stocks = aks.stock_board_industry_cons_ths(symbol = symbol)
    df = stocks.to_json(orient='records', force_ascii=False)
    return df

# 同花顺-板块-行业板块-成份股数据
# Industry
# Code
@app.route(f'/{url}/getTHStocksByIndustryCode', methods=['GET'])
@cross_origin()
def getTHStocksByIndustryCode():
    symbol = request.args.to_dict().get('symbol')
    stocks = aks.stock_board_cons_ths(symbol = symbol)
    stocks['code'] = stocks['代码']
    stocks['name'] = stocks['名称']
    stocks['flow_current'] = stocks['流通市值']
    stocks['price'] = stocks['现价']
    stocks['price_change'] = stocks['涨跌幅']
    df = stocks.to_json(orient='records', force_ascii=False)
    return df

###################################################################################################
# 东方财富-沪深板块-概念板块
# Concept
@app.route(f'/{url}/getDCConcept', methods=['GET'])
@cross_origin()
def getDCConcept():
    dci = aks.stock_board_concept_name_em()
    dci['code'] = dci['板块代码']
    dci['name'] = dci['板块名称']
    dci['count'] = dci['上涨家数'] + dci['下跌家数']
    data = dci[['code', 'name', 'count']]
    df = data.to_json(orient='records', force_ascii=False)
    return df


# 东方财富-沪深板块-概念板块-板块成份
# Concept
# Name
@app.route(f'/{url}/getDCStocksByConceptName', methods=['GET'])
@cross_origin()
def getDCStocksByConceptName():
    symbol = request.args.to_dict().get('symbol')
    stocks = aks.stock_board_concept_cons_em(symbol = symbol)
    df = stocks.to_json(orient='records', force_ascii=False)
    return df


# 东方财富-沪深京板块-行业板块
# Industry
@app.route(f'/{url}/getDCIndustry', methods=['GET'])
@cross_origin()
def getDCIndustry():
    thi = aks.stock_board_industry_name_em()
    thi['name'] = thi['概念名称']
    thi['code'] = thi['代码'].str.slice(38, 44, 1)
    thi['count'] = thi['成分股数量']
    data = thi[['code', 'name', 'count']]

    df = data.to_json(orient='records', force_ascii=False)
    return df

# 东方财富-沪深板块-行业板块-板块成份
# Industry
# Name
@app.route(f'/{url}/getDCStocksByIndustryName', methods=['GET'])
@cross_origin()
def getDCStocksByIndustryName():
    symbol = request.args.to_dict().get('symbol')
    stocks = aks.stock_board_industry_cons_em(symbol = symbol)
    df = stocks.to_json(orient='records', force_ascii=False)
    return df


#############################################################################################
#请求获取概念股
@app.route(f'/{url}/getConcept', methods=['GET'])
@cross_origin()
def getConcept():
    data = pro.concept()
    df = data.to_json(orient='records', force_ascii=False)
    return df


#请求获取概念股详情
@app.route(f'/{url}/getConceptDetail', methods=['GET'])
@cross_origin()
def getConceptDetail():
    id = request.args.to_dict().get('id')
    ts_code = request.args.to_dict().get('ts_code')
    if (id):
        data = pro.concept_detail(id = id, fields='ts_code,name')
    else:
        data = pro.concept_detail(ts_code=ts_code)
    df = data.to_json(orient='records', force_ascii=False)
    return df


#请求tushare接口
@app.route(f'/{url}/query', methods=['GET'])
@cross_origin()
def query():
    code = request.args.to_dict().get('ts_code')
    start = request.args.to_dict().get('start_date') or '20220101'
    data = pro.query('daily', ts_code = code, start_date = start)
    df = data.to_json(orient='records', force_ascii=False)
    return df


if __name__=='__main__':
    app.run(debug=True, port='8000')