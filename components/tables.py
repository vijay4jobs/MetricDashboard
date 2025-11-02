"""Table display components."""
import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional
import io
from config.settings import Settings


class TableGenerator:
    """Generate and display tables for metrics."""
    
    def __init__(self):
        self.settings = Settings()
        self.accent_colors = self.settings.ACCENT_COLORS
    
    @staticmethod
    def _capitalize_header(text: str) -> str:
        """Capitalize each word in header, preserving text in parentheses."""
        text_str = str(text)
        if text_str and text_str[0].isupper() and ' ' in text_str:
            return text_str
        import re
        parts = re.split(r'([()])', text_str.replace('_', ' '))
        result_parts = []
        in_parentheses = False
        for part in parts:
            if part == '(':
                in_parentheses = True
                result_parts.append(part)
            elif part == ')':
                in_parentheses = False
                result_parts.append(part)
            elif in_parentheses:
                result_parts.append(part)
            else:
                result_parts.append(' '.join(word.capitalize() for word in part.split()))
        result = ''.join(result_parts)
        result = ' '.join(result.split())
        return result
    
    def display_dataframe(self, df: pd.DataFrame, use_container_width: bool = True,
                         height: Optional[int] = None):
        """Display DataFrame as styled interactive table."""
        styled_df = df.copy()
        styled_df.columns = [self._capitalize_header(col) for col in styled_df.columns]
        st.dataframe(styled_df, use_container_width=use_container_width, height=height)

    def display_styled_table(self, df: pd.DataFrame, use_container_width: bool = True, 
                            height: Optional[int] = None):
        """Display DataFrame as styled HTML table with center-aligned formatting."""
        df_display = df.copy()
        df_display.columns = [self._capitalize_header(col) for col in df_display.columns]

        # Force center alignment using applymap to set inline styles on all cells
        def center_align(val):
            """Return CSS style string for center alignment."""
            return 'text-align: center !important;'

        # Center alignment for all columns
        styled = (
            df_display.style
            .set_properties(subset=None, **{'text-align': 'center'})
            .applymap(center_align)  # Force center alignment on all cells with inline style
            .set_table_styles([
                {
                    'selector': 'thead th',
                    'props': [
                        ('background-color', self.accent_colors['primary']),
                        ('color', 'white'),
                        ('font-weight', 'bold'),
                        ('font-size', f'{self.settings.FONT_SIZE_LABEL}px'),
                        ('text-align', 'center'),
                        ('padding', '10px'),
                        ('font-family', self.settings.FONT_FAMILY),
                        ('border', 'none')
                    ]
                },
                {
                    'selector': 'tbody td',
                    'props': [
                        ('text-align', 'center !important'),
                        ('padding', '8px'),
                        ('font-size', f'{self.settings.FONT_SIZE_LABEL - 2}px'),
                        ('font-family', self.settings.FONT_FAMILY)
                    ]
                },
                {
                    'selector': 'tbody tr:nth-of-type(even)',
                    'props': [
                        ('background-color', self.accent_colors['background'])
                    ]
                },
                {
                    'selector': 'tbody tr:hover',
                    'props': [
                        ('background-color', '#f0f0f0')
                    ]
                },
                {
                    'selector': 'thead',
                    'props': [
                        ('background-color', self.accent_colors['primary']),
                    ]
                },
                {
                    'selector': 'table',
                    'props': [
                        ('width', '100%'),
                        ('border-collapse', 'collapse'),
                        ('margin-left', 'auto'),
                        ('margin-right', 'auto'),
                        ('margin', '0px auto !important'),
                    ]
                },
                {
                    'selector': 'td',
                    'props': [
                        ('text-align', 'center !important')
                    ]
                },
                {
                    'selector': 'td[style*="text-align"]',
                    'props': [
                        ('text-align', 'center !important')
                    ]
                }
            ])
            .format_index(lambda x: self._capitalize_header(x))
        )

        if height is not None:
            st.markdown(
                f'<div style="max-height: {height}px; overflow-y: auto; margin:auto;">',
                unsafe_allow_html=True
            )
            st.dataframe(styled, use_container_width=use_container_width)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.dataframe(styled, use_container_width=use_container_width)

    def summary_table(self, df: pd.DataFrame, group_by: str = 'team') -> pd.DataFrame:
        """Create summary statistics table."""
        if group_by not in df.columns:
            return pd.DataFrame()
        summary = df.groupby(group_by).agg({
            'value': ['count', 'mean', 'std', 'min', 'max']
        }).round(2)
        summary.columns = ['Count', 'Mean', 'Std Dev', 'Min', 'Max']
        summary = summary.reset_index()
        summary.rename(columns={group_by: self._capitalize_header(group_by)}, inplace=True)
        return summary
    
    def comparison_table(self, df: pd.DataFrame, teams: List[str],
                        metrics: List[str]) -> pd.DataFrame:
        """Create team comparison table."""
        filtered_df = df[(df['team'].isin(teams)) & (df['metric'].isin(metrics))]
        if filtered_df.empty:
            return pd.DataFrame()
        pivot = filtered_df.pivot_table(
            index='team',
            columns='metric',
            values='value',
            aggfunc='mean'
        ).round(2)
        pivot.columns = [self._capitalize_header(col) for col in pivot.columns]
        pivot.index.name = self._capitalize_header(pivot.index.name) if pivot.index.name else 'Team'
        return pivot
    
    def benchmark_comparison_table(self, df: pd.DataFrame, benchmarks: Dict[str, float],
                                  metrics: List[str]) -> pd.DataFrame:
        """Create benchmark comparison table."""
        comparison_data = []
        for metric in metrics:
            metric_data = df[df['metric'] == metric]
            actual_mean = metric_data['value'].mean() if not metric_data.empty else 0
            benchmark_value = benchmarks.get(metric, 0)
            gap = actual_mean - benchmark_value
            gap_pct = (gap / benchmark_value * 100) if benchmark_value != 0 else 0
            comparison_data.append({
                'Metric': metric,
                'Actual (Avg)': round(actual_mean, 2),
                'Benchmark': round(benchmark_value, 2),
                'Gap': round(gap, 2),
                'Gap %': f"{round(gap_pct, 2)}%"
            })
        return pd.DataFrame(comparison_data)
    
    @staticmethod
    def color_code_table(df: pd.DataFrame, column: str, 
                        threshold: float = 0, reverse: bool = False) -> pd.DataFrame:
        """Apply color coding to table based on values."""
        def color_cell(val):
            if pd.isna(val):
                return ''
            if reverse:
                color = 'red' if val > threshold else 'green'
            else:
                color = 'green' if val > threshold else 'red'
            return f'background-color: {color}'
        styled_df = df.style.applymap(color_cell, subset=[column])
        return styled_df
    
    @staticmethod
    def export_to_csv(df: pd.DataFrame) -> bytes:
        """Export DataFrame to CSV bytes."""
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue().encode()
    
    @staticmethod
    def export_to_excel(df: pd.DataFrame) -> bytes:
        """Export DataFrame to Excel bytes."""
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        return excel_buffer.getvalue()