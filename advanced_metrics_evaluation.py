# Advanced Metrics Evaluation System
# Comprehensive forecast accuracy and FinOps KPI tracking
# For MBA Project - Predictive AWS Cost Optimization

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AdvancedMetricsEvaluator:
    """
    Comprehensive metrics evaluator for AWS cost forecasting and FinOps KPIs
    """
    
    def __init__(self, actual, predicted, forecast_lower=None, forecast_upper=None):
        """
        Initialize with actual and predicted values
        
        Parameters:
        -----------
        actual : array-like
            Actual cost values
        predicted : array-like
            Predicted cost values
        forecast_lower : array-like, optional
            Lower bound of prediction interval (95%)
        forecast_upper : array-like, optional
            Upper bound of prediction interval (95%)
        """
        self.actual = np.array(actual)
        self.predicted = np.array(predicted)
        self.forecast_lower = np.array(forecast_lower) if forecast_lower is not None else None
        self.forecast_upper = np.array(forecast_upper) if forecast_upper is not None else None
        
    # ==================== FORECAST ACCURACY METRICS ====================
    
    def calculate_mape(self):
        """Mean Absolute Percentage Error - Primary metric"""
        # Avoid division by zero
        mask = self.actual != 0
        mape = np.mean(np.abs((self.actual[mask] - self.predicted[mask]) / self.actual[mask])) * 100
        return round(mape, 2)
    
    def calculate_smape(self):
        """Symmetric MAPE - Scale-robust alternative"""
        numerator = np.abs(self.actual - self.predicted)
        denominator = (np.abs(self.actual) + np.abs(self.predicted)) / 2
        mask = denominator != 0
        smape = np.mean(numerator[mask] / denominator[mask]) * 100
        return round(smape, 2)
    
    def calculate_wape(self):
        """Weighted Absolute Percentage Error"""
        wape = (np.sum(np.abs(self.actual - self.predicted)) / np.sum(np.abs(self.actual))) * 100
        return round(wape, 2)
    
    def calculate_mae(self):
        """Mean Absolute Error"""
        mae = mean_absolute_error(self.actual, self.predicted)
        return round(mae, 2)
    
    def calculate_rmse(self):
        """Root Mean Squared Error - Penalizes large errors"""
        rmse = np.sqrt(mean_squared_error(self.actual, self.predicted))
        return round(rmse, 2)
    
    def calculate_mdape(self):
        """Median Absolute Percentage Error - Outlier robust"""
        mask = self.actual != 0
        ape = np.abs((self.actual[mask] - self.predicted[mask]) / self.actual[mask]) * 100
        mdape = np.median(ape)
        return round(mdape, 2)
    
    def calculate_r2(self):
        """R-squared - Variance explained by model"""
        r2 = r2_score(self.actual, self.predicted)
        return round(r2, 3)
    
    def calculate_bias(self):
        """Mean Error - Systematic over/under forecasting"""
        bias = np.mean(self.predicted - self.actual)
        return round(bias, 2)
    
    def calculate_bias_percentage(self):
        """Bias as percentage of mean actual"""
        mean_actual = np.mean(self.actual)
        bias = np.mean(self.predicted - self.actual)
        bias_pct = (bias / mean_actual) * 100 if mean_actual != 0 else 0
        return round(bias_pct, 2)
    
    def calculate_picp(self):
        """Prediction Interval Coverage Probability - % actuals inside 95% band"""
        if self.forecast_lower is None or self.forecast_upper is None:
            return None
        
        inside_interval = np.sum((self.actual >= self.forecast_lower) & 
                                (self.actual <= self.forecast_upper))
        picp = (inside_interval / len(self.actual)) * 100
        return round(picp, 2)
    
    def calculate_mase(self, naive_forecast):
        """Mean Absolute Scaled Error - Compare against naive forecast"""
        mae_model = np.mean(np.abs(self.actual - self.predicted))
        mae_naive = np.mean(np.abs(naive_forecast))
        mase = mae_model / mae_naive if mae_naive != 0 else np.inf
        return round(mase, 3)
    
    def get_all_forecast_metrics(self):
        """Return all forecast accuracy metrics as dictionary"""
        metrics = {
            'MAPE (%)': self.calculate_mape(),
            'sMAPE (%)': self.calculate_smape(),
            'WAPE (%)': self.calculate_wape(),
            'MAE (INR)': self.calculate_mae(),
            'RMSE (INR)': self.calculate_rmse(),
            'MdAPE (%)': self.calculate_mdape(),
            'R² Score': self.calculate_r2(),
            'Bias (INR)': self.calculate_bias(),
            'Bias (%)': self.calculate_bias_percentage(),
            'PICP (%)': self.calculate_picp()
        }
        return metrics
    
    # ==================== FINOPS KPIs ====================
    
    @staticmethod
    def calculate_waste_rate(total_cost, idle_cost):
        """Percentage of spending on idle/underutilized resources"""
        waste_rate = (idle_cost / total_cost) * 100 if total_cost > 0 else 0
        return round(waste_rate, 2)
    
    @staticmethod
    def calculate_unit_cost(total_cost, total_units):
        """Cost per unit (request/transaction/GB/customer)"""
        unit_cost = total_cost / total_units if total_units > 0 else 0
        return round(unit_cost, 2)
    
    @staticmethod
    def calculate_budget_variance(actual_cost, budgeted_cost):
        """Variance between actual and budgeted costs"""
        variance = actual_cost - budgeted_cost
        variance_pct = (variance / budgeted_cost) * 100 if budgeted_cost > 0 else 0
        return {
            'variance_inr': round(variance, 2),
            'variance_pct': round(variance_pct, 2)
        }
    
    @staticmethod
    def calculate_ri_sp_coverage(total_hours, covered_hours):
        """Reserved Instance / Savings Plans coverage percentage"""
        coverage = (covered_hours / total_hours) * 100 if total_hours > 0 else 0
        return round(coverage, 2)
    
    @staticmethod
    def calculate_ri_sp_utilization(purchased_hours, used_hours):
        """Reserved Instance / Savings Plans utilization percentage"""
        utilization = (used_hours / purchased_hours) * 100 if purchased_hours > 0 else 0
        return round(utilization, 2)
    
    @staticmethod
    def calculate_tag_compliance(total_resources, tagged_resources):
        """Percentage of resources with required tags"""
        compliance = (tagged_resources / total_resources) * 100 if total_resources > 0 else 0
        return round(compliance, 2)
    
    @staticmethod
    def calculate_cagr(initial_cost, final_cost, num_years):
        """Compound Annual Growth Rate of spending"""
        if initial_cost <= 0 or num_years <= 0:
            return 0
        cagr = (((final_cost / initial_cost) ** (1 / num_years)) - 1) * 100
        return round(cagr, 2)
    
    @staticmethod
    def calculate_coefficient_of_variation(costs):
        """Measure of spending volatility (std dev / mean)"""
        mean_cost = np.mean(costs)
        std_cost = np.std(costs)
        cv = (std_cost / mean_cost) * 100 if mean_cost > 0 else 0
        return round(cv, 2)
    
    @staticmethod
    def calculate_seasonality_strength(seasonal_component):
        """Variance explained by seasonal component"""
        if len(seasonal_component) == 0:
            return 0
        var_seasonal = np.var(seasonal_component)
        var_total = np.var(seasonal_component) + 1  # Simplified
        strength = (var_seasonal / var_total) * 100
        return round(strength, 2)
    
    # ==================== VISUALIZATION ====================
    
    def plot_forecast_accuracy(self, dates=None, save_path='metrics_plots'):
        """Create comprehensive visualization of forecast accuracy"""
        import os
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Forecast Accuracy Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Actual vs Predicted
        ax1 = axes[0, 0]
        if dates is not None:
            ax1.plot(dates, self.actual, label='Actual', color='blue', linewidth=2)
            ax1.plot(dates, self.predicted, label='Predicted', color='red', linestyle='--', linewidth=2)
            if self.forecast_lower is not None and self.forecast_upper is not None:
                ax1.fill_between(dates, self.forecast_lower, self.forecast_upper, 
                                alpha=0.3, color='gray', label='95% Confidence Interval')
        else:
            ax1.plot(self.actual, label='Actual', color='blue', linewidth=2)
            ax1.plot(self.predicted, label='Predicted', color='red', linestyle='--', linewidth=2)
        
        ax1.set_title('Actual vs Predicted Costs', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Time Period')
        ax1.set_ylabel('Cost (INR)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Residuals
        ax2 = axes[0, 1]
        residuals = self.actual - self.predicted
        ax2.scatter(range(len(residuals)), residuals, alpha=0.6, color='purple')
        ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
        ax2.set_title('Residuals (Actual - Predicted)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Observation')
        ax2.set_ylabel('Residual (INR)')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Error Distribution
        ax3 = axes[1, 0]
        percentage_errors = ((self.actual - self.predicted) / self.actual) * 100
        ax3.hist(percentage_errors, bins=30, color='teal', alpha=0.7, edgecolor='black')
        ax3.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax3.set_title('Distribution of Percentage Errors', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Percentage Error (%)')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Metrics Summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        metrics = self.get_all_forecast_metrics()
        
        metrics_text = "Forecast Accuracy Metrics:\n" + "="*40 + "\n\n"
        for key, value in metrics.items():
            if value is not None:
                metrics_text += f"{key:.<30} {value}\n"
        
        ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(f'{save_path}/forecast_accuracy_analysis.png', dpi=300, bbox_inches='tight')
        print(f"✅ Forecast accuracy plot saved to '{save_path}/forecast_accuracy_analysis.png'")
        
        return fig
    
    def plot_metrics_comparison(self, save_path='metrics_plots'):
        """Create bar chart comparing different error metrics"""
        import os
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        metrics = self.get_all_forecast_metrics()
        
        # Separate percentage and absolute metrics
        pct_metrics = {k: v for k, v in metrics.items() if '(%)' in k and v is not None}
        abs_metrics = {k: v for k, v in metrics.items() if '(INR)' in k and v is not None}
        other_metrics = {k: v for k, v in metrics.items() 
                        if '(%)' not in k and '(INR)' not in k and v is not None}
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Forecast Metrics Comparison', fontsize=16, fontweight='bold')
        
        # Plot percentage metrics
        if pct_metrics:
            ax1 = axes[0]
            bars1 = ax1.bar(range(len(pct_metrics)), list(pct_metrics.values()), 
                           color='skyblue', edgecolor='black', linewidth=1.5)
            ax1.set_xticks(range(len(pct_metrics)))
            ax1.set_xticklabels(list(pct_metrics.keys()), rotation=45, ha='right')
            ax1.set_ylabel('Percentage (%)')
            ax1.set_title('Percentage-based Metrics', fontweight='bold')
            ax1.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for i, bar in enumerate(bars1):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}%', ha='center', va='bottom', fontsize=9)
        
        # Plot absolute metrics
        if abs_metrics:
            ax2 = axes[1]
            bars2 = ax2.bar(range(len(abs_metrics)), list(abs_metrics.values()), 
                           color='lightcoral', edgecolor='black', linewidth=1.5)
            ax2.set_xticks(range(len(abs_metrics)))
            ax2.set_xticklabels(list(abs_metrics.keys()), rotation=45, ha='right')
            ax2.set_ylabel('Cost (INR)')
            ax2.set_title('Absolute Error Metrics', fontweight='bold')
            ax2.grid(axis='y', alpha=0.3)
            
            for i, bar in enumerate(bars2):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'₹{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        # Plot other metrics
        if other_metrics:
            ax3 = axes[2]
            bars3 = ax3.bar(range(len(other_metrics)), list(other_metrics.values()), 
                           color='lightgreen', edgecolor='black', linewidth=1.5)
            ax3.set_xticks(range(len(other_metrics)))
            ax3.set_xticklabels(list(other_metrics.keys()), rotation=45, ha='right')
            ax3.set_ylabel('Score')
            ax3.set_title('Other Metrics', fontweight='bold')
            ax3.grid(axis='y', alpha=0.3)
            
            for i, bar in enumerate(bars3):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f'{save_path}/metrics_comparison.png', dpi=300, bbox_inches='tight')
        print(f"✅ Metrics comparison plot saved to '{save_path}/metrics_comparison.png'")
        
        return fig


def generate_comprehensive_metrics_report(df, forecast_df, output_path='metrics_reports'):
    """
    Generate comprehensive metrics report for the entire project
    
    Parameters:
    -----------
    df : DataFrame
        Original cost data with columns: date, cost_inr, idle_cost_inr, cpu_utilization, etc.
    forecast_df : DataFrame
        Forecast data with columns: ds, yhat, yhat_lower, yhat_upper
    output_path : str
        Directory to save reports
    """
    import os
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE METRICS EVALUATION REPORT")
    print("="*60 + "\n")
    
    # ==================== FORECAST ACCURACY METRICS ====================
    print("🎯 FORECAST ACCURACY METRICS")
    print("-" * 60)
    
    # For demonstration, we'll use a train-test split approach
    split_idx = int(len(df) * 0.8)
    train_df = df[:split_idx].copy()
    test_df = df[split_idx:].copy()
    
    # Simulate predictions on test set (in real scenario, use your Prophet model)
    # For now, use a simple method to demonstrate metrics
    test_actual = test_df['cost_inr'].values
    # Simple moving average as prediction for demonstration
    test_predicted = np.convolve(train_df['cost_inr'].values, 
                                 np.ones(7)/7, mode='valid')[-len(test_actual):]
    
    # Ensure same length
    min_len = min(len(test_actual), len(test_predicted))
    test_actual = test_actual[:min_len]
    test_predicted = test_predicted[:min_len]
    
    # Create evaluator
    evaluator = AdvancedMetricsEvaluator(test_actual, test_predicted)
    forecast_metrics = evaluator.get_all_forecast_metrics()
    
    for metric, value in forecast_metrics.items():
        if value is not None:
            status = "✅" if (
                (metric == 'MAPE (%)' and value <= 15) or
                (metric == 'R² Score' and value >= 0.85) or
                (metric == 'PICP (%)' and 93 <= value <= 97)
            ) else "⚠️"
            print(f"{status} {metric:.<35} {value}")
    
    # ==================== FINOPS KPIs ====================
    print("\n💰 FINOPS KEY PERFORMANCE INDICATORS")
    print("-" * 60)
    
    total_cost = df['cost_inr'].sum()
    total_idle = df['idle_cost_inr'].sum() if 'idle_cost_inr' in df.columns else 0
    
    # Waste Rate
    waste_rate = AdvancedMetricsEvaluator.calculate_waste_rate(total_cost, total_idle)
    status = "✅" if waste_rate < 15 else "⚠️"
    print(f"{status} Waste Rate:............................ {waste_rate}%")
    print(f"   Total Cost: ₹{total_cost:,.2f}")
    print(f"   Idle Cost: ₹{total_idle:,.2f}")
    
    # Unit Cost (assuming 10000 requests/transactions per day for demonstration)
    total_requests = len(df) * 10000  # Simulated
    unit_cost = AdvancedMetricsEvaluator.calculate_unit_cost(total_cost, total_requests)
    print(f"\n✅ Unit Cost (per 1000 requests):.......... ₹{unit_cost * 1000:.4f}")
    
    # Budget Variance (assuming budget is 5% higher than actual for demonstration)
    budgeted_cost = total_cost * 1.05
    variance = AdvancedMetricsEvaluator.calculate_budget_variance(total_cost, budgeted_cost)
    status = "✅" if abs(variance['variance_pct']) <= 5 else "⚠️"
    print(f"{status} Budget Variance:....................... {variance['variance_pct']}%")
    print(f"   Budgeted: ₹{budgeted_cost:,.2f}")
    print(f"   Variance: ₹{variance['variance_inr']:,.2f}")
    
    # RI/SP Coverage (simulated - 65% coverage)
    coverage = 65.0  # Simulated
    status = "✅" if 60 <= coverage <= 80 else "⚠️"
    print(f"{status} Savings Plans/RI Coverage:............. {coverage}%")
    
    # RI/SP Utilization (simulated - 92% utilization)
    utilization = 92.0  # Simulated
    status = "✅" if utilization >= 90 else "⚠️"
    print(f"{status} Savings Plans/RI Utilization:.......... {utilization}%")
    
    # Tag Compliance (simulated - 88% compliance)
    tag_compliance = 88.0  # Simulated
    status = "✅" if tag_compliance >= 90 else "⚠️"
    print(f"{status} Tag Compliance:........................ {tag_compliance}%")
    
    # CAGR
    initial_cost = df.head(30)['cost_inr'].mean()
    final_cost = df.tail(30)['cost_inr'].mean()
    num_years = (df['date'].max() - df['date'].min()).days / 365.25
    cagr = AdvancedMetricsEvaluator.calculate_cagr(initial_cost, final_cost, num_years)
    trend = "⬇️ Decreasing" if cagr < 0 else "⬆️ Increasing"
    print(f"\n📈 Cost Growth (CAGR):..................... {cagr}% {trend}")
    
    # Coefficient of Variation (spending volatility)
    cv = AdvancedMetricsEvaluator.calculate_coefficient_of_variation(df['cost_inr'].values)
    status = "✅ Stable" if cv < 20 else "⚠️ Volatile"
    print(f"📊 Spending Volatility (CV):............... {cv}% {status}")
    
    # ==================== OPERATIONAL METRICS ====================
    print("\n⚙️ OPERATIONAL METRICS")
    print("-" * 60)
    
    # Average utilization by service
    if 'cpu_utilization' in df.columns and 'service' in df.columns:
        util_by_service = df[df['cpu_utilization'] > 0].groupby('service')['cpu_utilization'].mean()
        print("CPU Utilization by Service:")
        for service, util in util_by_service.items():
            status = "✅" if util >= 70 else "⚠️"
            print(f"  {status} {service:.<30} {util:.1f}%")
    
    # ==================== SAVE METRICS TO CSV ====================
    metrics_summary = pd.DataFrame({
        'Metric Category': ['Forecast Accuracy'] * len(forecast_metrics) + 
                          ['FinOps KPI'] * 7 + ['Operational'] * 2,
        'Metric Name': list(forecast_metrics.keys()) + 
                      ['Waste Rate (%)', 'Unit Cost (INR)', 'Budget Variance (%)',
                       'RI/SP Coverage (%)', 'RI/SP Utilization (%)', 
                       'Tag Compliance (%)', 'CAGR (%)'] +
                      ['Spending Volatility (CV %)', 'Avg CPU Utilization (%)'],
        'Value': list(forecast_metrics.values()) + 
                [waste_rate, unit_cost, variance['variance_pct'],
                 coverage, utilization, tag_compliance, cagr] +
                [cv, df['cpu_utilization'].mean() if 'cpu_utilization' in df.columns else 0],
        'Target': ['≤15%', '≤15%', '≤15%', '-', '-', '-', '≥0.85', '±5%', '±5%', '93-97%'] +
                 ['<15%', '-', '±5%', '60-80%', '≥90%', '≥90%', '-', '<20%', '≥70%'],
        'Status': ['Pass' if forecast_metrics.get('MAPE (%)', 100) <= 15 else 'Review'] * 10 +
                 ['Pass' if waste_rate < 15 else 'Review',
                  'N/A',
                  'Pass' if abs(variance['variance_pct']) <= 5 else 'Review',
                  'Pass', 'Pass', 'Review', 'Pass', 'Pass', 'Review']
    })
    
    metrics_summary.to_csv(f'{output_path}/comprehensive_metrics_summary.csv', index=False)
    print(f"\n✅ Metrics summary saved to '{output_path}/comprehensive_metrics_summary.csv'")
    
    # ==================== GENERATE VISUALIZATIONS ====================
    evaluator.plot_forecast_accuracy(dates=test_df['date'].values[:min_len], 
                                     save_path=output_path)
    evaluator.plot_metrics_comparison(save_path=output_path)
    
    print("\n" + "="*60)
    print("✅ COMPREHENSIVE METRICS EVALUATION COMPLETE")
    print("="*60 + "\n")
    
    return metrics_summary


if __name__ == '__main__':
    print("Advanced Metrics Evaluation System")
    print("=" * 60)
    print("This module provides comprehensive forecast accuracy and FinOps KPI tracking.")
    print("\nKey Features:")
    print("  • Forecast Accuracy: MAPE, sMAPE, WAPE, MAE, RMSE, MdAPE, R², Bias, PICP")
    print("  • FinOps KPIs: Waste Rate, Unit Cost, Budget Variance, RI/SP metrics")
    print("  • Operational: Tag Compliance, Utilization, CAGR, Volatility")
    print("  • Visualizations: Forecast accuracy plots, metrics comparison charts")
    print("\nUsage:")
    print("  from advanced_metrics_evaluation import generate_comprehensive_metrics_report")
    print("  report = generate_comprehensive_metrics_report(df, forecast_df)")
    print("=" * 60)
