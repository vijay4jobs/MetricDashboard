"""Data validation and cleaning."""
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from config.settings import Settings


class DataValidator:
    """Validate and clean metric data."""
    
    def __init__(self):
        self.settings = Settings()
        self.errors = []
        self.warnings = []
    
    def validate_dataframe(self, df: pd.DataFrame, 
                          required_cols: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
        """Validate DataFrame structure.
        
        Args:
            df: DataFrame to validate
            required_cols: List of required columns (default: from settings)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self.errors = []
        self.warnings = []
        
        if required_cols is None:
            required_cols = self.settings.REQUIRED_COLUMNS
        
        # Check if DataFrame is empty
        if df.empty:
            self.errors.append("DataFrame is empty")
            return False, self.errors
        
        # Check required columns (flexible matching)
        df_cols_lower = [col.lower() for col in df.columns]
        missing_cols = []
        
        for req_col in required_cols:
            req_col_lower = req_col.lower()
            # Try exact match first
            if req_col not in df.columns and req_col_lower not in df_cols_lower:
                # Try partial match
                matches = [col for col in df.columns if req_col_lower in col.lower()]
                if not matches:
                    missing_cols.append(req_col)
        
        if missing_cols:
            self.errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            self.errors.append(f"Available columns: {', '.join(df.columns)}")
        
        # Validate data types
        if 'value' in df.columns:
            non_numeric = pd.to_numeric(df['value'], errors='coerce').isna().sum()
            if non_numeric > 0:
                self.warnings.append(f"{non_numeric} non-numeric values found in 'value' column")
        
        # Check for missing values in required columns
        for col in required_cols:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    self.warnings.append(f"{missing_count} missing values in '{col}' column")
        
        return len(self.errors) == 0, self.errors
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize DataFrame.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Remove completely empty rows
        df_clean = df_clean.dropna(how='all')
        
        # Strip whitespace from string columns
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].replace('nan', None)
            df_clean[col] = df_clean[col].replace('None', None)
        
        # Convert value column to numeric
        if 'value' in df_clean.columns:
            df_clean['value'] = pd.to_numeric(df_clean['value'], errors='coerce')
        
        # Convert date column
        date_cols = ['date', 'Date', 'DATE']
        for col in date_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
        
        # Remove rows with missing required values
        required_cols = ['team', 'metric', 'value']
        for col in required_cols:
            if col in df_clean.columns:
                before = len(df_clean)
                df_clean = df_clean.dropna(subset=[col])
                after = len(df_clean)
                if before != after:
                    self.warnings.append(f"Removed {before - after} rows with missing '{col}'")
        
        return df_clean
    
    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to standard format.
        
        Args:
            df: DataFrame with potentially non-standard column names
            
        Returns:
            DataFrame with normalized column names
        """
        df_norm = df.copy()
        column_mapping = {}
        
        # Common variations
        name_variations = {
            'team': ['team', 'Team', 'TEAM', 'group', 'Group', 'squad', 'Squad'],
            'metric': ['metric', 'Metric', 'METRIC', 'measure', 'Measure', 'kpi', 'KPI'],
            'value': ['value', 'Value', 'VALUE', 'score', 'Score', 'result', 'Result'],
            'date': ['date', 'Date', 'DATE', 'time', 'Time', 'timestamp', 'Timestamp'],
            'project': ['project', 'Project', 'PROJECT', 'initiative', 'Initiative']
        }
        
        # Map columns to standard names
        for standard_name, variations in name_variations.items():
            for col in df_norm.columns:
                if col in variations or any(var.lower() in col.lower() for var in variations if var):
                    column_mapping[col] = standard_name
                    break
        
        df_norm = df_norm.rename(columns=column_mapping)
        
        return df_norm
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get validation report with errors and warnings.
        
        Returns:
            Dictionary with validation results
        """
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }

