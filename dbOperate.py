
import pandas as pd
import akshare as aks
import pymysql
from sqlalchemy import create_engine
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
    
db_host = 'mttcug-public.mysql.rds.aliyuncs.com'
db_port = 3306
db_user = 'mtt_db'
db_passwd = 'Mtt676992'
db_name = 'stock_db'

engine = create_engine(f'mysql+pymysql://{db_user}:{db_passwd}@{db_host}:{db_port}/{db_name}', pool_recycle=3).connect()

# BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()
# # 更新数据库股票列表
@scheduler.scheduled_job("cron", day_of_week='1-5', hour='9', minute='10')
def update_stock_table():
    stocks = aks.stock_info_a_code_name()
    stocks.to_sql('all_stocks_list', engine, if_exists='replace', index=False)

# 更新股票分类列表
@scheduler.scheduled_job("cron", day_of_week='1-5', hour='9', minute='5')
def update_type_stock_table():
    # 删除数据库中的表
    # with engine.connect() as conn:
    #     conn.execute('drop table all_type_stocks_list;')  # 返回值为ResultProxy类型
    
    thi = aks.stock_info_sh_name_code(indicator='主板A股')
    thi['code'] = thi['公司代码']
    thi['name']=thi['公司简称']
    thi['type']='SH-A'
    data = thi[['code', 'name', 'type']]

    thi1 = aks.stock_info_sh_name_code(indicator='主板B股')
    thi1['code'] = thi1['公司代码']
    thi1['name']=thi1['公司简称']
    thi1['type']='SH-B'
    data1 = thi1[['code', 'name', 'type']]

    thi2 = aks.stock_info_sh_name_code(indicator='科创板')
    thi2['code'] = thi2['公司代码']
    thi2['name']=thi2['公司简称']
    thi2['type']='SH-K'
    data2 = thi2[['code', 'name', 'type']]

    thi3 = aks.stock_info_sz_name_code(indicator='A股列表')
    thi3['code'] = thi3['A股代码']
    thi3['name']=thi3['A股简称']
    thi3['type']='SZ-A'
    data3 = thi3[['code', 'name', 'type']]

    thi4 = aks.stock_info_sz_name_code(indicator='B股列表')
    thi4['code'] = thi4['B股代码']
    thi4['name']=thi4['B股简称']
    thi4['type']='SZ-B'
    data4 = thi4[['code', 'name', 'type']]

    thi5 = aks.stock_info_bj_name_code()
    thi5['code'] = thi5['证券代码']
    thi5['name']=thi5['证券简称']
    thi5['type']='BJ'
    data5 = thi5[['code', 'name', 'type']]

    data = data.append(data1).append(data2).append(data3).append(data4).append(data5)
    data.to_sql('all_type_stocks_list', engine, if_exists='replace', index=False)


