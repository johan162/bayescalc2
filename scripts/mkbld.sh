#!/bin/bash
# BayesCalc2 Build Script
# Description: Automates testing, static analysis, formatting checks, and package building for BayesCalc2.
# CI/CD Support: Yes. Can be run in CI environments.
# Usage: ./scripts/mkbld.sh [--dry-run] [--help]
#
# Example: ./scripts/mkbld.sh
# Example: ./scripts/mkbld.sh --dry-run
# Example: ./scripts/mkbld.sh --help

set -euo pipefail # Exit on any error or uninitialized variable

# Detect CI environment
if [ -n "${CI:-}" ] || [ -n "${GITHUB_ACTIONS:-}" ]; then
    echo "🔧 Running in CI mode"
    CI_MODE=true
else
    echo "🔧 Running in local mode"
    CI_MODE=false
fi

# Color codes (disabled in CI)
if [ "$CI_MODE" = true ]; then
    GREEN=""
    RED=""
    YELLOW=""
    BLUE=""
    NC=""
else
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
fi

# Default options
DRY_RUN=false
HELP=false

# =====================================
# Functions to print colored output
# =====================================
print_step() {
    echo -e "${BLUE}==>${NC} ${1}"
}

print_step_colored() {
    echo -e "${BLUE}==> ${1}${NC}"
}

print_sub_step() {
    echo -e "${BLUE}  ->${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ Success: ${1}${NC}"
}

print_success_colored() {
    if [ "$CI_MODE" = true ]; then
        echo -e "✓ Success: ${1}"
    else
        echo -e "${GREEN}✅ Success: ${1}${NC}"
    fi
}

print_error() {
    echo -e "${RED}✗ Error: ${NC} ${1}" >&2
}

print_error_colored() {
    if [ "$CI_MODE" = true ]; then
        echo -e "✗ Error: ${1}"
    else
        echo -e "${RED}❌ Error: ${1}${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠ Warning:${NC} ${1}"
}

print_warning_colored() {
    if [ "$CI_MODE" = true ]; then
        echo -e "⚠ Warning: ${1}"
    else
        echo -e "${YELLOW}⚠️  Warning: ${1}${NC}"
    fi
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_info_colored() {
    if [ "$CI_MODE" = true ]; then
        echo -e "ℹ $1"
    else
        echo -e "${BLUE}ℹ️  ${1}${NC}"
    fi
}

# Function to execute command or print it in dry-run mode
run_command() {
    local cmd="$1"
    local description="$2"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} Would execute: ${cmd}"
    else
        print_sub_step "$description"
        echo "Executing: $cmd"
        if eval "$cmd"; then
            print_success_colored "$description completed"
        else
            print_error_colored "$description failed"
            exit 1
        fi
    fi
}

# Help function
show_help() {
    cat << EOF
🚀 BayesCalc2 Build Script

DESCRIPTION:
    This script automates the build and validation process for the BayesCalc2 project.
    It runs tests, performs static analysis, checks code formatting, builds the package,
    and validates the built package.
    
    This script performs a complete build and validation process:
    1. Runs pytest with coverage reporting
    2. Performs static analysis with flake8 and mypy
    3. Checks code formatting with black
    4. Builds the Python package
    5. Validates the built package with twine 

USAGE: 
    $0 [OPTIONS]

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



echo "=========================================="
echo "  BayesCalc2 Build Script"
echo "=========================================="
echo "Branch: $(git branch --show-current)"
echo "Commit: $(git rev-parse --short HEAD)"
if [ "$DRY_RUN" = true ]; then
    print_warning ""
    print_warning_colored "DRY-RUN MODE: Commands will be printed but not executed!"
    print_warning ""
fi
echo ""

# =====================================
# PHASE 1: PRE-BUILD VALIDATION
# =====================================

print_step_colored ""
print_step_colored "🔍 PHASE 1: PRE-BUILD VALIDATION"
print_step_colored ""

# Check if we're in the root directory (pyproject.toml must exist)
run_command "test -f pyproject.toml" "Build script must be run from project root."

# Check if dev dependencies are available
if [ "$DRY_RUN" = false ]; then
    if ! command -v pytest &> /dev/null; then
        print_error "Error: pytest not found. Please install dev dependencies: pip install -e \".[dev]\""
        exit 2
    fi
fi

# If not in CI mode, ensure we are in a virtual environment
print_sub_step "Updating virtual environment if needed"
if [ "$CI_MODE" = false ]; then
    # Step 0: Verify we are running in a virtual environment and if not try to activate one
    if [ "$DRY_RUN" = false ]; then
        if [ -z "$VIRTUAL_ENV" ]; then
            # Activate virtual environment if exists
            if [ -f ".venv/bin/activate" ]; then
                print_warning "No virtual environment detected. Activating venv/bin/activate"
                # shellcheck disable=SC1091
                source .venv/bin/activate
            else
                print_warning "No virtual environment detected and venv/bin/activate not found. Exiting."
                exit 2
            fi
        else
            echo "Using virtual environment: $VIRTUAL_ENV"
        fi
    fi
fi

# =====================================
# PHASE 2: RUN TESTS WITH COVERAGE
# =====================================

echo ""
print_step_colored ""
print_step_colored "🧪 PHASE 2: CHECKING UNIT TESTS & COVERAGE"
print_step_colored ""

# Step 2.1: Run tests with coverage
run_command "python -m pytest tests/ --cov=src/bayescalc --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=80" "Running tests with coverage"

# Step 2.2: Update coverage badge in README
if [ "$CI_MODE" = false ] && [ "$DRY_RUN" = false ]; then
    print_sub_step "Updating coverage badge in README.md"
    if [ -f "scripts/mkcovupd.sh" ]; then
        ./scripts/mkcovupd.sh
    else
        print_warning "Coverage badge update script not found"
    fi
fi

# =======================================
# PHASE 3: STATIC ANALYSIS AND FORMATTING
# =======================================

echo ""
print_step_colored ""
print_step_colored "🧪 PHASE 3: STATIC ANALYSIS WITH FLAKE8, MYPY, AND BLACK"
print_step_colored ""

# Step 3.1: Static analysis with flake8
run_command "python -m flake8 src/bayescalc tests/ --max-line-length=120 --extend-ignore=E203,W503,E501,E402" "Running flake8 static analysis"

# Step 3.2: Type checking with mypy
run_command "python -m mypy src/bayescalc --ignore-missing-imports" "Running mypy type checking"

# Step 3.3: Code formatting check with black
run_command "python -m black --check --diff src/bayescalc tests/" "Checking code formatting with black"

# =======================================
# PHASE 4: BUILD AND VALIDATE PACKAGE
# =======================================

echo ""
print_step_colored ""
print_step_colored "📦 PHASE 4: PACKAGE BUILD & VALIDATION"
print_step_colored ""

# Step 4.1: Clean previous builds
run_command "rm -rf dist/ build/ src/*.egg-info/" "Cleaning previous builds"

# Step 4.2: Build package
run_command "python -m build" "Building package"

# Step 4.3: Check package with twine
run_command "python -m twine check dist/*" "Validating package with twine"


# =======================================
# PHASE 5: BUILD SUMMARY
# =======================================

if [ "$DRY_RUN" = false ]; then
    LAST_COMMIT_SHORT=$(git rev-parse --short HEAD)
    TIMESTAMP=$(git log -1 --format=%ct)
    LAST_COMMIT_DATE_TIME=$(TZ=UTC git log -1 --format=%cd --date=format-local:'%Y-%m-%d %H:%M:%S UTC')
    LAST_COMMIT_BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
    echo ""
    print_step_colored "=========================================="
    print_success_colored "BUILD COMPLETED SUCCESSFULLY!"
    print_step_colored "=========================================="
    echo ""
    echo "📊 Build Summary:"
    echo "     Last commit: ${LAST_COMMIT_SHORT} on ${LAST_COMMIT_BRANCH_NAME}"
    echo "     Date:        ${LAST_COMMIT_DATE_TIME}"
    echo "     Build date:  $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    echo ""
    echo "📦 Artifacts:"
    if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
        for file in dist/*; do
            if [ -f "$file" ]; then
                FILENAME=$(basename "$file")
                SIZE=$(ls -lh "$file" | awk '{print $5}')
                echo -e "     - ${FILENAME}: ${BLUE}${SIZE}${NC}"
            fi
        done
    else
        print_warning "No artifacts found in 'dist/'!"
    fi
    echo ""
    echo "📊 Coverage report:"
    echo "     - [htmlcov/index.html](htmlcov/index.html)"
else
    echo ""
    print_warning_colored "DRY-RUN completed. No commands were executed."
fi

echo ""
exit 0
# End of script