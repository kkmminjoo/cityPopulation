import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import matplotlib.font_manager as fm
from sector import sector

#폰트
fm.fontManager.addfont('font.ttf')
plt.rc('font', family=fm.FontProperties(fname='font.ttf').get_name())

#데이터 불러오기
data_longforeigner = pd.read_csv("https://raw.githubusercontent.com/kkmminjoo/OHNO/main/LONG_FOREIGNER_GU_2021.csv",  encoding='euc-kr')
data_tempforeigner = pd.read_csv("https://raw.githubusercontent.com/kkmminjoo/OHNO/main/TEMP_FOREIGNER_GU_2021.csv", encoding='euc-kr')
data_local = pd.read_csv("https://raw.githubusercontent.com/kkmminjoo/OHNO/main/LOCAL_PEOPLE_GU_2021.csv",  encoding='euc-kr')
code = pd.read_csv("https://raw.githubusercontent.com/kkmminjoo/OHNO/main/%ED%96%89%EC%A0%95%EB%8F%99%EC%BD%94%EB%93%9C_%EB%A7%A4%ED%95%91%EC%A0%95%EB%B3%B4.csv", encoding='euc-kr')

#데이터 전처리
data_longforeigner.drop(columns = ['중국인체류인구수', '중국외외국인체류인구수'], inplace = True)
data_tempforeigner.drop(columns = ['중국인체류인구수', '중국외외국인체류인구수'], inplace = True)

data_local = data_local[(data_local["기준일ID"] >= 20210305) & (data_local["기준일ID"] <= 20210309)]
data_longforeigner = data_longforeigner[(data_longforeigner["기준일ID"] >= 20210305) & (data_longforeigner["기준일ID"] <= 20210309)]
data_tempforeigner = data_tempforeigner[(data_tempforeigner["기준일ID"] >= 20210305) & (data_tempforeigner["기준일ID"] <= 20210309)]

data_local = data_local.rename(columns={'총생활인구수':'local총생활인구수'})
data_longforeigner = data_longforeigner.rename(columns={'총생활인구수' : 'lf총생활인구수'})
data_tempforeigner = data_tempforeigner.rename(columns={'총생활인구수' : 'tf총생활인구수'})

#자치구명 리스트로 반환
gu = []
for i in code.index:
    if code.loc[i,'RESD_DO_NM'] == '서울':
        gu.append(code.loc[i,'RESC_CT_NM'])

st.title('자치구별 생활 인구 분석')
loc = st.sidebar.selectbox('자치구 선택', gu)

#종로구로 코드 예시
data = sector(loc)
name, mean = data.de_facto_population()
plt.figure(figsize=(10, 6))
plt.title(name + " 시간대별 생활인구", fontdict={"fontsize": 20})
plt.bar(mean.index, mean['평균 총생활인구수'])

st.pyplot(plt)