import pandas as pd
import re
from utils import calculate_similarity
from utils import similar_wine_top10

seoul_wine = pd.read_csv('team_share/20231115_seoul_wine_anju.csv')

# 전처리
seoul_wine = seoul_wine[(seoul_wine['제품대분류코드명']=='주류') & (seoul_wine['제품중분류코드명']=='와인')]
seoul_wine['user'] = seoul_wine['연령대_10세'] + " " + seoul_wine['성별'] + " " + seoul_wine['추정라이프스테이지'] + " " + seoul_wine['추정직업군'] + " " + seoul_wine['추정연소득구간']
seoul_wine['wine'] = seoul_wine['제품코드명'].apply(lambda x: re.sub("\(.*\)|\s-\s.*",'',str(x)))
seoul_wine['wine'] = seoul_wine['wine'].apply(lambda x: re.sub(r'[^A-Z0-9가-힣\s.]+', '', re.sub('(\d+(\.\d+)?(ml|ML|Ml|M|L))', '', (re.sub(".*\)|\s-\s.*", "", str(x))))))
data = seoul_wine[['user','제품코드명','wine']] # 제품코드명:실제와인명, wine:전처리한 와인명

# pivot df 생성
data['value'] = 1  # aggfunc를 위한 value 컬럼 추가
data_pivot = pd.pivot_table(data, values='value', index='user', columns='wine', aggfunc=pd.Series.nunique)
data_pivot.fillna(0, inplace=True)

# 유사도 계산
user_sim_df, item_sim_df = calculate_similarity(data_pivot)

# 유저별 추천 와인 10개 dataframe 저장
user_list = list(data['user'].unique())

result = pd.DataFrame()
for user in user_list:
    similar_df = similar_wine_top10(user, data_pivot, user_sim_df)
    similar_df['user'] = user

    result = pd.concat([result, similar_df])

result.reset_index(drop=True).to_csv('user_per_recommended_wine.csv', encoding='utf-8-sig', index=False)