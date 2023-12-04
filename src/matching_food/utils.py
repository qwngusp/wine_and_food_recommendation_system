
def make_list(df):
    temp_listing = df['제품코드명'].value_counts().to_frame().reset_index()
    temp_listing = temp_listing.rename(columns={'index':'name', '제품코드명':'count'})
    temp_listing['matching_food'] = ''
    try:
        temp_listing['matching_food'] = selected_category.loc[idx]['matching_food']
    except:
        pass
    return temp_listing

def top_10_anju_name(anju_list):
    anju_list['rank'] = anju_list['count'].rank(method="dense", ascending=False)
    anju_list['rank'] = anju_list['rank'].apply(lambda x: int(x))
    top_10_anju = anju_list[anju_list['rank']<=10].sort_values(by='count', ascending=False) # count 정보도 담겨있음
    top_10_anju_name = list(top_10_anju['name'][:10])
    return top_10_anju_name

def check_anju_list_no_matching_food(anju_list):
    if len(anju_list)==0: # 함께산 안주가 없는 경우
        anju_df = seoul_wine_anju[cond_list]
        anju_list_df = make_list(anju_df)
        top_10_anju = top_10_anju_name(anju_list_df)
        recommend_anju.loc[anju_idx] = [item, wine_color, 0, '', '', len(anju_list_df), top_10_anju]
    else: # 있는 경우
        anju_list_df = make_list(anju_list)
        top_10_anju = top_10_anju_name(anju_list_df)
        recommend_anju.loc[anju_idx] = [item, wine_color, 0, '', '', len(anju_list_df), top_10_anju]
    return recommend_anju

def check_anju_list_yes_matching_food(anju_list):
    if len(anju_list)==0: # 함께산 안주가 없는 경우
        anju_df = seoul_wine_anju[category_cond]
        anju_list_df = make_list(anju_df)
        top_10_anju = top_10_anju_name(anju_list_df)
        recommend_anju.loc[anju_idx] = [item, wine_color, 1, selected_matching_food_list, food, len(anju_list), top_10_anju]
    else: # 있는 경우
        top_10_anju = top_10_anju_name(anju_list)
        recommend_anju.loc[anju_idx] = [item, wine_color, 1, selected_matching_food_list, food, len(anju_list), top_10_anju]
    return recommend_anju