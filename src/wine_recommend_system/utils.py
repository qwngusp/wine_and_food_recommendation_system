import pandas as pd
import scipy
from sklearn.metrics.pairwise import cosine_similarity

# 코사인 유사도 계산
def calculate_similarity(pivot_df):
    piv_sparse = scipy.sparse.csr_matrix(pivot_df.values)

    item_similarity = cosine_similarity(piv_sparse.T)
    user_similarity = cosine_similarity(piv_sparse)

    item_sim_df = pd.DataFrame(item_similarity, index=pivot_df.columns, columns=pivot_df.columns)
    user_sim_df = pd.DataFrame(user_similarity, index=pivot_df.index, columns=pivot_df.index)
    
    return user_sim_df, item_sim_df

# 유사도 높은 TOP10 유저 출력
def top_users(user, pivot_df, sim_df):
    if user not in pivot_df.columns:
        return('No data available on user {}'.format(user))
    
    print('Most Similar Users:\n')
    result = sim_df.sort_values(by=user, ascending=False).loc[:, user][1:11]
    for user, sim in result.items():
        print('User #{0}, Similarity value: {1:.2f}'.format(user, sim))
        
# 모든 유저 유사도와 순위 df return
def similar_user_recs_add_rank(user, data_pivot, user_sim_df):
    if user not in data_pivot.index:
        return('No data available on user {}'.format(user))
    
    sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:11]
    
    best = []
    most_common = {}
    
    for i in sim_users:
        result_sorted = data_pivot.loc[i,:][(data_pivot.loc[user,:]==0)].sort_values(ascending=False)
        best.append(result_sorted.index[:10].tolist())
    for i in range(len(best)):
        for j in best[i]:
            if j in most_common:
                most_common[j] += 1
            else:
                most_common[j] = 1
    most_df = pd.DataFrame.from_dict(data=most_common, orient='index', columns=['count'])
    most_df['ranking'] = most_df['count'].rank(method='first', ascending=False)
    most_df = most_df.sort_values(by='ranking')
    most_df = most_df.reset_index(drop=True)
    most_df = most_df.rename(columns={'index':'wine'})
    return most_df


# 10가지 추천와인과 갯수 df return
def similar_wine_top10(user, data_pivot, user_sim_df):
    if user not in data_pivot.index:
        return('No data available on user {}'.format(user))
    sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:11]
    print('sim_users', sim_users)
    
    best = []
    most_common = {}
    
    for i in sim_users:
        result_sorted = data_pivot.loc[i,:][(data_pivot.loc[user,:]==0)].sort_values(ascending=False)
        best.append(result_sorted.index[:10].tolist())
    for i in range(len(best)):
        for j in best[i]:
            if j in most_common:
                most_common[j] += 1
            else:
                most_common[j] = 1
    key_list = most_common.keys()
    value_list = most_common.values()
    sorted_df = pd.DataFrame(columns=['wine','count'], data=zip(key_list, value_list))
    sorted_df = sorted_df.sort_values(by=['count'], ascending=False).reset_index(drop=True)
    
    return sorted_df[:10]

# 추천 시스템 성능 검증(train/test)
def validation(func, test_df, train_data_pivot, train_user_sim_df):
    test_user_list = list(set(test_df['user'].unique()))

    user_list = []
    wine_name_list = []
    temp_list = []
    rank_list = []

    for user in test_user_list:
        similar_df = func(user, train_data_pivot, train_user_sim_df)
        check_wine = test_df[test_df['user']==user]['wine'].unique()
        for item in check_wine:
            for idx, s_item in enumerate(similar_df['wine']):
                if item==s_item:
                    user_list.append(user)
                    wine_name_list.append(item)
                    temp_list.append(s_item)
                    rank_list.append(similar_df.loc[idx]['ranking'])
    result = pd.DataFrame(columns=['user','wine1','wine2','rank'],
                        data=zip(user_list, wine_name_list, temp_list, rank_list))
    
    return result