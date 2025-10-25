# Comprehensive FinOps Dashboard with All Metrics
# Integrates forecast accuracy, waste tracking, RI/SP metrics, tag compliance
# For MBA Project - Predictive AWS Cost Optimization

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def create_comprehensive_finops_dashboard(data_file='aws_cost_data_enhanced_with_finops.csv'):
    """
    Create comprehensive FinOps dashboard with all metrics
    """
    print("\n" + "="*80)
    print("📊 CREATING COMPREHENSIVE FINOPS DASHBOARD")
    print("="*80 + "\n")
    
    # Load data
    df = pd.read_csv(data_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    gs = fig.add_gridspec(4, 3, hspace=0.4, wspace=0.3)
    
    # Title
    fig.suptitle('Comprehensive FinOps Dashboard - AWS Cost Optimization with Prophet Forecasting',
                 fontsize=18, fontweight='bold', y=0.995)
    
    # ==================== PLOT 1: Cost Overview & Waste ====================
    ax1 = fig.add_subplot(gs[0, 0])
    total_cost = df['cost_inr'].sum()
    total_idle = df['idle_cost_inr'].sum()
    active_cost = total_cost - total_idle
    
    sizes = [active_cost, total_idle]
    labels = [f'Active Cost\n₹{active_cost:,.0f}', f'Idle/Waste\n₹{total_idle:,.0f}']
    colors = ['#2ecc71', '#e74c3c']
    explode = (0, 0.1)
    
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            explode=explode, startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
    ax1.set_title(f'Cost Distribution & Waste\nTotal: ₹{total_cost:,.0f}', 
                  fontsize=12, fontweight='bold')
    
    # ==================== PLOT 2: Monthly Cost Trend ====================
    ax2 = fig.add_subplot(gs[0, 1:])
    monthly = df.groupby(df['date'].dt.to_period('M').astype(str)).agg({
        'cost_inr': 'sum',
        'idle_cost_inr': 'sum'
    })
    
    x = range(len(monthly))
    ax2.bar(x, monthly['cost_inr'], label='Total Cost', alpha=0.7, color='steelblue')
    ax2.bar(x, monthly['idle_cost_inr'], label='Idle Cost', alpha=0.9, color='coral')
    ax2.set_xticks(x)
    ax2.set_xticklabels(monthly.index, rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Cost (INR)', fontsize=10, fontweight='bold')
    ax2.set_title('Monthly Cost Trend - Total vs Idle', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right')
    ax2.grid(axis='y', alpha=0.3)
    
    # ==================== PLOT 3: Service Cost Breakdown ====================
    ax3 = fig.add_subplot(gs[1, 0])
    service_cost = df.groupby('service')['cost_inr'].sum().sort_values(ascending=False)
    colors_service = sns.color_palette("Set2", len(service_cost))
    ax3.barh(range(len(service_cost)), service_cost.values, color=colors_service)
    ax3.set_yticks(range(len(service_cost)))
    ax3.set_yticklabels(service_cost.index, fontsize=10)
    ax3.set_xlabel('Total Cost (INR)', fontsize=10, fontweight='bold')
    ax3.set_title('Cost by Service', fontsize=12, fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(service_cost.values):
        ax3.text(v + 5000, i, f'₹{v:,.0f}', va='center', fontsize=9)
    
    # ==================== PLOT 4: Regional Distribution ====================
    ax4 = fig.add_subplot(gs[1, 1])
    region_cost = df.groupby('region')['cost_inr'].sum()
    colors_region = sns.color_palette("Set3", len(region_cost))
    wedges, texts, autotexts = ax4.pie(region_cost.values, labels=region_cost.index,
                                        autopct='%1.1f%%', colors=colors_region,
                                        startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    ax4.set_title('Cost by Region', fontsize=12, fontweight='bold')
    
    # ==================== PLOT 5: Utilization Heatmap ====================
    ax5 = fig.add_subplot(gs[1, 2])
    compute_services = df[df['cpu_utilization'] > 0]
    if len(compute_services) > 0:
        util_pivot = compute_services.pivot_table(
            index='service',
            columns=compute_services['date'].dt.to_period('M').astype(str),
            values='cpu_utilization',
            aggfunc='mean'
        )
        sns.heatmap(util_pivot, annot=True, fmt='.1f', cmap='RdYlGn',
                   ax=ax5, cbar_kws={'label': 'Avg CPU %'}, vmin=0, vmax=100)
        ax5.set_title('CPU Utilization by Service & Month', fontsize=12, fontweight='bold')
        ax5.set_xlabel('')
        ax5.set_ylabel('Service', fontsize=10, fontweight='bold')
    
    # ==================== PLOT 6: Tag Compliance Trend ====================
    ax6 = fig.add_subplot(gs[2, 0])
    tag_monthly = df.groupby(df['date'].dt.to_period('M').astype(str)).agg({
        'has_required_tags': lambda x: (x.sum() / len(x)) * 100
    })
    ax6.plot(range(len(tag_monthly)), tag_monthly['has_required_tags'], 
            marker='o', linewidth=2, markersize=8, color='purple')
    ax6.axhline(y=90, color='green', linestyle='--', label='Target: 90%', linewidth=2)
    ax6.set_xticks(range(len(tag_monthly)))
    ax6.set_xticklabels(tag_monthly.index, rotation=45, ha='right', fontsize=8)
    ax6.set_ylabel('Compliance %', fontsize=10, fontweight='bold')
    ax6.set_title('Tag Compliance Trend', fontsize=12, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    ax6.set_ylim(0, 100)
    
    # ==================== PLOT 7: RI/SP Coverage & Utilization ====================
    ax7 = fig.add_subplot(gs[2, 1])
    ri_eligible = df[df['is_covered_by_ri_sp'].notna()]
    if len(ri_eligible) > 0:
        coverage = (ri_eligible['is_covered_by_ri_sp'].sum() / len(ri_eligible)) * 100
        covered = ri_eligible[ri_eligible['is_covered_by_ri_sp']]
        utilization = covered['ri_sp_utilization'].mean() if len(covered) > 0 else 0
        
        metrics_ri = ['Coverage', 'Utilization']
        values_ri = [coverage, utilization]
        colors_ri = ['#3498db', '#2ecc71']
        
        bars = ax7.bar(metrics_ri, values_ri, color=colors_ri, alpha=0.8, edgecolor='black', linewidth=2)
        ax7.axhline(y=60, color='orange', linestyle='--', label='Coverage Target: 60-80%', linewidth=1.5)
        ax7.axhline(y=90, color='green', linestyle='--', label='Utilization Target: >90%', linewidth=1.5)
        ax7.set_ylabel('Percentage (%)', fontsize=10, fontweight='bold')
        ax7.set_title('RI/Savings Plans Metrics', fontsize=12, fontweight='bold')
        ax7.legend(fontsize=8)
        ax7.set_ylim(0, 100)
        ax7.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # ==================== PLOT 8: Rightsizing Opportunities ====================
    ax8 = fig.add_subplot(gs[2, 2])
    rightsizing = df['rightsizing_opportunity'].value_counts()
    colors_right = {'Optimal': '#2ecc71', 'Downsize': '#e74c3c', 'Upsize': '#f39c12'}
    colors_list = [colors_right.get(x, '#95a5a6') for x in rightsizing.index]
    
    ax8.barh(range(len(rightsizing)), rightsizing.values, color=colors_list, edgecolor='black', linewidth=1.5)
    ax8.set_yticks(range(len(rightsizing)))
    ax8.set_yticklabels(rightsizing.index, fontsize=10, fontweight='bold')
    ax8.set_xlabel('Count', fontsize=10, fontweight='bold')
    ax8.set_title('Rightsizing Analysis', fontsize=12, fontweight='bold')
    ax8.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(rightsizing.values):
        ax8.text(v + 1, i, str(v), va='center', fontsize=10, fontweight='bold')
    
    # ==================== PLOT 9: Budget Variance Distribution ====================
    ax9 = fig.add_subplot(gs[3, 0])
    ax9.hist(df['budget_variance_pct'], bins=30, color='teal', alpha=0.7, edgecolor='black')
    ax9.axvline(x=0, color='red', linestyle='--', linewidth=2, label='On Budget')
    ax9.axvline(x=df['budget_variance_pct'].mean(), color='orange', linestyle='--', 
               linewidth=2, label=f'Avg: {df["budget_variance_pct"].mean():.1f}%')
    ax9.set_xlabel('Budget Variance (%)', fontsize=10, fontweight='bold')
    ax9.set_ylabel('Frequency', fontsize=10, fontweight='bold')
    ax9.set_title('Budget Variance Distribution', fontsize=12, fontweight='bold')
    ax9.legend()
    ax9.grid(axis='y', alpha=0.3)
    
    # ==================== PLOT 10: Unit Cost by Service ====================
    ax10 = fig.add_subplot(gs[3, 1])
    services_with_requests = df[df['requests_per_day'] > 0]
    if len(services_with_requests) > 0:
        unit_cost_by_service = services_with_requests.groupby('service')['unit_cost_per_1k_requests_inr'].mean().sort_values()
        colors_unit = sns.color_palette("coolwarm", len(unit_cost_by_service))
        
        ax10.barh(range(len(unit_cost_by_service)), unit_cost_by_service.values, color=colors_unit)
        ax10.set_yticks(range(len(unit_cost_by_service)))
        ax10.set_yticklabels(unit_cost_by_service.index, fontsize=10)
        ax10.set_xlabel('Unit Cost (INR per 1K requests)', fontsize=10, fontweight='bold')
        ax10.set_title('Unit Cost Efficiency by Service', fontsize=12, fontweight='bold')
        ax10.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(unit_cost_by_service.values):
            ax10.text(v + 0.5, i, f'₹{v:.2f}', va='center', fontsize=9)
    
    # ==================== PLOT 11: Key Metrics Summary ====================
    ax11 = fig.add_subplot(gs[3, 2])
    ax11.axis('off')
    
    # Calculate key metrics
    waste_rate = (total_idle / total_cost) * 100
    avg_utilization = df[df['cpu_utilization'] > 0]['cpu_utilization'].mean()
    tag_compliance = (df['has_required_tags'].sum() / len(df)) * 100
    anomaly_count = df['is_cost_anomaly'].sum()
    total_savings_potential = df['potential_rightsizing_savings_inr'].sum()
    
    metrics_text = "KEY PERFORMANCE INDICATORS\n" + "="*45 + "\n\n"
    metrics_text += f"💰 Total AWS Spend: ₹{total_cost:,.0f}\n"
    metrics_text += f"⚠️  Waste Rate: {waste_rate:.1f}%\n"
    metrics_text += f"💡 Potential Savings: ₹{total_savings_potential:,.0f}/mo\n\n"
    
    metrics_text += f"⚙️  Avg CPU Utilization: {avg_utilization:.1f}%\n"
    metrics_text += f"🏷️  Tag Compliance: {tag_compliance:.1f}%\n"
    metrics_text += f"🚨 Cost Anomalies: {anomaly_count}\n\n"
    
    # Status indicators
    metrics_text += "STATUS INDICATORS:\n"
    metrics_text += f"  Waste: {'✓ Good' if waste_rate < 20 else '✗ Needs Attention'}\n"
    metrics_text += f"  Utilization: {'✓ Good' if avg_utilization >= 70 else '✗ Low'}\n"
    metrics_text += f"  Tags: {'✓ Good' if tag_compliance >= 90 else '✗ Needs Work'}\n"
    
    ax11.text(0.05, 0.95, metrics_text, transform=ax11.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8, pad=1))
    
    # Save dashboard
    plt.savefig('comprehensive_finops_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ Dashboard saved to 'comprehensive_finops_dashboard.png'")
    plt.show()
    
    print("\n" + "="*80)
    print("✅ COMPREHENSIVE FINOPS DASHBOARD COMPLETE")
    print("="*80 + "\n")


if __name__ == '__main__':
    create_comprehensive_finops_dashboard()
