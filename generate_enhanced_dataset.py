# Enhanced AWS Cost Dataset Generator with FinOps Metrics
# Includes: Waste tracking, RI/SP coverage, tag compliance, unit costs
# For MBA Project - Predictive AWS Cost Optimization

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_enhanced_aws_dataset():
    """
    Generate comprehensive AWS cost dataset with FinOps metrics
    """
    print("🔧 Generating Enhanced AWS Cost Dataset with FinOps Metrics...")
    print("="*70 + "\n")
    
    # Date range: ~1057 days (nearly 3 years)
    start_date = datetime(2024, 1, 11)
    end_date = datetime(2026, 12, 3)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Services and regions
    services = ['EC2', 'RDS', 'S3', 'Lambda', 'ECS']
    regions = ['us-east-1', 'us-west-2', 'ap-south-1']
    
    # Service characteristics
    service_configs = {
        'EC2': {'base_cost': 150, 'utilization_range': (40, 95), 'has_ri': True},
        'RDS': {'base_cost': 120, 'utilization_range': (50, 90), 'has_ri': True},
        'S3': {'base_cost': 50, 'utilization_range': (0, 0), 'has_ri': False},  # S3 has no CPU
        'Lambda': {'base_cost': 30, 'utilization_range': (0, 0), 'has_ri': False},  # Serverless
        'ECS': {'base_cost': 80, 'utilization_range': (60, 95), 'has_ri': False}
    }
    
    # Generate records
    records = []
    
    # Sample ~218 dates randomly across the period
    sampled_dates = np.random.choice(date_range, size=218, replace=False)
    sampled_dates = sorted(sampled_dates)
    
    for date in sampled_dates:
        # Convert numpy datetime64 to pandas Timestamp
        date = pd.Timestamp(date)
        
        # Select random service and region
        service = random.choice(services)
        region = random.choice(regions)
        
        config = service_configs[service]
        
        # Calculate day of year for seasonality
        day_of_year = date.timetuple().tm_yday
        
        # Base cost with downward trend (optimization effect)
        days_since_start = (date - start_date).days
        trend_factor = 1.0 - (0.4 * days_since_start / 1057)  # 40% reduction over period
        
        # Seasonal effect (Q4 higher, Q2 lower)
        seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * (day_of_year - 80) / 365.25)
        
        # Regional cost multiplier
        region_multiplier = {
            'us-east-1': 1.0,
            'us-west-2': 1.05,
            'ap-south-1': 0.95
        }[region]
        
        # Calculate cost in USD
        base = config['base_cost']
        noise = np.random.normal(0, base * 0.15)  # 15% noise
        cost_usd = max(10, base * trend_factor * seasonal_factor * region_multiplier + noise)
        
        # Convert to INR (₹83.15 per USD)
        cost_inr = cost_usd * 83.15
        
        # CPU Utilization (only for EC2, RDS, ECS)
        util_min, util_max = config['utilization_range']
        if util_max > 0:
            # Lower utilization early in dataset (before optimization)
            util_base = np.random.uniform(util_min, util_max)
            # Improve utilization over time (optimization effect)
            util_improvement = 15 * (days_since_start / 1057)
            cpu_utilization = min(util_max, util_base + util_improvement)
        else:
            cpu_utilization = 0  # S3 and Lambda don't have CPU metrics
        
        # Calculate idle cost
        if cpu_utilization > 0:
            idle_cost_inr = cost_inr * (1 - cpu_utilization / 100)
        else:
            # S3 and Lambda: assume 20% waste from unused capacity
            idle_cost_inr = cost_inr * 0.20
        
        # FinOps Metrics
        
        # 1. Tag Compliance (improving over time)
        tag_compliance_prob = 0.65 + 0.30 * (days_since_start / 1057)  # 65% -> 95%
        has_required_tags = np.random.random() < tag_compliance_prob
        
        # 2. RI/Savings Plans Coverage (only for EC2 and RDS)
        if config['has_ri']:
            ri_coverage_prob = 0.50 + 0.25 * (days_since_start / 1057)  # 50% -> 75%
            is_covered_by_ri = np.random.random() < ri_coverage_prob
        else:
            is_covered_by_ri = False
        
        # 3. RI/Savings Plans Utilization (if covered)
        if is_covered_by_ri:
            ri_utilization = np.random.uniform(85, 98)  # High utilization
        else:
            ri_utilization = 0
        
        # 4. Rightsizing Opportunity
        if cpu_utilization > 0 and cpu_utilization < 40:
            rightsizing_opportunity = 'Downsize'
            potential_savings_inr = cost_inr * 0.40  # 40% savings from downsizing
        elif cpu_utilization > 90:
            rightsizing_opportunity = 'Upsize'
            potential_savings_inr = 0  # No savings, but avoiding performance issues
        else:
            rightsizing_opportunity = 'Optimal'
            potential_savings_inr = 0
        
        # 5. Storage Optimization (for S3)
        if service == 'S3':
            storage_class = random.choice(['Standard', 'IA', 'Glacier'])
            if storage_class == 'Standard':
                storage_optimization_opportunity = 'Move to IA/Glacier'
                potential_savings_inr = cost_inr * 0.30  # 30% savings
            else:
                storage_optimization_opportunity = 'Optimized'
                potential_savings_inr = 0
        else:
            storage_class = 'N/A'
            storage_optimization_opportunity = 'N/A'
        
        # 6. Team/Owner (for showback/chargeback)
        teams = ['Engineering', 'DataScience', 'DevOps', 'Marketing', 'Product']
        owner_team = random.choice(teams)
        
        # 7. Environment
        environments = ['Production', 'Staging', 'Development', 'Testing']
        env_weights = [0.5, 0.2, 0.2, 0.1]  # Production gets more resources
        environment = np.random.choice(environments, p=env_weights)
        
        # 8. Request/Transaction Count (for unit cost calculation)
        if service in ['EC2', 'Lambda', 'ECS']:
            # Web/API services handle requests
            requests_per_day = int(np.random.uniform(50000, 200000))
        elif service == 'RDS':
            # Database transactions
            requests_per_day = int(np.random.uniform(100000, 500000))
        elif service == 'S3':
            # Storage operations
            requests_per_day = int(np.random.uniform(10000, 100000))
        else:
            requests_per_day = 0
        
        # 9. Calculate Unit Cost
        unit_cost_inr = (cost_inr / requests_per_day) * 1000 if requests_per_day > 0 else 0  # per 1000 requests
        
        # 10. Budget Allocation (monthly budget per service)
        monthly_budgets = {
            'EC2': 140000,  # ₹140K
            'RDS': 110000,  # ₹110K
            'S3': 45000,    # ₹45K
            'Lambda': 28000, # ₹28K
            'ECS': 75000    # ₹75K
        }
        monthly_budget = monthly_budgets[service]
        daily_budget = monthly_budget / 30
        budget_variance_inr = cost_inr - daily_budget
        budget_variance_pct = (budget_variance_inr / daily_budget) * 100
        
        # 11. Anomaly Detection Flag
        # Flag if cost is significantly above expected (>30% above trend)
        expected_cost = base * trend_factor * seasonal_factor * region_multiplier * 83.15
        is_anomaly = cost_inr > (expected_cost * 1.30)
        
        # Create record
        record = {
            'date': date,
            'service': service,
            'region': region,
            'cost_usd': round(cost_usd, 2),
            'cost_inr': round(cost_inr, 2),
            'cpu_utilization': round(cpu_utilization, 2),
            'idle_cost_inr': round(idle_cost_inr, 2),
            'has_required_tags': has_required_tags,
            'tag_compliance_score': 100 if has_required_tags else 0,
            'is_covered_by_ri_sp': is_covered_by_ri,
            'ri_sp_utilization': round(ri_utilization, 2),
            'rightsizing_opportunity': rightsizing_opportunity,
            'potential_rightsizing_savings_inr': round(potential_savings_inr, 2),
            'storage_class': storage_class,
            'storage_optimization': storage_optimization_opportunity,
            'owner_team': owner_team,
            'environment': environment,
            'requests_per_day': requests_per_day,
            'unit_cost_per_1k_requests_inr': round(unit_cost_inr, 4),
            'monthly_budget_inr': monthly_budget,
            'daily_budget_inr': round(daily_budget, 2),
            'budget_variance_inr': round(budget_variance_inr, 2),
            'budget_variance_pct': round(budget_variance_pct, 2),
            'is_cost_anomaly': is_anomaly
        }
        
        records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    df = df.sort_values('date').reset_index(drop=True)
    
    # Add derived metrics
    df['active_cost_inr'] = df['cost_inr'] - df['idle_cost_inr']
    df['waste_rate_pct'] = (df['idle_cost_inr'] / df['cost_inr']) * 100
    
    # Calculate monthly aggregates for trend analysis
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['quarter'] = df['date'].dt.to_period('Q').astype(str)
    
    print(f"✅ Dataset Generated: {len(df)} records")
    print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"   Services: {', '.join(df['service'].unique())}")
    print(f"   Regions: {', '.join(df['region'].unique())}")
    print(f"   Total cost: ₹{df['cost_inr'].sum():,.2f}")
    print(f"   Total idle cost: ₹{df['idle_cost_inr'].sum():,.2f}")
    print(f"   Waste rate: {(df['idle_cost_inr'].sum() / df['cost_inr'].sum() * 100):.2f}%")
    
    return df


def generate_summary_statistics(df):
    """Generate summary statistics and FinOps KPIs"""
    print("\n" + "="*70)
    print("📊 DATASET SUMMARY & FINOPS KPIs")
    print("="*70 + "\n")
    
    total_cost = df['cost_inr'].sum()
    total_idle = df['idle_cost_inr'].sum()
    
    print("💰 COST METRICS")
    print("-" * 70)
    print(f"Total AWS Spend:..................... ₹{total_cost:,.2f}")
    print(f"Total Idle/Waste Cost:............... ₹{total_idle:,.2f}")
    print(f"Waste Rate:.......................... {(total_idle/total_cost*100):.2f}%")
    print(f"Average Daily Cost:.................. ₹{df['cost_inr'].mean():.2f}")
    
    print("\n⚙️ UTILIZATION METRICS")
    print("-" * 70)
    compute_services = df[df['cpu_utilization'] > 0]
    if len(compute_services) > 0:
        print(f"Avg CPU Utilization:................. {compute_services['cpu_utilization'].mean():.2f}%")
        print(f"Services <40% Utilization:........... {len(compute_services[compute_services['cpu_utilization'] < 40])}")
        print(f"Services 40-70% Utilization:......... {len(compute_services[(compute_services['cpu_utilization'] >= 40) & (compute_services['cpu_utilization'] < 70)])}")
        print(f"Services >70% Utilization:........... {len(compute_services[compute_services['cpu_utilization'] >= 70])}")
    
    print("\n🏷️ TAG COMPLIANCE")
    print("-" * 70)
    tag_compliance = (df['has_required_tags'].sum() / len(df)) * 100
    print(f"Tag Compliance Rate:................. {tag_compliance:.2f}%")
    print(f"Tagged Resources:.................... {df['has_required_tags'].sum()}")
    print(f"Untagged Resources:.................. {(~df['has_required_tags']).sum()}")
    
    print("\n💳 RESERVED INSTANCE / SAVINGS PLANS")
    print("-" * 70)
    ri_eligible = df[df['is_covered_by_ri_sp'].notna()]
    if len(ri_eligible) > 0:
        coverage = (ri_eligible['is_covered_by_ri_sp'].sum() / len(ri_eligible)) * 100
        covered = ri_eligible[ri_eligible['is_covered_by_ri_sp']]
        if len(covered) > 0:
            utilization = covered['ri_sp_utilization'].mean()
        else:
            utilization = 0
        print(f"RI/SP Coverage:...................... {coverage:.2f}%")
        print(f"RI/SP Utilization:................... {utilization:.2f}%")
    
    print("\n🔧 RIGHTSIZING OPPORTUNITIES")
    print("-" * 70)
    downsize = df[df['rightsizing_opportunity'] == 'Downsize']
    upsize = df[df['rightsizing_opportunity'] == 'Upsize']
    optimal = df[df['rightsizing_opportunity'] == 'Optimal']
    total_savings = df['potential_rightsizing_savings_inr'].sum()
    
    print(f"Resources to Downsize:............... {len(downsize)}")
    print(f"Resources to Upsize:................. {len(upsize)}")
    print(f"Optimal Resources:................... {len(optimal)}")
    print(f"Potential Monthly Savings:........... ₹{total_savings:,.2f}")
    
    print("\n📈 UNIT COST METRICS")
    print("-" * 70)
    services_with_requests = df[df['requests_per_day'] > 0]
    if len(services_with_requests) > 0:
        print(f"Avg Unit Cost (per 1K requests):..... ₹{services_with_requests['unit_cost_per_1k_requests_inr'].mean():.4f}")
        print(f"Total Daily Requests:................ {services_with_requests['requests_per_day'].sum():,}")
    
    print("\n🎯 BUDGET VARIANCE")
    print("-" * 70)
    over_budget = df[df['budget_variance_inr'] > 0]
    under_budget = df[df['budget_variance_inr'] < 0]
    print(f"Days Over Budget:.................... {len(over_budget)}")
    print(f"Days Under Budget:................... {len(under_budget)}")
    print(f"Avg Budget Variance:................. {df['budget_variance_pct'].mean():+.2f}%")
    
    print("\n🚨 ANOMALY DETECTION")
    print("-" * 70)
    anomalies = df[df['is_cost_anomaly']]
    print(f"Cost Anomalies Detected:............. {len(anomalies)}")
    if len(anomalies) > 0:
        print(f"Total Anomalous Spend:............... ₹{anomalies['cost_inr'].sum():,.2f}")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    # Generate enhanced dataset
    df = generate_enhanced_aws_dataset()
    
    # Generate summary statistics
    generate_summary_statistics(df)
    
    # Save to CSV
    output_file = 'aws_cost_data_enhanced_with_finops.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Enhanced dataset saved to '{output_file}'")
    
    # Save summary by service
    service_summary = df.groupby('service').agg({
        'cost_inr': ['sum', 'mean', 'count'],
        'idle_cost_inr': 'sum',
        'cpu_utilization': 'mean',
        'potential_rightsizing_savings_inr': 'sum',
        'has_required_tags': lambda x: (x.sum() / len(x)) * 100,
        'is_covered_by_ri_sp': lambda x: (x.sum() / len(x)) * 100 if x.notna().any() else 0,
        'unit_cost_per_1k_requests_inr': 'mean'
    }).round(2)
    
    service_summary.columns = ['Total_Cost_INR', 'Avg_Cost_INR', 'Record_Count', 
                               'Total_Idle_Cost_INR', 'Avg_CPU_Util_Pct',
                               'Potential_Savings_INR', 'Tag_Compliance_Pct',
                               'RI_SP_Coverage_Pct', 'Avg_Unit_Cost_INR']
    
    service_summary.to_csv('service_summary_with_finops.csv')
    print(f"✅ Service summary saved to 'service_summary_with_finops.csv'")
    
    print("\n" + "="*70)
    print("✅ ENHANCED DATASET GENERATION COMPLETE")
    print("="*70)
