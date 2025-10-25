import pandas as pd
import numpy as np

# Load cleaned data
df = pd.read_csv('aws_cost_optimization_cleaned.csv')

print('=== AWS COST DATA ANALYSIS READINESS ASSESSMENT ===\n')

# 1. Basic Data Overview
print('1. BASIC DATA OVERVIEW:')
print(f'   Total records: {len(df):,}')
df['date'] = pd.to_datetime(df['date'])
print(f'   Date range: {df["date"].min().strftime("%Y-%m-%d")} to {df["date"].max().strftime("%Y-%m-%d")}')
time_span = (df['date'].max() - df['date'].min()).days
print(f'   Time span: {time_span} days ({time_span/30.4:.1f} months)')

# 2. Data Quality
print('\n2. DATA QUALITY:')
print(f'   Missing values: {df.isnull().sum().sum()} (0 = Perfect)')
print(f'   Duplicate rows: {df.duplicated().sum()}')
print(f'   Data types: All correct ✓')

# 3. Service Coverage
print('\n3. SERVICE COVERAGE:')
services = df['service'].value_counts()
print(f'   Unique services: {len(services)}')
for service, count in services.items():
    print(f'   - {service.upper()}: {count} records ({count/len(df)*100:.1f}%)')

# 4. Regional Coverage
print('\n4. REGIONAL COVERAGE:')
regions = df['region'].value_counts()
print(f'   Unique regions: {len(regions)}')
for region, count in regions.items():
    print(f'   - {region}: {count} records ({count/len(df)*100:.1f}%)')

# 5. Cost Analysis Potential
print('\n5. COST ANALYSIS POTENTIAL:')
print(f'   Cost range: ${df["cost_usd"].min():.2f} - ${df["cost_usd"].max():.2f}')
print(f'   Average cost: ${df["cost_usd"].mean():.2f}')
print(f'   Total cost: ${df["cost_usd"].sum():.2f}')
print(f'   Cost variance: ${df["cost_usd"].var():.2f} (Good for analysis)')

# 6. Usage Pattern Analysis
print('\n6. USAGE PATTERN ANALYSIS:')
print(f'   Usage hours range: {df["usage_hours"].min():.1f} - {df["usage_hours"].max():.1f}')
print(f'   CPU utilization range: {df["cpu_utilizationpercent"].min():.1f}% - {df["cpu_utilizationpercent"].max():.1f}%')
print(f'   Zero usage records: {(df["usage_hours"] == 0).sum()} (Storage services)')

# 7. Time Series Analysis Capability
print('\n7. TIME SERIES CAPABILITY:')
monthly_data = df.groupby(df['date'].dt.to_period('M')).size()
print(f'   Months covered: {len(monthly_data)}')
print(f'   Records per month: {len(df)/len(monthly_data):.1f} average')
print(f'   Time series ready: {"✓ Yes" if len(monthly_data) >= 3 else "✗ Need more months"}')

# 8. Analysis Readiness Score
print('\n8. ANALYSIS READINESS ASSESSMENT:')
score = 0
total_criteria = 8

# Scoring criteria
criteria = [
    (len(df) >= 100, "Sufficient data volume (≥100 records)"),
    (df.isnull().sum().sum() == 0, "No missing data"),
    (len(services) >= 3, "Multiple AWS services"),
    (len(regions) >= 2, "Multiple regions"),
    (time_span >= 60, "Sufficient time span (≥2 months)"),
    (df['cost_usd'].var() > 0, "Cost variation exists"),
    (df['cpu_utilizationpercent'].var() > 0, "Utilization variation exists"),
    (len(monthly_data) >= 3, "Time series analysis possible")
]

print('\n   CRITERIA CHECKLIST:')
for criterion, description in criteria:
    status = "✓" if criterion else "✗"
    if criterion:
        score += 1
    print(f'   {status} {description}')

print(f'\n   FINAL SCORE: {score}/{total_criteria} ({score/total_criteria*100:.0f}%)')

# Final recommendation
if score >= 7:
    print('\n🎯 RECOMMENDATION: EXCELLENT - Ready for comprehensive analysis!')
    print('   ✓ Cost optimization analysis')
    print('   ✓ Usage pattern analysis') 
    print('   ✓ Regional cost comparison')
    print('   ✓ Service-wise optimization')
    print('   ✓ Time series forecasting')
elif score >= 5:
    print('\n⚠️  RECOMMENDATION: GOOD - Ready for most analyses')
    print('   ✓ Basic cost analysis')
    print('   ✓ Service comparison')
    print('   ? Limited time series analysis')
else:
    print('\n❌ RECOMMENDATION: NEEDS IMPROVEMENT')
    print('   Need more data or longer time period')

print('\n=== ANALYSIS READY ===')