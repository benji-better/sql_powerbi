import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler


df = pd.read_csv(r'..\supply_chain_portf_10_16_26.csv')

df['Date'] = pd.to_datetime(df['Date'])
stack_df = df.loc[df['SKU_ID'] == 'SKU_1']
stack_df = stack_df.groupby(pd.Grouper(key='Date', freq='W'))['Units_Sold'].sum().reset_index()

# Remove week with only 1 day at end of year
stack_df = stack_df.loc[stack_df['Date'] < (pd.to_datetime('2025-01-01'))]
w_list = list(range(1, 53))
week_list = [f'week_{num}' for num in w_list]

stack_df['Date'] = week_list
stack_df.set_index('Date', inplace=True)

stack_df = stack_df.T
stack_df['SKU_ID'] = 'SKU_1'

week_list_1 = [f'week_{num}' for num in w_list]
sku_56_df = pd.read_csv('sku_56_season_shift.csv')
sku_56_df['SKU_ID'] = 'SKU_56'
stack_df = pd.concat([stack_df, sku_56_df])

for sku in list(range(2, 56)):
    loop_df = df.loc[df['SKU_ID'] == f'SKU_{sku}']
    loop_df = loop_df.groupby(pd.Grouper(key='Date', freq='W'))['Units_Sold'].sum().reset_index()

    # Remove week with only 1 day at end of year
    loop_df = loop_df.loc[loop_df['Date'] < (pd.to_datetime('2025-01-01'))]

    loop_df['Date'] = week_list
    loop_df.set_index('Date', inplace=True)

    loop_df = loop_df.T
    loop_df['SKU_ID'] = f'SKU_{sku}'
    stack_df = pd.concat([stack_df, loop_df])

stack_df = stack_df.reset_index(drop=True)

stripped_df = stack_df.drop(columns="SKU_ID").values
scaler = MinMaxScaler()

normalized_stack = scaler.fit_transform(stripped_df.T).T
###
# K-Means Clustering

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
stack_df["cluster"] = kmeans.fit_predict(normalized_stack)

print(stack_df)
