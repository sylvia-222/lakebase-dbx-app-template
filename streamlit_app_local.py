import streamlit as st
import psycopg2
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="Campaign Performance Data Viewer",
    page_icon="📊",
    layout="wide"
)

def get_database_connection():
    """Get connection to the PostgreSQL database using hardcoded parameters for local testing"""
    try:
        conn_params = {
            'host': 'instance-95946f75-1682-4d20-b279-0e9fcb954310.database.cloud.databricks.com',
            'user': os.environ.get('DB_USER', 'default_user'),
            'password': os.environ.get('DB_PASSWORD', 'default_password'),
            'dbname': 'ssylvia_postgres_database',
            'port': 5432,
            'sslmode': 'require'
        }
        return psycopg2.connect(**conn_params)
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

def get_campaign_data(limit=100):
    """Fetch data from the synced table"""
    try:
        conn = get_database_connection()
        if conn is None:
            return None
        
        query = f"""
        SELECT * FROM adtech_bootcamp.campaign_performance_synced_from_copy 
        LIMIT {limit}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def get_table_info():
    """Get information about the synced table"""
    try:
        conn = get_database_connection()
        if conn is None:
            return None
        
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
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching table info: {str(e)}")
        return None

def get_row_count():
    """Get the total number of rows in the synced table"""
    try:
        conn = get_database_connection()
        if conn is None:
            return None
        
        query = "SELECT COUNT(*) as total_rows FROM adtech_bootcamp.campaign_performance_synced_from_copy"
        cursor = conn.cursor()
        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
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
    st.title("📊 Campaign Performance Data Viewer (Local Test)")
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