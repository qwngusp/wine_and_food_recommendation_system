import pandas as pd
from utils import make_list
from utils import check_anju_list_no_matching_food
from utils import check_anju_list_yes_matching_food

# 데이터 로드
wine21_food_category_merge = pd.read_csv('real_data/wine21_food_category_merge.csv') # 와인별 전문가 추천 페어링푸드 정보
seoul_wine_anju = pd.read_csv('real_data/seoul_wine_anju_add_wine_info.csv') # 서울시 와인 + 안주 데이터 + 와인정보
seoul_wine_anju = seoul_wine_anju.iloc[:,1:]


## 안주 매핑
recommend_wine = ['##와인명리스트##']
recommend_anju = pd.DataFrame(columns=['wine_name', 'type', 'matching_food','matching_food_list', 'match_food', 'anju_cnt', 'anju'])
anju_idx = 0
for item in recommend_wine:
   # 해당 와인 정보만 select
    matching_food_list = wine21_food_category_merge[wine21_food_category_merge['emart_name']==item]
    matching_food_list = matching_food_list.reset_index(drop=True)
    anju_list = pd.DataFrame()
    # matching_food에 해당하는 대/중/소 카테고리만 selected_category dataframe에 저장
    selected_category = matching_food_list
    selected_matching_food_list = list(matching_food_list['matching_food'].unique())
    
    # matching_food 없을 때
    if len(selected_category)==0:
        cond1 = seoul_wine_anju['제품대분류코드명']!='주류'
        cond2 = seoul_wine_anju['제품대분류코드명']!='음료'
        cond3 = seoul_wine_anju['제품중분류코드명']!='생수'
        cond4 = seoul_wine_anju['제품중분류코드명']!='얼음'
        cond5 = seoul_wine_anju['제품중분류코드명']!='우유'
        cond_list = cond1 & cond2 & cond3 & cond4 & cond5
        
        color_info = seoul_wine_anju[seoul_wine_anju['product_name']==item]['제품소분류코드명']
        if len(color_info) == 0:
            anju_list = seoul_wine_anju[cond_list]
        else:
            wine_color = seoul_wine_anju[seoul_wine_anju['product_name']==item]['제품소분류코드명'].unique()[0]
            if wine_color=='레드와인':
                anju_list = seoul_wine_anju[cond_list & (seoul_wine_anju['red']==1)]
            elif wine_color=='화이트와인':
                anju_list = seoul_wine_anju[cond_list & (seoul_wine_anju['white']==1)]
            else: # 레드/화이트가 아닌 다른 카테고리일 경우
                anju_list = seoul_wine_anju[cond_list]
        recommend_anju = check_anju_list_no_matching_food(anju_list)
        anju_idx += 1
    
    # matching_food 있을 때
    else:
        for food in list(selected_category['matching_food'].unique()):
            anju_list = pd.DataFrame()
            for idx in range(len(selected_category)):
                if food == selected_category.loc[idx]['matching_food']:
                    temp = pd.DataFrame()
                    big = selected_category.loc[idx]['제품대분류']
                    mid = selected_category.loc[idx]['제품중분류']
                    small = selected_category.loc[idx]['제품소분류']
                    category_cond = (seoul_wine_anju['제품대분류코드명']==big) & (seoul_wine_anju['제품중분류코드명']==mid) & (seoul_wine_anju['제품소분류코드명']==small)
                    
                    sweetness = selected_category.loc[idx]['sweetness']; bodied = selected_category.loc[idx]['bodied']
                    country = selected_category.loc[idx]['country']
                    wine_cond1 = (seoul_wine_anju['sweetness']==sweetness) & (seoul_wine_anju['bodied']==bodied)
                    wine_cond2 = seoul_wine_anju['country']==country
                    similar_wine_order_num = list(seoul_wine_anju[wine_cond1 & wine_cond2]['매출_일련번호'])
                    
                    wine_color = seoul_wine_anju[seoul_wine_anju['product_name']==item]['제품소분류코드명'].unique()[0]
                    if wine_color=='레드와인':
                        cond1_df = seoul_wine_anju[category_cond & (seoul_wine_anju['red']==1)]
                        cond2_df = cond1_df[cond1_df['매출_일련번호'].isin(similar_wine_order_num)]
                        anju_list = pd.concat([anju_list, make_list(cond2_df)])
                        if len(cond2_df)==0:
                            print(item, big, mid, small, wine_color, '0')
                            cond2_df = cond1_df
                        else:
                            pass
                    if wine_color=='화이트와인':
                        cond1_df = seoul_wine_anju[category_cond & (seoul_wine_anju['white']==1)]
                        cond2_df = cond1_df[cond1_df['매출_일련번호'].isin(similar_wine_order_num)]
                        if len(cond2_df)==0:
                            print(item, big, mid, small, wine_color, '0')
                            cond2_df = cond1_df
                        else:
                            pass
                        anju_list = pd.concat([anju_list, make_list(cond2_df)])
                else:
                    pass
            recommend_anju = check_anju_list_yes_matching_food(anju_list)
            anju_idx += 1

recommend_anju.to_csv('recommend_anju.csv', index=False, encoding='utf-8-sig')