# MetricDashboard
Metric Dashboard Python-based dashboard using Streamlit for rapid development and interactive UI.

A comprehensive Python-based dashboard application built with Streamlit for visualizing, comparing, and managing metrics across teams and projects. The system supports Excel file imports, database connections, flexible metric handling, team-to-team comparisons, industry benchmark comparisons, and mitigation planning.

## Features

- **📊 Interactive Dashboards**: Real-time metric visualization with multiple chart types
- **📥 Data Import**: Excel file upload and database connection support (SQLite, PostgreSQL, MySQL)
- **⚖️ Team Comparisons**: Side-by-side team performance analysis
- **🎯 Benchmark Comparisons**: Compare metrics against industry standards
- **🔧 Mitigation Plans**: Create and manage action items for improving metrics
- **📈 Multiple Visualization Types**: Bar, line, scatter, pie, radar, and time series charts
- **🔍 Flexible Filtering**: Filter by teams, metrics, dates, and projects
- **💾 Flexible Schema**: Auto-detects metric structure from input data

## Project Structure

```
MetricDashboard/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration for databases, benchmarks
├── data/
│   ├── __init__.py
│   ├── excel_loader.py         # Excel file reading and processing
│   ├── database.py             # Database connection and queries
│   └── data_validator.py       # Data validation and cleaning
├── components/
│   ├── __init__.py
│   ├── charts.py               # Chart visualization components
│   ├── tables.py               # Table display components
│   └── filters.py              # Filtering and selection UI
├── utils/
│   ├── __init__.py
│   ├── comparisons.py          # Team vs team, vs benchmark logic
│   └── metrics.py              # Metric calculation utilities
├── mitigation/
│   ├── __init__.py
│   ├── action_items.py         # Mitigation plan and action item models
│   └── mitigation_db.py        # Database/storage for mitigation plans
└── benchmarks/
    └── industry_benchmarks.json # Industry benchmark data storage
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd MetricDashboard
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file for database configuration (optional):**
   ```env
   DB_TYPE=sqlite
   DB_NAME=metrics.db
   
   # For PostgreSQL:
   # DB_TYPE=postgresql
   # DB_HOST=localhost
   # DB_PORT=5432
   # DB_NAME=metrics
   # DB_USER=your_username
   # DB_PASSWORD=your_password
   
   # For MySQL:
   # DB_TYPE=mysql
   # DB_HOST=localhost
   # DB_PORT=3306
   # DB_NAME=metrics
   # DB_USER=your_username
   # DB_PASSWORD=your_password
   ```

## Usage

### Starting the Application

1. **Activate your virtual environment** (if using one)

2. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to the URL shown in the terminal (typically `http://localhost:8501`)

### Using the Dashboard

#### 1. **Settings Page** (Start Here)

- Configure your database connection:
  - **SQLite** (default): Just specify the database file name
  - **PostgreSQL/MySQL**: Enter host, port, database name, username, and password
- Test the connection before proceeding
- View and configure industry benchmarks

#### 2. **Data Import Page**

**Excel Upload:**
- Upload an Excel file (`.xlsx` or `.xls`)
- Select the sheet to import
- The system will:
  - Auto-detect data format (wide or long)
  - Validate data structure
  - Normalize column names
  - Convert wide format to long format if needed
- Preview the data before saving
- Save validated data to the database

**Database Query:**
- Query existing data from the database
- Filter by teams, metrics, and date ranges
- View results in an interactive table

#### 3. **Dashboard Main Page**

- View summary statistics (total records, teams, metrics)
- Filter by teams and metrics
- Visualize data with:
  - Bar charts
  - Line charts
  - Time series charts
- View summary statistics tables
- Browse recent data

#### 4. **Team Comparison Page**

- Select 2+ teams to compare
- Select metrics to analyze
- View:
  - Comparison charts (grouped bars or multi-line)
  - Comparison tables with metrics as columns
  - Detailed difference analysis relative to a baseline team
  - Best/worst performers identification
  - Performance rankings

#### 5. **Benchmark Comparison Page**

- Compare your metrics against industry benchmarks
- Select teams and metrics with available benchmarks
- View:
  - Benchmark comparison results table
  - Visual charts comparing actual vs benchmark
  - Gap analysis with percentage differences
- Identify metrics that meet or exceed benchmarks

#### 6. **Mitigation Plans Page**

- **View Plans**: See all existing mitigation plans with progress tracking
- **Create Plan**: 
  - Select a team and metric
  - Set target value
  - Add description
  - Create action items
- **Manage Action Items**:
  - Add action items to plans
  - Set priority, assignee, and due dates
  - Update status (To Do, In Progress, Done, Blocked, Cancelled)
  - Track progress

## Data Format

### Excel File Format

The system supports two data formats:

**Long Format (Recommended):**
```
| team | metric | value | date | category | unit |
|------|--------|-------|------|----------|------|
| TeamA| Velocity| 25    | 2024-01-01 | velocity | points |
| TeamB| Velocity| 30    | 2024-01-01 | velocity | points |
```

**Wide Format:**
```
| team | date | Velocity | Quality | Efficiency |
|------|------|----------|---------|------------|
| TeamA| 2024-01-01 | 25 | 85 | 75 |
| TeamB| 2024-01-01 | 30 | 90 | 80 |
```

The system will auto-detect the format and can convert wide format to long format.

### Required Columns

- **team** (or similar): Team/project identifier
- **metric** (or similar): Metric name
- **value**: Numeric metric value

### Optional Columns

- **date**: Date/timestamp
- **category**: Metric category
- **unit**: Unit of measurement
- **project**: Project identifier
- **notes**: Additional notes

## Database Schema

The system uses SQLAlchemy ORM with the following schema:

- `id`: Unique identifier
- `team`: Team name (indexed)
- `metric`: Metric name (indexed)
- `value`: Metric value (float)
- `date`: Date/time (indexed, optional)
- `category`: Category (optional)
- `unit`: Unit of measurement (optional)
- `project`: Project name (indexed, optional)
- `notes`: Additional notes (optional)
- `created_at`: Record creation timestamp

## Benchmark Data

Industry benchmarks are stored in `benchmarks/industry_benchmarks.json`. The file contains benchmark values organized by category:

- **productivity**: Velocity, commits, lines of code
- **quality**: Defect rate, code coverage, bug resolution time
- **velocity**: Sprint completion, cycle time, lead time
- **efficiency**: Utilization rate, throughput, waste percentage
- **customer_satisfaction**: NPS, satisfaction score, response time

You can modify this file to add custom benchmarks for your organization.

## Technology Stack

- **Streamlit**: Web dashboard framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and visualizations
- **SQLAlchemy**: Database ORM and abstraction
- **openpyxl/xlrd**: Excel file reading
- **python-dotenv**: Environment variable management

## Configuration

### Database Configuration

Database settings can be configured via:
1. **Settings page** in the application (session-only)
2. **Environment variables** in `.env` file (persistent)
3. **Direct configuration** in code (for development)

### Chart Colors

Chart color schemes are defined in `config/settings.py`. You can customize colors by modifying the `CHART_COLORS` dictionary.

## Troubleshooting

### Database Connection Issues

- **SQLite**: Ensure the database file path is correct and writable
- **PostgreSQL/MySQL**: 
  - Verify host, port, and credentials
  - Check if the database exists
  - Ensure network connectivity and firewall rules

### Excel Import Issues

- Ensure Excel file is not open in another application
- Check file format (`.xlsx` or `.xls`)
- Verify required columns are present (team, metric, value)
- Check for empty rows/columns that might cause issues

### Data Validation Errors

- Ensure numeric values in the 'value' column
- Check for missing required columns
- Verify data types match expected formats
- Use the normalization feature to fix column names

## Development

### Adding New Chart Types

Add new chart generation methods to `components/charts.py` following the existing pattern.

### Adding New Comparison Methods

Extend `utils/comparisons.py` with new comparison functions.

### Custom Benchmarks

Edit `benchmarks/industry_benchmarks.json` to add organization-specific benchmarks.

## License

This project is open source and available for modification and distribution.

## Support

For issues, questions, or contributions, please refer to the project repository or documentation.

---

**Happy Metric Tracking! 📊**