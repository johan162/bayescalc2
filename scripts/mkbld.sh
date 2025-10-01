#!/bin/bash

# mkbld.sh - Build script for BayesCalc2
# This script runs tests, static analysis, formatting checks, and builds the package

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
DRY_RUN=false
HELP=false

# Function to print colored output
print_step() {
    echo -e "${BLUE}==>${NC} ${1}"
}

print_success() {
    echo -e "${GREEN}✓${NC} ${1}"
}

print_error() {
    echo -e "${RED}✗${NC} ${1}" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} ${1}"
}

# Function to execute command or print it in dry-run mode
execute_cmd() {
    local cmd="$1"
    local description="$2"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} Would execute: ${cmd}"
    else
        print_step "$description"
        echo "Executing: $cmd"
        if eval "$cmd"; then
            print_success "$description completed"
        else
            print_error "$description failed"
            exit 1
        fi
    fi
}

# Help function
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

BayesCalc2 Build Script

This script performs a complete build and validation process:
1. Runs pytest with coverage reporting
2. Performs static analysis with flake8 and mypy
3. Checks code formatting with black
4. Builds the Python package
5. Validates the built package with twine

OPTIONS:
    --dry-run       Print commands that would be executed without running them
    --help          Show this help message and exit

REQUIREMENTS:
    - Development dependencies must be installed: pip install -e ".[dev]"
    - Must be run from the project root directory

EXAMPLES:
    $0                  # Run full build process
    $0 --dry-run        # Show what would be executed
    $0 --help           # Show this help

EXIT CODES:
    0    Success
    1    Build failure (tests, linting, or package build failed)
    2    Usage error
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Use --help for usage information" >&2
            exit 2
            ;;
    esac
done

# Show help if requested
if [ "$HELP" = true ]; then
    show_help
    exit 0
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Error: pyproject.toml not found. Please run this script from the project root directory."
    exit 2
fi

# Check if dev dependencies are available
if [ "$DRY_RUN" = false ]; then
    if ! command -v pytest &> /dev/null; then
        print_error "Error: pytest not found. Please install dev dependencies: pip install -e \".[dev]\""
        exit 2
    fi
fi

echo "=========================================="
echo "  BayesCalc2 Build Script"
echo "=========================================="
echo "Branch: $(git branch --show-current)"
echo "Commit: $(git rev-parse --short HEAD)"
if [ "$DRY_RUN" = true ]; then
    print_warning "DRY-RUN MODE: Commands will be printed but not executed"
fi
echo ""

# Step 1: Run tests with coverage
execute_cmd "python -m pytest tests/ --cov=src/bayescalc --cov-report=term-missing --cov-report=html --cov-fail-under=70" "Running tests with coverage"

# Step 2: Static analysis with flake8
execute_cmd "python -m flake8 src/bayescalc tests/ --max-line-length=100 --extend-ignore=E203,W503" "Running flake8 static analysis"

# Step 3: Type checking with mypy
execute_cmd "python -m mypy src/bayescalc --ignore-missing-imports" "Running mypy type checking"

# Step 4: Code formatting check with black
execute_cmd "python -m black --check --diff src/bayescalc tests/" "Checking code formatting with black"

# Step 5: Clean previous builds
execute_cmd "rm -rf dist/ build/ src/*.egg-info/" "Cleaning previous builds"

# Step 6: Build package
execute_cmd "python -m build" "Building package"

# Step 7: Check package with twine
execute_cmd "python -m twine check dist/*" "Validating package with twine"

if [ "$DRY_RUN" = false ]; then
    echo ""
    echo "=========================================="
    print_success "Build completed successfully!"
    echo "=========================================="
    echo "Built packages:"
    ls -la dist/
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
else
    echo ""
    print_warning "DRY-RUN completed. No commands were executed."
fi