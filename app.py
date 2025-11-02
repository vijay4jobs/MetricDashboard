"""Main Streamlit application for Metric Dashboard."""
import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime, date
import io

# Import modules
from config.settings import Settings, DatabaseConfig
from data.excel_loader import ExcelLoader
from data.database import DatabaseManager, User
from data.data_validator import DataValidator
from components.charts import ChartGenerator
from components.tables import TableGenerator
from components.filters import FilterComponent
from utils.comparisons import ComparisonEngine
from utils.metrics import MetricCalculator
from mitigation.mitigation_db import MitigationDB
from mitigation.action_items import Priority, Status

# Page configuration
settings = Settings()
st.set_page_config(**settings.PAGE_CONFIG)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = None
if 'current_data' not in st.session_state:
    st.session_state.current_data = pd.DataFrame()
if 'mitigation_db' not in st.session_state:
    st.session_state.mitigation_db = MitigationDB()
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Dashboard"


def load_benchmarks() -> dict:
    """Load industry benchmarks from JSON file."""
    benchmarks_path = Path("benchmarks/industry_benchmarks.json")
    if benchmarks_path.exists():
        with open(benchmarks_path, 'r') as f:
            return json.load(f)
    return {}


def get_benchmark_values(benchmarks: dict) -> dict:
    """Extract benchmark values as flat dictionary."""
    flat_benchmarks = {}
    for category, metrics in benchmarks.items():
        for metric_name, metric_data in metrics.items():
            flat_benchmarks[metric_name] = metric_data.get('value', 0)
    return flat_benchmarks


def init_database(config: DatabaseConfig):
    """Initialize database connection."""
    try:
        db_manager = DatabaseManager(config)
        if db_manager.test_connection():
            st.session_state.db_manager = db_manager
            return True
        else:
            st.error("Database connection test failed")
            return False
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")
        return False


def show_login_page():
    """Display login page with login and signup options."""
    st.title("🔐 Login to Metric Dashboard")
    st.markdown("---")
    
    # Create tabs for Login and Signup
    login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with login_tab:
        st.markdown("### Enter Your Credentials")
        
        # Center the form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username", key="login_username")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
                login_button = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
                
                if login_button:
                    if not username or not password:
                        st.error("⚠️ Please enter both username and password")
                    else:
                        # Try to authenticate with default SQLite database first
                        try:
                            from config.settings import DatabaseConfig
                            config = DatabaseConfig(db_type="sqlite", database="metrics.db")
                            db_manager = DatabaseManager(config)
                            
                            # Ensure admin user exists with correct privileges
                            ensure_admin_user(db_manager)
                            
                            user_info = db_manager.authenticate_user(username, password)
                            if user_info:
                                st.session_state.authenticated = True
                                st.session_state.username = user_info['username']
                                st.session_state.is_admin = user_info.get('is_admin', False)
                                st.session_state.db_manager = db_manager
                                st.success(f"✅ Welcome back, {user_info['username']}!")
                                st.rerun()
                            else:
                                st.error("❌ Invalid username or password")
                        except Exception as e:
                            st.error(f"❌ Login failed: {str(e)}")
                            st.info("💡 Make sure the database is initialized. You can sign up in the Sign Up tab.")
        
        st.markdown("---")
        st.info("ℹ️ Don't have an account? Switch to the **Sign Up** tab to create one.")
    
    with signup_tab:
        st.markdown("### Create New Account")
        st.info("Fill in the details below to create a new account")
        
        # Center the form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("signup_form"):
                new_username = st.text_input("Username", placeholder="Choose a username", key="signup_username")
                new_password = st.text_input("Password", type="password", placeholder="Choose a password (min 6 characters)", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="signup_confirm_password")
                new_email = st.text_input("Email (Optional)", placeholder="your.email@example.com", key="signup_email")
                
                signup_button = st.form_submit_button("📝 Sign Up", type="primary", use_container_width=True)
                
                if signup_button:
                    # Validation
                    if not new_username or not new_password:
                        st.error("⚠️ Username and password are required")
                    elif len(new_password) < 6:
                        st.error("⚠️ Password must be at least 6 characters long")
                    elif new_password != confirm_password:
                        st.error("⚠️ Passwords do not match")
                    else:
                        try:
                            from config.settings import DatabaseConfig
                            config = DatabaseConfig(db_type="sqlite", database="metrics.db")
                            db_manager = DatabaseManager(config)
                            
                            # Ensure admin user exists with correct privileges
                            ensure_admin_user(db_manager)
                            
                            # Create new user (non-admin by default)
                            if db_manager.create_user(new_username, new_password, new_email if new_email else None, is_admin=False):
                                st.success(f"✅ Account created successfully! You can now login with username: {new_username}")
                                st.info("ℹ️ Switch to the **Login** tab to sign in")
                            else:
                                st.error("❌ Signup failed. Username may already exist. Please try a different username.")
                        except Exception as e:
                            st.error(f"❌ Signup failed: {str(e)}")
                            st.info("💡 Make sure the database is initialized. Run 'python setup_database.py' to initialize.")
        
        st.markdown("---")
        st.info("ℹ️ Already have an account? Switch to the **Login** tab to sign in.")
    
    st.markdown("---")
    st.caption("Default database: metrics.db (SQLite)")


def ensure_admin_user(db_manager):
    """Ensure admin user exists with correct privileges. Fix if needed."""
    try:
        # First, ensure is_admin column exists
        try:
            from sqlalchemy import text
            session = db_manager.get_session()
            try:
                # Check if column exists (SQLite specific)
                result = session.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'is_admin' not in columns:
                    # Add is_admin column
                    session.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                    session.commit()
            except Exception:
                pass  # Column might already exist or table might not exist
            finally:
                session.close()
        except Exception:
            pass
        
        # Now check/create admin user
        session = db_manager.get_session()
        try:
            from data.database import User
            admin_user = session.query(User).filter(User.username == "admin").first()
            
            if admin_user:
                # Check if admin user has correct password (verify)
                if db_manager.verify_password("admin123", admin_user.password_hash):
                    # Update is_admin flag if not set
                    if not admin_user.is_admin:
                        admin_user.is_admin = True
                        session.commit()
                else:
                    # If password doesn't match, reset it
                    admin_user.password_hash = db_manager.hash_password("admin123")
                    admin_user.is_admin = True
                    session.commit()
            else:
                # Create admin user if it doesn't exist
                db_manager.create_user("admin", "admin123", None, is_admin=True)
        except Exception as e:
            # Log error but don't interrupt login flow
            import traceback
            traceback.print_exc()
        finally:
            session.close()
    except Exception:
        # Silently fail - don't show error on login page
        pass


def show_main_app():
    """Display main application (only if authenticated)."""
    # Sidebar with app info, navigation, and logout
    with st.sidebar:
        st.title("📊 Metric Dashboard")
        st.markdown("---")
        
        # User info
        if st.session_state.username:
            st.success(f"👤 Logged in as: **{st.session_state.username}**")
        
        # Quick database status
        if st.session_state.db_manager:
            db = st.session_state.db_manager
            try:
                summary = db.get_summary_stats()
                st.success("✅ Database Connected")
                # st.metric("Records", f"{summary.get('total_records', 0):,}")
                # st.metric("Teams", summary.get('teams', 0))
                # st.metric("Metrics", summary.get('metrics', 0))
            except:
                st.warning("⚠️ Database Error")
        else:
            st.warning("⚠️ Database Not Connected")
            st.info("Go to Settings to configure database")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.session_state.db_manager = None
            st.rerun()
        
        st.markdown("---")
        st.caption("Version 1.0 | Metric Dashboard")


# Check authentication
if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# Show main app
show_main_app()

# Main navigation using tabs - conditionally show Settings based on admin status
tabs_list = [
    "📊 Dashboard",
    "📥 Data Query", 
    "⚖️ Team Comparison",
    "🎯 Benchmark Comparison",
    "🔧 Mitigation Plans"
]

# Only add Settings tab for admin users
if st.session_state.is_admin:
    tabs_list.append("⚙️ Settings")

# Create tabs
tabs = st.tabs(tabs_list)

# Map tabs to variables
tab1 = tabs[0]  # Dashboard
tab2 = tabs[1]  # Data Query
tab3 = tabs[2]  # Team Comparison
tab4 = tabs[3]  # Benchmark Comparison
tab5 = tabs[4]  # Mitigation Plans
tab6 = tabs[5] if st.session_state.is_admin else None  # Settings (only for admin)

# ==================== DASHBOARD TAB ====================
with tab1:
    st.title("📊 Metric Dashboard Overview")
    st.markdown("---")
    
    # Initialize database if available
    if st.session_state.db_manager is None:
        st.info("ℹ️ Please configure database connection in Settings tab first.")
    else:
        db = st.session_state.db_manager
        
        # Summary cards with better styling
        st.subheader("📈 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        summary = db.get_summary_stats()
        
        with col1:
            st.metric("Total Records", f"{summary.get('total_records', 0):,}")
        with col2:
            st.metric("Teams", summary.get('teams', 0))
        with col3:
            st.metric("Metrics", summary.get('metrics', 0))
        with col4:
            last_updated = summary.get('last_updated', None)
            if last_updated:
                st.metric("Last Updated", last_updated.strftime("%Y-%m-%d"))
        
        st.markdown("---")
        
        # Filters section
        st.subheader("🔍 Filters & Visualization")
        col1, col2 = st.columns(2)
        
        teams = db.get_teams()
        metrics = db.get_metrics()
        
        with col1:
            selected_teams = st.multiselect(
                "Select Teams", 
                teams, 
                default=teams[:min(5, len(teams))] if teams else [],
                help="Select one or more teams to visualize"
            )
        with col2:
            selected_metrics = st.multiselect(
                "Select Metrics", 
                metrics, 
                default=metrics[:min(5, len(metrics))] if metrics else [],
                help="Select one or more metrics to visualize"
            )
        
        if selected_teams and selected_metrics:
            # Load data
            data = db.query_metrics(teams=selected_teams, metrics=selected_metrics)
            
            if not data.empty:
                st.session_state.current_data = data
                
                # Chart selection and visualization
                st.markdown("### 📊 Charts")
                
                chart_type = st.selectbox(
                    "Chart Type", 
                    ["Bar Chart", "Line Chart", "Time Series"],
                    help="Select the type of visualization"
                )
                
                chart_gen = ChartGenerator()
                
                if chart_type == "Bar Chart":
                    fig = chart_gen.team_comparison_chart(data, selected_teams, selected_metrics, "bar")
                    st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                elif chart_type == "Line Chart":
                    fig = chart_gen.team_comparison_chart(data, selected_teams, selected_metrics, "line")
                    st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                elif chart_type == "Time Series":
                    metric_for_ts = st.selectbox("Select Metric for Time Series", selected_metrics)
                    if metric_for_ts:
                        fig = chart_gen.time_series_chart(data, metric_for_ts, selected_teams)
                        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                
                st.markdown("---")
                
                # Summary statistics table
                st.markdown("### 📋 Summary Statistics by Team")
                table_gen = TableGenerator()
                summary_table = table_gen.summary_table(data, 'team')
                table_gen.display_styled_table(summary_table, use_container_width=True)
                
                st.markdown("---")
                
                # Recent data table
                st.markdown("### 📄 Recent Data")
                table_gen = TableGenerator()
                table_gen.display_styled_table(data.tail(100), use_container_width=True, height=400)
            else:
                st.warning("⚠️ No data found for selected filters.")
        else:
            st.info("ℹ️ Please select at least one team and one metric to view visualizations.")


# ==================== DATA IMPORT TAB ====================
with tab2:
    st.title("📥 Data Query")
    st.markdown("---")
    
    # sub_tab1, sub_tab2 = st.tabs(["📤 Excel Upload", "🔍 Database Query"])
    sub_tabs = st.tabs(["🔍 Database Query"])
    sub_tab1 = sub_tabs[0]
    
    # Excel Upload sub-tab is commented out and not shown.
    # If you uncomment and need to fix, see below for correct tab usage!

    with sub_tab1:
        st.subheader("Database Query")
        
        if st.session_state.db_manager:
            st.success("✅ Database connected")
            
            db = st.session_state.db_manager
            
            # Query options
            col1, col2 = st.columns(2)
            
            with col1:
                teams = db.get_teams()
                selected_teams = st.multiselect("Filter by Teams", teams)
            with col2:
                metrics = db.get_metrics()
                selected_metrics = st.multiselect("Filter by Metrics", metrics)
            
            col3, col4 = st.columns(2)
            with col3:
                start_date = st.date_input("Start Date", value=None)
            with col4:
                end_date = st.date_input("End Date", value=None)
            
            if st.button("🔍 Query Data", type="primary"):
                # Make sure datetime is imported at the top of your file!
                from datetime import datetime

                data = db.query_metrics(
                    teams=selected_teams if selected_teams else None,
                    metrics=selected_metrics if selected_metrics else None,
                    start_date=datetime.combine(start_date, datetime.min.time()) if start_date else None,
                    end_date=datetime.combine(end_date, datetime.max.time()) if end_date else None
                )
                
                if not data.empty:
                    st.session_state.current_data = data
                    st.success(f"✅ Loaded {len(data)} records")
                    table_gen = TableGenerator()
                    table_gen.display_styled_table(data, use_container_width=True, height=500)
                else:
                    st.info("ℹ️ No data found for selected filters.")
        else:
            st.warning("⚠️ Please configure database connection in Settings first.")

# ==================== TEAM COMPARISON TAB ====================
with tab3:
    st.title("⚖️ Team Comparison")
    st.markdown("---")
    
    if st.session_state.db_manager:
        db = st.session_state.db_manager
        
        # Filters
        teams = db.get_teams()
        metrics = db.get_metrics()
        
        if teams and metrics:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_teams = st.multiselect(
                    "Select Teams to Compare", 
                    teams, 
                    default=teams[:min(2, len(teams))] if len(teams) >= 2 else teams,
                    help="Select at least 2 teams"
                )
            with col2:
                selected_metrics = st.multiselect(
                    "Select Metrics", 
                    metrics, 
                    default=metrics[:min(3, len(metrics))] if len(metrics) >= 3 else metrics,
                    help="Select one or more metrics"
                )
            
            if len(selected_teams) >= 2 and selected_metrics:
                # Load data
                data = db.query_metrics(teams=selected_teams, metrics=selected_metrics)
                
                if not data.empty:
                    # Comparison chart
                    st.markdown("### 📊 Comparison Chart")
                    chart_gen = ChartGenerator()
                    chart_type = st.radio("Chart Type", ["Bar", "Line"], horizontal=True)
                    fig = chart_gen.team_comparison_chart(data, selected_teams, selected_metrics, chart_type.lower())
                    st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                    
                    st.markdown("---")
                    
                    # Comparison table
                    st.markdown("### 📋 Comparison Table")
                    table_gen = TableGenerator()
                    comparison_table = table_gen.comparison_table(data, selected_teams, selected_metrics)
                    # Make table responsive - height based on number of teams
                    responsive_height = max(200, len(selected_teams) * 50 + 100)
                    table_gen.display_styled_table(comparison_table)
                    
                    st.markdown("---")
                    
                    # Detailed analysis
                    st.markdown("### 📊 Detailed Analysis")
                    comparison_engine = ComparisonEngine()
                    
                    baseline_team = st.selectbox("Select Baseline Team", selected_teams)
                    compare_teams = [t for t in selected_teams if t != baseline_team]
                    
                    if compare_teams:
                        st.markdown("#### 📉 Difference Analysis")
                        differences = comparison_engine.calculate_differences(
                            data, baseline_team, compare_teams, selected_metrics
                        )
                        table_gen.display_styled_table(differences)
                    
                    st.markdown("---")
                    
                    # Best/Worst performers
                    st.markdown("### 🏆 Best and Worst Performers")
                    best_worst = comparison_engine.identify_best_worst(data, selected_metrics)
                    table_gen.display_styled_table(best_worst)
                    
                    st.markdown("---")
                    
                    # Performance ranking
                    st.markdown("### 🎯 Performance Ranking")
                    rankings = comparison_engine.performance_ranking(data, selected_metrics)
                    table_gen.display_styled_table(rankings)
                else:
                    st.info("ℹ️ No data found for selected filters.")
            else:
                st.warning("⚠️ Please select at least 2 teams and at least one metric.")
        else:
            st.info("ℹ️ No teams or metrics available. Please import data first.")
    else:
        st.warning("⚠️ Please configure database connection in Settings first.")


# ==================== BENCHMARK COMPARISON TAB ====================
with tab4:
    st.title("🎯 Benchmark Comparison")
    st.markdown("---")
    
    benchmarks_data = load_benchmarks()
    flat_benchmarks = get_benchmark_values(benchmarks_data)
    
    if st.session_state.db_manager and flat_benchmarks:
        db = st.session_state.db_manager
        
        # Filters
        teams = db.get_teams()
        available_metrics = db.get_metrics()
        benchmark_metrics = [m for m in available_metrics if m in flat_benchmarks]
        
        if benchmark_metrics:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_teams = st.multiselect("Select Teams", teams, default=teams[:min(5, len(teams))] if teams else [])
            with col2:
                selected_metrics = st.multiselect(
                    "Select Metrics (with benchmarks)",
                    benchmark_metrics,
                    default=benchmark_metrics[:min(3, len(benchmark_metrics))] if len(benchmark_metrics) >= 3 else benchmark_metrics
                )
            
            if selected_teams and selected_metrics:
                # Load data
                data = db.query_metrics(teams=selected_teams, metrics=selected_metrics)
                
                if not data.empty:
                    # Benchmark comparison
                    comparison_engine = ComparisonEngine()
                    table_gen = TableGenerator()
                    selected_benchmarks = {m: flat_benchmarks[m] for m in selected_metrics}
                    
                    # Use TableGenerator method which returns properly formatted DataFrame
                    comparison_results = table_gen.benchmark_comparison_table(
                        data, selected_benchmarks, selected_metrics
                    )
                    
                    st.markdown("### 📋 Benchmark Comparison Results")
                    
                    # Display styled table
                    table_gen.display_styled_table(comparison_results)
                    
                    st.markdown("---")
                    
                    # # Benchmark charts
                    # st.markdown("### 📊 Visualizations")
                    # chart_gen = ChartGenerator()
                    # 
                    # for metric in selected_metrics[:3]:
                    #     st.markdown(f"#### {metric}")
                    #     fig = chart_gen.benchmark_comparison_chart(
                    #         data, selected_benchmarks, metric,
                    #         selected_teams[0] if selected_teams else None
                    #     )
                    #     st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                    # 
                    # st.markdown("---")
                    # 
                    # # Gap analysis - use comparison_results with capitalized column names
                    # st.markdown("### 📊 Gap Analysis")
                    # for _, row in comparison_results.iterrows():
                    #     col1, col2, col3, col4 = st.columns(4)
                    #     with col1:
                    #         st.metric("Metric", row['Metric'])
                    #     with col2:
                    #         st.metric("Actual", f"{row['Actual (Avg)']:.2f}")
                    #     with col3:
                    #         st.metric("Benchmark", f"{row['Benchmark']:.2f}")
                    #     with col4:
                    #         # Gap % is stored as string, need to parse it
                    #         gap_pct_str = row['Gap %']
                    #         gap_pct = float(gap_pct_str.replace('%', ''))
                    #         st.metric("Gap", gap_pct_str, 
                    #                  delta="Above" if gap_pct > 0 else "Below")
                    #     st.markdown("---")
                else:
                    st.info("ℹ️ No data found for selected filters.")
            else:
                st.info("ℹ️ Please select teams and metrics with benchmarks.")
        else:
            st.warning("⚠️ No metrics with benchmark data found. Please check benchmark configuration.")
    else:
        st.warning("⚠️ Please configure database connection and load benchmarks.")


# ==================== MITIGATION PLANS TAB ====================
with tab5:
    st.title("🔧 Mitigation Plans & Action Items")
    st.markdown("---")
    
    mitigation_db = st.session_state.mitigation_db
    
    plan_tab1, plan_tab2, plan_tab3 = st.tabs(["📋 View Plans", "➕ Create Plan", "✅ Action Items"])
    
    with plan_tab1:
        st.subheader("Existing Mitigation Plans")
        
        plans = mitigation_db.get_all_plans()
        
        if plans:
            for plan in plans:
                with st.expander(f"📊 {plan.metric} - {plan.team}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Value", f"{plan.current_value:.2f}")
                    with col2:
                        st.metric("Target Value", f"{plan.target_value:.2f}")
                    
                    st.write(f"**Description:** {plan.description}")
                    
                    progress = plan.get_progress()
                    st.progress(progress['percentage'] / 100)
                    st.caption(f"Progress: {progress['completed']}/{progress['total']} action items completed")
                    
                    # Action items
                    if plan.action_items:
                        st.markdown("#### Action Items")
                        for item in plan.action_items:
                            st.write(f"- **{item.title}** ({item.status.value}) - {item.description}")
                    
                    if st.button(f"🗑️ Delete Plan", key=f"delete_{plan.id}"):
                        mitigation_db.delete_plan(plan.id)
                        st.rerun()
        else:
            st.info("ℹ️ No mitigation plans created yet.")
    
    with plan_tab2:
        st.subheader("Create New Mitigation Plan")
        
        if st.session_state.db_manager:
            db = st.session_state.db_manager
            
            teams = db.get_teams()
            metrics = db.get_metrics()
            
            if teams and metrics:
                selected_team = st.selectbox("Select Team", teams)
                selected_metric = st.selectbox("Select Metric", metrics)
                
                # Get current value
                if selected_team and selected_metric:
                    data = db.query_metrics(teams=[selected_team], metrics=[selected_metric])
                    current_value = data['value'].mean() if not data.empty else 0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Value", f"{current_value:.2f}")
                    with col2:
                        target_value = st.number_input("Target Value", value=float(current_value * 1.1))
                    
                    description = st.text_area("Plan Description")
                    
                    if st.button("✅ Create Mitigation Plan", type="primary"):
                        plan = mitigation_db.create_plan(
                            metric=selected_metric,
                            team=selected_team,
                            description=description,
                            current_value=current_value,
                            target_value=target_value
                        )
                        st.success(f"✅ Mitigation plan created: {plan.id}")
                        st.rerun()
            else:
                st.info("ℹ️ No teams or metrics available. Please import data first.")
        else:
            st.warning("⚠️ Please configure database connection first.")
    
    with plan_tab3:
        st.subheader("Manage Action Items")
        
        plans = mitigation_db.get_all_plans()
        
        if plans:
            selected_plan_id = st.selectbox(
                "Select Mitigation Plan",
                options=[p.id for p in plans],
                format_func=lambda x: f"{next(p for p in plans if p.id == x).metric} - {next(p for p in plans if p.id == x).team}"
            )
            
            selected_plan = next(p for p in plans if p.id == selected_plan_id)
            
            st.write(f"**Plan:** {selected_plan.metric} - {selected_plan.team}")
            
            # Add action item
            st.markdown("#### Add Action Item")
            title = st.text_input("Title")
            desc = st.text_area("Description")
            priority = st.selectbox("Priority", [p.value for p in Priority])
            assigned = st.text_input("Assigned To")
            due = st.date_input("Due Date")
            
            if st.button("➕ Add Action Item", type="primary"):
                mitigation_db.add_action_item(
                    selected_plan_id,
                    title=title,
                    description=desc,
                    priority=Priority(priority),
                    assigned_to=assigned,
                    due_date=datetime.combine(due, datetime.min.time()) if due else None
                )
                st.success("✅ Action item added!")
                st.rerun()
            
            # List action items
            st.markdown("---")
            st.markdown("#### Action Items")
            for item in selected_plan.action_items:
                with st.expander(f"📌 {item.title} - {item.status.value}"):
                    st.write(f"**Description:** {item.description}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Priority:** {item.priority.value}")
                    with col2:
                        st.write(f"**Assigned To:** {item.assigned_to}")
                    with col3:
                        st.write(f"**Due Date:** {item.due_date.strftime('%Y-%m-%d') if item.due_date else 'N/A'}")
                    
                    new_status = st.selectbox(
                        "Update Status",
                        [s.value for s in Status],
                        index=[s.value for s in Status].index(item.status.value),
                        key=f"status_{item.id}"
                    )
                    
                    if st.button(f"🔄 Update", key=f"update_{item.id}"):
                        mitigation_db.update_action_item(
                            selected_plan_id,
                            item.id,
                            status=Status(new_status)
                        )
                        st.rerun()
        else:
            st.info("ℹ️ Create a mitigation plan first.")


# ==================== SETTINGS TAB ====================
if tab6 is not None:  # Only show if user is admin
    with tab6:
        st.title("⚙️ Settings")
        st.markdown("---")
        
        st.subheader("Database Configuration")
        
        db_type = st.selectbox("Database Type", ["sqlite", "postgresql", "mysql"])
        
        if db_type == "sqlite":
            database = st.text_input("Database File", value="metrics.db")
            config = DatabaseConfig(db_type=db_type, database=database)
        else:
            col1, col2 = st.columns(2)
            with col1:
                host = st.text_input("Host", value="localhost")
                port = st.number_input("Port", value=5432 if db_type == "postgresql" else 3306, min_value=1, max_value=65535)
            with col2:
                database = st.text_input("Database Name", value="metrics")
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            config = DatabaseConfig(
                db_type=db_type,
                host=host,
                port=int(port),
                database=database,
                username=username,
                password=password
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Test Connection"):
                if init_database(config):
                    st.success("✅ Database connection successful!")
                else:
                    st.error("❌ Database connection failed!")
        
        with col2:
            if st.button("💾 Save and Connect", type="primary"):
                if init_database(config):
                    st.success("✅ Database connected and saved!")
                    st.info("Database configuration is saved in session. For permanent storage, use environment variables.")
                else:
                    st.error("❌ Failed to connect to database!")
        
        st.markdown("---")
        
        # User Management Section
        st.subheader("👥 User Management")
        st.info("Create new user accounts for dashboard access")
        
        user_tab1, user_tab2 = st.tabs(["Create User", "View Users"])
        
        with user_tab1:
            with st.form("create_user_form"):
                new_username = st.text_input("Username", placeholder="Enter username")
                new_password = st.text_input("Password", type="password", placeholder="Enter password")
                new_email = st.text_input("Email (Optional)", placeholder="user@example.com")
                
                # Only admin can grant admin privileges
                is_admin_new = False
                if st.session_state.is_admin:
                    is_admin_new = st.checkbox("Grant Admin Privileges", value=False, key="new_user_admin")
                
                create_user_btn = st.form_submit_button("➕ Create User", type="primary", use_container_width=True)
                
                if create_user_btn:
                    if not new_username or not new_password:
                        st.error("⚠️ Username and password are required")
                    elif len(new_password) < 6:
                        st.error("⚠️ Password must be at least 6 characters long")
                    else:
                        if st.session_state.db_manager:
                            if st.session_state.db_manager.create_user(new_username, new_password, new_email if new_email else None, is_admin=is_admin_new):
                                st.success(f"✅ User '{new_username}' created successfully!")
                            else:
                                st.error("❌ User creation failed. Username may already exist.")
                        else:
                            st.warning("⚠️ Please connect to database first")
        
        with user_tab2:
            if st.session_state.db_manager:
                try:
                    users = st.session_state.db_manager.get_all_users()
                    if users:
                        user_data = []
                        for user in users:
                            user_data.append({
                                'Username': user['username'],
                                'Email': user['email'] or 'N/A',
                                'Admin': 'Yes' if user.get('is_admin', False) else 'No',
                                'Active': 'Yes' if user['is_active'] else 'No',
                                'Created': user['created_at'].strftime('%Y-%m-%d') if user['created_at'] else 'N/A',
                                'Last Login': user['last_login'].strftime('%Y-%m-%d %H:%M') if user['last_login'] else 'Never'
                            })
                        user_df = pd.DataFrame(user_data)
                        table_gen = TableGenerator()
                        table_gen.display_styled_table(user_df, use_container_width=True)
                    else:
                        st.info("ℹ️ No users found. Create a user account first.")
                except Exception as e:
                    st.error(f"❌ Error loading users: {str(e)}")
            else:
                st.warning("⚠️ Please connect to database first")
        
        st.markdown("---")
        
        # Database initialization with dummy data
        st.subheader("Initialize Database with Dummy Data")
        st.info("This will create sample metric data in the database (SQLite only)")
        
        if st.button("🚀 Initialize Database (SQLite Only)", type="primary"):
            if db_type != "sqlite":
                st.warning("⚠️ Dummy data initialization is only available for SQLite databases.")
            else:
                try:
                    from setup_database import create_dummy_data
                    from data.database import MetricData
                    
                    # Initialize database connection
                    if not st.session_state.db_manager:
                        if not init_database(config):
                            st.error("Failed to connect to database")
                            st.stop()
                    
                    db = st.session_state.db_manager
                    
                    # Check if data exists
                    existing_teams = db.get_teams()
                    if existing_teams:
                        st.info(f"Database already contains {len(existing_teams)} teams. New data will be added to existing data.")
                    
                    # Generate and insert dummy data (6 months = 26 weeks)
                    with st.spinner("Generating and inserting dummy data..."):
                        dummy_data = create_dummy_data(num_weeks=26)
                        
                        # Create default admin user if no users exist
                        try:
                            users = db.get_all_users()
                            if not users:
                                from setup_database import create_default_user
                                create_default_user(db, username="admin", password="admin123")
                                st.success("✅ Default admin user created! Username: admin, Password: admin123")
                        except:
                            pass  # User creation is optional
                        
                        session = db.get_session()
                        try:
                            inserted = 0
                            total = len(dummy_data)
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i, data in enumerate(dummy_data):
                                metric_record = MetricData(**data)
                                session.add(metric_record)
                                inserted += 1
                                
                                # Commit in batches and update progress
                                if inserted % 50 == 0:
                                    session.commit()
                                    progress = min((i + 1) / total, 1.0)
                                    progress_bar.progress(progress)
                                    status_text.text(f"Inserted {inserted}/{total} records...")
                            
                            session.commit()
                            progress_bar.progress(1.0)
                            status_text.text(f"Completed! Inserted {inserted} records.")
                            
                            # Refresh database manager
                            st.session_state.db_manager = DatabaseManager(config)
                            db = st.session_state.db_manager
                            
                            st.success(f"✅ Successfully inserted {inserted} dummy records!")
                            
                            # Show summary
                            summary = db.get_summary_stats()
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Records", summary['total_records'])
                            with col2:
                                st.metric("Teams", summary['teams'])
                            with col3:
                                st.metric("Metrics", summary['metrics'])
                            
                            # Clear progress elements
                            progress_bar.empty()
                            status_text.empty()
                            
                        except Exception as e:
                            session.rollback()
                            st.error(f"Error inserting data: {str(e)}")
                        finally:
                            session.close()
                            
                except ImportError as e:
                    st.error(f"Could not import setup_database module: {str(e)}. Please ensure setup_database.py exists.")
                except Exception as e:
                    st.error(f"Error initializing database: {str(e)}")
        
        st.markdown("---")
        
        st.subheader("Benchmark Configuration")
        
        benchmarks_data = load_benchmarks()
        
        if benchmarks_data:
            st.info(f"Loaded {sum(len(v) for v in benchmarks_data.values())} benchmark metrics")
            
            category = st.selectbox("Category", list(benchmarks_data.keys()), key="benchmark_category")
            
            if category:
                st.write(f"**Metrics in {category}:**")
                for metric_name, metric_data in benchmarks_data[category].items():
                    st.write(f"- {metric_name}: {metric_data.get('value', 'N/A')} {metric_data.get('unit', '')}")
        else:
            st.warning("No benchmark data found. Please check benchmarks/industry_benchmarks.json")


if __name__ == "__main__":
    pass
