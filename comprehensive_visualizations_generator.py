#!/usr/bin/env python3
"""
Comprehensive Visualizations Generator for MBA Project
AWS Cost Optimization Analysis - Business Analytics
Author: Mohammed Abdul Basith
Date: October 12, 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# Set style for professional charts
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Currency conversion
USD_TO_INR = 83.15

def create_visualizations_directory():
    """Create directory for visualizations"""
    viz_dir = "visualizations"
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
    return viz_dir

def load_and_prepare_data():
    """Load and prepare data with INR conversion"""
    print("📊 Loading and preparing data...")
    
    df = pd.read_csv('aws_cost_optimization_cleaned.csv')
    df['cost_inr'] = df['cost_usd'] * USD_TO_INR
    df['idle_cost_inr'] = df['cost_inr'] * (1 - df['cpu_utilizationpercent']/100)
    df['utilized_cost_inr'] = df['cost_inr'] - df['idle_cost_inr']
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    df['efficiency_score'] = df['cpu_utilizationpercent']
    
    return df

def create_executive_summary_charts(df, viz_dir):
    """Create executive summary visualizations for report and PPT"""
    print("📈 Creating executive summary charts...")
    
    # 1. Cost Overview Pie Chart
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('AWS Cost Optimization - Executive Summary Dashboard', fontsize=16, fontweight='bold')
    
    # Total Cost vs Optimization Opportunity
    cost_data = [
        df['utilized_cost_inr'].sum(),
        df['idle_cost_inr'].sum()
    ]
    labels = ['Utilized Cost', 'Optimization Opportunity']
    colors = ['#2E8B57', '#FF6B6B']
    
    ax1.pie(cost_data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax1.set_title(f'Total AWS Investment: ₹{df["cost_inr"].sum():,.0f}', fontweight='bold')
    
    # Service-wise Cost Distribution
    service_costs = df.groupby('service')['cost_inr'].sum()
    ax2.pie(service_costs.values, labels=service_costs.index, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Cost Distribution by Service', fontweight='bold')
    
    # Regional Cost Distribution
    region_costs = df.groupby('region')['cost_inr'].sum()
    ax3.bar(region_costs.index, region_costs.values, color=['#FF9999', '#66B2FF', '#99FF99'])
    ax3.set_title('Regional Cost Distribution (INR)', fontweight='bold')
    ax3.set_ylabel('Cost (INR)')
    ax3.tick_params(axis='x', rotation=45)
    
    # Efficiency Scores by Service
    efficiency_by_service = df.groupby('service')['cpu_utilizationpercent'].mean()
    bars = ax4.bar(efficiency_by_service.index, efficiency_by_service.values, 
                   color=['#FF7F7F' if x < 70 else '#90EE90' for x in efficiency_by_service.values])
    ax4.set_title('Average Utilization by Service (%)', fontweight='bold')
    ax4.set_ylabel('CPU Utilization (%)')
    ax4.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Target (70%)')
    ax4.legend()
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/01_executive_summary_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. KPI Summary Table Chart
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Create KPI table data
    kpi_data = [
        ['Total AWS Investment', f'₹{df["cost_inr"].sum():,.2f}', '100%'],
        ['Utilized Cost', f'₹{df["utilized_cost_inr"].sum():,.2f}', f'{(df["utilized_cost_inr"].sum()/df["cost_inr"].sum())*100:.1f}%'],
        ['Optimization Opportunity', f'₹{df["idle_cost_inr"].sum():,.2f}', f'{(df["idle_cost_inr"].sum()/df["cost_inr"].sum())*100:.1f}%'],
        ['Annual Savings Potential', f'₹{df["idle_cost_inr"].sum() * 0.6 * 12:,.2f}', 'Target'],
        ['Average Utilization', f'{df["cpu_utilizationpercent"].mean():.1f}%', 'Current'],
        ['Target Utilization', '70%', 'Benchmark'],
        ['Services Analyzed', f'{df["service"].nunique()}', 'Complete'],
        ['Regions Covered', f'{df["region"].nunique()}', 'Multi-Region']
    ]
    
    table = ax.table(cellText=kpi_data,
                    colLabels=['Key Performance Indicator', 'Value (INR)', 'Status'],
                    cellLoc='center',
                    loc='center',
                    bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2)
    
    # Style the table
    for i in range(len(kpi_data) + 1):
        for j in range(3):
            cell = table[(i, j)]
            if i == 0:  # Header
                cell.set_facecolor('#4472C4')
                cell.set_text_props(weight='bold', color='white')
            elif 'Optimization' in kpi_data[i-1][0] if i > 0 else False:
                cell.set_facecolor('#FFE6E6')
            elif 'Savings' in kpi_data[i-1][0] if i > 0 else False:
                cell.set_facecolor('#E6F3E6')
    
    plt.title('AWS Cost Optimization - Key Performance Indicators', 
              fontsize=14, fontweight='bold', pad=20)
    plt.savefig(f'{viz_dir}/02_kpi_summary_table.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_service_analysis_charts(df, viz_dir):
    """Create service-wise analysis charts"""
    print("🔧 Creating service analysis charts...")
    
    # 1. Service Performance Matrix
    fig, ax = plt.subplots(figsize=(12, 8))
    
    service_summary = df.groupby('service').agg({
        'cost_inr': 'sum',
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': 'mean'
    }).reset_index()
    
    service_summary['optimization_percent'] = (service_summary['idle_cost_inr'] / service_summary['cost_inr']) * 100
    
    # Bubble chart
    scatter = ax.scatter(service_summary['cpu_utilizationpercent'], 
                        service_summary['optimization_percent'],
                        s=service_summary['cost_inr']/10,  # Size based on cost
                        alpha=0.7,
                        c=range(len(service_summary)),
                        cmap='viridis')
    
    # Add service labels
    for i, service in enumerate(service_summary['service']):
        ax.annotate(service.upper(), 
                   (service_summary.iloc[i]['cpu_utilizationpercent'], 
                    service_summary.iloc[i]['optimization_percent']),
                   xytext=(5, 5), textcoords='offset points', fontweight='bold')
    
    ax.set_xlabel('Average CPU Utilization (%)', fontweight='bold')
    ax.set_ylabel('Optimization Opportunity (%)', fontweight='bold')
    ax.set_title('Service Performance Matrix\n(Bubble size = Total Cost)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add quadrant lines
    ax.axvline(x=70, color='red', linestyle='--', alpha=0.5, label='Target Utilization')
    ax.axhline(y=30, color='red', linestyle='--', alpha=0.5, label='High Optimization')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/03_service_performance_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Service Cost Breakdown with Optimization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Cost breakdown
    service_costs = service_summary.set_index('service')[['cost_inr', 'idle_cost_inr']]
    service_costs['utilized_cost_inr'] = service_costs['cost_inr'] - service_costs['idle_cost_inr']
    
    service_costs[['utilized_cost_inr', 'idle_cost_inr']].plot(kind='bar', stacked=True, ax=ax1,
                                                               color=['#2E8B57', '#FF6B6B'])
    ax1.set_title('Service-wise Cost Breakdown (INR)', fontweight='bold')
    ax1.set_ylabel('Cost (INR)')
    ax1.legend(['Utilized Cost', 'Idle Cost'])
    ax1.tick_params(axis='x', rotation=45)
    
    # Utilization comparison
    utilization_data = service_summary.set_index('service')['cpu_utilizationpercent']
    bars = ax2.bar(utilization_data.index, utilization_data.values,
                   color=['#FF7F7F' if x < 70 else '#90EE90' for x in utilization_data.values])
    ax2.set_title('Service Utilization Performance', fontweight='bold')
    ax2.set_ylabel('CPU Utilization (%)')
    ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Target (70%)')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars, utilization_data.values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/04_service_cost_utilization.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_regional_analysis_charts(df, viz_dir):
    """Create regional analysis charts"""
    print("🌍 Creating regional analysis charts...")
    
    # 1. Regional Performance Comparison
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Regional Analysis Dashboard', fontsize=16, fontweight='bold')
    
    regional_summary = df.groupby('region').agg({
        'cost_inr': 'sum',
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': 'mean',
        'service': 'nunique'
    }).reset_index()
    
    regional_summary['optimization_percent'] = (regional_summary['idle_cost_inr'] / regional_summary['cost_inr']) * 100
    
    # Total cost by region
    bars1 = ax1.bar(regional_summary['region'], regional_summary['cost_inr'], 
                    color=['#FF9999', '#66B2FF', '#99FF99'])
    ax1.set_title('Total Cost by Region (INR)', fontweight='bold')
    ax1.set_ylabel('Cost (INR)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, value in zip(bars1, regional_summary['cost_inr']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 100,
                f'₹{value:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    # Optimization opportunity by region
    bars2 = ax2.bar(regional_summary['region'], regional_summary['optimization_percent'],
                    color=['#FFB366', '#66B2FF', '#99FF99'])
    ax2.set_title('Optimization Opportunity by Region (%)', fontweight='bold')
    ax2.set_ylabel('Optimization Opportunity (%)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, value in zip(bars2, regional_summary['optimization_percent']):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Regional utilization comparison
    bars3 = ax3.bar(regional_summary['region'], regional_summary['cpu_utilizationpercent'],
                    color=['#FF7F7F' if x < 70 else '#90EE90' for x in regional_summary['cpu_utilizationpercent']])
    ax3.set_title('Average Utilization by Region', fontweight='bold')
    ax3.set_ylabel('CPU Utilization (%)')
    ax3.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Target (70%)')
    ax3.legend()
    ax3.tick_params(axis='x', rotation=45)
    
    # Service diversity by region
    bars4 = ax4.bar(regional_summary['region'], regional_summary['service'],
                    color=['#FFCC99', '#99CCFF', '#CCFFCC'])
    ax4.set_title('Service Diversity by Region', fontweight='bold')
    ax4.set_ylabel('Number of Services')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/05_regional_analysis_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_time_series_analysis(df, viz_dir):
    """Create time series analysis charts"""
    print("📅 Creating time series analysis...")
    
    # 1. Monthly Cost Trends
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    monthly_data = df.groupby('month').agg({
        'cost_inr': 'sum',
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': 'mean'
    }).reset_index()
    
    monthly_data['month_str'] = monthly_data['month'].astype(str)
    monthly_data['utilized_cost_inr'] = monthly_data['cost_inr'] - monthly_data['idle_cost_inr']
    
    # Stacked area chart for costs
    ax1.fill_between(monthly_data['month_str'], 0, monthly_data['utilized_cost_inr'], 
                     label='Utilized Cost', alpha=0.7, color='#2E8B57')
    ax1.fill_between(monthly_data['month_str'], monthly_data['utilized_cost_inr'], 
                     monthly_data['cost_inr'], label='Idle Cost', alpha=0.7, color='#FF6B6B')
    
    ax1.set_title('Monthly Cost Trends - Utilized vs Idle', fontweight='bold')
    ax1.set_ylabel('Cost (INR)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Utilization trend
    ax2.plot(monthly_data['month_str'], monthly_data['cpu_utilizationpercent'], 
             marker='o', linewidth=2, markersize=8, color='#4472C4')
    ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Target (70%)')
    ax2.set_title('Monthly Utilization Trend', fontweight='bold')
    ax2.set_ylabel('CPU Utilization (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/06_time_series_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_optimization_priority_matrix(df, viz_dir):
    """Create optimization priority analysis"""
    print("🎯 Creating optimization priority matrix...")
    
    # Calculate priority scores
    service_analysis = df.groupby('service').agg({
        'cost_inr': 'sum',
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': 'mean'
    }).reset_index()
    
    service_analysis['optimization_potential'] = service_analysis['idle_cost_inr']
    service_analysis['implementation_ease'] = 100 - service_analysis['cpu_utilizationpercent']  # Lower utilization = easier to optimize
    
    # Create priority matrix
    fig, ax = plt.subplots(figsize=(12, 8))
    
    scatter = ax.scatter(service_analysis['implementation_ease'], 
                        service_analysis['optimization_potential'],
                        s=service_analysis['cost_inr']/5,  # Size based on total cost
                        alpha=0.7,
                        c=['#FF6B6B', '#FFD93D', '#6BCF7F', '#4ECDC4', '#45B7D1'],
                        edgecolors='black',
                        linewidth=1)
    
    # Add service labels
    for i, service in enumerate(service_analysis['service']):
        ax.annotate(service.upper(), 
                   (service_analysis.iloc[i]['implementation_ease'], 
                    service_analysis.iloc[i]['optimization_potential']),
                   xytext=(5, 5), textcoords='offset points', 
                   fontweight='bold', fontsize=10)
    
    # Add quadrant lines
    ax.axvline(x=30, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=service_analysis['optimization_potential'].median(), color='gray', linestyle='--', alpha=0.5)
    
    # Add quadrant labels
    ax.text(15, service_analysis['optimization_potential'].max() * 0.9, 'High Impact\nHigh Effort', 
            ha='center', va='center', fontweight='bold', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFE6E6'))
    ax.text(45, service_analysis['optimization_potential'].max() * 0.9, 'High Impact\nLow Effort', 
            ha='center', va='center', fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#E6F3E6'))
    ax.text(15, service_analysis['optimization_potential'].min() * 1.1, 'Low Impact\nHigh Effort', 
            ha='center', va='center', fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#F0F0F0'))
    ax.text(45, service_analysis['optimization_potential'].min() * 1.1, 'Low Impact\nLow Effort', 
            ha='center', va='center', fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#FFF2E6'))
    
    ax.set_xlabel('Implementation Ease Score', fontweight='bold')
    ax.set_ylabel('Optimization Potential (INR)', fontweight='bold')
    ax.set_title('Optimization Priority Matrix\n(Bubble size = Total Cost)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/07_optimization_priority_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_roi_analysis_charts(df, viz_dir):
    """Create ROI and business impact analysis"""
    print("💰 Creating ROI analysis charts...")
    
    # Calculate ROI scenarios
    total_cost = df['cost_inr'].sum()
    total_idle = df['idle_cost_inr'].sum()
    
    scenarios = {
        'Conservative (40% reduction)': total_idle * 0.4,
        'Moderate (60% reduction)': total_idle * 0.6,
        'Aggressive (80% reduction)': total_idle * 0.8
    }
    
    # 1. ROI Scenario Analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Monthly savings scenarios
    scenario_names = list(scenarios.keys())
    monthly_savings = [scenarios[s] for s in scenario_names]
    annual_savings = [s * 12 for s in monthly_savings]
    
    x = np.arange(len(scenario_names))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, monthly_savings, width, label='Monthly Savings', color='#66B2FF')
    bars2 = ax1.bar(x + width/2, annual_savings, width, label='Annual Savings', color='#99FF99')
    
    ax1.set_title('ROI Scenarios Analysis', fontweight='bold')
    ax1.set_ylabel('Savings (INR)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenario_names, rotation=45, ha='right')
    ax1.legend()
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(annual_savings)*0.01,
                    f'₹{height:,.0f}', ha='center', va='bottom', fontsize=9)
    
    # 3-Year Value Projection
    years = ['Year 1', 'Year 2', 'Year 3']
    cumulative_savings = []
    
    for i, year in enumerate(years):
        cumulative = sum(annual_savings[1] for _ in range(i + 1))  # Using moderate scenario
        cumulative_savings.append(cumulative)
    
    ax2.plot(years, cumulative_savings, marker='o', linewidth=3, markersize=10, color='#FF6B6B')
    ax2.fill_between(years, 0, cumulative_savings, alpha=0.3, color='#FF6B6B')
    ax2.set_title('3-Year Cumulative Savings (Moderate Scenario)', fontweight='bold')
    ax2.set_ylabel('Cumulative Savings (INR)')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for i, value in enumerate(cumulative_savings):
        ax2.text(i, value + max(cumulative_savings)*0.02,
                f'₹{value:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/08_roi_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_implementation_roadmap(df, viz_dir):
    """Create implementation roadmap visualization"""
    print("🗺️ Creating implementation roadmap...")
    
    # Implementation phases data
    phases = {
        'Phase 1\n(30 Days)': {
            'actions': ['Database Optimization', 'Automated Scaling', 'Basic Monitoring'],
            'savings': df[df['service'] == 'rds']['idle_cost_inr'].sum() * 0.6,
            'effort': 'Low',
            'color': '#99FF99'
        },
        'Phase 2\n(90 Days)': {
            'actions': ['Compute Rightsizing', 'Storage Optimization', 'Advanced Monitoring'],
            'savings': df[df['service'] == 'ec2']['idle_cost_inr'].sum() * 0.5,
            'effort': 'Medium',
            'color': '#FFD93D'
        },
        'Phase 3\n(180 Days)': {
            'actions': ['Predictive Scaling', 'Multi-Region Optimization', 'AI-driven Management'],
            'savings': df['idle_cost_inr'].sum() * 0.2,
            'effort': 'High',
            'color': '#FF6B6B'
        }
    }
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Phase timeline with savings
    phase_names = list(phases.keys())
    phase_savings = [phases[p]['savings'] for p in phase_names]
    phase_colors = [phases[p]['color'] for p in phase_names]
    
    bars = ax1.bar(phase_names, phase_savings, color=phase_colors, alpha=0.8, edgecolor='black')
    ax1.set_title('Implementation Roadmap - Savings by Phase', fontweight='bold')
    ax1.set_ylabel('Expected Savings (INR)')
    
    # Add value labels and action details
    for i, (bar, phase) in enumerate(zip(bars, phase_names)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(phase_savings)*0.02,
                f'₹{height:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Add action items below x-axis
        actions_text = '\n'.join(phases[phase]['actions'])
        ax1.text(bar.get_x() + bar.get_width()/2., -max(phase_savings)*0.05,
                actions_text, ha='center', va='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=phase_colors[i], alpha=0.3))
    
    # Cumulative impact over time
    cumulative_impact = np.cumsum(phase_savings)
    months = [1, 3, 6]  # Timeline in months
    
    ax2.plot(months, cumulative_impact, marker='o', linewidth=3, markersize=10, color='#4472C4')
    ax2.fill_between(months, 0, cumulative_impact, alpha=0.3, color='#4472C4')
    ax2.set_title('Cumulative Optimization Impact Timeline', fontweight='bold')
    ax2.set_xlabel('Timeline (Months)')
    ax2.set_ylabel('Cumulative Savings (INR)')
    ax2.grid(True, alpha=0.3)
    
    # Add milestone markers
    for i, (month, impact) in enumerate(zip(months, cumulative_impact)):
        ax2.text(month, impact + max(cumulative_impact)*0.03,
                f'₹{impact:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/09_implementation_roadmap.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_detailed_tables(df, viz_dir):
    """Create detailed analytical tables"""
    print("📋 Creating detailed analytical tables...")
    
    # 1. Service Performance Summary Table
    service_summary = df.groupby('service').agg({
        'cost_inr': ['sum', 'mean'],
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': ['mean', 'std'],
        'usage_hours': 'sum'
    }).round(2)
    
    service_summary.columns = ['Total_Cost_INR', 'Avg_Cost_INR', 'Idle_Cost_INR', 
                              'Avg_Utilization_%', 'Utilization_StdDev', 'Total_Hours']
    service_summary['Optimization_%'] = ((service_summary['Idle_Cost_INR'] / 
                                        service_summary['Total_Cost_INR']) * 100).round(1)
    service_summary['Priority_Score'] = (service_summary['Optimization_%'] * 0.6 + 
                                       (100 - service_summary['Avg_Utilization_%']) * 0.4).round(1)
    
    # 2. Regional Analysis Table
    regional_summary = df.groupby('region').agg({
        'cost_inr': 'sum',
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': 'mean',
        'service': 'nunique'
    }).round(2)
    
    regional_summary.columns = ['Total_Cost_INR', 'Idle_Cost_INR', 'Avg_Utilization_%', 'Services_Count']
    regional_summary['Cost_Efficiency_%'] = ((regional_summary['Total_Cost_INR'] - 
                                            regional_summary['Idle_Cost_INR']) / 
                                           regional_summary['Total_Cost_INR'] * 100).round(1)
    
    # 3. Monthly Trends Table
    monthly_summary = df.groupby(df['date'].dt.to_period('M')).agg({
        'cost_inr': 'sum',
        'idle_cost_inr': 'sum',
        'cpu_utilizationpercent': 'mean'
    }).round(2)
    
    monthly_summary.columns = ['Total_Cost_INR', 'Idle_Cost_INR', 'Avg_Utilization_%']
    monthly_summary['Efficiency_Trend'] = monthly_summary['Avg_Utilization_%'].pct_change().round(3)
    
    # Save tables as CSV for easy import
    service_summary.to_csv(f'{viz_dir}/service_performance_table.csv')
    regional_summary.to_csv(f'{viz_dir}/regional_analysis_table.csv')
    monthly_summary.to_csv(f'{viz_dir}/monthly_trends_table.csv')
    
    # Create visual table representations
    create_table_visualizations(service_summary, regional_summary, monthly_summary, viz_dir)

def create_table_visualizations(service_summary, regional_summary, monthly_summary, viz_dir):
    """Create visual representations of tables"""
    
    # Service Performance Table Visualization
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare data for display
    display_data = service_summary.reset_index()
    display_data['Total_Cost_INR'] = display_data['Total_Cost_INR'].apply(lambda x: f'₹{x:,.0f}')
    display_data['Idle_Cost_INR'] = display_data['Idle_Cost_INR'].apply(lambda x: f'₹{x:,.0f}')
    
    table = ax.table(cellText=display_data.values,
                    colLabels=['Service', 'Total Cost', 'Avg Cost', 'Idle Cost', 
                              'Avg Util%', 'Util StdDev', 'Total Hours', 'Optimization%', 'Priority Score'],
                    cellLoc='center',
                    loc='center',
                    bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 2)
    
    # Color code cells based on performance
    for i in range(1, len(display_data) + 1):
        # Color code optimization percentage
        opt_pct = service_summary.iloc[i-1]['Optimization_%']
        if opt_pct > 40:
            table[(i, 7)].set_facecolor('#FFE6E6')  # High optimization needed
        elif opt_pct > 25:
            table[(i, 7)].set_facecolor('#FFF2E6')  # Medium optimization needed
        else:
            table[(i, 7)].set_facecolor('#E6F3E6')  # Low optimization needed
    
    # Header styling
    for j in range(9):
        table[(0, j)].set_facecolor('#4472C4')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    plt.title('Service Performance Analysis - Detailed Table', fontsize=14, fontweight='bold', pad=20)
    plt.savefig(f'{viz_dir}/10_service_performance_table.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_powerpoint_guide(viz_dir):
    """Generate PowerPoint slide recommendations"""
    
    slide_guide = """
# PowerPoint Presentation - Slide-by-Slide Visualization Guide

## SLIDE 1: Title Slide
- Title: "AWS Cost Optimization: Data-Driven Business Analytics"
- Subtitle: "Strategic Implementation Framework for Cloud Financial Management"
- Author: Mohammed Abdul Basith
- Date: October 12, 2025

## SLIDE 2: Executive Summary
**Visualization:** 01_executive_summary_dashboard.png
**Key Points:**
- Total AWS Investment: ₹48,126.39
- Optimization Opportunity: 32.9% (₹15,816.19)
- Annual Savings Potential: ₹1,14,001.79
- Services Analyzed: 5 across 3 regions

## SLIDE 3: Key Performance Indicators
**Visualization:** 02_kpi_summary_table.png
**Key Points:**
- Comprehensive KPI dashboard
- Current vs Target performance metrics
- Strategic benchmarks and goals

## SLIDE 4: Service Performance Analysis
**Visualization:** 03_service_performance_matrix.png + 04_service_cost_utilization.png
**Key Points:**
- Service-wise utilization patterns
- Cost distribution and optimization opportunities
- Performance matrix quadrant analysis

## SLIDE 5: Regional Cost Distribution
**Visualization:** 05_regional_analysis_dashboard.png
**Key Points:**
- Multi-region cost comparison
- Regional optimization opportunities
- Geographic resource efficiency

## SLIDE 6: Time Series Trends
**Visualization:** 06_time_series_analysis.png
**Key Points:**
- Monthly cost evolution
- Utilization improvement trends
- Seasonal patterns and insights

## SLIDE 7: Optimization Priority Matrix
**Visualization:** 07_optimization_priority_matrix.png
**Key Points:**
- High Impact / Low Effort opportunities
- Implementation priority ranking
- Resource allocation guidance

## SLIDE 8: ROI and Business Impact
**Visualization:** 08_roi_analysis.png
**Key Points:**
- Multiple scenario analysis
- 3-year value projection
- Conservative to aggressive savings estimates

## SLIDE 9: Implementation Roadmap
**Visualization:** 09_implementation_roadmap.png
**Key Points:**
- 3-phase implementation strategy
- Timeline: 30-180 days
- Cumulative impact progression

## SLIDE 10: Detailed Analytics
**Visualization:** 10_service_performance_table.png
**Key Points:**
- Comprehensive service metrics
- Priority scoring methodology
- Data-driven decision support

## SLIDE 11: Strategic Recommendations
**Text Slide with Key Bullet Points:**
- Immediate: Database optimization (30 days)
- Strategic: Compute rightsizing (90 days)
- Advanced: AI-driven management (180 days)

## SLIDE 12: Conclusion and Next Steps
**Text Slide with Action Items:**
- Implementation timeline
- Resource requirements
- Success metrics and KPIs
"""
    
    with open(f'{viz_dir}/PowerPoint_Slide_Guide.md', 'w', encoding='utf-8') as f:
        f.write(slide_guide)

def generate_report_placement_guide(viz_dir):
    """Generate guide for placing visualizations in the Word report"""
    
    report_guide = """
# MBA Report - Visualization Placement Guide

## CHAPTER 1: INTRODUCTION
**Section 1.2: Problem Statement**
- Insert: 01_executive_summary_dashboard.png
- Purpose: Illustrate the cost optimization challenge and opportunity

## CHAPTER 4: DATA ANALYSIS AND FINDINGS

### Section 4.1: Descriptive Analysis
**Table 4.1: Descriptive Statistics Summary**
- Insert: 02_kpi_summary_table.png
- Purpose: Comprehensive KPI overview

### Section 4.2: Cost Distribution Analysis
**Figure 4.1: Cost Distribution by Service Category**
- Insert: 04_service_cost_utilization.png
- Purpose: Service-wise cost breakdown

**Table 4.2: Service-wise Cost Analysis (INR)**
- Insert: 10_service_performance_table.png
- Purpose: Detailed service metrics

### Section 4.3: Utilization Pattern Analysis
**Figure 4.2: Service Performance Matrix**
- Insert: 03_service_performance_matrix.png
- Purpose: Utilization vs optimization opportunity correlation

**Table 4.3: Utilization Performance Metrics**
- Use data from: service_performance_table.csv

### Section 4.4: Regional Cost Comparison
**Figure 4.3: Regional Cost Distribution**
- Insert: 05_regional_analysis_dashboard.png
- Purpose: Multi-region analysis

**Table 4.4: Regional Analysis Summary**
- Use data from: regional_analysis_table.csv

### Section 4.5: Predictive Analysis
**Figure 4.4: Time Series Cost Analysis**
- Insert: 06_time_series_analysis.png
- Purpose: Temporal trends and patterns

## CHAPTER 5: STRATEGIC RECOMMENDATIONS

### Section 5.1: Optimization Priority Matrix
**Figure 5.1: Priority Analysis Framework**
- Insert: 07_optimization_priority_matrix.png
- Purpose: Strategic prioritization guidance

### Section 5.2: Implementation Roadmap
**Figure 5.2: Strategic Implementation Timeline**
- Insert: 09_implementation_roadmap.png
- Purpose: Phased implementation strategy

## CHAPTER 6: BUSINESS IMPACT AND ROI ANALYSIS

### Section 6.1: Financial Impact Assessment
**Figure 6.1: ROI Projection Analysis**
- Insert: 08_roi_analysis.png
- Purpose: Multi-scenario financial impact

**Table 6.1: ROI Analysis Summary (INR)**
- Create table from ROI calculations in the visualization

### Section 6.2: Value Creation Timeline
**Table 6.2: Implementation Value Progression**
- Use implementation roadmap data

## APPENDICES

### Appendix B: Statistical Analysis Results
- Insert: All CSV tables
- service_performance_table.csv
- regional_analysis_table.csv
- monthly_trends_table.csv

### Appendix C: Visualization Portfolio
- Include all PNG files as supporting documentation
- Reference each visualization with detailed captions

## FORMATTING GUIDELINES

1. **Figure Captions:**
   - "Figure X.X: [Title] - [Brief Description]"
   - Include source: "Source: AWS Infrastructure Analysis, 2024-2025"

2. **Table Captions:**
   - "Table X.X: [Title] - [Purpose]"
   - Include units: "All costs in Indian Rupees (INR)"

3. **Image Quality:**
   - Use 300 DPI PNG files
   - Maintain aspect ratios
   - Ensure readability at print size

4. **Professional Presentation:**
   - Consistent color schemes
   - Clear axis labels and legends
   - Professional font choices
   - High contrast for readability
"""
    
    with open(f'{viz_dir}/Report_Placement_Guide.md', 'w', encoding='utf-8') as f:
        f.write(report_guide)

def main():
    """Main execution function for comprehensive visualization generation"""
    print("🎨 Starting Comprehensive Visualization Generation for MBA Project...")
    print("="*70)
    
    # Create visualizations directory
    viz_dir = create_visualizations_directory()
    
    # Load and prepare data
    df = load_and_prepare_data()
    
    print(f"📊 Data Overview:")
    print(f"   • Total Records: {len(df)}")
    print(f"   • Services: {df['service'].nunique()} ({', '.join(df['service'].unique())})")
    print(f"   • Regions: {df['region'].nunique()} ({', '.join(df['region'].unique())})")
    print(f"   • Total Cost: ₹{df['cost_inr'].sum():,.2f}")
    print(f"   • Optimization Opportunity: ₹{df['idle_cost_inr'].sum():,.2f}")
    print("="*70)
    
    # Generate all visualizations
    create_executive_summary_charts(df, viz_dir)
    create_service_analysis_charts(df, viz_dir)
    create_regional_analysis_charts(df, viz_dir)
    create_time_series_analysis(df, viz_dir)
    create_optimization_priority_matrix(df, viz_dir)
    create_roi_analysis_charts(df, viz_dir)
    create_implementation_roadmap(df, viz_dir)
    create_detailed_tables(df, viz_dir)
    
    # Generate guides
    generate_powerpoint_guide(viz_dir)
    generate_report_placement_guide(viz_dir)
    
    print("\n🎉 Comprehensive Visualization Generation Complete!")
    print("="*70)
    print("📊 Generated Visualizations:")
    print("   1. 01_executive_summary_dashboard.png - Executive overview")
    print("   2. 02_kpi_summary_table.png - Key performance indicators")
    print("   3. 03_service_performance_matrix.png - Service analysis matrix")
    print("   4. 04_service_cost_utilization.png - Cost and utilization breakdown")
    print("   5. 05_regional_analysis_dashboard.png - Regional comparison")
    print("   6. 06_time_series_analysis.png - Temporal trends")
    print("   7. 07_optimization_priority_matrix.png - Priority framework")
    print("   8. 08_roi_analysis.png - ROI and business impact")
    print("   9. 09_implementation_roadmap.png - Strategic timeline")
    print("   10. 10_service_performance_table.png - Detailed analytics")
    
    print("\n📋 Supporting Data Tables:")
    print("   • service_performance_table.csv")
    print("   • regional_analysis_table.csv") 
    print("   • monthly_trends_table.csv")
    
    print("\n📖 Implementation Guides:")
    print("   • PowerPoint_Slide_Guide.md - PPT slide-by-slide guide")
    print("   • Report_Placement_Guide.md - Word report placement guide")
    
    print(f"\n📁 All files saved in: {viz_dir}/")
    print("\n✨ Ready for MBA report and presentation integration!")

if __name__ == "__main__":
    main()