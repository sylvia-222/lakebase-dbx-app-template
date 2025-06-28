import psycopg2
import os

def test_connection():
    """Test connection to the PostgreSQL database"""
    try:
        conn_params = {
            'host': 'instance-95946f75-1682-4d20-b279-0e9fcb954310.database.cloud.databricks.com',
            'user': os.environ.get('DB_USER', 'default_user'),
            'password': os.environ.get('DB_PASSWORD', 'default_password'),
            'dbname': 'ssylvia_postgres_database',
            'port': 5432,
            'sslmode': 'require'
        }
        
        print("Attempting to connect to database...")
        print(f"Host: {conn_params['host']}")
        print(f"User: {conn_params['user']}")
        print(f"Database: {conn_params['dbname']}")
        print(f"Port: {conn_params['port']}")
        
        conn = psycopg2.connect(**conn_params)
        print("✅ Successfully connected to database!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM adtech_bootcamp.campaign_performance_synced_from_copy")
        count = cursor.fetchone()[0]
        print(f"✅ Table has {count} rows")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    test_connection() 