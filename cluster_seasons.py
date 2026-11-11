import pandas as pd
from sklearn.cluster import KMeans
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

query = (
    "SELECT DATE_TRUNC('week', date) AS sale_week, sku_id, SUM(units_sold) AS week_sales FROM supply_data "
    "GROUP BY DATE_TRUNC('week', date), sku_id "
    "ORDER BY sale_week DESC, week_sales DESC;")
df = pd.read_sql(query, con=engine)

df = df.rename(columns={'week_sales': 'units_sold', 'sale_week': 'date'})
df['date'] = pd.to_datetime(df['date'], utc=True)
df['date'] = df['date'].dt.tz_convert(None)

# Remove week with only 1 day at end of year
filter_df = df.loc[df['date'] < (pd.to_datetime('2024-12-30'))]
filter_df = filter_df.sort_values('date', ascending=False)

wide_sku_df = filter_df.pivot(index='sku_id', columns='date', values='units_sold').reset_index()

wide_sku_df['SKU_ID1'] = wide_sku_df['sku_id'].str.replace('[SKU_]', '', regex=True)
wide_sku_df['SKU_ID1'] = wide_sku_df['SKU_ID1'].astype(int)
wide_sku_df = wide_sku_df.sort_values(by='SKU_ID1')

wide_sku_df = wide_sku_df.reset_index(drop=True)
wide_sku_df = wide_sku_df.drop(columns=['SKU_ID1'])
stripped_df = wide_sku_df.drop(columns=['sku_id']).values

scaler = MinMaxScaler()
normalized_sku_df = scaler.fit_transform(stripped_df.T).T

###
# Cluster
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
wide_sku_df['cluster'] = kmeans.fit_predict(normalized_sku_df)

clustered_df = wide_sku_df[['cluster', 'sku_id']]

###
# Export CSV

# clustered_df.to_csv('seasonality_clustered_skus.csv')
