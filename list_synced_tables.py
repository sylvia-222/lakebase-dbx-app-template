#!/usr/bin/env python3
"""
Script to list all synced tables in Databricks PostgreSQL compute.
Supports both REST API and direct database queries.
"""

import os
import psycopg2
import requests
import json
from typing import List, Dict, Any

def get_synced_tables_via_api() -> List[Dict[str, Any]]:
    """Get synced tables using Databricks REST API"""
    host = os.getenv('DATABRICKS_HOST')
    token = os.getenv('DATABRICKS_TOKEN')
    
    if not host or not token:
        print("❌ DATABRICKS_HOST and DATABRICKS_TOKEN environment variables required")
        return []
    
    url = f"{host}/api/2.0/database/synced_tables"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('synced_tables', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return []

def get_synced_tables_via_postgres() -> List[Dict[str, Any]]:
    """Get synced tables using direct PostgreSQL connection"""
    # Connection parameters from your setup
    conn_params = {
        'host': 'instance-8b09a63f-7f3f-4e94-9e3f-a8067c2764c2.database.cloud.databricks.com',
        'user': 'sylvia.schumacher@databricks.com',
        'dbname': 'databricks_postgres',
        'port': 5432,
        'sslmode': 'require'
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Query to find synced tables
        # Synced tables typically have specific naming patterns or metadata
        queries = [
            # Look for tables with synced metadata
            """
            SELECT 
                schemaname as schema_name,
                tablename as table_name,
                'synced_table' as table_type
            FROM pg_tables 
            WHERE tablename LIKE '%synced%' OR tablename LIKE '%sync%'
            ORDER BY schemaname, tablename
            """,
            
            # Look for tables in information_schema that might be synced
            """
            SELECT 
                table_schema as schema_name,
                table_name,
                'potential_synced' as table_type
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            AND table_name LIKE '%synced%'
            ORDER BY table_schema, table_name
            """,
            
            # Check for any tables with sync-related comments or metadata
            """
            SELECT DISTINCT
                n.nspname as schema_name,
                c.relname as table_name,
                'table_with_metadata' as table_type
            FROM pg_class c
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relkind = 'r' 
            AND n.nspname NOT IN ('information_schema', 'pg_catalog')
            AND (c.relname LIKE '%sync%' OR c.relname LIKE '%databricks%')
            ORDER BY n.nspname, c.relname
            """
        ]
        
        all_tables = []
        for i, query in enumerate(queries, 1):
            print(f"\n🔍 Running query {i}...")
            cursor.execute(query)
            results = cursor.fetchall()
            
            for row in results:
                all_tables.append({
                    'schema_name': row[0],
                    'table_name': row[1],
                    'table_type': row[2],
                    'source': f'query_{i}'
                })
        
        cursor.close()
        conn.close()
        return all_tables
        
    except Exception as e:
        print(f"❌ PostgreSQL connection error: {e}")
        return []

def list_all_tables_postgres() -> List[Dict[str, Any]]:
    """List all tables in the PostgreSQL database for reference"""
    conn_params = {
        'host': 'instance-8b09a63f-7f3f-4e94-9e3f-a8067c2764c2.database.cloud.databricks.com',
        'user': 'sylvia.schumacher@databricks.com',
        'dbname': 'databricks_postgres',
        'port': 5432,
        'sslmode': 'require'
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            schemaname as schema_name,
            tablename as table_name
        FROM pg_tables 
        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
        ORDER BY schemaname, tablename
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        tables = []
        for row in results:
            tables.append({
                'schema_name': row[0],
                'table_name': row[1]
            })
        
        cursor.close()
        conn.close()
        return tables
        
    except Exception as e:
        print(f"❌ PostgreSQL connection error: {e}")
        return []

def main():
    print("🔍 Searching for synced tables in Databricks PostgreSQL...")
    print("=" * 60)
    
    # Method 1: REST API
    print("\n📡 Method 1: Using Databricks REST API")
    print("-" * 40)
    api_tables = get_synced_tables_via_api()
    
    if api_tables:
        print(f"✅ Found {len(api_tables)} synced tables via API:")
        for table in api_tables:
            print(f"  • {table.get('name', 'Unknown')}")
            if 'spec' in table:
                spec = table['spec']
                print(f"    Source: {spec.get('source_table_full_name', 'Unknown')}")
                print(f"    Primary Keys: {spec.get('primary_key_columns', [])}")
    else:
        print("❌ No synced tables found via API or API call failed")
    
    # Method 2: Direct PostgreSQL queries
    print("\n🗄️ Method 2: Using direct PostgreSQL queries")
    print("-" * 40)
    pg_tables = get_synced_tables_via_postgres()
    
    if pg_tables:
        print(f"✅ Found {len(pg_tables)} potential synced tables via PostgreSQL:")
        for table in pg_tables:
            print(f"  • {table['schema_name']}.{table['table_name']} ({table['table_type']})")
    else:
        print("❌ No potential synced tables found via PostgreSQL queries")
    
    # Method 3: List all tables for reference
    print("\n📋 Method 3: All tables in PostgreSQL database")
    print("-" * 40)
    all_tables = list_all_tables_postgres()
    
    if all_tables:
        print(f"📊 Total tables found: {len(all_tables)}")
        schemas = {}
        for table in all_tables:
            schema = table['schema_name']
            if schema not in schemas:
                schemas[schema] = []
            schemas[schema].append(table['table_name'])
        
        for schema, tables in schemas.items():
            print(f"\n📁 Schema: {schema} ({len(tables)} tables)")
            for table in sorted(tables):
                print(f"  • {table}")
    else:
        print("❌ Could not retrieve table list from PostgreSQL")

if __name__ == "__main__":
    main() 