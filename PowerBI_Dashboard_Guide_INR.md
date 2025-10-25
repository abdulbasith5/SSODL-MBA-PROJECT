
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
