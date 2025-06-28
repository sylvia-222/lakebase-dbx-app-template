# Campaign Performance Data Viewer

A functional Gradio app that displays data from a PostgreSQL database synced table in Databricks.

## Features

- 📊 **Data Display**: Shows campaign performance data from the synced table
- 📋 **Table Schema**: Displays column information and data types
- 📈 **Row Count**: Shows total number of rows in the table
- 🔄 **Refresh Functionality**: Buttons to refresh data and view schema

## Database Connection

The app connects to a PostgreSQL database in Databricks OLTP. Set the following environment variables:

```bash
export DB_HOST="instance-95946f75-1682-4d20-b279-0e9fcb954310.database.cloud.databricks.com"
export DB_USER="sylvia.schumacher@databricks.com"
export DB_PASSWORD="your_jwt_token_here"
export DB_NAME="ssylvia_postgres_database"
export DB_PORT="5432"
```

## Table Information

- **Schema**: `adtech_bootcamp`
- **Table**: `campaign_performance_synced_from_copy`
- **Columns**: 21 columns including campaign_id, week_start, performance_tier, publisher, region, device_type, ad_type, impressions, clicks, CTR, conversions, conversion_rate, cost, CPC, budget, revenue, ROAS, target_CTR, target_CR, platform_ratios, primary_key
- **Data**: 50,000 rows of campaign performance data

## Deployment

The app is deployed on Databricks using Asset Bundles (DABs) and can be accessed at:
https://sylvia-fresh-gradio-app-2024-1444828305810485.aws.databricksapps.com

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables for database connection
3. Run the app: `python gradio_app.py`
4. Test database connection: `python test_db_connection.py`
