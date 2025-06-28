import gradio as gr
import psycopg2
import pandas as pd
from databricks.sdk import WorkspaceClient
import os

def get_database_connection():
    """Get connection to the PostgreSQL database using environment variables"""
    try:
        conn_params = {
            'host': os.getenv('DB_HOST', 'instance-95946f75-1682-4d20-b279-0e9fcb954310.database.cloud.databricks.com'),
            'user': os.getenv('DB_USER', 'sylvia.schumacher@databricks.com'),
            'password': os.getenv('DB_PASSWORD', ''),
            'dbname': os.getenv('DB_NAME', 'ssylvia_postgres_database'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'sslmode': 'require'
        }
        return psycopg2.connect(**conn_params)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_campaign_data():
    """Fetch data from the synced table"""
    try:
        conn = get_database_connection()
        if conn is None:
            return "Error: Could not connect to database"
        query = """
        SELECT * FROM adtech_bootcamp.campaign_performance_synced_from_copy 
        LIMIT 100
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            return "No data found in the synced table"
        return df.to_html(index=False, classes='table table-striped')
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def get_table_info():
    """Get information about the synced table"""
    try:
        conn = get_database_connection()
        if conn is None:
            return "Error: Could not connect to database"
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
        if df.empty:
            return "Table schema information not found"
        return df.to_html(index=False, classes='table table-striped')
    except Exception as e:
        return f"Error fetching table info: {str(e)}"

def get_row_count():
    """Get the total number of rows in the synced table"""
    try:
        conn = get_database_connection()
        if conn is None:
            return "Error: Could not connect to database"
        query = "SELECT COUNT(*) as total_rows FROM adtech_bootcamp.campaign_performance_synced_from_copy"
        cursor = conn.cursor()
        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return f"Total rows in campaign_performance_synced_from_copy: {count:,}"
    except Exception as e:
        return f"Error getting row count: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="Campaign Performance Data Viewer") as demo:
    gr.Markdown("# 📊 Campaign Performance Data from Synced Table")
    gr.Markdown("This app displays data from the `adtech_bootcamp.campaign_performance_synced_from_copy` table in your PostgreSQL database.")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📈 Data Overview")
            row_count_output = gr.Textbox(label="Row Count", interactive=False)
            refresh_btn = gr.Button("🔄 Refresh Data", variant="primary")
        
        with gr.Column():
            gr.Markdown("### 📋 Table Schema")
            schema_btn = gr.Button("📋 Show Table Schema")
            schema_output = gr.HTML(label="Table Schema")
    
    gr.Markdown("### 📊 Campaign Performance Data")
    data_output = gr.HTML(label="Data Table")
    
    # Set up event handlers
    refresh_btn.click(fn=get_row_count, outputs=row_count_output)
    refresh_btn.click(fn=get_campaign_data, outputs=data_output)
    schema_btn.click(fn=get_table_info, outputs=schema_output)
    
    # Load initial data
    demo.load(fn=get_row_count, outputs=row_count_output)
    demo.load(fn=get_campaign_data, outputs=data_output)

if __name__ == "__main__":
    demo.launch() 