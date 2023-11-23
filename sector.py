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