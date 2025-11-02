"""Comparison logic for team vs team and vs benchmarks."""
import pandas as pd
from typing import List, Dict, Any, Optional
import numpy as np


class ComparisonEngine:
    """Handle various comparison operations."""
    
    @staticmethod
    def team_vs_team(df: pd.DataFrame, teams: List[str],
                    metrics: List[str]) -> pd.DataFrame:
        """Compare teams across metrics.
        
        Args:
            df: DataFrame with metric data
            teams: List of teams to compare (must be 2+)
            metrics: List of metrics to compare
            
        Returns:
            DataFrame with comparison results
        """
        if len(teams) < 2:
            raise ValueError("Need at least 2 teams for comparison")
        
        filtered_df = df[(df['team'].isin(teams)) & (df['metric'].isin(metrics))]
        
        comparison_results = []
        
        for metric in metrics:
            metric_data = filtered_df[filtered_df['metric'] == metric]
            
            for team in teams:
                team_values = metric_data[metric_data['team'] == team]['value']
                
                if len(team_values) == 0:
                    continue
                
                comparison_results.append({
                    'metric': metric,
                    'team': team,
                    'mean': team_values.mean(),
                    'median': team_values.median(),
                    'std': team_values.std(),
                    'min': team_values.min(),
                    'max': team_values.max(),
                    'count': len(team_values)
                })
        
        return pd.DataFrame(comparison_results)
    
    @staticmethod
    def calculate_differences(df: pd.DataFrame, baseline_team: str,
                             compare_teams: List[str], metrics: List[str]) -> pd.DataFrame:
        """Calculate differences between teams relative to baseline.
        
        Args:
            df: DataFrame with metric data
            baseline_team: Baseline team for comparison
            compare_teams: Teams to compare against baseline
            metrics: List of metrics
            
        Returns:
            DataFrame with difference calculations
        """
        filtered_df = df[(df['team'].isin([baseline_team] + compare_teams)) & 
                        (df['metric'].isin(metrics))]
        
        differences = []
        
        for metric in metrics:
            metric_data = filtered_df[filtered_df['metric'] == metric]
            baseline_values = metric_data[metric_data['team'] == baseline_team]['value']
            baseline_mean = baseline_values.mean() if len(baseline_values) > 0 else 0
            
            for team in compare_teams:
                team_values = metric_data[metric_data['team'] == team]['value']
                team_mean = team_values.mean() if len(team_values) > 0 else 0
                
                if baseline_mean == 0:
                    pct_diff = 0
                else:
                    pct_diff = ((team_mean - baseline_mean) / baseline_mean) * 100
                
                abs_diff = team_mean - baseline_mean
                
                differences.append({
                    'metric': metric,
                    'team': team,
                    'baseline_team': baseline_team,
                    'baseline_value': round(baseline_mean, 2),
                    'team_value': round(team_mean, 2),
                    'absolute_difference': round(abs_diff, 2),
                    'percentage_difference': round(pct_diff, 2)
                })
        
        return pd.DataFrame(differences)
    
    @staticmethod
    def identify_best_worst(df: pd.DataFrame, metrics: List[str],
                           higher_is_better: Dict[str, bool] = None) -> pd.DataFrame:
        """Identify best and worst performers for each metric.
        
        Args:
            df: DataFrame with metric data
            metrics: List of metrics to analyze
            higher_is_better: Dict mapping metric names to whether higher is better
            
        Returns:
            DataFrame with best/worst performers
        """
        if higher_is_better is None:
            higher_is_better = {m: True for m in metrics}
        
        results = []
        
        for metric in metrics:
            metric_data = df[df['metric'] == metric]
            
            if metric_data.empty:
                continue
            
            team_means = metric_data.groupby('team')['value'].mean()
            
            if higher_is_better.get(metric, True):
                best_team = team_means.idxmax()
                worst_team = team_means.idxmin()
            else:
                best_team = team_means.idxmin()
                worst_team = team_means.idxmax()
            
            results.append({
                'metric': metric,
                'best_team': best_team,
                'best_value': round(team_means[best_team], 2),
                'worst_team': worst_team,
                'worst_value': round(team_means[worst_team], 2),
                'range': round(team_means.max() - team_means.min(), 2)
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def benchmark_comparison(df: pd.DataFrame, benchmarks: Dict[str, float],
                            metrics: List[str], teams: Optional[List[str]] = None) -> pd.DataFrame:
        """Compare actual values against benchmarks.
        
        Args:
            df: DataFrame with metric data
            benchmarks: Dictionary of metric names to benchmark values
            metrics: List of metrics to compare
            teams: Optional list of teams to filter
            
        Returns:
            DataFrame with benchmark comparison results
        """
        filtered_df = df[df['metric'].isin(metrics)]
        
        if teams:
            filtered_df = filtered_df[filtered_df['team'].isin(teams)]
        
        comparison_results = []
        
        for metric in metrics:
            metric_data = filtered_df[filtered_df['metric'] == metric]
            
            if metric_data.empty:
                continue
            
            actual_mean = metric_data['value'].mean()
            benchmark_value = benchmarks.get(metric, 0)
            
            gap = actual_mean - benchmark_value
            
            if benchmark_value == 0:
                gap_pct = 0
                achievement_pct = 0
            else:
                gap_pct = (gap / benchmark_value) * 100
                achievement_pct = (actual_mean / benchmark_value) * 100
            
            comparison_results.append({
                'metric': metric,
                'actual_mean': round(actual_mean, 2),
                'benchmark': round(benchmark_value, 2),
                'gap': round(gap, 2),
                'gap_percentage': round(gap_pct, 2),
                'achievement_percentage': round(achievement_pct, 2),
                'meets_benchmark': actual_mean >= benchmark_value if benchmark_value > 0 else False
            })
        
        return pd.DataFrame(comparison_results)
    
    @staticmethod
    def time_period_comparison(df: pd.DataFrame, metric: str,
                              period1_start: str, period1_end: str,
                              period2_start: str, period2_end: str) -> pd.DataFrame:
        """Compare metrics across two time periods.
        
        Args:
            df: DataFrame with metric data
            metric: Metric name to compare
            period1_start: Start of period 1 (date string)
            period1_end: End of period 1 (date string)
            period2_start: Start of period 2 (date string)
            period2_end: End of period 2 (date string)
            
        Returns:
            DataFrame with period comparison results
        """
        if 'date' not in df.columns:
            raise ValueError("DataFrame must have a 'date' column")
        
        metric_df = df[df['metric'] == metric].copy()
        metric_df['date'] = pd.to_datetime(metric_df['date'])
        
        period1 = metric_df[
            (metric_df['date'] >= period1_start) & 
            (metric_df['date'] <= period1_end)
        ]
        
        period2 = metric_df[
            (metric_df['date'] >= period2_start) & 
            (metric_df['date'] <= period2_end)
        ]
        
        results = {
            'metric': metric,
            'period1_start': period1_start,
            'period1_end': period1_end,
            'period1_mean': round(period1['value'].mean(), 2) if not period1.empty else 0,
            'period1_count': len(period1),
            'period2_start': period2_start,
            'period2_end': period2_end,
            'period2_mean': round(period2['value'].mean(), 2) if not period2.empty else 0,
            'period2_count': len(period2),
        }
        
        if results['period1_mean'] > 0:
            change_pct = ((results['period2_mean'] - results['period1_mean']) / 
                         results['period1_mean']) * 100
        else:
            change_pct = 0
        
        results['change_percentage'] = round(change_pct, 2)
        results['absolute_change'] = round(results['period2_mean'] - results['period1_mean'], 2)
        
        return pd.DataFrame([results])
    
    @staticmethod
    def performance_ranking(df: pd.DataFrame, metrics: List[str],
                           aggregation: str = 'mean') -> pd.DataFrame:
        """Rank teams by performance across metrics.
        
        Args:
            df: DataFrame with metric data
            metrics: List of metrics to consider
            aggregation: Aggregation method ('mean', 'sum', 'max', 'min')
            
        Returns:
            DataFrame with team rankings
        """
        filtered_df = df[df['metric'].isin(metrics)]
        
        agg_func = {
            'mean': 'mean',
            'sum': 'sum',
            'max': 'max',
            'min': 'min'
        }.get(aggregation, 'mean')
        
        rankings = filtered_df.groupby(['team', 'metric'])['value'].agg(agg_func).reset_index()
        
        # Normalize scores (0-100 scale) per metric
        normalized_scores = []
        for metric in metrics:
            metric_data = rankings[rankings['metric'] == metric]
            if metric_data.empty:
                continue
            
            min_val = metric_data['value'].min()
            max_val = metric_data['value'].max()
            range_val = max_val - min_val
            
            if range_val == 0:
                normalized = 50  # Neutral score if all values are the same
            else:
                normalized = ((metric_data['value'] - min_val) / range_val) * 100
            
            metric_data = metric_data.copy()
            metric_data['normalized_score'] = normalized
            normalized_scores.append(metric_data)
        
        if not normalized_scores:
            return pd.DataFrame()
        
        combined = pd.concat(normalized_scores, ignore_index=True)
        
        # Aggregate normalized scores per team
        team_scores = combined.groupby('team')['normalized_score'].mean().reset_index()
        team_scores = team_scores.sort_values('normalized_score', ascending=False)
        team_scores['rank'] = range(1, len(team_scores) + 1)
        
        return team_scores

