import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import matplotlib.font_manager as fm
from PIL import Image


#폰트
fm.fontManager.addfont('font.ttf')
plt.rc('font', family=fm.FontProperties(fname='font.ttf').get_name())

#데이터 불러오기
data_longforeigner = pd.read_csv("https://raw.githubusercontent.com/kkmminjoo/OHNO/main/LONG_FOREIGNER_GU_2021.csv",  encoding='euc-kr')
data_tempforeigner = pd.read_csv("https://raw.githubusercontent.com/kkmminjoo/OHNO/main/TEMP_FOREIGNER_GU_2021.csv", encoding='euc-kr')
data_local = pd.read_csv("https://raw.githubusercontent.com/kkmminjoo/OHNO/main/LOCAL_PEOPLE_GU_2021.csv",  encoding='euc-kr')
code= pd.read_csv("https://raw.githubusercontent.com/kkmminjoo/OHNO/main/%ED%96%89%EC%A0%95%EB%8F%99%EC%BD%94%EB%93%9C_%EB%A7%A4%ED%95%91%EC%A0%95%EB%B3%B4.csv", encoding='euc-kr')

#데이터 전처리
data_longforeigner.drop(columns = ['중국인체류인구수', '중국외외국인체류인구수'], inplace = True)
data_tempforeigner.drop(columns = ['중국인체류인구수', '중국외외국인체류인구수'], inplace = True)

data_local = data_local[(data_local["기준일ID"] >= 20210305) & (data_local["기준일ID"] <= 20210309)]
data_longforeigner = data_longforeigner[(data_longforeigner["기준일ID"] >= 20210305) & (data_longforeigner["기준일ID"] <= 20210309)]
data_tempforeigner = data_tempforeigner[(data_tempforeigner["기준일ID"] >= 20210305) & (data_tempforeigner["기준일ID"] <= 20210309)]

data_local = data_local.rename(columns={'총생활인구수':'local총생활인구수'})
data_longforeigner = data_longforeigner.rename(columns={'총생활인구수' : 'lf총생활인구수'})
data_tempforeigner = data_tempforeigner.rename(columns={'총생활인구수' : 'tf총생활인구수'})

#자치구별로 데이터 가공하기
class sector:
    def __init__(self, name):
      self.name = name

    def de_facto_population(self):
        # 자치구코드 찾기
        filtered = code[code['RESC_CT_NM'] == self.name]
        if filtered.empty:
            print ("올바른 자치구명이 아닙니다.")
        self.id = filtered.iloc[0]['RESD_CD']

        # 자치구코드에 따라 데이터 추출
        self.data_local = data_local[data_local["자치구코드"] == self.id].copy()
        self.data_longforeigner = data_longforeigner[data_longforeigner["자치구코드"] == self.id].copy()
        self.data_tempforeigner = data_tempforeigner[data_tempforeigner["자치구코드"] == self.id].copy()

        # 컬럼 이름 변경
        self.data_local.rename(columns={'총생활인구수': self.name+'총생활인구수'}, inplace=True)
        self.data_longforeigner.rename(columns={'총생활인구수': self.name+'총생활인구수'}, inplace=True)
        self.data_tempforeigner.rename(columns={'총생활인구수': self.name+'총생활인구수'}, inplace=True)

        #일주일 평균 생활인구 계산
        #1. 데이터프레임 병합
        self.total = pd.merge(self.data_local, self.data_longforeigner,  how='outer', on=['기준일ID', '시간대구분', '자치구코드'])
        self.total = pd.merge(self.total, self.data_tempforeigner,  how='outer', on=['기준일ID', '시간대구분', '자치구코드'])
        self.total.drop(columns = ['자치구코드', '기준일ID'], inplace = True)
        #2. '시간대구분' 값이 같은 것끼리 한 행에 위치하도록 함
        self.mean=self.total.groupby('시간대구분').sum()
        self.mean = self.mean.apply(np.floor) # 소수점 아래 버림 (만)단위
        #3. local,lf,tf 더한 뒤 평균 구하기
        self.mean['평균 총생활인구수'] = (self.mean['local총생활인구수'] + self.mean['lf총생활인구수'] + self.mean['tf총생활인구수'])//5
        self.mean.drop(columns = ['local총생활인구수', 'lf총생활인구수', 'tf총생활인구수'], inplace=True)

        return self.name, self.mean


#자치구명 리스트로 반환
gu = []
for i in code.index:
    if code.loc[i,'RESD_DO_NM'] == '서울':
        gu.append(code.loc[i,'RESC_CT_NM'])

#자치구명에 따른 생활인구 그래프 웹페이지에서 보여주기
st.title('서울시 자치구별 생활 인구 분석을 통한 기능 지역 분화 현상 관찰')
tab1, tab2, tab3 = st.tabs(['자치구별 생활인구', '기능 지역 분화 현상', 'Dataset'])

with tab1:
    st.sidebar.title('자치구 선택')
    loc = st.sidebar.selectbox('생활인구를 확인하고 싶은 자치구를 선택하세요', gu)  
    data = sector(loc)
    name, mean = data.de_facto_population()
    plt.figure(figsize=(10, 6))
    st.subheader(loc+' 생활인구')
    plt.title(name + " 시간대별 생활인구")
    if (sum(mean['평균 총생활인구수'][0:8]) + sum(mean['평균 총생활인구수'][20:])) // 12 < sum(mean['평균 총생활인구수'][8:20]) // 12:
        plt.bar(mean.index, mean['평균 총생활인구수'], color='red')
        st.pyplot(plt)
        st.markdown(loc + "는 <span style='color:red;'>__상업 및 공업지역__</span>입니다.", unsafe_allow_html=True)
    else:
        plt.bar(mean.index, mean['평균 총생활인구수'], color='blue')
        st.pyplot(plt)
        st.markdown(loc + "는 <span style='color: blue;'>__주거지역__</span>입니다.", unsafe_allow_html=True)

with tab2:
    city_img = Image.open('city.png')
    Seoul_img = Image.open('Seoul.jpg')
    st.subheader("도시 구조도")
    st.write("")
    st.image(city_img)
    st.write("")
    st.subheader("서울시 내 기능 지역 분화 현황")
    st.write("")
    st.image(Seoul_img)

with tab3:
    st.write("__서울 열린데이터 광장__")
    st.markdown("""
- 서울 생활인구(내국인)
- 서울 생활인구(장기체류 외국인)
- 서울 생활인구(단기체류 외국인)
""")