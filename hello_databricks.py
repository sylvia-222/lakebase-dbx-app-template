import sys

try:
    # Make yourself at home with the normal databricks notebook variables you're used to
    from databricks.connect import DatabricksSession
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.errors import PermissionDenied, NotFound, DatabricksError

    print("Attempting to connect to Databricks...")

    # This connects using the details in your local databricks config file
    # The profile name defaults to 'DEFAULT'.
    # It should find the `serverless_compute_id = auto` setting.
    spark = DatabricksSession.builder.getOrCreate()
    print("Spark Session created.")

    # Again, this is using your local databricks config file
    # The profile name defaults to 'DEFAULT'.
    w = WorkspaceClient()
    dbutils = w.dbutils
    print("WorkspaceClient and dbutils initialized.")

    print("Running test Spark SQL query...")
    # Run a simple query
    df = spark.sql("select 'hello_databricks' as greeting")

    # Fetch the result
    result = df.first()['greeting']
    print("Query executed successfully.")

    # Validate the result
    if result == 'hello_databricks':
        print(f"✅ Success! Connected to Databricks and ran Spark SQL. Result: {result}")
    else:
        print(f"⚠️ Warning! Query ran but the result was unexpected: {result}")

except ImportError as e:
    print(f"❌ Failed! Missing required libraries: {e}")
    print("Please ensure you have activated your virtual environment (`source .venv/bin/activate`)")
    print("and installed the requirements (`pip install -r requirements.txt`).")
    sys.exit(1)
except (PermissionDenied, NotFound, DatabricksError) as e:
    print(f"❌ Failed! Databricks API/Permissions Error: {e}")
    print("Please check:")
    print("  1. Your Databricks host and token in `~/.databrickscfg` (profile: DEFAULT).")
    print("  2. Your token has not expired and has cluster/compute permissions.")
    print("  3. The `serverless_compute_id = auto` setting in `~/.databrickscfg` is correct (if using).")
    sys.exit(1)
except Exception as e:
    print(f"❌ Failed! An unexpected error occurred: {e}")
    print("Potential issues:")
    print("  - Network connectivity to your Databricks workspace.")
    print("  - Databricks compute (cluster or warehouse) status.")
    print("  - Correct configuration in `~/.databrickscfg`.")
    sys.exit(1) 