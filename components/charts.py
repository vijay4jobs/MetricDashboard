"""Chart visualization components using Plotly."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
import streamlit as st
from config.settings import Settings


class ChartGenerator:
    """Generate various chart types for metrics visualization."""
    
    def __init__(self):
        self.settings = Settings()
        self.colors = self.settings.CHART_COLORS
        self.accent_colors = self.settings.ACCENT_COLORS
        self.font_size = self.settings.FONT_SIZE_LABEL
        self.font_family = self.settings.FONT_FAMILY
        
        self.default_layout = {
            'font': {'family': self.font_family, 'size': self.font_size, 'color': self.accent_colors['text']},
            'plot_bgcolor': self.accent_colors['surface'],
            'paper_bgcolor': self.accent_colors['background'],
            'margin': dict(l=70, r=50, t=100, b=80),
            'hovermode': 'x unified',
            'showlegend': True,
            'legend': {
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': -0.25,
                'xanchor': 'center',
                'x': 0.5,
                'font': {'size': self.font_size, 'family': self.font_family}
            }
        }
    
    def bar_chart(self, df: pd.DataFrame, x: str, y: str, 
                 color: Optional[str] = None, title: str = "") -> go.Figure:
        """Create bar chart.
        
        Args:
            df: DataFrame with data
            x: Column name for x-axis
            y: Column name for y-axis
            color: Optional column for color grouping
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if color:
            fig = px.bar(df, x=x, y=y, color=color, title=title,
                        color_discrete_sequence=px.colors.qualitative.Set2,
                        labels={x: x.replace('_', ' ').title(), 
                               y: y.replace('_', ' ').title()})
        else:
            fig = px.bar(df, x=x, y=y, title=title,
                        color_discrete_sequence=[self.colors['primary']],
                        labels={x: x.replace('_', ' ').title(), 
                               y: y.replace('_', ' ').title()})
        
        layout = self.default_layout.copy()
        if title:
            layout['title'] = {'text': title, 'x': 0.5, 'xanchor': 'center',
                             'font': {'size': self.settings.FONT_SIZE_TITLE, 'color': self.accent_colors['text'], 'family': self.font_family}}
        fig.update_layout(**layout)
        
        fig.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': x.replace('_', ' ').title(), 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        fig.update_yaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': y.replace('_', ' ').title(), 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        return fig
    
    def line_chart(self, df: pd.DataFrame, x: str, y: str,
                  color: Optional[str] = None, title: str = "") -> go.Figure:
        """Create line chart.
        
        Args:
            df: DataFrame with data
            x: Column name for x-axis
            y: Column name for y-axis
            color: Optional column for color grouping
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if color:
            fig = px.line(df, x=x, y=y, color=color, title=title,
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         labels={x: x.replace('_', ' ').title(), 
                                y: y.replace('_', ' ').title()},
                         markers=True)
        else:
            fig = px.line(df, x=x, y=y, title=title,
                         color_discrete_sequence=[self.colors['primary']],
                         labels={x: x.replace('_', ' ').title(), 
                                y: y.replace('_', ' ').title()},
                         markers=True)
        
        layout = self.default_layout.copy()
        if title:
            layout['title'] = {'text': title, 'x': 0.5, 'xanchor': 'center',
                             'font': {'size': self.settings.FONT_SIZE_TITLE, 'color': self.accent_colors['text'], 'family': self.font_family}}
        fig.update_layout(**layout)
        
        fig.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': x.replace('_', ' ').title(), 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        fig.update_yaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': y.replace('_', ' ').title(), 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        return fig
    
    def scatter_chart(self, df: pd.DataFrame, x: str, y: str,
                     color: Optional[str] = None, size: Optional[str] = None,
                     title: str = "") -> go.Figure:
        """Create scatter chart.
        
        Args:
            df: DataFrame with data
            x: Column name for x-axis
            y: Column name for y-axis
            color: Optional column for color grouping
            size: Optional column for size mapping
            title: Chart title
            
        Returns:
            Plotly figure
        """
        fig = px.scatter(df, x=x, y=y, color=color, size=size, title=title,
                        color_discrete_sequence=px.colors.qualitative.Set2)
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest',
            xaxis_title=x.replace('_', ' ').title(),
            yaxis_title=y.replace('_', ' ').title()
        )
        return fig
    
    def pie_chart(self, df: pd.DataFrame, values: str, names: str,
                  title: str = "") -> go.Figure:
        """Create pie chart.
        
        Args:
            df: DataFrame with data
            values: Column name for values
            names: Column name for labels
            title: Chart title
            
        Returns:
            Plotly figure
        """
        fig = px.pie(df, values=values, names=names, title=title,
                    color_discrete_sequence=px.colors.qualitative.Set2)
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
    
    def team_comparison_chart(self, df: pd.DataFrame, teams: List[str],
                             metrics: List[str], chart_type: str = "bar") -> go.Figure:
        """Create team comparison chart (responsive to data).
        
        Args:
            df: DataFrame with team and metric data
            teams: List of team names to compare
            metrics: List of metric names to compare
            chart_type: 'bar' or 'line'
            
        Returns:
            Plotly figure
        """
        filtered_df = df[(df['team'].isin(teams)) & (df['metric'].isin(metrics))].copy()
        
        # Aggregate by team and metric (average values)
        if len(filtered_df) > 0:
            filtered_df = filtered_df.groupby(['team', 'metric'])['value'].mean().reset_index()
        
        # Responsive height based on data size
        num_metrics = len(metrics)
        base_height = 500
        responsive_height = max(base_height, num_metrics * 60 + 200)
        
        # Use accent color palette
        accent_palette = [
            self.accent_colors['primary'],
            self.accent_colors['secondary'],
            self.accent_colors['tertiary'],
            self.accent_colors['quaternary'],
            self.accent_colors['success'],
            self.accent_colors['danger']
        ]
        
        if chart_type == "bar":
            fig = px.bar(filtered_df, x='metric', y='value', color='team',
                        barmode='group', title='Team Comparison by Metric',
                        color_discrete_sequence=accent_palette,
                        labels={'metric': 'Metric', 'value': 'Average Value', 'team': 'Team'},
                        text='value',
                        height=responsive_height)
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        else:
            fig = px.line(filtered_df, x='metric', y='value', color='team',
                         title='Team Comparison by Metric',
                         color_discrete_sequence=accent_palette,
                         labels={'metric': 'Metric', 'value': 'Average Value', 'team': 'Team'},
                         markers=True,
                         height=responsive_height)
        
        layout = self.default_layout.copy()
        layout['title'] = {'text': 'Team Comparison by Metric', 
                          'x': 0.5, 'xanchor': 'center', 
                          'font': {'size': self.settings.FONT_SIZE_TITLE, 'color': self.accent_colors['text'], 'family': self.font_family}}
        layout['height'] = responsive_height
        layout['autosize'] = True
        fig.update_layout(**layout)
        
        # Capitalize metric names on x-axis
        if chart_type == "bar":
            fig.update_xaxes(
                showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
                showline=True, linewidth=2, linecolor=self.accent_colors['border'],
                title={'text': 'Metric', 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
                tickfont={'size': self.font_size, 'family': self.font_family},
                tickangle=-45,
                tickmode='linear'
            )
        else:
            fig.update_xaxes(
                showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
                showline=True, linewidth=2, linecolor=self.accent_colors['border'],
                title={'text': 'Metric', 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
                tickfont={'size': self.font_size, 'family': self.font_family}
            )
        
        fig.update_yaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': 'Average Value', 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        return fig
    
    def benchmark_comparison_chart(self, df: pd.DataFrame, benchmarks: Dict[str, float],
                                  metric: str, team: Optional[str] = None) -> go.Figure:
        """Create benchmark comparison chart.
        
        Args:
            df: DataFrame with metric data
            benchmarks: Dictionary of metric names to benchmark values
            metric: Metric name to display
            team: Optional team name to filter
            
        Returns:
            Plotly figure
        """
        filtered_df = df[df['metric'] == metric].copy()
        if team:
            filtered_df = filtered_df[filtered_df['team'] == team]
        
        avg_value = filtered_df['value'].mean() if not filtered_df.empty else 0
        benchmark_value = benchmarks.get(metric, 0)
        # Metric is already in "Capitalize Each Word" format
        
        fig = go.Figure()
        
        # Add actual value bar
        fig.add_trace(go.Bar(
            name='Actual Average',
            x=[metric],
            y=[avg_value],
            marker_color=self.colors['primary'],
            text=[f'{avg_value:.2f}'],
            textposition='outside',
            width=0.4
        ))
        
        # Add benchmark line
        fig.add_hline(
            y=benchmark_value,
            line_dash="dash",
            line_color=self.colors['quaternary'],
            annotation_text=f"Benchmark: {benchmark_value:.2f}",
            annotation_position="right",
            annotation_font_size=12,
            annotation_font_color=self.colors['quaternary']
        )
        
        layout = self.default_layout.copy()
        layout['title'] = {'text': f'{metric} vs Benchmark', 
                          'x': 0.5, 'xanchor': 'center', 
                          'font': {'size': self.settings.FONT_SIZE_TITLE, 'color': self.accent_colors['text'], 'family': self.font_family}}
        layout['barmode'] = 'group'
        layout['autosize'] = True
        fig.update_layout(**layout)
        
        fig.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': '', 'font': {'size': self.font_size}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        fig.update_yaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': 'Value', 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        
        return fig
    
    def radar_chart(self, df: pd.DataFrame, teams: List[str],
                   metrics: List[str]) -> go.Figure:
        """Create radar chart for multi-metric team comparison.
        
        Args:
            df: DataFrame with team and metric data
            teams: List of team names
            metrics: List of metric names
            
        Returns:
            Plotly figure
        """
        filtered_df = df[(df['team'].isin(teams)) & (df['metric'].isin(metrics))]
        
        fig = go.Figure()
        
        for team in teams:
            team_data = filtered_df[filtered_df['team'] == team]
            values = [team_data[team_data['metric'] == m]['value'].mean() 
                     if len(team_data[team_data['metric'] == m]) > 0 else 0 
                     for m in metrics]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metrics,
                fill='toself',
                name=team
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            showlegend=True,
            title="Radar Chart: Team Comparison Across Metrics"
        )
        
        return fig
    
    def time_series_chart(self, df: pd.DataFrame, metric: str,
                         teams: Optional[List[str]] = None) -> go.Figure:
        """Create time series chart.
        
        Args:
            df: DataFrame with date and metric data
            metric: Metric name
            teams: Optional list of teams to filter
            
        Returns:
            Plotly figure
        """
        filtered_df = df[df['metric'] == metric].copy()
        
        if teams:
            filtered_df = filtered_df[filtered_df['team'].isin(teams)]
        
        if 'date' not in filtered_df.columns or filtered_df['date'].isna().all():
            st.warning("No date column available for time series")
            return go.Figure()
        
        filtered_df = filtered_df.sort_values('date')
        # Metric is already in "Capitalize Each Word" format
        
        if 'team' in filtered_df.columns and len(filtered_df['team'].unique()) > 1:
            fig = px.line(filtered_df, x='date', y='value', color='team',
                         title=f'{metric} Over Time',
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         labels={'date': 'Date', 'value': 'Value', 'team': 'Team'},
                         markers=True)
        else:
            fig = px.line(filtered_df, x='date', y='value',
                         title=f'{metric} Over Time',
                         color_discrete_sequence=[self.colors['primary']],
                         labels={'date': 'Date', 'value': 'Value'},
                         markers=True)
        
        # Responsive height for time series
        num_data_points = len(filtered_df)
        responsive_height = max(500, min(800, num_data_points * 2))
        
        layout = self.default_layout.copy()
        layout['title'] = {'text': f'{metric} Over Time', 
                          'x': 0.5, 'xanchor': 'center', 
                          'font': {'size': self.settings.FONT_SIZE_TITLE, 'color': self.accent_colors['text'], 'family': self.font_family}}
        layout['height'] = responsive_height
        layout['autosize'] = True
        fig.update_layout(**layout)
        
        fig.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': 'Date', 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        fig.update_yaxes(
            showgrid=True, gridwidth=1, gridcolor=self.accent_colors['grid'],
            showline=True, linewidth=2, linecolor=self.accent_colors['border'],
            title={'text': 'Value', 'font': {'size': self.font_size, 'color': self.accent_colors['text'], 'family': self.font_family, 'weight': 'bold'}},
            tickfont={'size': self.font_size, 'family': self.font_family}
        )
        
        return fig

