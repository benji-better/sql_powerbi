import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv('secure_env_creds.env')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
DATABASE = os.getenv('DB_NAME')

engine = create_engine(f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DATABASE}')

query = "SELECT * FROM supply_data;"
df = pd.read_sql(query, con=engine)
df['date'] = pd.to_datetime(df['date'])

clustered_df = pd.read_csv('seasonality_clustered_skus.csv')

#####
####
# Find Peaks and Troughs

df = df[['sku_id', 'date', 'units_sold']]

cluster_num = 0

sku_list = (clustered_df.loc[clustered_df['cluster'] == cluster_num]['sku_id']).to_list()
filter_df = df[df['sku_id'].isin(sku_list)]
wide_sku_df = filter_df.pivot_table(index='sku_id', columns='date', values='units_sold', aggfunc='sum').reset_index()



wide_sku_df['SKU_ID1'] = wide_sku_df['sku_id'].str.replace('[SKU_]', '', regex=True)
wide_sku_df['SKU_ID1'] = wide_sku_df['SKU_ID1'].astype(int)
wide_sku_df = wide_sku_df.sort_values(by='SKU_ID1')

wide_sku_df = wide_sku_df.reset_index(drop=True)

wide_sku_df = wide_sku_df.drop(columns=['sku_id', 'SKU_ID1'])
df_columns = wide_sku_df.columns.to_list()

stripped_df = wide_sku_df.values
scaler = MinMaxScaler()

normalized_sku_df = scaler.fit_transform(stripped_df.T).T

normalized_sales_df = pd.DataFrame(normalized_sku_df, columns=df_columns)

normalized_sales_days_avg = normalized_sales_df.mean()

normalized_sales_days_avg_df = pd.DataFrame(normalized_sales_days_avg)
normalized_sales_days_avg_df = normalized_sales_days_avg_df.reset_index()
normalized_sales_days_avg_df.columns = ['date', 'Norm_Sales']

cluster_yearly_sales_0 = pd.DataFrame({
    'Min Sales Date': [
        (pd.to_datetime(normalized_sales_days_avg_df.loc[normalized_sales_days_avg_df['Norm_Sales'] == normalized_sales_days_avg_df['Norm_Sales'].min(), 'date'].tolist())[0])],
    'Min Normalized Sales': [(normalized_sales_days_avg_df['Norm_Sales'].min())],
    'Max Sales Date': [(pd.to_datetime(normalized_sales_days_avg_df.loc[normalized_sales_days_avg_df['Norm_Sales'] == normalized_sales_days_avg_df['Norm_Sales'].max(), 'date'].tolist())[0])],
    'Max Normalized Sales': [(normalized_sales_days_avg_df['Norm_Sales'].max())],
    'Cluster': [cluster_num]
})

quarter_list = ['Q1', 'Q2', 'Q3', 'Q4']

quarters_df_dict = {str(q): group for q, group in normalized_sales_days_avg_df.groupby(normalized_sales_days_avg_df['date'].dt.to_period('Q'))}

min_norm_sales_list = []
max_norm_sales_list = []
min_date_norm_sales_list = []
max_date_norm_sales_list = []

# Loop body start

for q in quarter_list:
    loop_df = quarters_df_dict[f'2024{q}']

    min_norm_sales_list.append(loop_df['Norm_Sales'].min())
    max_norm_sales_list.append(loop_df['Norm_Sales'].max())

    min_date_norm_sales_list.append(
        (pd.to_datetime(loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].min(), 'date'].tolist())[0]))
    max_date_norm_sales_list.append(
        (loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].max(), 'date'].tolist())[0])

uni_sku_cluster_list = [cluster_num, cluster_num, cluster_num, cluster_num]

quarter_seasonal_table_0 = pd.DataFrame({
    'Min Sales Date': min_date_norm_sales_list,
    'Min Normalized Sales': min_norm_sales_list,
    'Max Sales Date': max_date_norm_sales_list,
    'Max Normalized Sales': max_norm_sales_list,
    'Quarter': quarter_list,
    'Cluster': uni_sku_cluster_list
})

del min_norm_sales_list
del max_norm_sales_list
del min_date_norm_sales_list
del max_date_norm_sales_list

min_norm_sales_list = []
max_norm_sales_list = []
min_date_norm_sales_list = []
max_date_norm_sales_list = []

first_half_df = pd.concat([quarters_df_dict['2024Q1'], quarters_df_dict['2024Q2']])
second_half_df = pd.concat([quarters_df_dict['2024Q3'], quarters_df_dict['2024Q4']])

biannual_list = ['1st Half', '2nd Half']
biann_df_list = [first_half_df, second_half_df]
for h in biann_df_list:
    loop_df = h

    min_norm_sales_list.append(loop_df['Norm_Sales'].min())
    max_norm_sales_list.append(loop_df['Norm_Sales'].max())

    min_date_norm_sales_list.append(
        (pd.to_datetime(loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].min(), 'date'].tolist())[0]))
    max_date_norm_sales_list.append(
        (loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].max(), 'date'].tolist())[0])

biann_seasonal_table_0 = pd.DataFrame({
    'Min Sales Date': min_date_norm_sales_list,
    'Min Normalized Sales': min_norm_sales_list,
    'Max Sales Date': max_date_norm_sales_list,
    'Max Normalized Sales': max_norm_sales_list,
    'Period': biannual_list,
    'Cluster': [cluster_num, cluster_num]})

del min_norm_sales_list
del max_norm_sales_list
del min_date_norm_sales_list
del max_date_norm_sales_list
del quarters_df_dict

cluster_num = 1

sku_list = (clustered_df.loc[clustered_df['cluster'] == cluster_num]['sku_id']).to_list()

filter_df = df[df['sku_id'].isin(sku_list)]

wide_sku_df = filter_df.pivot_table(index='sku_id', columns='date', values='units_sold', aggfunc='sum').reset_index()

wide_sku_df['SKU_ID1'] = wide_sku_df['sku_id'].str.replace('[SKU_]', '', regex=True)
wide_sku_df['SKU_ID1'] = wide_sku_df['SKU_ID1'].astype(int)
wide_sku_df = wide_sku_df.sort_values(by='SKU_ID1')

wide_sku_df = wide_sku_df.reset_index(drop=True)

wide_sku_df = wide_sku_df.drop(columns=['sku_id', 'SKU_ID1'])
df_columns = wide_sku_df.columns.to_list()

stripped_df = wide_sku_df.values
scaler = MinMaxScaler()

normalized_sku_df = scaler.fit_transform(stripped_df.T).T

normalized_sales_df = pd.DataFrame(normalized_sku_df, columns=df_columns)

normalized_sales_days_avg = normalized_sales_df.mean()

normalized_sales_days_avg_df = pd.DataFrame(normalized_sales_days_avg)
normalized_sales_days_avg_df = normalized_sales_days_avg_df.reset_index()
normalized_sales_days_avg_df.columns = ['date', 'Norm_Sales']

cluster_yearly_sales_1 = pd.DataFrame({
    'Min Sales Date': [
        (pd.to_datetime(normalized_sales_days_avg_df.loc[normalized_sales_days_avg_df['Norm_Sales'] == normalized_sales_days_avg_df['Norm_Sales'].min(), 'date'].tolist())[0])],
    'Min Normalized Sales': [(normalized_sales_days_avg_df['Norm_Sales'].min())],
    'Max Sales Date': [(pd.to_datetime(normalized_sales_days_avg_df.loc[normalized_sales_days_avg_df['Norm_Sales'] == normalized_sales_days_avg_df['Norm_Sales'].max(), 'date'].tolist())[0])],
    'Max Normalized Sales': [(normalized_sales_days_avg_df['Norm_Sales'].max())],
    'Cluster': [cluster_num]
})

quarters_df_dict = {str(q): group for q, group in normalized_sales_days_avg_df.groupby(normalized_sales_days_avg_df['date'].dt.to_period('Q'))}

min_norm_sales_list = []
max_norm_sales_list = []
min_date_norm_sales_list = []
max_date_norm_sales_list = []

# Loop body start

for q in quarter_list:
    loop_df = quarters_df_dict[f'2024{q}']

    min_norm_sales_list.append(loop_df['Norm_Sales'].min())
    max_norm_sales_list.append(loop_df['Norm_Sales'].max())

    min_date_norm_sales_list.append(
        (pd.to_datetime(loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].min(), 'date'].tolist())[0]))
    max_date_norm_sales_list.append(
        (loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].max(), 'date'].tolist())[0])

uni_sku_cluster_list = [cluster_num, cluster_num, cluster_num, cluster_num]

quarter_seasonal_table_1 = pd.DataFrame({
    'Min Sales Date': min_date_norm_sales_list,
    'Min Normalized Sales': min_norm_sales_list,
    'Max Sales Date': max_date_norm_sales_list,
    'Max Normalized Sales': max_norm_sales_list,
    'Quarter': quarter_list,
    'Cluster': uni_sku_cluster_list
})

del min_norm_sales_list
del max_norm_sales_list
del min_date_norm_sales_list
del max_date_norm_sales_list

min_norm_sales_list = []
max_norm_sales_list = []
min_date_norm_sales_list = []
max_date_norm_sales_list = []

first_half_df = pd.concat([quarters_df_dict['2024Q1'], quarters_df_dict['2024Q2']])
second_half_df = pd.concat([quarters_df_dict['2024Q3'], quarters_df_dict['2024Q4']])

biannual_list = ['1st Half', '2nd Half']
biann_df_list = [first_half_df, second_half_df]
for h in biann_df_list:
    loop_df = h

    min_norm_sales_list.append(loop_df['Norm_Sales'].min())
    max_norm_sales_list.append(loop_df['Norm_Sales'].max())

    min_date_norm_sales_list.append(
        (pd.to_datetime(loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].min(), 'date'].tolist())[0]))
    max_date_norm_sales_list.append(
        (loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].max(), 'date'].tolist())[0])

biann_seasonal_table_1 = pd.DataFrame({
    'Min Sales Date': min_date_norm_sales_list,
    'Min Normalized Sales': min_norm_sales_list,
    'Max Sales Date': max_date_norm_sales_list,
    'Max Normalized Sales': max_norm_sales_list,
    'Period': biannual_list,
    'Cluster': [cluster_num, cluster_num]})

del min_norm_sales_list
del max_norm_sales_list
del min_date_norm_sales_list
del max_date_norm_sales_list
del quarters_df_dict

cluster_num = 2

sku_list = (clustered_df.loc[clustered_df['cluster'] == cluster_num]['sku_id']).to_list()

filter_df = df[df['sku_id'].isin(sku_list)]


wide_sku_df = filter_df.pivot_table(index='sku_id', columns='date', values='units_sold', aggfunc='sum').reset_index()

wide_sku_df['SKU_ID1'] = wide_sku_df['sku_id'].str.replace('[SKU_]', '', regex=True)
wide_sku_df['SKU_ID1'] = wide_sku_df['SKU_ID1'].astype(int)
wide_sku_df = wide_sku_df.sort_values(by='SKU_ID1')

wide_sku_df = wide_sku_df.reset_index(drop=True)

wide_sku_df = wide_sku_df.drop(columns=['sku_id', 'SKU_ID1'])
df_columns = wide_sku_df.columns.to_list()

stripped_df = wide_sku_df.values
scaler = MinMaxScaler()

normalized_sku_df = scaler.fit_transform(stripped_df.T).T

normalized_sales_df = pd.DataFrame(normalized_sku_df, columns=df_columns)


normalized_sales_days_avg = normalized_sales_df.mean()

normalized_sales_days_avg_df = pd.DataFrame(normalized_sales_days_avg)
normalized_sales_days_avg_df = normalized_sales_days_avg_df.reset_index()
normalized_sales_days_avg_df.columns = ['date', 'Norm_Sales']

cluster_yearly_sales_2 = pd.DataFrame({
    'Min Sales Date': [
        (pd.to_datetime(normalized_sales_days_avg_df.loc[normalized_sales_days_avg_df['Norm_Sales'] == normalized_sales_days_avg_df['Norm_Sales'].min(), 'date'].tolist())[0])],
    'Min Normalized Sales': [(normalized_sales_days_avg_df['Norm_Sales'].min())],
    'Max Sales Date': [(pd.to_datetime(normalized_sales_days_avg_df.loc[normalized_sales_days_avg_df['Norm_Sales'] == normalized_sales_days_avg_df['Norm_Sales'].max(), 'date'].tolist())[0])],
    'Max Normalized Sales': [(normalized_sales_days_avg_df['Norm_Sales'].max())],
    'Cluster': [cluster_num]
})

quarters_df_dict = {str(q): group for q, group in normalized_sales_days_avg_df.groupby(normalized_sales_days_avg_df['date'].dt.to_period('Q'))}

min_norm_sales_list = []
max_norm_sales_list = []
min_date_norm_sales_list = []
max_date_norm_sales_list = []

# Loop body start

for q in quarter_list:
    loop_df = quarters_df_dict[f'2024{q}']

    min_norm_sales_list.append(loop_df['Norm_Sales'].min())
    max_norm_sales_list.append(loop_df['Norm_Sales'].max())

    min_date_norm_sales_list.append(
        (pd.to_datetime(loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].min(), 'date'].tolist())[0]))
    max_date_norm_sales_list.append(
        (loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].max(), 'date'].tolist())[0])

uni_sku_cluster_list = [cluster_num, cluster_num, cluster_num, cluster_num]

quarter_seasonal_table_2 = pd.DataFrame({
    'Min Sales Date': min_date_norm_sales_list,
    'Min Normalized Sales': min_norm_sales_list,
    'Max Sales Date': max_date_norm_sales_list,
    'Max Normalized Sales': max_norm_sales_list,
    'Quarter': quarter_list,
    'Cluster': uni_sku_cluster_list
})

del min_norm_sales_list
del max_norm_sales_list
del min_date_norm_sales_list
del max_date_norm_sales_list

min_norm_sales_list = []
max_norm_sales_list = []
min_date_norm_sales_list = []
max_date_norm_sales_list = []

first_half_df = pd.concat([quarters_df_dict['2024Q1'], quarters_df_dict['2024Q2']])
second_half_df = pd.concat([quarters_df_dict['2024Q3'], quarters_df_dict['2024Q4']])

biannual_list = ['1st Half', '2nd Half']
biann_df_list = [first_half_df, second_half_df]
for h in biann_df_list:
    loop_df = h

    min_norm_sales_list.append(loop_df['Norm_Sales'].min())
    max_norm_sales_list.append(loop_df['Norm_Sales'].max())

    min_date_norm_sales_list.append(
        (pd.to_datetime(loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].min(), 'date'].tolist())[0]))
    max_date_norm_sales_list.append(
        (loop_df.loc[loop_df['Norm_Sales'] == loop_df['Norm_Sales'].max(), 'date'].tolist())[0])

biann_seasonal_table_2 = pd.DataFrame({
    'Min Sales Date': min_date_norm_sales_list,
    'Min Normalized Sales': min_norm_sales_list,
    'Max Sales Date': max_date_norm_sales_list,
    'Max Normalized Sales': max_norm_sales_list,
    'Period': biannual_list,
    'Cluster': [cluster_num, cluster_num]})

del min_norm_sales_list
del max_norm_sales_list
del min_date_norm_sales_list
del max_date_norm_sales_list
del quarters_df_dict

biann_columns = biann_seasonal_table_1.columns.tolist()

conc_quarter_seasonal_table = pd.concat([quarter_seasonal_table_0, quarter_seasonal_table_1, quarter_seasonal_table_2])
conc_biann_seasonal_table = pd.concat([biann_seasonal_table_0, biann_seasonal_table_1, biann_seasonal_table_2])
conc_annual_seasonal_table = pd.concat([cluster_yearly_sales_0, cluster_yearly_sales_1, cluster_yearly_sales_2])

# conc_quarter_seasonal_table.to_csv('cluster_quarter_sales.csv')
# conc_biann_seasonal_table.to_csv('cluster_biann_sales.csv')
# conc_annual_seasonal_table.to_csv('cluster_annual_sales.csv')

