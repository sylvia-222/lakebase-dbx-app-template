# Cursor + Databricks Connect Quickstart

This project provides a minimal example to get you started using [Cursor](https://cursor.com/) with [Databricks Connect](https://docs.databricks.com/en/dev-tools/databricks-connect/index.html) on your local machine.

It guides you through installing the necessary tools, configuring Databricks authentication, setting up a Python environment, and running a simple test script.

## Prerequisites

*   **macOS:** [Homebrew](https://brew.sh/) (for simplified installation steps)
*   **Python:** Version 3.8 or higher.
*   **Databricks Account:** Access to a Databricks workspace with permissions to create/use compute resources (clusters or SQL warehouses).

## Setup Instructions

Follow these steps in your terminal:

### 1. Install Cursor

Cursor is an AI-first code editor.

*   **Using Homebrew (Recommended for macOS):**
    ```bash
    brew install --cask cursor
    ```
*   **Manual Download:**
    Visit the [Cursor website](https://cursor.com/) and download the installer for your operating system.

### 2. Install Databricks CLI

The Databricks command-line interface (CLI) is used for authentication and workspace interaction.

*   **Using Homebrew (Recommended for macOS):**
    ```bash
    brew tap databricks/tap
    brew install databricks
    ```
*   **Other Methods:**
    Follow the official [Databricks CLI installation guide](https://docs.databricks.com/en/dev-tools/cli/install.html).

### 3. Configure Databricks Authentication

This step creates a configuration profile (`~/.databrickscfg`) that the Databricks SDK and Databricks Connect will use to authenticate. The recommended method is OAuth user-to-machine (U2M) authentication.

1.  Run the configure command. It will prompt you for your Databricks Host URL (e.g., `https://<your-workspace-id>.databricks.net`) and initiate the OAuth browser-based authentication flow.
    ```bash
    databricks configure --profile DEFAULT
    ```
    *   **Important:** Ensure you use `DEFAULT` as the profile name, as this is what the sample script expects.
    *   Follow the prompts in your terminal and browser to complete the OAuth login.
    *   Refer to [Databricks CLI authentication](https://docs.databricks.com/en/dev-tools/cli/authentication.html) for more details on authentication methods.

2.  **Manually Edit `~/.databrickscfg` for Serverless Compute:**
    Open the `~/.databrickscfg` file in a text editor. Find the `[DEFAULT]` profile section and add the `serverless_compute_id = auto` line. This tells Databricks Connect to automatically try and use a Serverless SQL Warehouse if available, falling back to other compute otherwise.

    Your `[DEFAULT]` profile should look something like this after successful OAuth configuration and manual editing:
    ```ini
    [DEFAULT]
    host                  = https://<your-workspace-id>.databricks.net
    auth_type             = oauth-m2m # Or similar, depending on exact flow
    # Other OAuth related fields might be populated automatically
    serverless_compute_id = auto
    ```
    *Replace the host with your actual value.* Save the file.

### 4. Create a Python Virtual Environment

It's crucial to use a virtual environment to isolate project dependencies. We'll use `uv`, a fast Python package manager.

1.  **Install `uv` (if you don't have it):**
    ```bash
    brew install uv
    ```

2.  **Create the virtual environment:**
    This command creates a `.venv` directory and uses Python 3.11 if available.
    ```bash
    uv venv --python 3.11
    ```

3.  **Activate the environment:**
    ```bash
    source .venv/bin/activate
    ```
    You should see `(.venv)` prepended to your terminal prompt after activation.

### 5. Install Dependencies

Install the required Python libraries (`databricks-sdk` and `databricks-connect`) specified in `pyproject.toml` into your active virtual environment using `uv sync`.

```bash
# Make sure your venv is active first!
uv sync
```

### 6. Configure Cursor Python Interpreter

Tell Cursor to use the Python interpreter from your virtual environment:

1.  Open this project folder in Cursor.
2.  Open the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`).
3.  Search for and select `Python: Select Interpreter`.
4.  Choose `Enter interpreter path...` or browse if `.venv/bin/python` is listed.
5.  If entering manually, provide the full path: `<path_to_this_project>/.venv/bin/python` (e.g., `/Users/youruser/cursor_for_humans/.venv/bin/python`).

Cursor will now use this environment for running Python code, providing code intelligence, etc.

## Running the Sample Script

With your virtual environment activated (`source .venv/bin/activate`) and dependencies installed via `uv sync`, run the validation script first:

```bash
python validate_config.py
```

If the validation script succeeds, you can run the simpler example:

```bash
python hello_databricks.py
```

## Expected Output

**For `validate_config.py`:**
```
Attempting to connect to Databricks...
Spark Session created.
WorkspaceClient and dbutils initialized.
Running test Spark SQL query...
Query executed successfully.
✅ Success! Connected to Databricks and ran Spark SQL. Result: hello_databricks
```

## Troubleshooting

*   **`ImportError: No module named databricks...`:** Ensure your virtual environment is activated (`source .venv/bin/activate`) and you've installed dependencies (`uv sync`). Check that Cursor is using the correct interpreter (`.venv/bin/python`).
*   **`PermissionDenied` / `NotFound` / Authentication Errors:** Double-check your Databricks host in `~/.databrickscfg` under the `[DEFAULT]` profile. Re-run `databricks configure --profile DEFAULT` if you suspect authentication issues. Ensure your user has the necessary permissions in the Databricks workspace.
*   **Connection Timeouts / Network Errors:** Verify your network connection to the Databricks workspace URL. Check if the cluster or SQL warehouse Databricks Connect is trying to use is running and accessible.
*   **`ValueError: serverless_compute_id must be set...` (or similar):** Make sure you added `serverless_compute_id = auto` correctly to your `[DEFAULT]` profile in `~/.databrickscfg`.
*   **`Cluster id is required but was not specified` Error:** This typically means Databricks Connect could not automatically determine a compute resource. Ensure `serverless_compute_id = auto` is correctly added to your `[DEFAULT]` profile in `~/.databrickscfg`. This setting allows Connect to use available Serverless compute for interactive sessions. Verify your user/workspace has access to Serverless compute. 