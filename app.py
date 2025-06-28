import streamlit as st
import pandas as pd
import time
from databricks import sdk
from databricks.sdk.core import Config
from sqlalchemy import create_engine, event, text

# Databricks config.
app_config = Config()
workspace_client = sdk.WorkspaceClient()

# PostgreSQL config to connect to your database.
postgres_username = app_config.client_id
postgres_host = "instance-95946f75-1682-4d20-b279-0e9fcb954310.database.cloud.databricks.com"
postgres_port = 5432
postgres_database = "ssylvia_postgres_database"

# sqlalchemy setup + function to refresh the OAuth token that gets used as the PostgreSQL password every 15 minutes.
postgres_pool = create_engine(f"postgresql+psycopg://{postgres_username}:@{postgres_host}:{postgres_port}/{postgres_database}")
postgres_password = None
last_password_refresh = time.time()

@event.listens_for(postgres_pool, "do_connect")
def provide_token(dialect, conn_rec, cargs, cparams):
    global postgres_password, last_password_refresh
    if postgres_password is None or time.time() - last_password_refresh > 900:
        print("Refreshing PostgreSQL OAuth token")
        postgres_password = workspace_client.config.oauth_token().access_token
        last_password_refresh = time.time()
    cparams["password"] = postgres_password

# Page configuration
st.set_page_config(
    page_title="Campaign Performance Data Viewer",
    page_icon="📊",
    layout="wide"
)

def get_campaign_data(limit=100):
    """Fetch data from the synced table using SQLAlchemy engine"""
    try:
        with postgres_pool.connect() as conn:
            query = f"""
            SELECT * FROM adtech_bootcamp.campaign_performance_synced_from_copy 
            LIMIT {limit}
            """
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def get_table_info():
    """Get information about the synced table using SQLAlchemy engine"""
    try:
        with postgres_pool.connect() as conn:
            query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'adtech_bootcamp' AND table_name = 'campaign_performance_synced_from_copy'
            ORDER BY ordinal_position
            """
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching table info: {str(e)}")
        return None

def get_row_count():
    """Get the total number of rows in the synced table using SQLAlchemy engine"""
    try:
        with postgres_pool.connect() as connection:
            query = "SELECT COUNT(*) as total_rows FROM adtech_bootcamp.campaign_performance_synced_from_copy"
            result = connection.execute(text(query)).scalar()
        return result
    except Exception as e:
        st.error(f"Error getting row count: {str(e)}")
        return None

def get_summary_stats(df):
    """Calculate summary statistics for numeric columns"""
    if df is None or df.empty:
        return None
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    summary = df[numeric_cols].describe()
    return summary

def main():
    # Header
    st.title("📊 Campaign Performance Data Viewer")
    st.markdown("This app displays data from the `adtech_bootcamp.campaign_performance_synced_from_copy` table in your PostgreSQL database.")
    
    # Sidebar for controls
    st.sidebar.header("🎛️ Controls")
    
    # Data limit selector
    data_limit = st.sidebar.slider(
        "Number of rows to display",
        min_value=10,
        max_value=1000,
        value=100,
        step=10
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📈 Data Overview")
        
        # Get row count
        row_count = get_row_count()
        if row_count is not None:
            st.metric("Total Rows", f"{row_count:,}")
        
        # Get and display data
        with st.spinner("Loading data..."):
            df = get_campaign_data(data_limit)
        
        if df is not None and not df.empty:
            st.success(f"✅ Successfully loaded {len(df)} rows of data")
            
            # Display data
            st.subheader("📋 Campaign Performance Data")
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download data as CSV",
                data=csv,
                file_name="campaign_performance_data.csv",
                mime="text/csv"
            )
        else:
            st.error("❌ No data found or error loading data")
    
    with col2:
        st.header("📊 Quick Stats")
        
        if df is not None and not df.empty:
            # Summary statistics
            summary_stats = get_summary_stats(df)
            if summary_stats is not None:
                st.subheader("📈 Numeric Summary")
                st.dataframe(summary_stats, use_container_width=True)
            
            # Performance tier distribution
            if 'performance_tier' in df.columns:
                st.subheader("🏆 Performance Tier Distribution")
                tier_counts = df['performance_tier'].value_counts()
                st.bar_chart(tier_counts)
            
            # Publisher distribution
            if 'publisher' in df.columns:
                st.subheader("📰 Publisher Distribution")
                publisher_counts = df['publisher'].value_counts()
                st.bar_chart(publisher_counts)
    
    # Table schema section
    st.header("📋 Table Schema")
    
    if st.button("🔍 Show Table Schema"):
        with st.spinner("Loading schema information..."):
            schema_df = get_table_info()
        
        if schema_df is not None and not schema_df.empty:
            st.dataframe(schema_df, use_container_width=True)
        else:
            st.error("❌ Could not load table schema")

if __name__ == "__main__":
    main() 