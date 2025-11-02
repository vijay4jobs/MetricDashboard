"""Script to create database tables and insert dummy data."""

import sys
from datetime import datetime, timedelta
import random
import uuid
from config.settings import DatabaseConfig, Settings
from data.database import DatabaseManager, MetricData, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def create_dummy_data(num_weeks: int = 26):
    """Create dummy metric data.

    Args:
        num_weeks: Number of weeks of data to generate (default: 26 for ~6 months)

    Returns:
        List of dictionaries containing dummy metric data
    """

    teams = ["Alpha Team", "Beta Team", "Gamma Team", "Delta Team", "Epsilon Team"]

    # Metric names in "Capitalize Each Word" format
    metrics = [
        "Velocity Points Per Sprint",
        "Code Commits Per Week",
        "Defect Rate",
        "Code Coverage",
        "Bug Resolution Time",
        "Sprint Completion Rate",
        "Cycle Time",
        "Lead Time",
        "Utilization Rate",
        "Throughput",
        "Customer Satisfaction Score",
        "Response Time"
    ]

    categories = {
        "Velocity Points Per Sprint": "Productivity",
        "Code Commits Per Week": "Productivity",
        "Defect Rate": "Quality",
        "Code Coverage": "Quality",
        "Bug Resolution Time": "Quality",
        "Sprint Completion Rate": "Velocity",
        "Cycle Time": "Velocity",
        "Lead Time": "Velocity",
        "Utilization Rate": "Efficiency",
        "Throughput": "Efficiency",
        "Customer Satisfaction Score": "Customer Satisfaction",
        "Response Time": "Customer Satisfaction"
    }

    units = {
        "Velocity Points Per Sprint": "Story Points",
        "Code Commits Per Week": "Commits",
        "Defect Rate": "Defects Per 100 LOC",
        "Code Coverage": "Percentage",
        "Bug Resolution Time": "Hours",
        "Sprint Completion Rate": "Percentage",
        "Cycle Time": "Days",
        "Lead Time": "Days",
        "Utilization Rate": "Percentage",
        "Throughput": "Items Per Week",
        "Customer Satisfaction Score": "Rating (1-5)",
        "Response Time": "Hours"
    }

    base_values = {
        "Velocity Points Per Sprint": (20, 35),
        "Code Commits Per Week": (10, 25),
        "Defect Rate": (0.01, 0.05),
        "Code Coverage": (70, 90),
        "Bug Resolution Time": (24, 72),
        "Sprint Completion Rate": (75, 95),
        "Cycle Time": (3, 8),
        "Lead Time": (7, 15),
        "Utilization Rate": (65, 85),
        "Throughput": (8, 18),
        "Customer Satisfaction Score": (3.5, 4.8),
        "Response Time": (1, 4)
    }

    projects = ["Apollo Initiative", "Beacon Upgrade", "Catalyst Rollout", "Delta Revamp"]

    start_date = datetime.now() - timedelta(weeks=num_weeks)
    end_date = datetime.now()

    dummy_data = []

    current_date = start_date
    while current_date <= end_date:
        for team in teams:
            for metric in metrics:
                if random.random() > 0.3:
                    min_val, max_val = base_values[metric]
                    value = round(random.uniform(min_val, max_val), 2)

                    team_factor = teams.index(team) * 0.05
                    value = value * (1 + team_factor - 0.1)

                    if metric == "Defect Rate":
                        value = max(0.001, min(value, 0.1))
                    elif metric in ["Code Coverage", "Sprint Completion Rate", "Utilization Rate"]:
                        value = max(0, min(value, 100))
                    elif metric == "Customer Satisfaction Score":
                        value = max(1, min(value, 5))

                    dummy_data.append({
                        'id': str(uuid.uuid4()),
                        'team': team,
                        'metric': metric,
                        'value': round(value, 2),
                        'date': current_date,
                        'category': categories[metric],
                        'unit': units[metric],
                        'project': random.choice(projects),
                        'notes': f"Generated data point for {team}",
                        'created_at': datetime.utcnow()
                    })

        current_date += timedelta(days=7)

    return dummy_data


def initialize_database(database_path: str = "metrics.db", clear_existing: bool = False):
    """Initialize database with tables and dummy data.

    Args:
        database_path: Path to SQLite database file
        clear_existing: Whether to clear existing data before inserting

    Returns:
        Tuple of (success: bool, message: str, summary: dict)
    """
    print("Initializing database...")

    config = DatabaseConfig(
        db_type="sqlite",
        database=database_path
    )

    try:
        db_manager = DatabaseManager(config)
        print("✓ Database connection established")

        existing_teams = db_manager.get_teams()
        if existing_teams and clear_existing:
            session = db_manager.get_session()
            try:
                session.query(MetricData).delete()
                session.commit()
                print("✓ Cleared existing data")
            finally:
                session.close()
        elif existing_teams:
            print("Keeping existing data. Adding new dummy data...")

        print("Generating dummy data...")
        dummy_data = create_dummy_data(num_weeks=26)
        print(f"✓ Generated {len(dummy_data)} data points")

        print("Inserting data into database...")
        session = db_manager.get_session()

        try:
            inserted = 0
            for data in dummy_data:
                metric_record = MetricData(**data)
                session.add(metric_record)
                inserted += 1

                if inserted % 100 == 0:
                    session.commit()
                    print(f"  Inserted {inserted} records...")

            session.commit()
            print(f"✓ Successfully inserted {inserted} records")

            print("\n" + "=" * 50)
            print("Database Summary:")
            print("=" * 50)
            summary = db_manager.get_summary_stats()
            print(f"Total Records: {summary['total_records']}")
            print(f"Teams: {summary['teams']}")
            print(f"Metrics: {summary['metrics']}")

            teams = db_manager.get_teams()
            metrics = db_manager.get_metrics()

            print(f"\nTeams: {', '.join(teams)}")
            print(f"\nMetrics: {', '.join(metrics[:5])}... ({len(metrics)} total)")
            print("\n✓ Database initialization complete!")
            print(f"Database file: {config.database}")

            return True, "Database initialized successfully", summary

        finally:
            session.close()

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"✗ {error_msg}")
        return False, error_msg, {}


if __name__ == "__main__":
    clear = len(sys.argv) > 1 and sys.argv[1] == "--clear"
    success, message, summary = initialize_database(clear_existing=clear)
    if not success:
        sys.exit(1)