"""Database connection and query interface."""
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, DateTime, select, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import streamlit as st
from config.settings import DatabaseConfig

Base = declarative_base()


class MetricData(Base):
    """SQLAlchemy model for metric data."""
    __tablename__ = 'metrics'
    
    id = Column(String, primary_key=True)
    team = Column(String, nullable=False, index=True)
    metric = Column(String, nullable=False, index=True)
    value = Column(Float, nullable=False)
    date = Column(DateTime, index=True)
    category = Column(String)
    unit = Column(String)
    project = Column(String, index=True)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MetricData(team={self.team}, metric={self.metric}, value={self.value})>"


class DatabaseManager:
    """Manage database connections and operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database manager with configuration."""
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            connection_string = self.config.get_connection_string()
            
            # Special handling for SQLite
            if self.config.db_type == "sqlite":
                self.engine = create_engine(
                    connection_string,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool
                )
            else:
                self.engine = create_engine(connection_string)
            
            self.SessionLocal = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(select(1))
            return True
        except Exception as e:
            st.error(f"Connection test failed: {str(e)}")
            return False
    
    def insert_metrics(self, df: pd.DataFrame, team_col: str = 'team', 
                      metric_col: str = 'metric', value_col: str = 'value') -> int:
        """Insert metrics from DataFrame into database.
        
        Args:
            df: DataFrame with metric data
            team_col: Column name for team identifier
            metric_col: Column name for metric name
            value_col: Column name for metric value
            
        Returns:
            Number of records inserted
        """
        session = self.get_session()
        inserted = 0
        
        try:
            for _, row in df.iterrows():
                # Generate unique ID
                import uuid
                metric_id = str(uuid.uuid4())
                
                metric_data = MetricData(
                    id=metric_id,
                    team=str(row.get(team_col, 'Unknown')),
                    metric=str(row.get(metric_col, 'Unknown')),
                    value=float(row.get(value_col, 0)),
                    date=pd.to_datetime(row.get('date', None)) if 'date' in row else None,
                    category=str(row.get('category', '')) if 'category' in row else None,
                    unit=str(row.get('unit', '')) if 'unit' in row else None,
                    project=str(row.get('project', '')) if 'project' in row else None,
                    notes=str(row.get('notes', '')) if 'notes' in row else None
                )
                session.add(metric_data)
                inserted += 1
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise ValueError(f"Error inserting metrics: {str(e)}")
        finally:
            session.close()
        
        return inserted
    
    def query_metrics(self, teams: Optional[List[str]] = None,
                     metrics: Optional[List[str]] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     projects: Optional[List[str]] = None) -> pd.DataFrame:
        """Query metrics from database.
        
        Args:
            teams: Filter by team names
            metrics: Filter by metric names
            start_date: Start date filter
            end_date: End date filter
            projects: Filter by project names
            
        Returns:
            DataFrame with queried metrics
        """
        session = self.get_session()
        
        try:
            query = session.query(MetricData)
            
            if teams:
                query = query.filter(MetricData.team.in_(teams))
            if metrics:
                query = query.filter(MetricData.metric.in_(metrics))
            if start_date:
                query = query.filter(MetricData.date >= start_date)
            if end_date:
                query = query.filter(MetricData.date <= end_date)
            if projects:
                query = query.filter(MetricData.project.in_(projects))
            
            results = query.all()
            
            # Convert to DataFrame
            data = []
            for result in results:
                data.append({
                    'team': result.team,
                    'metric': result.metric,
                    'value': result.value,
                    'date': result.date,
                    'category': result.category,
                    'unit': result.unit,
                    'project': result.project,
                    'notes': result.notes
                })
            
            return pd.DataFrame(data)
        finally:
            session.close()
    
    def get_teams(self) -> List[str]:
        """Get list of unique teams."""
        session = self.get_session()
        try:
            teams = session.query(MetricData.team).distinct().all()
            return [team[0] for team in teams]
        finally:
            session.close()
    
    def get_metrics(self) -> List[str]:
        """Get list of unique metrics."""
        session = self.get_session()
        try:
            metrics = session.query(MetricData.metric).distinct().all()
            return [metric[0] for metric in metrics]
        finally:
            session.close()
    
    def get_projects(self) -> List[str]:
        """Get list of unique projects."""
        session = self.get_session()
        try:
            projects = session.query(MetricData.project).distinct().all()
            return [p[0] for p in projects if p[0]]
        finally:
            session.close()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from database."""
        session = self.get_session()
        try:
            total_records = session.query(MetricData).count()
            teams = len(session.query(MetricData.team).distinct().all())
            metrics = len(session.query(MetricData.metric).distinct().all())
            
            return {
                'total_records': total_records,
                'teams': teams,
                'metrics': metrics,
                'last_updated': session.query(MetricData.created_at).order_by(
                    MetricData.created_at.desc()).first()[0] if total_records > 0 else None
            }
        finally:
            session.close()


# Global database manager (initialized in app)
db_manager: Optional[DatabaseManager] = None

