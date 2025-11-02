"""Configuration settings for Metric Dashboard."""
import os
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "metrics.db"
    username: str = ""
    password: str = ""
    connection_string: str = ""

    def get_connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        if self.connection_string:
            return self.connection_string
        
        if self.db_type == "sqlite":
            return f"sqlite:///{self.database}"
        elif self.db_type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "mysql":
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


class Settings:
    """Application settings."""
    
    # Accent color theme
    ACCENT_COLORS = {
        "primary": "#0066CC",      # Blue accent
        "secondary": "#FF6B35",    # Orange accent
        "tertiary": "#4ECDC4",     # Teal accent
        "quaternary": "#FFE66D",   # Yellow accent
        "success": "#06D6A0",      # Green accent
        "danger": "#EF476F",       # Red accent
        "background": "#F8F9FA",    # Light background
        "surface": "#FFFFFF",       # White surface
        "text": "#212529",          # Dark text
        "text_secondary": "#6C757D", # Gray text
        "border": "#DEE2E6",        # Light border
        "grid": "#E9ECEF"           # Grid lines
    }
    
    # Chart color schemes (using accent colors)
    CHART_COLORS = {
        "primary": ACCENT_COLORS["primary"],
        "secondary": ACCENT_COLORS["secondary"],
        "tertiary": ACCENT_COLORS["tertiary"],
        "quaternary": ACCENT_COLORS["quaternary"],
        "quinary": "#9467bd",
        "background": ACCENT_COLORS["background"],
        "grid": ACCENT_COLORS["grid"]
    }
    
    # Font settings
    FONT_SIZE_LABEL = 15  # Standard label font size
    FONT_SIZE_TITLE = 16  # Title font size
    FONT_FAMILY = "Arial, sans-serif"
    
    # Default benchmark categories
    BENCHMARK_CATEGORIES = [
        "productivity",
        "quality",
        "velocity",
        "efficiency",
        "customer_satisfaction"
    ]
    
    # Default page configuration
    PAGE_CONFIG = {
        "page_title": "Metric Dashboard",
        "page_icon": "📊",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Data validation settings
    REQUIRED_COLUMNS = ["team", "metric", "value"]
    OPTIONAL_COLUMNS = ["date", "category", "unit", "notes", "project"]
    
    # File upload settings
    MAX_UPLOAD_SIZE_MB = 100
    ALLOWED_EXTENSIONS = [".xlsx", ".xls"]
    
    @staticmethod
    def get_db_config() -> DatabaseConfig:
        """Load database configuration from environment or defaults."""
        return DatabaseConfig(
            db_type=os.getenv("DB_TYPE", "sqlite"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "metrics.db"),
            username=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            connection_string=os.getenv("DB_CONNECTION_STRING", "")
        )


# Global settings instance
settings = Settings()

