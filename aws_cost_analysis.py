# AWS Cost Optimization - EDA (Exploratory Data Analysis) Script
# For MBA Project in Business Analytics
# Current Date: 2025-10-12

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import os

# Create output directory for visualizations
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

print("Loading and analyzing the AWS cost data...")

# Load the cleaned data
df = pd.read_csv('aws_cost_optimization_cleaned.csv')

# Ensure date is in datetime format
df['date'] = pd.to_datetime(df['date'])

# Basic information about the dataset
print("\n===== DATASET INFO =====")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Total records: {len(df)}")
print(f"Unique services: {df['service'].nunique()} ({', '.join(df['service'].unique())})")
print(f"Unique regions: {df['region'].nunique()} ({', '.join(df['region'].unique())})")
print(f"Total AWS spend: ${df['cost_usd'].sum():.2f}")

# Add month column for monthly analysis
df['month'] = df['date'].dt.strftime('%Y-%m')
df['day_of_week'] = df['date'].dt.day_name()

# If idle_cost not already in the dataset, calculate it
if 'idle_cost' not in df.columns:
    df['idle_cost'] = df['cost_usd'] * (1 - df['cpu_utilizationpercent']/100)
    
if 'efficiency_score' not in df.columns:
    # Higher score = better efficiency (more utilization per dollar)
    df['efficiency_score'] = np.where(df['cost_usd'] > 0, df['cpu_utilizationpercent'] / df['cost_usd'], 0)

# ===========================================
# 1. TIME SERIES ANALYSIS
# ===========================================
print("\nGenerating time series visualizations...")

# Daily cost trend
plt.figure(figsize=(12, 6))
daily_costs = df.groupby('date')['cost_usd'].sum()
daily_costs.plot(title='Daily AWS Cost Trend')
plt.ylabel('Total Cost (USD)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/daily_cost_trend.png')

# Monthly cost trend
plt.figure(figsize=(12, 6))
monthly_costs = df.groupby('month')['cost_usd'].sum()
monthly_costs.plot(kind='bar', color='teal')
plt.title('Monthly AWS Costs')
plt.ylabel('Total Cost (USD)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('visualizations/monthly_costs.png')

# Cost trend by service over time
plt.figure(figsize=(14, 7))
service_costs_over_time = df.pivot_table(
    index='date', 
    columns='service', 
    values='cost_usd', 
    aggfunc='sum'
).fillna(0)
service_costs_over_time.plot(title='Daily Cost by Service')
plt.ylabel('Cost (USD)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='Service')
plt.tight_layout()
plt.savefig('visualizations/service_costs_over_time.png')

# ===========================================
# 2. COST DISTRIBUTION ANALYSIS
# ===========================================
print("Analyzing cost distribution...")

# Cost by service
service_cost = df.groupby('service')['cost_usd'].sum().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
service_cost.plot(kind='bar', color='skyblue')
plt.title('Total Cost by AWS Service')
plt.ylabel('Total Cost (USD)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/cost_by_service.png')

# Cost by region
region_cost = df.groupby('region')['cost_usd'].sum().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
explode = [0.1] * len(region_cost)  # Explode all slices slightly
region_cost.plot(kind='pie', autopct='%1.1f%%', explode=explode)
plt.title('Cost Distribution by Region')
plt.ylabel('')
plt.tight_layout()
plt.savefig('visualizations/cost_by_region.png')

# Service cost distribution by region
plt.figure(figsize=(12, 8))
region_service_cost = df.pivot_table(
    index='region',
    columns='service',
    values='cost_usd',
    aggfunc='sum'
)
region_service_cost.plot(kind='bar', stacked=True)
plt.title('Service Costs by Region')
plt.ylabel('Total Cost (USD)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title='Service')
plt.tight_layout()
plt.savefig('visualizations/region_service_cost.png')

# ===========================================
# 3. UTILIZATION ANALYSIS
# ===========================================
print("Analyzing resource utilization...")

# Filter for services that have CPU utilization (exclude S3, Lambda, etc.)
cpu_services = df[df['cpu_utilizationpercent'] > 0]

# Scatter plot: CPU Utilization vs Cost
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=cpu_services, 
    x='cpu_utilizationpercent', 
    y='cost_usd', 
    hue='service',
    style='region',
    alpha=0.7
)
plt.title('EC2 Instances: Cost vs. CPU Utilization')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/utilization_vs_cost.png')

# Average CPU utilization by service
utilization = cpu_services.groupby('service')['cpu_utilizationpercent'].mean().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
utilization.plot(kind='bar', color='purple')
plt.title('Average CPU Utilization by Service')
plt.ylabel('Average CPU Utilization (%)')
plt.axhline(y=70, color='r', linestyle='--', label='Target Utilization (70%)')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/utilization_by_service.png')

# Utilization distribution (histogram)
plt.figure(figsize=(10, 6))
sns.histplot(data=cpu_services, x='cpu_utilizationpercent', hue='service', bins=20, kde=True)
plt.title('CPU Utilization Distribution by Service')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/utilization_distribution.png')

# ===========================================
# 4. IDLE COST ANALYSIS
# ===========================================
print("Analyzing idle costs...")

# Top days with highest idle costs
idle_days = df.groupby('date')['idle_cost'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10, 6))
idle_days.plot(kind='bar', color='coral')
plt.title('Top 10 Days with Highest Idle Costs')
plt.ylabel('Idle Cost (USD)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/top_idle_days.png')

# Idle cost by service
idle_by_service = df.groupby('service')['idle_cost'].sum().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
idle_by_service.plot(kind='bar', color='salmon')
plt.title('Total Idle Cost by Service')
plt.ylabel('Idle Cost (USD)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/idle_by_service.png')

# Idle cost percentage of total cost
total_cost = df['cost_usd'].sum()
total_idle = df['idle_cost'].sum()
idle_percent = (total_idle / total_cost) * 100

plt.figure(figsize=(8, 8))
plt.pie([total_idle, total_cost - total_idle], 
        labels=['Idle Cost', 'Active Cost'],
        autopct='%1.1f%%',
        colors=['salmon', 'lightgreen'],
        explode=[0.1, 0])
plt.title(f'Idle Cost: ${total_idle:.2f} ({idle_percent:.1f}% of Total)')
plt.tight_layout()
plt.savefig('visualizations/idle_cost_percent.png')

# ===========================================
# 5. COST FORECASTING
# ===========================================
print("Generating cost forecasts...")

# Group by date and sum costs
daily_cost = df.groupby('date')['cost_usd'].sum().reset_index()
daily_cost = daily_cost.set_index('date')

# Simple exponential smoothing for forecasting
try:
    model = ExponentialSmoothing(daily_cost, trend='add', seasonal=None).fit()
    forecast_days = 30
    forecast = model.forecast(forecast_days)  # Forecast next 30 days
    
    # Plot actual vs forecast
    plt.figure(figsize=(12, 6))
    daily_cost.plot(label='Historical Cost')
    forecast.plot(label='Forecast', color='red')
    plt.title(f'AWS Cost Forecast (Next {forecast_days} Days)')
    plt.ylabel('Daily Cost (USD)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig('visualizations/cost_forecast.png')
    
    # Calculate forecast metrics
    current_month_avg = daily_cost.iloc[-30:].mean()[0]
    forecast_avg = forecast.mean()
    change_percent = ((forecast_avg - current_month_avg) / current_month_avg) * 100
    
    print(f"\nFORECAST INSIGHTS:")
    print(f"Current daily average: ${current_month_avg:.2f}")
    print(f"Forecasted daily average: ${forecast_avg:.2f}")
    print(f"Projected change: {change_percent:.1f}%")
    
except Exception as e:
    print(f"Error in forecasting: {e}")

# ===========================================
# 6. OPTIMIZATION OPPORTUNITIES
# ===========================================
print("\nIdentifying optimization opportunities...")

# Underutilized instances (high cost, low utilization)
ec2_data = df[df['service'] == 'ec2'].copy()
ec2_data['utilization_category'] = pd.cut(
    ec2_data['cpu_utilizationpercent'], 
    bins=[0, 20, 40, 60, 80, 100], 
    labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
)

# Count instances by utilization category
util_counts = ec2_data['utilization_category'].value_counts().sort_index()
plt.figure(figsize=(10, 6))
util_counts.plot(kind='bar', color='lightblue')
plt.title('EC2 Instances by CPU Utilization Category')
plt.ylabel('Number of Instances')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/utilization_categories.png')

# Cost by utilization category
util_cost = ec2_data.groupby('utilization_category')['cost_usd'].sum()
plt.figure(figsize=(10, 6))
util_cost.plot(kind='bar', color='orange')
plt.title('EC2 Cost by Utilization Category')
plt.ylabel('Total Cost (USD)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('visualizations/cost_by_utilization.png')

# ===========================================
# 7. EXPORT SUMMARY DATA
# ===========================================
print("\nExporting summary data...")

# Create a results directory
if not os.path.exists('results'):
    os.makedirs('results')

# Export summary statistics
service_summary = df.groupby('service').agg({
    'cost_usd': ['sum', 'mean', 'count'],
    'cpu_utilizationpercent': ['mean', 'min', 'max'],
    'idle_cost': 'sum'
}).reset_index()
service_summary.columns = ['service', 'total_cost', 'avg_cost', 'instance_count', 
                          'avg_utilization', 'min_utilization', 'max_utilization', 'total_idle_cost']
service_summary['utilization_efficiency'] = service_summary['avg_utilization'] / service_summary['avg_cost']
service_summary['optimization_score'] = service_summary['total_idle_cost'] / service_summary['total_cost'] * 100
service_summary.to_csv('results/service_optimization_summary.csv', index=False)

# Region summary
region_summary = df.groupby('region').agg({
    'cost_usd': ['sum', 'mean', 'count'],
    'cpu_utilizationpercent': 'mean',
    'idle_cost': 'sum'
}).reset_index()
region_summary.columns = ['region', 'total_cost', 'avg_cost', 'instance_count', 'avg_utilization', 'total_idle_cost']
region_summary['utilization_efficiency'] = region_summary['avg_utilization'] / region_summary['avg_cost']
region_summary.to_csv('results/region_summary.csv', index=False)

# Monthly summary
monthly_summary = df.groupby('month').agg({
    'cost_usd': 'sum',
    'idle_cost': 'sum'
}).reset_index()
monthly_summary['idle_percent'] = monthly_summary['idle_cost'] / monthly_summary['cost_usd'] * 100
monthly_summary.to_csv('results/monthly_summary.csv', index=False)

# Top optimization recommendations
low_util_instances = ec2_data[ec2_data['cpu_utilizationpercent'] < 40].copy()
low_util_instances['potential_savings'] = low_util_instances['cost_usd'] * 0.5  # Assuming 50% savings from resizing

top_recommendations = low_util_instances.groupby(['region', 'date']).agg({
    'potential_savings': 'sum',
    'cost_usd': 'sum',
    'cpu_utilizationpercent': 'mean'
}).reset_index().sort_values(by='potential_savings', ascending=False).head(10)

top_recommendations.to_csv('results/top_optimization_recommendations.csv', index=False)

# ===========================================
# ANALYSIS SUMMARY
# ===========================================
print("\n===== ANALYSIS SUMMARY =====")
print(f"Total AWS Cost: ${total_cost:.2f}")
print(f"Total Idle Cost: ${total_idle:.2f} ({idle_percent:.1f}% of total)")
print(f"Most expensive service: {service_cost.index[0]} (${service_cost.iloc[0]:.2f})")
print(f"Most expensive region: {region_cost.index[0]} (${region_cost.iloc[0]:.2f})")

if 'forecast_avg' in locals():
    print(f"Forecasted daily cost: ${forecast_avg:.2f} ({change_percent:.1f}% {'increase' if change_percent > 0 else 'decrease'})")

print("\nTop optimization opportunities:")
print(f"  - Low utilization instances: {len(low_util_instances)} instances below 40% CPU")
print(f"  - Potential monthly savings: ${low_util_instances['potential_savings'].sum():.2f}")

print("\nAll visualizations saved to 'visualizations/' folder")
print("All data summaries exported to 'results/' folder")
print("\nAnalysis complete!")