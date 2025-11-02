"""Filtering and selection UI components."""
import streamlit as st
import pandas as pd
from typing import List, Optional
from datetime import datetime, date


class FilterComponent:
    """UI components for filtering data."""
    
    @staticmethod
    def team_selector(df: pd.DataFrame, key: str = "team_filter",
                     default: Optional[List[str]] = None) -> List[str]:
        """Team/project selector widget.
        
        Args:
            df: DataFrame with team data
            key: Unique key for widget
            default: Default selected teams
            
        Returns:
            List of selected team names
        """
        if 'team' not in df.columns:
            return []
        
        teams = sorted(df['team'].unique().tolist())
        
        if default is None:
            default = teams
        
        selected = st.multiselect(
            "Select Teams",
            teams,
            default=default,
            key=key
        )
        
        return selected
    
    @staticmethod
    def metric_selector(df: pd.DataFrame, key: str = "metric_filter",
                       default: Optional[List[str]] = None) -> List[str]:
        """Metric selector widget.
        
        Args:
            df: DataFrame with metric data
            key: Unique key for widget
            default: Default selected metrics
            
        Returns:
            List of selected metric names
        """
        if 'metric' not in df.columns:
            return []
        
        metrics = sorted(df['metric'].unique().tolist())
        
        if default is None:
            default = metrics
        
        selected = st.multiselect(
            "Select Metrics",
            metrics,
            default=default,
            key=key
        )
        
        return selected
    
    @staticmethod
    def date_range_picker(df: pd.DataFrame, key: str = "date_filter",
                         date_col: str = 'date') -> tuple:
        """Date range picker widget.
        
        Args:
            df: DataFrame with date data
            key: Unique key for widget
            date_col: Name of date column
            
        Returns:
            Tuple of (start_date, end_date) or (None, None)
        """
        if date_col not in df.columns:
            return None, None
        
        dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
        
        if dates.empty:
            return None, None
        
        min_date = dates.min().date()
        max_date = dates.max().date()
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key=f"{key}_start"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key=f"{key}_end"
            )
        
        return start_date, end_date
    
    @staticmethod
    def chart_type_selector(key: str = "chart_type") -> str:
        """Chart type selector widget.
        
        Args:
            key: Unique key for widget
            
        Returns:
            Selected chart type
        """
        chart_types = ["Bar", "Line", "Scatter", "Pie", "Radar"]
        
        selected = st.selectbox(
            "Chart Type",
            chart_types,
            key=key
        )
        
        return selected.lower()
    
    @staticmethod
    def benchmark_category_selector(categories: List[str],
                                   key: str = "benchmark_category") -> str:
        """Benchmark category selector widget.
        
        Args:
            categories: List of available categories
            key: Unique key for widget
            
        Returns:
            Selected category
        """
        selected = st.selectbox(
            "Benchmark Category",
            categories,
            key=key
        )
        
        return selected
    
    @staticmethod
    def project_selector(df: pd.DataFrame, key: str = "project_filter",
                        default: Optional[List[str]] = None) -> List[str]:
        """Project selector widget.
        
        Args:
            df: DataFrame with project data
            key: Unique key for widget
            default: Default selected projects
            
        Returns:
            List of selected project names
        """
        if 'project' not in df.columns:
            return []
        
        projects = sorted([p for p in df['project'].unique().tolist() if p and str(p) != 'nan'])
        
        if not projects:
            return []
        
        if default is None:
            default = projects
        
        selected = st.multiselect(
            "Select Projects",
            projects,
            default=default,
            key=key
        )
        
        return selected

