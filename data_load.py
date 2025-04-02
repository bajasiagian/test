import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import requests
import json
import numpy as np
import datetime as dt

# Data Uploader -- Sheets
scopes = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = Credentials.from_service_account_file("secret.json",scopes=scopes)
client = gspread.authorize(creds)

#Database Need Cluster
need_cluster = client.open("Gen x Needed Actual Lead Type 71").worksheet('By Cluster')
data_need_cluster = need_cluster.get_all_values()
column_names_need_cluster = data_need_cluster[0]
data_need_cluster = data_need_cluster[1:]
cluster_left = pd.DataFrame(data_need_cluster, columns=column_names_need_cluster)

#Database Need Cluster
location_detail = client.open("Car Brands Lead Monthly").worksheet('Sheet3')
data_location_detail = location_detail.get_all_values()
column_names_location_detail = data_location_detail[0]
data_location_detail = data_location_detail[1:]
location_detail = pd.DataFrame(data_location_detail, columns=column_names_location_detail)

#Database Visit
df_visit = client.open("Dealer Penetration Main Data").worksheet('Workdata')
data_df_visit = df_visit.get_all_values()
column_names_df_visit = data_df_visit[0]
data_df_visit = data_df_visit[1:]
df_visit = pd.DataFrame(data_df_visit, columns=column_names_df_visit)

df_visit = df_visit[['Employee Name','Client Name','Date Time Start','Date Time End','Note Start','Note End','Longitude Start','Latitude Start']]
df_visit.rename(columns={'Employee Name':'employee_name','Client Name':'client_name','Date Time Start':'date_time_start','Date Time End':'date_time_end',
                         'Note Start':'note_start','Note End':'note_end','Longitude Start':'long','Latitude Start':'lat'},inplace=True)
df_visit['time_start'] = df_visit['date_time_start'].astype(str).apply(lambda x: x.split('@')[1] if '@' in x else np.nan) + ":00"
df_visit['time_end'] = df_visit['date_time_end'].astype(str).apply(lambda x: x.split('@')[1] if '@' in x else np.nan) + ":00"
df_visit['date'] = df_visit['date_time_start'].astype(str).apply(lambda x: x.split('@')[0] if '@' in x else np.nan)

df_visit['date'] = df_visit['date'].str.strip()
df_visit['date'] = pd.to_datetime(df_visit['date'])
df_visit.drop(columns=['date_time_start','date_time_end'],inplace=True)

#Database Dealer
df_dealer = client.open("Dealer Penetration Main Data").worksheet('Dealer Data')
data_df_dealer = df_dealer.get_all_values()
column_names_df_dealer = data_df_dealer[0]
data_df_dealer = data_df_dealer[1:]
df_dealer = pd.DataFrame(data_df_dealer, columns=column_names_df_dealer)

df_dealer['business_type'] = "Car"
df_dealer = df_dealer[['id_dealer_outlet','brand','business_type','city','name','state','latitude','longitude']]
df_dealer = df_dealer[df_dealer.business_type.isin(['Car','Bike'])]
df_dealer = df_dealer.dropna().reset_index(drop=True)
df_dealer['latitude'] = df_dealer['latitude'].str.replace(',', '', regex=False).astype(float)
df_dealer['longitude'] = df_dealer['longitude'].str.replace(',', '', regex=False).str.strip('.').astype(float)

#Database Sales
sales_data = client.open("ID NCD - Sales Dashboard").worksheet('NCD Sales Tracker')
data_sales_data = sales_data.get_all_values()
column_names_sales_data = data_sales_data[0]
data_sales_data = data_sales_data[1:]
sales_data = pd.DataFrame(data_sales_data, columns=column_names_sales_data)

#Database Sales
running_order = client.open("ID NCD - Package Master").worksheet('Database')
data_running_order = running_order.get_all_values()
column_names_running_order = data_running_order[0]
data_running_order = data_running_order[1:]
running_order = pd.DataFrame(data_running_order, columns=column_names_running_order)


#Get Data for Today
headers_visit = {
    'accept': 'application/json',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMDM5Y2YyNTZiMzFjM2MzYjg4MDc1MmRjM2QxNGVlMGNiMWM3NDUxN2QxMjYwMzBhOTJhYzgxYzI4MDM0ZjczNmU5N2QxMzJkNTMyNDIzMTAiLCJpYXQiOjE3NDAyNDkwMTgsIm5iZiI6MTc0MDI0OTAxOCwiZXhwIjoxNzcxNzg1MDE4LCJzdWIiOiI0NDA2MiIsInNjb3BlcyI6W119.Ft1JTpsyydzpsDYvYBWHEL1RHOuNRNK0YoVfrAM2mJ92wQzZjXQxap-cZMHTOdtlJEC5Sg2GHBQTmWpnEGuJiIY_ksK8d5MH0b8ojSRydaiUdre_J-5EFMdxWbfFVKK14wrxazd10KY07E82wZ7zoledYFfW4ewl4gAzc1mJ9EIKKVECTRSsS8tC208Ur24C0mHha86LV9Z3GEV0lC2QbgZxehL9vcZ5M7bP3sfN8VlKZh3_dVHp3KCgWQRqeAf0XDRx6oe26FoETkwB5x8Pr9Z5KgFcBH9v3B4i4bs4b84_GR3ElHXnfOWz1wPWhDvKjje7xmVFMcH7mf8S8ip1qjPGqeooDKhxGjCmyAMlGjifSyRjECegblq28DRBKy7h-f7aQ0bYVsFs96wcUuj2kln3wOOzUS174QmSV1SY9mJ2MufT7rtSjmr9fom-oybqbVl3zmmSDp2kslzzWZFWtUu7zyVcp-tEvaL8R1dSgDIv4fmxVmWO63P9DYKxHQsiRekYvIPGcWTQ2-n2MmXkdtYEH-Q3RQouNF8A4H9B3tcZwaPDtXHvR94fWfiqHKXhXRHbU9tdYjXRhafz55S6bR3tPf-9TRoW_8XFi-vNRbmnXMGqMgaasPiQn_mMawFu42eYN-6taZ95cp7rMU_5GaceFAWofEWrdxCHy51CxEc',
}
params_visit = {'date_start': '2024-02-22',}
response_visit = requests.get('https://api.kerjoo.com/tenant11170/api/v1/client-visits', params=params_visit, headers=headers_visit)

string_visit = response_visit.text
visit = json.loads(string_visit)
visit_today = pd.DataFrame(visit['data'])

visit_today['name'] = visit_today['personnel'].apply(lambda x: x['name'])