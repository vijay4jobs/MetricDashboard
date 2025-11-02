"""Excel file loading and processing."""
import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional
import io


class ExcelLoader:
    """Handle Excel file reading and processing."""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls']
    
    def load_excel(self, file_buffer: io.BytesIO, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Load Excel file into DataFrame.
        
        Args:
            file_buffer: File buffer from Streamlit uploader
            sheet_name: Specific sheet to load (None for first sheet)
            
        Returns:
            DataFrame with loaded data
        """
        try:
            if sheet_name:
                df = pd.read_excel(file_buffer, sheet_name=sheet_name, engine='openpyxl')
            else:
                df = pd.read_excel(file_buffer, engine='openpyxl')
            return df
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def get_sheet_names(self, file_buffer: io.BytesIO) -> List[str]:
        """Get list of sheet names from Excel file.
        
        Args:
            file_buffer: File buffer from Streamlit uploader
            
        Returns:
            List of sheet names
        """
        try:
            excel_file = pd.ExcelFile(file_buffer, engine='openpyxl')
            return excel_file.sheet_names
        except Exception as e:
            raise ValueError(f"Error reading Excel file sheets: {str(e)}")
    
    def load_multiple_sheets(self, file_buffer: io.BytesIO) -> Dict[str, pd.DataFrame]:
        """Load all sheets from Excel file.
        
        Args:
            file_buffer: File buffer from Streamlit uploader
            
        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        try:
            excel_file = pd.ExcelFile(file_buffer, engine='openpyxl')
            return {sheet: pd.read_excel(excel_file, sheet_name=sheet) for sheet in excel_file.sheet_names}
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def detect_format(self, df: pd.DataFrame) -> str:
        """Detect if DataFrame is in wide or long format.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            'wide' or 'long'
        """
        # Check if metrics are columns (wide format)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # If many numeric columns, likely wide format
        if len(numeric_cols) > len(text_cols) and len(numeric_cols) > 2:
            return 'wide'
        else:
            return 'long'
    
    def normalize_to_long_format(self, df: pd.DataFrame, 
                                  id_columns: List[str] = None) -> pd.DataFrame:
        """Convert wide format DataFrame to long format.
        
        Args:
            df: DataFrame in wide format
            id_columns: Columns to use as identifiers (default: all non-numeric)
            
        Returns:
            DataFrame in long format with columns: [id_cols..., 'metric', 'value']
        """
        if id_columns is None:
            # Auto-detect ID columns (non-numeric columns)
            id_columns = df.select_dtypes(exclude=['number']).columns.tolist()
        
        if not id_columns:
            raise ValueError("No identifier columns found. Need at least one non-numeric column.")
        
        # Melt the DataFrame
        value_vars = [col for col in df.columns if col not in id_columns]
        df_long = pd.melt(df, id_vars=id_columns, value_vars=value_vars,
                         var_name='metric', value_name='value')
        
        return df_long
    
    def extract_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract metadata from DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with metadata (teams, metrics, date_range, etc.)
        """
        metadata = {
            'total_rows': len(df),
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict()
        }
        
        # Detect teams/projects
        potential_team_cols = [col for col in df.columns 
                             if any(keyword in col.lower() for keyword in 
                                   ['team', 'project', 'group', 'squad', 'unit'])]
        if potential_team_cols:
            metadata['team_column'] = potential_team_cols[0]
            metadata['teams'] = df[potential_team_cols[0]].unique().tolist()
        
        # Detect metrics
        if 'metric' in df.columns:
            metadata['metrics'] = df['metric'].unique().tolist()
        
        # Detect dates
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols:
            metadata['date_column'] = date_cols[0]
            metadata['date_range'] = {
                'min': df[date_cols[0]].min(),
                'max': df[date_cols[0]].max()
            }
        
        return metadata
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize DataFrame.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        # Convert numeric columns
        numeric_cols = df.select_dtypes(include=['object']).columns
        for col in numeric_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
        
        return df

