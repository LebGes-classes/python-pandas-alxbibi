from datetime import datetime
import pandas as pd
import numpy as np


df = pd.read_excel('medical_diagnostic_devices_10000.xlsx')

df['install_date'] = pd.to_datetime(df['install_date'], format='mixed', dayfirst=True)
df['warranty_until'] = pd.to_datetime(df['warranty_until'], format='mixed', dayfirst=True)
df['last_calibration_date'] = pd.to_datetime(df['last_calibration_date'], format='mixed', dayfirst=True)
df['last_service_date'] = pd.to_datetime(df['last_service_date'], format='mixed', dayfirst=True)

report_date = datetime(2026, 3, 7)

filtered_df = df[(df['last_calibration_date'] >= df['install_date']) & (df['warranty_until'] > report_date)].copy()

filtered_df['status'] = filtered_df['status'].str.strip()

states = {
    'planned_installation': ['planned_installation', 'to_install', 'planned', 'scheduled_install'],
    'operational': ['operational', 'working', 'Operational', 'OK', 'op'],
    'maintenance_scheduled': ['maintenance_scheduled', 'maintenance', 'service_scheduled', 'maint_sched'],
    'faulty': ['faulty', 'FAULTY', 'needs_repair', 'broken', 'error']
}

for state in states.keys():
    filtered_df.loc[filtered_df['status'].isin(states[state]), 'status'] = state

filtered_df['issues_count'] = filtered_df['issues_text'].str.split(';').str.len()
filtered_df['overall_issues_count'] = filtered_df.groupby('clinic_id')['issues_count'].transform('sum')

max_count_issues = filtered_df['overall_issues_count'].to_numpy().max()

clinic_with_top_problem_list = list(filtered_df[filtered_df['overall_issues_count'] == max_count_issues]['clinic_name'].unique())

filtered_df = filtered_df[filtered_df['clinic_name'].isin(clinic_with_top_problem_list)]
filtered_df['last_calibration_year'] = filtered_df['last_calibration_date'].dt.year

pivot = pd.pivot_table(filtered_df, values='last_calibration_date', index='clinic_name', columns='last_calibration_year', aggfunc='count', fill_value=0)

pivot.to_excel('pivot_table.xlsx')
