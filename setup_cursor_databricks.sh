#!/bin/bash

# Script to set up Cursor + Databricks Connect environment on macOS

# Colors for output
COLOR_RESET='\033[0m'
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[0;33m'
COLOR_BLUE='\033[0;34m'

# Helper function for messages
echo_info() { echo "${COLOR_BLUE}ℹ️  $1${COLOR_RESET}"; }
echo_success() { echo "${COLOR_GREEN}✅ $1${COLOR_RESET}"; }
echo_warn() { echo "${COLOR_YELLOW}⚠️  $1${COLOR_RESET}"; }
echo_error() { echo "${COLOR_RED}❌ $1${COLOR_RESET}"; }

# --- Prerequisite Checks ---
echo_info "Starting setup for Cursor + Databricks Connect..."
echo_info "Checking prerequisites..."

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo_error "Homebrew not found. Please install it first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
else
    echo_success "Homebrew found."
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo_error "Python 3 not found. Please install Python 3 first."
    echo "  You can often install it using Homebrew: brew install python3"
    exit 1
else
    echo_success "Python 3 found."
fi

# --- Installation/Updates ---

# Install/Update Cursor
echo_info "Checking Cursor installation..."
if brew list --cask cursor &> /dev/null; then
    echo_info "Cursor already installed. Attempting upgrade..."
    if ! brew upgrade --cask cursor; then
        echo_error "Failed to upgrade Cursor."
        exit 1
    fi
    echo_success "Cursor upgraded (or already up-to-date)."
else
    echo_info "Installing Cursor..."
    if ! brew install --cask cursor; then
        echo_error "Failed to install Cursor."
        exit 1
    fi
    echo_success "Cursor installed successfully."
fi

# Install/Update Databricks CLI
echo_info "Checking Databricks CLI installation..."
echo_info "Ensuring Databricks tap exists..."
if ! brew tap databricks/tap; then
    echo_error "Failed to add Databricks Homebrew tap."
    exit 1
fi
echo_success "Databricks tap ensured."

if brew list databricks &> /dev/null; then
    echo_info "Databricks CLI already installed. Attempting upgrade..."
    if ! brew upgrade databricks; then
        echo_error "Failed to upgrade Databricks CLI."
        exit 1
    fi
    echo_success "Databricks CLI upgraded (or already up-to-date)."
else
    echo_info "Installing Databricks CLI..."
    if ! brew install databricks; then
        echo_error "Failed to install Databricks CLI."
        exit 1
    fi
    echo_success "Databricks CLI installed successfully."
fi

# Install/Update uv
echo_info "Checking uv installation..."
if brew list uv &> /dev/null; then
    echo_info "uv already installed. Attempting upgrade..."
    if ! brew upgrade uv; then
        echo_error "Failed to upgrade uv."
        # Don't exit, maybe the old version is fine?
        echo_warn "Continuing with potentially older uv version."
    else
       echo_success "uv upgraded (or already up-to-date)."
    fi
else
    echo_info "Installing uv..."
    if ! brew install uv; then
        echo_error "Failed to install uv."
        exit 1
    fi
    echo_success "uv installed successfully."
fi

# --- Configuration ---

# Configure Databricks CLI
echo_info "------------------------------------------------------------"
echo_info "Next step: Configure Databricks CLI authentication."
echo_info "This will likely open a web browser for OAuth login."
echo_info "Please follow the prompts in the terminal and browser."
echo_info "Use 'DEFAULT' when asked for a profile name."
echo_info "Press Enter to continue..."
read -r

if ! databricks configure --profile DEFAULT; then
    echo_error "Databricks configuration failed. Please try running 'databricks configure --profile DEFAULT' manually."
    exit 1
fi
echo_success "Databricks CLI configured for DEFAULT profile."

echo_warn "Manual Step Required: You MUST manually edit '~/.databrickscfg'"
echo_warn "Add 'serverless_compute_id = auto' under the [DEFAULT] section."
echo_warn "Example [DEFAULT] section:"
echo "[DEFAULT]"
echo "host                  = https://<your-workspace-id>.databricks.net"
echo "auth_type             = oauth-m2m # Or similar"
# echo "# Other OAuth fields..."
echo "serverless_compute_id = auto"
echo_warn "Save the file after editing."
echo_info "Press Enter once you have edited and saved ~/.databrickscfg..."
read -r

# --- Environment Setup ---

# Create Virtual Environment
echo_info "Checking for existing virtual environment '.venv'..."
if [ -d ".venv" ]; then
    echo_warn "Virtual environment '.venv' already exists. Skipping creation."
else
    echo_info "Creating Python virtual environment using uv..."
    if ! uv venv .venv; then
        echo_error "Failed to create virtual environment."
        exit 1
    fi
    echo_success "Virtual environment '.venv' created."
fi

# Install Dependencies
echo_info "Installing Python dependencies from requirements.txt using uv..."
if [ ! -f "requirements.txt" ]; then
    echo_error "'requirements.txt' not found in the current directory."
    exit 1
fi

# Activate venv *conceptually* for the install command
# Note: The venv won't stay active after the script exits.
if [ -f ".venv/bin/activate" ]; then
    echo_info "(Activating venv for dependency installation...)"
    # We need to run uv pip *within* the context of the activated venv conceptually.
    # Running the command directly with uv should handle this if .venv exists.
    if ! uv pip install -r requirements.txt --python .venv/bin/python; then
       echo_error "Failed to install dependencies using uv."
       exit 1
    fi
    echo_success "Dependencies installed successfully."
else
    echo_error "Virtual environment activation script not found at .venv/bin/activate"
    exit 1
fi

# --- Final Instructions ---
echo_info "------------------------------------------------------------"
echo_success "Core setup complete!" 
echo_info "Remaining Manual Steps:"
echo_info " 1. Activate the virtual environment in your terminal:"
echo "    source .venv/bin/activate" 
echo_info " 2. Configure Cursor's Python Interpreter:"
echo "    - Open this folder in Cursor."
echo "    - Cmd+Shift+P -> 'Python: Select Interpreter'"
echo "    - Select '.venv/bin/python' (or enter the full path)."
echo_info " 3. Run the sample script (after activating the venv):"
echo "    python hello_databricks.py"
echo_info "------------------------------------------------------------" 