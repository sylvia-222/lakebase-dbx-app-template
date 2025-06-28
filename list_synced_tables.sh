#!/bin/bash
# Script to list all synced tables in Databricks PostgreSQL compute

set -e

echo "🔍 Searching for synced tables in Databricks PostgreSQL..."
echo "============================================================"

# Method 1: Using Databricks REST API
echo -e "\n📡 Method 1: Using Databricks REST API"
echo "----------------------------------------"

if [ -z "$DATABRICKS_TOKEN" ] || [ -z "$DATABRICKS_HOST" ]; then
    echo "❌ DATABRICKS_TOKEN and DATABRICKS_HOST environment variables required"
    echo "   Please set these variables and try again"
else
    echo "🔍 Fetching synced tables via REST API..."
    
    response=$(curl -s -X GET "${DATABRICKS_HOST}/api/2.0/database/synced_tables" \
        -H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
        -H "Content-Type: application/json")
    
    if [ $? -eq 0 ]; then
        echo "$response" | jq -r '.synced_tables[] | "  • \(.name) (Source: \(.spec.source_table_full_name // "Unknown"))"' 2>/dev/null || {
            echo "📋 Raw API response:"
            echo "$response"
        }
    else
        echo "❌ Failed to fetch synced tables via API"
    fi
fi

# Method 2: Using direct psql connection
echo -e "\n🗄️ Method 2: Using direct PostgreSQL queries"
echo "---------------------------------------------"

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "❌ psql command not found. Please install PostgreSQL client tools."
    echo "   On macOS: brew install postgresql"
    echo "   On Ubuntu: sudo apt-get install postgresql-client"
else
    echo "🔍 Querying PostgreSQL for synced tables..."
    
    # Connection string
    CONN_STRING="host=instance-8b09a63f-7f3f-4e94-9e3f-a8067c2764c2.database.cloud.databricks.com user=sylvia.schumacher@databricks.com dbname=databricks_postgres port=5432 sslmode=require"
    
    # Query 1: Look for tables with 'synced' in the name
    echo "📋 Tables with 'synced' in name:"
    psql "$CONN_STRING" -c "
    SELECT 
        schemaname as schema_name,
        tablename as table_name
    FROM pg_tables 
    WHERE tablename LIKE '%synced%' OR tablename LIKE '%sync%'
    ORDER BY schemaname, tablename;
    " 2>/dev/null || echo "❌ Failed to query PostgreSQL"
    
    # Query 2: List all tables for reference
    echo -e "\n📋 All tables in database (for reference):"
    psql "$CONN_STRING" -c "
    SELECT 
        schemaname as schema_name,
        tablename as table_name
    FROM pg_tables 
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    ORDER BY schemaname, tablename;
    " 2>/dev/null || echo "❌ Failed to query PostgreSQL"
fi

# Method 3: Using Databricks CLI (if available)
echo -e "\n🛠️ Method 3: Using Databricks CLI"
echo "----------------------------------"

if command -v databricks &> /dev/null; then
    echo "🔍 Checking if Databricks CLI supports synced tables..."
    
    # Try to list synced tables via CLI
    databricks database list-synced-tables 2>/dev/null || {
        echo "ℹ️ Databricks CLI doesn't have a direct command for synced tables"
        echo "   Using REST API method instead..."
    }
else
    echo "ℹ️ Databricks CLI not found. Install with: pip install databricks-cli"
fi

echo -e "\n✅ Search complete!" 