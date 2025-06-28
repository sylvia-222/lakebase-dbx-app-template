#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database connection
"""

import psycopg2
import pandas as pd
import os

def test_connection():
    """Test connection to the PostgreSQL database"""
    hostname = os.getenv('DB_HOST', 'instance-95946f75-1682-4d20-b279-0e9fcb954310.database.cloud.databricks.com')
    print(f"🔍 Testing PostgreSQL database connection to {hostname}...")
    print("=" * 60)
    
    # Connection parameters
    conn_params = {
        'host': hostname,
        'user': os.getenv('DB_USER', 'sylvia.schumacher@databricks.com'),
        'password': os.getenv('DB_PASSWORD', ''),
        'dbname': os.getenv('DB_NAME', 'ssylvia_postgres_database'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'sslmode': 'require'
    }
    
    print(f"📡 Connecting to: {conn_params['host']}")
    print(f"👤 User: {conn_params['user']}")
    print(f"🗄️ Database: {conn_params['dbname']}")
    print(f"🔌 Port: {conn_params['port']}")
    print()
    
    try:
        # Test connection
        print("🔄 Attempting to connect...")
        conn = psycopg2.connect(**conn_params)
        print("✅ Connection successful!")
        
        # Test query to list databases
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user, version()")
        result = cursor.fetchone()
        print(f"📊 Current database: {result[0]}")
        print(f"👤 Current user: {result[1]}")
        print(f"🔧 PostgreSQL version: {result[2].split(',')[0]}")
        
        # Find the table in all schemas
        print("\n🔍 Searching for synced table in all schemas...")
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name = 'campaign_performance_synced_from_copy'
            ORDER BY table_schema
        """)
        
        table_locations = cursor.fetchall()
        if table_locations:
            print(f"✅ Found table in {len(table_locations)} schema(s):")
            for schema, table in table_locations:
                print(f"  • {schema}.{table}")
            
            # Use the first schema found
            schema_name = table_locations[0][0]
            table_name = table_locations[0][1]
            full_table_name = f"{schema_name}.{table_name}"
            
            print(f"\n📋 Using table: {full_table_name}")
            
            # Get table info
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print(f"📋 Table has {len(columns)} columns:")
            for col in columns:
                print(f"  • {col[0]} ({col[1]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {full_table_name}")
            count = cursor.fetchone()[0]
            print(f"📊 Total rows: {count:,}")
            
            # Get sample data
            if count > 0:
                print(f"\n📋 Sample data (first 5 rows):")
                cursor.execute(f"SELECT * FROM {full_table_name} LIMIT 5")
                sample_data = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                column_names = [col[0] for col in cursor.fetchall()]
                
                # Display sample data
                for i, row in enumerate(sample_data, 1):
                    print(f"  Row {i}:")
                    for j, value in enumerate(row):
                        print(f"    {column_names[j]}: {value}")
                    print()
        else:
            print("❌ Table 'campaign_performance_synced_from_copy' not found in any schema!")
            
            # List all tables
            print("\n📋 Available tables:")
            cursor.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_schema, table_name
            """)
            
            tables = cursor.fetchall()
            for schema, table in tables:
                print(f"  • {schema}.{table}")
        
        cursor.close()
        conn.close()
        print("✅ Connection test completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_connection() 