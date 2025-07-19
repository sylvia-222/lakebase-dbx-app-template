# Lakebase Streamlit App

A Streamlit application for viewing and exploring PostgreSQL database tables synced with Databricks Lakebase. This app provides a clean interface for database table visualization with statistics and data exploration features.

## Features

- 🔗 **PostgreSQL Database Connection** - Connects to Databricks Lakebase PostgreSQL instances using OAuth authentication
- 📊 **Data Visualization** - Two-column layout with table data and statistics
- 📈 **Table Statistics** - Automatic key column detection, row counts, and numeric summaries
- 🎨 **Modern UI** - Clean Streamlit interface with gradient connection scorecard
- ⚡ **Auto Token Refresh** - Handles Databricks OAuth token refresh automatically

## Quick Start

### Prerequisites
- Databricks workspace access
- Databricks CLI installed and configured
- Access to a PostgreSQL database instance (Lakebase)

### Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sylvia-222/lakebase_in_apps.git
   cd lakebase_in_apps
   ```

2. **Configure your database connection** (see [Database Configuration](#database-configuration) below)

3. **Deploy using Databricks Asset Bundles:**
   ```bash
   databricks bundle deploy
   ```

4. **Access your app:**
   Your app will be available at the URL shown in the deployment output.

## Database Configuration

To connect to your own PostgreSQL database, update the `DB_CONFIG` section in `app.py`:

```python
# Database Configuration - Single source of truth
DB_CONFIG = {
    "host": "your-instance-hostname.database.cloud.databricks.com",  # Your PostgreSQL host
    "port": 5432,  
    "database": "your_database_name",      # Your database name
    "schema": "your_schema",               # Your schema name
    "table": "your_table_name"             # Your table name
}
```

### Required Changes for Different Databases:

1. **Host**: Update with your PostgreSQL instance hostname
   - Format: `instance-xxxxx.database.cloud.databricks.com`
   - Remove any `https://` prefix or trailing `/`

2. **Database**: Change to your target database name

3. **Schema**: Update to your target schema name

4. **Table**: Specify the table you want to visualize

### Example Configuration:
```python
DB_CONFIG = {
    "host": "instance-12345678-abcd-efgh-ijkl-123456789012.database.cloud.databricks.com",
    "port": 5432,
    "database": "my_analytics_db",
    "schema": "sales_data", 
    "table": "customer_metrics"
}
```

## File Structure

```
├── app.py                 # Main Streamlit application
├── app.yml                # App configuration for Databricks Apps
├── databricks.yml         # Databricks Asset Bundle configuration
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
└── README.md              # This file
```

## Key Files for DAB & App Deployment

- **`app.py`** - Main application code with database configuration
- **`app.yml`** - Streamlit app runtime configuration  
- **`databricks.yml`** - Databricks Asset Bundle definition
- **`requirements.txt`** - Python package dependencies
- **`pyproject.toml`** - Project metadata and configuration

## Authentication

The app uses Databricks OAuth authentication to connect to PostgreSQL:
- No manual token management required
- Automatic token refresh every 15 minutes
- Uses your Databricks workspace credentials

## App Features

### Connection Scorecard
Beautiful gradient display showing:
- Connected database host
- Database name
- Schema and table being viewed

### Data View (Left Column)
- Full table data display
- Scrollable interface with 600px height
- Row count indicator

### Statistics Panel (Right Column)
- Total rows and column count metrics
- Automatic primary key detection
- Statistical summary for numeric columns

## Troubleshooting

### Common Issues:

1. **Connection Failed**: 
   - Verify your database host format (no `https://` prefix)
   - Ensure you have access to the PostgreSQL instance
   - Check your Databricks workspace permissions

2. **Table Not Found**:
   - Verify schema and table names in `DB_CONFIG`
   - Use the "Test Connection" button to verify connectivity
   - Check that the table exists in your database

3. **Token Issues**:
   - The app handles token refresh automatically
   - If issues persist, restart the app

## Development

To run locally for development:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

## License

This project is part of the Databricks Lakebase ecosystem.
