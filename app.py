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

def get_campaign_data(limit=1000):
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

def update_campaign_record(row_id, new_device_type, new_performance_tier):
    try:
        with postgres_pool.connect() as conn:
            update_query = text("""
                UPDATE adtech_bootcamp.campaign_performance_synced_from_copy
                SET device_type = :device_type, performance_tier = :performance_tier
                WHERE primary_key = :row_id
            """)
            conn.execute(update_query, {
                "device_type": new_device_type,
                "performance_tier": new_performance_tier,
                "row_id": row_id
            })
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating record: {str(e)}")
        return False

def main():
    st.title("📊 Campaign Performance Data Viewer")
    st.markdown("This app displays data from the `adtech_bootcamp.campaign_performance_synced_from_copy` table in your PostgreSQL database.")

    # Top row: Refresh button on the right
    top_left, top_right = st.columns([6, 1])
    with top_right:
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()

    # Two large columns: left (table, quick stats), buffer, right (update campaign data)
    left_col, buffer_col, right_col = st.columns([2, 0.15, 1])

    with left_col:
        st.subheader("📋 Campaign Performance Data")
        # Load data with selected limit
        with st.spinner("Loading data..."):
            df = get_campaign_data()

        if df is None or df.empty:
            st.error("❌ No data found or error loading data")
            return

        # Show primary key as first column and sort by primary key ascending
        df_display = df.copy()
        cols = list(df_display.columns)
        if 'primary_key' in cols:
            cols.insert(0, cols.pop(cols.index('primary_key')))
        df_display = df_display[cols]
        df_display = df_display.sort_values(by='primary_key', ascending=True).reset_index(drop=True)
        primary_keys = df_display['primary_key'].tolist()
        selected_pk = st.selectbox(
            "Select a campaign primary key to view/edit:",
            options=primary_keys,
            format_func=lambda x: str(x),
            key="select_pk"
        )
        st.dataframe(df_display, use_container_width=True)

        st.markdown("<h4 style='margin-top:2em'>📊 Quick Stats</h4>", unsafe_allow_html=True)
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        with quick_col1:
            summary_stats = get_summary_stats(df)
            if summary_stats is not None:
                st.subheader("📈 Numeric Summary")
                st.dataframe(summary_stats, use_container_width=True)
        with quick_col2:
            if 'performance_tier' in df.columns:
                st.subheader("🏆 Performance Tier Distribution")
                tier_counts = df['performance_tier'].value_counts()
                st.bar_chart(tier_counts)
        with quick_col3:
            if 'publisher' in df.columns:
                st.subheader("📰 Publisher Distribution")
                publisher_counts = df['publisher'].value_counts()
                st.bar_chart(publisher_counts)

    with buffer_col:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

    with right_col:
        row_data = df_display[df_display['primary_key'] == selected_pk].iloc[0]
        st.subheader("Update Campaign Data")
        st.markdown("---")
        st.subheader("🔎 Selected Campaign Record")
        # Visually rich campaign view with primary key
        col1, col2, col3 = st.columns([1.5, 1.5, 1])
        with col1:
            st.markdown(f"<h3 style='margin-bottom:0'>🔑 <span style='color:#e67e22'>Primary Key: {row_data.get('primary_key', 'N/A')}</span></h3>", unsafe_allow_html=True)
            st.markdown(f"<b>📰 Publisher:</b> <span style='color:#6c757d'>{row_data.get('publisher', 'N/A')}</span>", unsafe_allow_html=True)
            device_icon = "📱" if row_data.get('device_type', '').lower() == 'mobile' else ("💻" if row_data.get('device_type', '').lower() == 'desktop' else "🖥️")
            st.markdown(f"<b>{device_icon} Device Type:</b> <span style='color:#2ca02c'>{row_data.get('device_type', 'N/A')}</span>", unsafe_allow_html=True)
            tier_icon = "🏆" if row_data.get('performance_tier', '').lower() == 'top' else ("⭐" if row_data.get('performance_tier', '').lower() == 'mid' else "🔸")
            st.markdown(f"<b>{tier_icon} Performance Tier:</b> <span style='color:#f39c12'>{row_data.get('performance_tier', 'N/A')}</span>", unsafe_allow_html=True)
        with col2:
            st.metric("💰 Spend", f"${row_data.get('spend', 0):,.2f}")
            st.metric("👁️ Impressions", f"{row_data.get('impressions', 0):,}")
            st.metric("🖱️ Clicks", f"{row_data.get('clicks', 0):,}")
            ctr = row_data.get('ctr', None)
            if ctr is not None:
                st.metric("📈 CTR", f"{ctr:.2%}")
        with col3:
            if 'start_date' in row_data:
                st.markdown(f"<b>🗓️ Start:</b> <span style='color:#17a2b8'>{row_data.get('start_date', 'N/A')}</span>", unsafe_allow_html=True)
            if 'end_date' in row_data:
                st.markdown(f"<b>🗓️ End:</b> <span style='color:#17a2b8'>{row_data.get('end_date', 'N/A')}</span>", unsafe_allow_html=True)
            if 'status' in row_data:
                status_color = '#28a745' if str(row_data.get('status', '')).lower() == 'active' else '#dc3545'
                st.markdown(f"<b>🔔 Status:</b> <span style='color:{status_color}'>{row_data.get('status', 'N/A')}</span>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Editable fields in a column
        st.markdown("### ✏️ Update Campaign Fields")
        edit_col1, edit_col2 = st.columns(2)
        device_type_options = df["device_type"].dropna().unique().tolist() if "device_type" in df.columns else []
        performance_tier_options = df["performance_tier"].dropna().unique().tolist() if "performance_tier" in df.columns else []
        with st.form("edit_form"):
            with edit_col1:
                new_device_type = st.selectbox(
                    "Device Type", device_type_options,
                    index=device_type_options.index(row_data["device_type"]) if row_data["device_type"] in device_type_options else 0,
                    key=f"device_type_{row_data['primary_key']}"
                ) if device_type_options else st.text_input("Device Type", value=row_data.get("device_type", ""), key=f"device_type_{row_data['primary_key']}")
            with edit_col2:
                new_performance_tier = st.selectbox(
                    "Performance Tier", performance_tier_options,
                    index=performance_tier_options.index(row_data["performance_tier"]) if row_data["performance_tier"] in performance_tier_options else 0,
                    key=f"performance_tier_{row_data['primary_key']}"
                ) if performance_tier_options else st.text_input("Performance Tier", value=row_data.get("performance_tier", ""), key=f"performance_tier_{row_data['primary_key']}")
            submitted = st.form_submit_button("Update Record", use_container_width=True)

        if submitted:
            success = update_campaign_record(row_data["primary_key"], new_device_type, new_performance_tier)
            if success:
                st.success("Record updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update record.")

    # Main content area (row count, table schema, etc.)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("📈 Data Overview")
        row_count = get_row_count()
        if row_count is not None:
            st.metric("Total Rows", f"{row_count:,}")
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