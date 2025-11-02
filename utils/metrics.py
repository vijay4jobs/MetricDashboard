"""Metric calculation utilities."""
import pandas as pd
from typing import List, Dict, Any, Optional
import numpy as np


class MetricCalculator:
    """Calculate various metric statistics and aggregations."""
    
    @staticmethod
    def calculate_statistics(df: pd.DataFrame, metric: str,
                            group_by: Optional[str] = None) -> Dict[str, float]:
        """Calculate basic statistics for a metric.
        
        Args:
            df: DataFrame with metric data
            metric: Metric name
            group_by: Optional column to group by
            
        Returns:
            Dictionary with statistics
        """
        metric_df = df[df['metric'] == metric] if 'metric' in df.columns else df
        
        if group_by:
            stats = metric_df.groupby(group_by)['value'].agg([
                'count', 'mean', 'std', 'min', 'max', 'median'
            ]).to_dict()
        else:
            values = metric_df['value']
            stats = {
                'count': len(values),
                'mean': values.mean(),
                'std': values.std(),
                'min': values.min(),
                'max': values.max(),
                'median': values.median()
            }
        
        # Round to 2 decimal places
        return {k: round(v, 2) if isinstance(v, (int, float)) else v 
                for k, v in stats.items()}
    
    @staticmethod
    def calculate_trend(df: pd.DataFrame, metric: str,
                       date_col: str = 'date') -> Dict[str, Any]:
        """Calculate trend analysis for a metric over time.
        
        Args:
            df: DataFrame with metric data
            metric: Metric name
            date_col: Date column name
            
        Returns:
            Dictionary with trend information
        """
        metric_df = df[df['metric'] == metric].copy()
        
        if date_col not in metric_df.columns:
            return {'error': 'No date column available'}
        
        metric_df[date_col] = pd.to_datetime(metric_df[date_col])
        metric_df = metric_df.sort_values(date_col)
        
        values = metric_df['value'].values
        
        if len(values) < 2:
            return {'error': 'Insufficient data points for trend'}
        
        # Linear regression for trend
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Percentage change
        first_half = values[:len(values)//2].mean() if len(values) > 1 else values[0]
        second_half = values[len(values)//2:].mean()
        pct_change = ((second_half - first_half) / first_half * 100) if first_half != 0 else 0
        
        trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
        
        return {
            'trend_direction': trend_direction,
            'slope': round(slope, 4),
            'first_half_mean': round(first_half, 2),
            'second_half_mean': round(second_half, 2),
            'percentage_change': round(pct_change, 2),
            'data_points': len(values)
        }
    
    @staticmethod
    def calculate_percentiles(df: pd.DataFrame, metric: str,
                             percentiles: List[float] = [25, 50, 75, 90, 95]) -> Dict[str, float]:
        """Calculate percentiles for a metric.
        
        Args:
            df: DataFrame with metric data
            metric: Metric name
            percentiles: List of percentiles to calculate
            
        Returns:
            Dictionary with percentile values
        """
        metric_df = df[df['metric'] == metric] if 'metric' in df.columns else df
        
        values = metric_df['value'].dropna()
        
        if values.empty:
            return {}
        
        percentile_values = np.percentile(values, percentiles)
        
        return {
            f'p{p}': round(val, 2) 
            for p, val in zip(percentiles, percentile_values)
        }
    
    @staticmethod
    def aggregate_metrics(df: pd.DataFrame, group_by: List[str],
                         aggregation: str = 'mean') -> pd.DataFrame:
        """Aggregate metrics by grouping columns.
        
        Args:
            df: DataFrame with metric data
            group_by: List of columns to group by
            aggregation: Aggregation method ('mean', 'sum', 'max', 'min', 'count')
            
        Returns:
            Aggregated DataFrame
        """
        agg_func = {
            'mean': 'mean',
            'sum': 'sum',
            'max': 'max',
            'min': 'min',
            'count': 'count'
        }.get(aggregation, 'mean')
        
        aggregated = df.groupby(group_by)['value'].agg(agg_func).reset_index()
        aggregated['value'] = aggregated['value'].round(2)
        
        return aggregated
    
    @staticmethod
    def detect_outliers(df: pd.DataFrame, metric: str,
                       method: str = 'iqr') -> pd.DataFrame:
        """Detect outliers in metric values.
        
        Args:
            df: DataFrame with metric data
            metric: Metric name
            method: Outlier detection method ('iqr' or 'zscore')
            
        Returns:
            DataFrame with outlier flags
        """
        metric_df = df[df['metric'] == metric].copy()
        values = metric_df['value']
        
        if method == 'iqr':
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            metric_df['is_outlier'] = (metric_df['value'] < lower_bound) | \
                                      (metric_df['value'] > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs((values - values.mean()) / values.std())
            metric_df['is_outlier'] = z_scores > 3
        
        return metric_df

