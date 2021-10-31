def sel_ticker():

  import requests
  import pandas as pd
  import numpy as np


  ##---------------------------------------------------------##
  #   KRW관련된 종목 조회
  ##---------------------------------------------------------##
  url = "https://api.upbit.com/v1/market/all"
  querystring = {"isDetails":"false"}
  headers = {"Accept": "application/json"}
  response = requests.request("GET", url, headers=headers, params=querystring)

  data=response.json()  ## 딕셔러니로 파일 저장
  len_data=int(len(data))
  data_code=[]
  for ii in range(0,len_data,1):
      data_tmp=data[ii]['market']
      if data_tmp[0:3]=="KRW":
        data_code.append(data_tmp)  ## KRW와 관련된 종목조회
  
  
  ##---------------------------------------------------------##
  #   차트 조회 및 해당 조건에 맞는 종목 선택
  #    0. 거래량이 200거래일 기준 10배이상 폭등한 종목 조회
  #    1. xx분 200거래일의 평균 거래량이
  #    2. 오늘일자 거래량이 10배 뛸 때 구매
  #    3. 이조건을 만족하는 것 중에서 가장많이 거래량이 발생한 종목 선택 
  #  lsh(20211030)
  ##---------------------------------------------------------##
  ## 차트
  #url_chart  = "https://api.upbit.com/v1/candles/minutes/10"
  url_chart  = "https://api.upbit.com/v1/candles/minutes/5"
  #url_chart  = "https://api.upbit.com/v1/candles/minutes/60"
  #url_chart  = "https://api.upbit.com/v1/candles/days"
  
  
  data_stn=[]
  data_fac=[]
  data_da1=[]
  data_da2=[]
  for kk in range(0,len(data_code)-1,1):
  #for kk in range(0,1,1):
    querystring = {"market":data_code[kk],"count":"200"}
    headers     = {"Accept": "application/json"}
  
    response    = requests.request("GET", url_chart, headers=headers, params=querystring)
    data        = response.json()
    df          = pd.DataFrame(data)
  
    #print(data_code[kk])  
    #print(df['candle_acc_trade_volume'])
    #print(np.mean(df['candle_acc_trade_volume']))
  
    ##-- 거래량을 체크해서 종목선택 
    avg_vol=np.mean(df['candle_acc_trade_volume'])
    cur_vol=df['candle_acc_trade_volume'][0]  
  
    ##-- 이평을 최근시간과 바로 전시간 구함(상승장을 구하기 위해)
    ma3_0 = df['trade_price'][0]
    ma3_1 = df['trade_price'][1]
  
    ##-- 200거래일 평균거래량의 5배가 넘는 거래가 발생하면 선택
    ##-- 이평 중에서 이전 거래보다 높을 때(상승일때만)
    if (cur_vol > 1*avg_vol) and (ma3_0 > ma3_1):
      data_stn.append(df['market'][1])
      data_fac.append((cur_vol/avg_vol)*100)
      data_da1.append(cur_vol)
      data_da2.append(avg_vol)
  
    data0=[data_stn,data_fac,data_da1,data_da2] 
    kk = kk+1

  ##-- 선택되는 종목이 없으면 'non'으로 표시
  if not data_stn:
    ticker = 'non'
  else:
    data2=pd.DataFrame(np.transpose(data0),columns=['stn_name','factor','Cur_Vol','Avg_Vol'])
    data2.sort_values(by=['factor'],axis=0,ascending=False,inplace=True)
    #print(data2)
    ticker = data2.stn_name[0]

  return ticker
