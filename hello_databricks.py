# Simple Databricks Connect Example

from databricks.connect import DatabricksSession
from databricks.sdk import WorkspaceClient

print("Attempting to create Spark session...")

# Connect using the DEFAULT profile from ~/.databrickscfg
# Assumes `serverless_compute_id = auto` is set if needed
spark = DatabricksSession.builder.getOrCreate()

print("Spark session created successfully.")

print("Initializing WorkspaceClient...")
w = WorkspaceClient() # Connects using the same DEFAULT profile
dbutils = w.dbutils
print("WorkspaceClient and dbutils initialized.")

print("Running simple Spark SQL query...")

# Run a basic query
df = spark.sql("select 'hello_databricks' as greeting")

# Show the result (will print a table-like structure)
df.show()

print("Query finished.") 