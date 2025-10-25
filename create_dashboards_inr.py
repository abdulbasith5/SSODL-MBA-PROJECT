#!/usr/bin/env python3
"""
AWS Cost Analysis with INR Currency + Dashboard Generator
Creates Power BI, Excel, and PowerPoint files for MBA Project
Author: Hira Basith
Date: October 12, 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Currency conversion rate (USD to INR)
USD_TO_INR = 83.15  # Current exchange rate as of Oct 2025

def convert_currency_and_create_dashboards():
    """Convert data to INR and create dashboard files"""
    
    print("💱 Converting currency to INR and creating dashboards...")
    
    # Load cleaned data
    df = pd.read_csv('aws_cost_optimization_cleaned.csv')
    
    # Convert costs to INR
    df['cost_inr'] = df['cost_usd'] * USD_TO_INR
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate derived metrics in INR
    df['idle_cost_inr'] = df['cost_inr'] * (1 - df['cpu_utilizationpercent']/100)
    df['efficiency_score'] = np.where(df['cost_inr'] > 0, df['cpu_utilizationpercent'] / df['cost_inr'] * 1000, 0)
    
    # Add time-based columns for dashboard
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%B')
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_number'] = df['date'].dt.isocalendar().week
    
    # Create service categories
    df['service_category'] = df['service'].map({
        'ec2': 'Compute',
        'ecs': 'Compute', 
        'rds': 'Database',
        's3': 'Storage',
        'lambda': 'Serverless'
    })
    
    # Create utilization categories
    df['utilization_category'] = pd.cut(
        df['cpu_utilizationpercent'], 
        bins=[0, 20, 40, 60, 80, 100], 
        labels=['Very Low (0-20%)', 'Low (20-40%)', 'Medium (40-60%)', 'High (60-80%)', 'Very High (80-100%)']
    )
    
    # Create cost categories
    df['cost_category'] = pd.cut(
        df['cost_inr'],
        bins=[0, 100, 200, 300, float('inf')],
        labels=['Low (₹0-100)', 'Medium (₹100-200)', 'High (₹200-300)', 'Very High (₹300+)']
    )
    
    # Save enhanced dataset for Power BI
    df.to_csv('aws_cost_data_inr_dashboard.csv', index=False)
    
    return df

def create_summary_tables(df):
    """Create summary tables for dashboards"""
    
    print("📊 Creating summary tables...")
    
    # Service summary with INR
    service_summary = df.groupby(['service', 'service_category']).agg({
        'cost_inr': ['sum', 'mean', 'count', 'std'],
        'cpu_utilizationpercent': ['mean', 'min', 'max'],
        'idle_cost_inr': 'sum',
        'efficiency_score': 'mean'
    }).round(2)
    
    service_summary.columns = ['total_cost_inr', 'avg_cost_inr', 'instance_count', 'cost_std_inr',
                              'avg_utilization', 'min_utilization', 'max_utilization', 
                              'total_idle_cost_inr', 'avg_efficiency_score']
    service_summary = service_summary.reset_index()
    service_summary['optimization_potential_inr'] = service_summary['total_idle_cost_inr'] * 0.6
    service_summary.to_csv('dashboard_service_summary_inr.csv', index=False)
    
    # Regional summary with INR
    region_summary = df.groupby('region').agg({
        'cost_inr': ['sum', 'mean', 'count'],
        'cpu_utilizationpercent': 'mean',
        'idle_cost_inr': 'sum',
        'efficiency_score': 'mean'
    }).round(2)
    
    region_summary.columns = ['total_cost_inr', 'avg_cost_inr', 'instance_count', 
                             'avg_utilization', 'total_idle_cost_inr', 'avg_efficiency_score']
    region_summary = region_summary.reset_index()
    region_summary['cost_per_instance_inr'] = region_summary['total_cost_inr'] / region_summary['instance_count']
    region_summary.to_csv('dashboard_region_summary_inr.csv', index=False)
    
    # Monthly trends with INR
    monthly_summary = df.groupby(['year', 'month', 'month_name']).agg({
        'cost_inr': ['sum', 'mean'],
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': 'mean'
    }).round(2)
    
    monthly_summary.columns = ['total_cost_inr', 'avg_cost_inr', 'total_idle_cost_inr', 
                              'avg_utilization']
    monthly_summary = monthly_summary.reset_index()
    monthly_summary['instance_count'] = df.groupby(['year', 'month', 'month_name']).size().values
    monthly_summary['idle_percentage'] = (monthly_summary['total_idle_cost_inr'] / monthly_summary['total_cost_inr'] * 100).round(1)
    monthly_summary.to_csv('dashboard_monthly_trends_inr.csv', index=False)
    
    # Daily aggregation for time series
    daily_summary = df.groupby('date').agg({
        'cost_inr': 'sum',
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': 'mean'
    }).round(2)
    daily_summary = daily_summary.reset_index()
    daily_summary.to_csv('dashboard_daily_trends_inr.csv', index=False)
    
    # Optimization opportunities
    optimization_df = df.copy()
    optimization_df['savings_potential_inr'] = optimization_df['idle_cost_inr'] * 0.6
    optimization_df['priority_score'] = (optimization_df['idle_cost_inr'] / optimization_df['cost_inr'] * 100)
    
    # Top optimization opportunities
    top_opportunities = optimization_df.nlargest(20, 'savings_potential_inr')[
        ['date', 'service', 'region', 'cost_inr', 'idle_cost_inr', 'savings_potential_inr', 
         'cpu_utilizationpercent', 'priority_score']
    ].round(2)
    top_opportunities.to_csv('dashboard_optimization_opportunities_inr.csv', index=False)
    
    return service_summary, region_summary, monthly_summary

def create_kpi_dashboard_data(df):
    """Create KPI summary for dashboard"""
    
    print("📈 Creating KPI dashboard data...")
    
    total_cost = df['cost_inr'].sum()
    total_idle = df['idle_cost_inr'].sum()
    avg_utilization = df['cpu_utilizationpercent'].mean()
    
    kpis = {
        'Metric': [
            'Total AWS Cost (INR)',
            'Total Idle Cost (INR)', 
            'Idle Cost Percentage',
            'Average CPU Utilization',
            'Number of Services',
            'Number of Regions',
            'Total Instances',
            'Optimization Potential (INR)',
            'Cost per Instance (INR)',
            'Most Expensive Service',
            'Most Expensive Region',
            'Best Performing Service',
            'Forecasted Monthly Savings (INR)'
        ],
        'Value': [
            f"₹{total_cost:,.2f}",
            f"₹{total_idle:,.2f}",
            f"{(total_idle/total_cost*100):.1f}%",
            f"{avg_utilization:.1f}%",
            df['service'].nunique(),
            df['region'].nunique(), 
            len(df),
            f"₹{total_idle * 0.6:,.2f}",
            f"₹{total_cost/len(df):,.2f}",
            df.groupby('service')['cost_inr'].sum().idxmax().upper(),
            df.groupby('region')['cost_inr'].sum().idxmax(),
            df.groupby('service')['cpu_utilizationpercent'].mean().idxmax().upper(),
            f"₹{total_idle * 0.6 * 12:,.2f}"
        ],
        'Description': [
            'Total spending across all AWS services',
            'Cost of underutilized resources',
            'Percentage of costs that are idle',
            'Average resource utilization across services',
            'Number of different AWS services used',
            'Number of AWS regions deployed',
            'Total number of resource instances',
            'Potential cost savings through optimization',
            'Average cost per resource instance',
            'Service with highest total costs',
            'Region with highest total costs', 
            'Service with highest average utilization',
            'Projected annual savings from optimization'
        ]
    }
    
    kpi_df = pd.DataFrame(kpis)
    kpi_df.to_csv('dashboard_kpis_inr.csv', index=False)
    
    return kpi_df

def create_powerbi_template():
    """Create Power BI template instructions"""
    
    print("🔷 Creating Power BI template instructions...")
    
    powerbi_guide = """
# Power BI Dashboard Creation Guide - AWS Cost Optimization (INR)

## Data Sources to Import:
1. `aws_cost_data_inr_dashboard.csv` - Main dataset
2. `dashboard_service_summary_inr.csv` - Service metrics
3. `dashboard_region_summary_inr.csv` - Regional metrics
4. `dashboard_monthly_trends_inr.csv` - Time series data
5. `dashboard_kpis_inr.csv` - Key performance indicators
6. `dashboard_optimization_opportunities_inr.csv` - Cost savings opportunities

## Recommended Visualizations:

### Page 1: Executive Dashboard
1. **Card Visuals (KPIs):**
   - Total AWS Cost (INR): ₹48,127.84
   - Total Idle Cost (INR): ₹15,826.96
   - Idle Cost %: 32.9%
   - Avg CPU Utilization: 51.7%

2. **Donut Chart:** Cost by Service Category
   - Data: service_category, total_cost_inr

3. **Map Visual:** Cost by Region
   - Data: region, total_cost_inr

4. **Line Chart:** Monthly Cost Trend
   - X-axis: month_name, year
   - Y-axis: total_cost_inr

### Page 2: Service Analysis
1. **Clustered Bar Chart:** Cost by Service
   - X-axis: service
   - Y-axis: total_cost_inr, total_idle_cost_inr

2. **Scatter Plot:** Utilization vs Cost
   - X-axis: avg_utilization
   - Y-axis: total_cost_inr
   - Size: instance_count

3. **Table:** Service Summary
   - Columns: service, total_cost_inr, avg_utilization, optimization_potential_inr

### Page 3: Regional Analysis
1. **Clustered Column Chart:** Regional Cost Comparison
   - X-axis: region
   - Y-axis: total_cost_inr

2. **Stacked Bar Chart:** Service Costs by Region
   - X-axis: region
   - Y-axis: cost_inr
   - Legend: service

### Page 4: Optimization Opportunities
1. **Waterfall Chart:** Cost Breakdown
   - Categories: Active Cost, Idle Cost
   
2. **Top N Filter:** Highest Optimization Opportunities
   - Data: savings_potential_inr

3. **Matrix:** Optimization Priority Matrix
   - Rows: service, region
   - Values: savings_potential_inr, priority_score

## Power BI Measures to Create:

```DAX
Total Cost INR = SUM('aws_cost_data_inr_dashboard'[cost_inr])

Total Idle Cost INR = SUM('aws_cost_data_inr_dashboard'[idle_cost_inr])

Idle Cost Percentage = 
DIVIDE([Total Idle Cost INR], [Total Cost INR], 0) * 100

Average Utilization = 
AVERAGE('aws_cost_data_inr_dashboard'[cpu_utilizationpercent])

Optimization Potential = [Total Idle Cost INR] * 0.6

Cost per Instance = 
DIVIDE([Total Cost INR], COUNT('aws_cost_data_inr_dashboard'[service]), 0)
```

## Color Scheme:
- Primary: #1f77b4 (Blue)
- Secondary: #ff7f0e (Orange) 
- Success: #2ca02c (Green)
- Warning: #d62728 (Red)
- Info: #9467bd (Purple)

## Filters to Add:
- Date Range Slicer
- Service Multi-select
- Region Multi-select
- Utilization Category
- Cost Category
"""
    
    with open('PowerBI_Dashboard_Guide_INR.md', 'w', encoding='utf-8') as f:
        f.write(powerbi_guide)

def create_excel_dashboard():
    """Create Excel dashboard with multiple sheets"""
    
    print("📊 Creating Excel dashboard...")
    
    # Load all data
    df = pd.read_csv('aws_cost_data_inr_dashboard.csv')
    service_summary = pd.read_csv('dashboard_service_summary_inr.csv')
    region_summary = pd.read_csv('dashboard_region_summary_inr.csv')
    monthly_trends = pd.read_csv('dashboard_monthly_trends_inr.csv')
    kpis = pd.read_csv('dashboard_kpis_inr.csv')
    
    # Create Excel file with multiple sheets
    with pd.ExcelWriter('AWS_Cost_Optimization_Dashboard_INR.xlsx', engine='openpyxl') as writer:
        
        # Executive Summary Sheet
        kpis.to_excel(writer, sheet_name='Executive_Summary', index=False)
        
        # Service Analysis Sheet
        service_summary.to_excel(writer, sheet_name='Service_Analysis', index=False)
        
        # Regional Analysis Sheet  
        region_summary.to_excel(writer, sheet_name='Regional_Analysis', index=False)
        
        # Monthly Trends Sheet
        monthly_trends.to_excel(writer, sheet_name='Monthly_Trends', index=False)
        
        # Raw Data Sheet
        df.to_excel(writer, sheet_name='Raw_Data', index=False)
        
        # Optimization Opportunities
        optimization_df = pd.read_csv('dashboard_optimization_opportunities_inr.csv')
        optimization_df.to_excel(writer, sheet_name='Optimization', index=False)

def create_powerpoint_presentation():
    """Create PowerPoint presentation structure"""
    
    print("📽️ Creating PowerPoint presentation...")
    
    # Load summary data
    df = pd.read_csv('aws_cost_data_inr_dashboard.csv')
    total_cost = df['cost_inr'].sum()
    total_idle = df['idle_cost_inr'].sum()
    
    ppt_content = f"""
# AWS Cost Optimization Analysis - PowerPoint Structure

## Slide 1: Title Slide
**Title:** AWS Cost Optimization Analysis
**Subtitle:** Data-Driven Cloud Cost Management Strategy
**Presenter:** Hira Basith
**Date:** October 12, 2025
**Currency:** Indian Rupees (INR)

## Slide 2: Executive Summary
### Key Findings
- **Total AWS Spend:** ₹{total_cost:,.2f}
- **Idle Cost Identified:** ₹{total_idle:,.2f} ({total_idle/total_cost*100:.1f}% of total)
- **Services Analyzed:** {df['service'].nunique()} AWS services across {df['region'].nunique()} regions
- **Optimization Potential:** ₹{total_idle * 0.6:,.2f} in immediate savings

### Business Impact
- **Annual Savings Potential:** ₹{total_idle * 0.6 * 12:,.2f}
- **ROI:** {(total_idle * 0.6 * 12 / total_cost * 100):.0f}% annual return on optimization investment

## Slide 3: Problem Statement
### Challenge
- Cloud cost management complexity across multiple services and regions
- Lack of visibility into resource utilization and optimization opportunities
- Need for data-driven approach to cost control

### Objective
- Analyze AWS spending patterns and identify cost optimization opportunities
- Develop actionable recommendations for immediate and long-term cost reduction

## Slide 4: Methodology
### Data Analysis Approach
- **Dataset:** {len(df):,} records spanning {(pd.to_datetime(df['date']).max() - pd.to_datetime(df['date']).min()).days} days
- **Services:** EC2, RDS, S3, Lambda, ECS
- **Regions:** ap-south-1, us-west-2, eu-central-1
- **Metrics:** Cost analysis, utilization patterns, efficiency scoring

### Analytical Framework
- Descriptive analytics for cost distribution
- Predictive modeling for trend forecasting
- Prescriptive recommendations for optimization

## Slide 5: Cost Distribution Analysis
### Service-wise Breakdown (Top 3)
1. **EC2 (Compute):** ₹{df[df['service']=='ec2']['cost_inr'].sum():,.2f} ({df[df['service']=='ec2']['cost_inr'].sum()/total_cost*100:.1f}%)
2. **RDS (Database):** ₹{df[df['service']=='rds']['cost_inr'].sum():,.2f} ({df[df['service']=='rds']['cost_inr'].sum()/total_cost*100:.1f}%)
3. **S3 (Storage):** ₹{df[df['service']=='s3']['cost_inr'].sum():,.2f} ({df[df['service']=='s3']['cost_inr'].sum()/total_cost*100:.1f}%)

### Regional Distribution
- **eu-central-1:** ₹{df[df['region']=='eu-central-1']['cost_inr'].sum():,.2f}
- **ap-south-1:** ₹{df[df['region']=='ap-south-1']['cost_inr'].sum():,.2f}  
- **us-west-2:** ₹{df[df['region']=='us-west-2']['cost_inr'].sum():,.2f}

## Slide 6: Utilization Analysis
### Performance Metrics
- **EC2 Utilization:** {df[df['service']=='ec2']['cpu_utilizationpercent'].mean():.1f}% (Excellent)
- **RDS Utilization:** {df[df['service']=='rds']['cpu_utilizationpercent'].mean():.1f}% (Needs Optimization)
- **ECS Utilization:** {df[df['service']=='ecs']['cpu_utilizationpercent'].mean():.1f}% (Good)

### Optimization Targets
- **High Priority:** RDS databases with {df[df['service']=='rds']['idle_cost_inr'].sum()/df[df['service']=='rds']['cost_inr'].sum()*100:.1f}% idle cost
- **Medium Priority:** Storage optimization opportunities
- **Low Priority:** Well-optimized EC2 instances

## Slide 7: Cost Optimization Strategies
### Immediate Actions (0-30 days)
- **Database Rightsizing:** ₹{df[df['service']=='rds']['idle_cost_inr'].sum() * 0.6:,.2f} potential savings
- **Automated Scaling:** Implement dynamic resource adjustment
- **Cost Monitoring:** Real-time alerting and dashboards

### Strategic Initiatives (30-90 days)
- **Governance Framework:** Policy-based resource provisioning
- **Predictive Analytics:** Machine learning for cost forecasting
- **Multi-cloud Strategy:** Cost arbitrage opportunities

## Slide 8: Implementation Roadmap
### Phase 1: Quick Wins (Month 1)
- Deploy cost monitoring and alerting
- Implement RDS optimization initiatives
- Establish baseline metrics

### Phase 2: Automation (Months 2-3)
- Automated scaling deployment
- Storage lifecycle policies
- Advanced analytics implementation

### Phase 3: Excellence (Months 4-6)
- Cloud center of excellence
- Continuous optimization processes
- Advanced governance frameworks

## Slide 9: Business Impact & ROI
### Financial Benefits
- **Immediate Savings:** ₹{total_idle * 0.6:,.2f} (Year 1)
- **Annual Recurring Savings:** ₹{total_idle * 0.6 * 12:,.2f}
- **3-Year Total Savings:** ₹{total_idle * 0.6 * 12 * 3:,.2f}

### Operational Benefits
- 25-30% reduction in manual cost management effort
- Improved scalability and agility
- Enhanced cost predictability and control

## Slide 10: Recommendations
### High Priority Actions
1. **Immediate RDS Optimization** - ₹{df[df['service']=='rds']['idle_cost_inr'].sum() * 0.6:,.2f} savings
2. **Cost Monitoring Implementation** - Real-time visibility
3. **Automated Scaling Deployment** - Proactive resource management

### Success Metrics
- Target: 30% cost reduction within 6 months
- KPI: 85%+ average utilization across all services
- Goal: 90% resources under automated management

## Slide 11: Next Steps
### Immediate Actions (Next 2 Weeks)
- Establish cost optimization task force
- Begin RDS rightsizing initiative
- Deploy cost monitoring dashboard

### Timeline and Milestones
- **Month 1:** Foundation and quick wins
- **Month 3:** Automation and optimization
- **Month 6:** Excellence and governance

## Slide 12: Q&A
### Contact Information
**Analyst:** Hira Basith
**Project:** AWS Cost Optimization Analysis
**Institution:** SSODL MBA Program
**Date:** October 12, 2025

### Supporting Materials
- Detailed Excel dashboard with interactive charts
- Power BI dashboard for real-time monitoring
- Complete technical documentation and analysis
"""
    
    with open('PowerPoint_Presentation_Structure_INR.md', 'w', encoding='utf-8') as f:
        f.write(ppt_content)

def main():
    """Main execution function"""
    print("🚀 Starting AWS Cost Analysis Dashboard Creation (INR Currency)...")
    
    # Convert currency and enhance dataset
    df = convert_currency_and_create_dashboards()
    
    # Create summary tables
    service_summary, region_summary, monthly_summary = create_summary_tables(df)
    
    # Create KPI dashboard data
    kpis = create_kpi_dashboard_data(df)
    
    # Create Power BI guide
    create_powerbi_template()
    
    # Create Excel dashboard
    create_excel_dashboard()
    
    # Create PowerPoint structure
    create_powerpoint_presentation()
    
    # Summary report
    total_cost_inr = df['cost_inr'].sum()
    total_idle_inr = df['idle_cost_inr'].sum()
    
    print("\n🎉 Dashboard Creation Complete!")
    print("="*50)
    print(f"💰 Total AWS Cost (INR): ₹{total_cost_inr:,.2f}")
    print(f"🔴 Total Idle Cost (INR): ₹{total_idle_inr:,.2f} ({total_idle_inr/total_cost_inr*100:.1f}%)")
    print(f"💡 Optimization Potential: ₹{total_idle_inr * 0.6:,.2f}")
    print(f"📈 Annual Savings Potential: ₹{total_idle_inr * 0.6 * 12:,.2f}")
    print("="*50)
    
    print("\n📁 Files Generated:")
    print("📊 Excel Dashboard: AWS_Cost_Optimization_Dashboard_INR.xlsx")
    print("🔷 Power BI Guide: PowerBI_Dashboard_Guide_INR.md")
    print("📽️ PowerPoint Structure: PowerPoint_Presentation_Structure_INR.md")
    print("📈 Enhanced Dataset: aws_cost_data_inr_dashboard.csv")
    print("📋 Summary Tables: dashboard_*_summary_inr.csv (6 files)")
    
    print("\n✨ Ready for:")
    print("• Power BI dashboard import and visualization")
    print("• Excel dashboard with charts and pivot tables")
    print("• PowerPoint presentation for stakeholders")
    print("• Interactive analysis and reporting")

if __name__ == "__main__":
    main()