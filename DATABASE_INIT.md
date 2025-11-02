# Database Initialization Guide

This guide explains how to initialize the database for the Metric Dashboard application.

## Method 1: Command Line Script (Recommended for First-Time Setup)

### Basic Initialization
Run the setup script from the command line:

```bash
python setup_database.py
```

This will:
- Create the database file `metrics.db` (if it doesn't exist)
- Create all required tables (metrics, users)
- Insert dummy metric data (26 weeks of data)
- Create a default admin user with credentials:
  - **Username**: `admin`
  - **Password**: `admin123`

### Clear Existing Data and Reinitialize
If you want to clear all existing data and start fresh:

```bash
python setup_database.py --clear
```

⚠️ **Warning**: This will delete all existing metric data!

### What Gets Created

1. **Database Tables**:
   - `metrics` - Stores metric data (team, metric, value, date, etc.)
   - `users` - Stores user authentication credentials

2. **Sample Data**:
   - 5 teams (Alpha Team, Beta Team, Gamma Team, Delta Team, Epsilon Team)
   - 12 different metrics (Velocity Points Per Sprint, Code Commits Per Week, etc.)
   - ~26 weeks of historical data
   - 4 sample projects

3. **Default User Account**:
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ **Change this password after first login!**

## Method 2: Using the Dashboard UI

### Steps:

1. **Start the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

2. **Login** (if database doesn't exist, you may need to create it first via Method 1)

3. **Navigate to Settings Tab**:
   - Click on the "⚙️ Settings" tab in the navigation

4. **Configure Database** (if needed):
   - Select "sqlite" as Database Type
   - Enter "metrics.db" as Database File
   - Click "💾 Save and Connect"

5. **Initialize Database**:
   - Scroll to "Initialize Database with Dummy Data" section
   - Click "🚀 Initialize Database (SQLite Only)"
   - Wait for the process to complete

6. **View Default Credentials**:
   - The success message will show the default admin credentials if a user was created

## What Happens During Initialization

1. **Connection**: Establishes connection to SQLite database
2. **Table Creation**: Creates `metrics` and `users` tables (if they don't exist)
3. **Data Generation**: Generates ~1,500+ dummy data points
4. **Data Insertion**: Inserts all data into the database
5. **User Creation**: Creates default admin user (if no users exist)
6. **Summary Display**: Shows summary of created data

## Sample Output

```
Initializing database...
✓ Database connection established
Generating dummy data...
✓ Generated 1560 data points
Inserting data into database...
  Inserted 100 records...
  Inserted 200 records...
  ...
✓ Successfully inserted 1560 records

==================================================
Database Summary:
==================================================
Total Records: 1560
Teams: 5
Metrics: 12

Teams: Alpha Team, Beta Team, Gamma Team, Delta Team, Epsilon Team

Metrics: Velocity Points Per Sprint, Code Commits Per Week, Defect Rate... (12 total)

Creating default admin user...
✅ Default user created successfully!
   Username: admin
   Password: admin123
   ⚠️  Please change the default password after first login!

✓ Database initialization complete!
Database file: metrics.db
```

## Troubleshooting

### Error: "Failed to connect to database"
- Make sure you have write permissions in the current directory
- Check if the database file is locked by another process

### Error: "User already exists"
- This is normal if you've already created the admin user
- You can create additional users from the Settings > User Management tab

### Error: "Table already exists"
- This is normal if the database was previously initialized
- Existing data will be preserved unless you use `--clear` flag

## After Initialization

1. **Login** to the dashboard using:
   - Username: `admin`
   - Password: `admin123`

2. **Change Password** (Recommended):
   - Go to Settings > User Management
   - Create a new user or keep using admin (but change password by creating a new admin user)

3. **Explore the Dashboard**:
   - View metrics in Dashboard tab
   - Compare teams in Team Comparison tab
   - Check benchmarks in Benchmark Comparison tab

## Database Location

By default, the database file `metrics.db` is created in the project root directory:
```
MetricDashboard/
├── metrics.db  ← Database file
├── app.py
├── setup_database.py
└── ...
```

You can change the database location by modifying the `database_path` parameter in `setup_database.py` or using the Settings UI.
