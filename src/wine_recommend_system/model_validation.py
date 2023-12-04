import re
import pandas as pd
from sklearn.model_selection import train_test_split
from utils import calculate_similarity
from utils import similar_user_recs_add_rank
from utils import similar_wine_top10
from utils import validation


seoul_wine = pd.read_csv('team_share/20231115_seoul_wine_anju.csv')
seoul_wine = seoul_wine[(seoul_wine['제품대분류코드명']=='주류') & (seoul_wine['제품중분류코드명']=='와인')] # 와인인 항목만 추출
seoul_wine['user'] = seoul_wine['연령대_10세'] + " " + seoul_wine['성별'] + " " + seoul_wine['추정라이프스테이지'] + " " + seoul_wine['추정직업군'] + " " + seoul_wine['추정연소득구간'] # 유니크한 유저 컬럼 생성

# 와인명 전처리
seoul_wine['wine'] = seoul_wine['제품코드명'].apply(lambda x: re.sub("\(.*\)|\s-\s.*",'',str(x)))
seoul_wine['wine'] = seoul_wine['wine'].apply(lambda x: re.sub(r'[^A-Z0-9가-힣\s.]+', '', re.sub('(\d+(\.\d+)?(ml|ML|Ml|M|L))', '', (re.sub(".*\)|\s-\s.*", "", str(x))))))

data = seoul_wine[['user','제품코드명','wine']] # 제품코드명:실제와인명, wine:전처리한 와인명

## 최소 사용자 필터링 & 최소 아이템 필터링
user_per_cnt = data[['user', 'wine']].groupby('user').count()
user_per_cnt = user_per_cnt.reset_index()
user_list = list(user_per_cnt[user_per_cnt['wine']>=5]['user'])
df_filtered = data[data['user'].isin(user_list)] # 49642, 548, 356

wine_per_cnt = df_filtered[['wine', 'user']].groupby('wine').count()
wine_per_cnt = wine_per_cnt.reset_index()
wine_list = list(wine_per_cnt[wine_per_cnt['user']>=4]['wine'])
df_filtered2 = df_filtered[df_filtered['wine'].isin(wine_list)] # 49501, 548, 261

data = df_filtered2

# train/test split
x_data = data['user']
y_data = data['wine']
X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, stratify=x_data)

train_df = pd.concat([X_train, y_train], axis=1)
train_df['value']=1
test_df = pd.concat([X_test, y_test], axis=1)

# train_data pivoting
train_data_pivot = pd.pivot_table(train_df, values='value', index='user', columns='wine', aggfunc='count')
train_data_pivot.fillna(0, inplace=True)

# 코사인 유사도 계산
train_user_sim_df, train_item_sim_df = calculate_similarity(train_data_pivot)

# 모든 와인 중 맞춘 확률
all_wine_df = validation(similar_user_recs_add_rank, test_df, train_data_pivot, train_user_sim_df)
print('모든 와인 중 맞춘 확률 : ', len(all_wine_df.groupby(['user']).count()[['wine1']])/len(list(test_df['user'].unique()))*100)


# top10 중 맞춘 확률
top10_wine_df = validation(similar_wine_top10, test_df, train_data_pivot, train_user_sim_df)
print('TOP10 와인 중 맞춘 확률 : ', len(top10_wine_df.groupby(['user']).count()[['wine1']])/len(list(test_df['user'].unique()))*100)