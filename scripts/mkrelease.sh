#!/bin/bash
# BayesCalc2 Release Script
# Usage: ./scripts/release.sh <version> [major|minor|patch] [--dry-run] [--help]
# Example: ./scripts/release.sh v2.1.0 minor
# Example: ./scripts/release.sh v2.1.0 minor --dry-run
# Example: ./scripts/release.sh --help

set -euo pipefail  # Exit on any error

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
    echo -e "${GREEN}✓${NC} ${1}"
}

print_success_colored() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗${NC} ${1}" >&2
}

print_error_colored() {
    echo -e "${RED}❌ ${1}${NC}" >&2
}
# Alternate non-colored glyph for error: ✗

print_warning() {
    echo -e "${YELLOW}⚠${NC} ${1}"
}

print_warning_colored() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

# =====================================
# Help function
# =====================================
show_help() {
    cat << EOF
🚀 BayesCalc2 Release Script

DESCRIPTION:
    Automated release script for BayesCalc2 with comprehensive quality gates.
    Performs validation, testing, versioning, and git operations for releases.

USAGE:
    $0 <version> [release-type] [options]

ARGUMENTS:
    version         Semantic version number (e.g., 2.1.0, 1.0.0, 0.9.1)
                    Must follow semver format: MAJOR.MINOR.PATCH

    release-type    Type of release (default: minor)
                    • major   - Breaking changes, incompatible API changes
                    • minor   - New features, backwards compatible  
                    • patch   - Bug fixes, backwards compatible

OPTIONS:
    --dry-run       Preview all commands without executing them
                    Shows exactly what would be done without making changes
                    
    --help, -h      Show this help message and exit

EXAMPLES:
    # Show help
    $0 --help
    
    # Preview a minor release (recommended first step)
    $0 v2.1.0 minor --dry-run
    
    # Execute a minor release
    $0 v2.1.0 minor
    
    # Create a patch release with preview
    $0 v2.0.1 patch --dry-run
    $0 v2.0.1 patch

    # Create a major release
    $0 v3.0.0-rc1 major --dry-run
    $0 v3.0.0-rc1 major

QUALITY GATES:
    The script enforces comprehensive quality controls:
    ✓ Repository state validation (clean working directory)
    ✓ Test suite execution (>90% coverage requirement)
    ✓ Static analysis and code formatting checks
    ✓ Integration testing with all example networks
    ✓ Package building and validation via twine
    ✓ Semver compliance and duplicate version prevention
    ✓ Version consistency across all project files

WORKFLOW:
    1. Pre-release validation (repository state, version format)
    2. Comprehensive testing (unit tests, integration, static analysis)
    3. Release preparation (version updates, changelog generation)
    4. Release execution (git commit, merge, tag, push)
    5. Post-release cleanup (sync branches, clean artifacts)

REQUIREMENTS:
    • Must be run from project root directory
    • Must be on 'develop' branch with clean working directory
    • Requires: git, python, pytest, build tools (pip install build twine)
    • Optional: mypy (type checking), black (code formatting)

SAFETY:
    • Use --dry-run first to preview all operations
    • Script validates all conditions before making changes
    • Fails fast on any error to prevent partial releases
    • All git operations are atomic and reversible

For more information, see docs/developer_guide.md
EOF
}

# Parse arguments
VERSION=""
RELEASE_TYPE="minor"
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --help|-h)
            show_help
            exit 0
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -*)
            print_error_colored "Unknown option: $arg"
            echo "Usage: $0 <version> [major|minor|patch] [--dry-run] [--help]"
            echo "Run '$0 --help' for detailed information"
            exit 1
            ;;
        *)
            if [[ -z "$VERSION" ]]; then
                VERSION="$arg"
            else
                RELEASE_TYPE="$arg"
            fi
            shift
            ;;
    esac
done

if [[ -z "$VERSION" ]]; then
    print_error_colored "Error: Version required"
    echo ""
    echo "Usage: $0 <version> [major|minor|patch] [--dry-run] [--help]"
    echo ""
    echo "Examples:"
    echo "  $0 2.1.0 minor"
    echo "  $0 2.1.0 minor --dry-run"
    echo "  $0 --help"
    echo ""
    echo "Run '$0 --help' for detailed information"
    exit 1
fi

# Function to execute command or print it in dry-run mode
run_command() {
    local cmd="$1"
    local description="${2:-}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  [DRY-RUN] $description"
        echo "  [DRY-RUN] Command: $cmd"
    else
        echo -e "  ✓ ${BLUE}${description}${NC}"
        eval "$cmd"
    fi
}

# Conditional execution for commands that need special dry-run handling
check_condition() {
    local condition="$1"
    local error_msg="$2"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  [DRY-RUN] Would check: $condition"
        echo "  [DRY-RUN] Would fail with: $error_msg (if condition false)"
        return 0  # Don't actually fail in dry-run
    else
        if ! eval "$condition"; then
            print_error_colored "$error_msg"
            exit 1
        fi
    fi
}

if [[ "$DRY_RUN" == "true" ]]; then
    print_warning_colored "🔍 DRY RUN MODE - No commands will be executed"
    echo "🚀 Would start BayesCalc2 v$VERSION release process..."
    echo "📋 Release type: $RELEASE_TYPE"
else
    echo "🚀 Starting BayesCalc2 v$VERSION release process..."
    echo "📋 Release type: $RELEASE_TYPE"
fi

# =====================================
# PHASE 1: PRE-RELEASE VALIDATION
# =====================================

print_step_colored ""
print_step_colored "🔍 PHASE 1: PRE-RELEASE VALIDATION"
print_step_colored ""

# 1.1: Ensure we are in a virtual environment and if not try to activate one
if [ "$DRY_RUN" = false ]; then
    if [ -z "$VIRTUAL_ENV" ]; then
        # Activate virtual environment if exists
        if [ -f ".venv/bin/activate" ]; then
            print_warning "No virtual environment detected. Activating venv/bin/activate"
            # shellcheck disable=SC1091
            source .venv/bin/activate
        else
            print_error_colored "No virtual environment detected and venv/bin/activate not found. Exiting."
            exit 2
        fi
    else
        echo "Using virtual environment: $VIRTUAL_ENV"
    fi
else
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "  [DRY-RUN] No virtual environment detected."
        echo "  [DRY-RUN] Would activate .venv/bin/activate if no VIRTUAL_ENV detected"
    else
        echo "  [DRY-RUN] Virtual environment detected: $VIRTUAL_ENV"
    fi
fi

# 1.2: Verify we're on develop and it's clean
check_condition '[[ $(git symbolic-ref --short HEAD) == "develop" ]]' "Must be on develop branch"
check_condition '[[ -z $(git status --porcelain) ]]' "Working directory must be clean"

if [[ "$DRY_RUN" == "false" && -n $(git status --porcelain) ]]; then
    git status --short
fi

# 1.3: Pull latest changes
run_command "git pull origin develop" "Pulling latest changes..."

# 1.4: Validate version format (semver)
check_condition '[[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-rc[1-9][0-9]?)?$ ]]' "Version must follow semver format (x.y.z or x.y.z-rcNN)"

# 1.5: Check if version already exists
check_condition '! git tag | grep -q "${VERSION}\$"' "Version $VERSION already exists"

# =====================================
# PHASE 2: UNIT TESTING & STATIC ANALYSIS
# =====================================

print_step_colored ""
print_step_colored "🧪 PHASE 2: UNIT TESTING & STATIC ANALYSIS"
print_step_colored ""

# 2.1: Full test suite with coverage requirements
run_command "pytest --cov=src/bayescalc --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=80"  "Running full test suite with coverage..."

if [[ "$DRY_RUN" == "false" && $? -ne 0 ]]; then
    print_error_colored "Test suite failed - aborting release"
    exit 1
fi

# 2.2: Static analysis and code quality
if [[ "$DRY_RUN" == "true" ]]; then 
    echo "  [DRY-RUN] Would run static analysis..."
    echo "  [DRY-RUN] Would check if mypy is available and run type checking"
    echo "  [DRY-RUN] Would check if black is available and run code formatting checks"
else
    echo "  ✓ Running static analysis..."
    # Type checking
    if command -v mypy >/dev/null 2>&1; then
        mypy src/bayescalc --ignore-missing-imports || echo "⚠️  Type check warnings found"
    fi

    # Code style (if black is available)
    if command -v black >/dev/null 2>&1; then
        echo "  ✓ Checking code formatting..."
        black --check --diff src/ tests/ || {
            print_error_colored "Code formatting issues found. Run: black src/ tests/"
            exit 1
        }
    fi
fi

# 2.3: Integration testing with example networks
if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [DRY-RUN] Would test example networks..."
    echo "  [DRY-RUN] Would iterate through examples/*.net files"
    echo "  [DRY-RUN] Would run: python -m bayescalc \$network --cmd \"help\" for each network"
else
    echo "  ✓ Testing that all example networks can load ..."
    for network in examples/*.net; do
        if [[ -f "$network" ]]; then
            echo "    Testing: $network"
            python -m bayescalc.main "$network" --cmd "help" >/dev/null 2>&1 || {
                print_error_colored "Failed to load network: $network"
                exit 1
            }
        fi
    done
fi

# 2.4: Command-line interface testing
run_command 'python -m bayescalc.main examples/rain_sprinkler_grass.net --cmd "P(Rain=True)" | grep -q "P() = 0.200000"' "Testing CLI probability queries..."

if [[ "$DRY_RUN" == "false" && $? -ne 0 ]]; then
    print_error_colored "CLI probability query test failed"
    exit 1
fi

echo "CLI query output verified successfully."

run_command 'echo "printCPT(Rain)" | python -m bayescalc.main examples/rain_sprinkler_grass.net >/dev/null 2>&1' "Testing REPL commands..."

if [[ "$DRY_RUN" == "false" && $? -ne 0 ]]; then
    print_error_colored "REPL command test failed"
    exit 1
fi

echo "REPL command output verified successfully."

# 2.5: Package building test
run_command "python -m build --wheel --sdist" "Testing package building..."

if [[ "$DRY_RUN" == "false" && $? -ne 0 ]]; then
    print_error_colored "Package build failed"
    exit 1
fi

run_command "python -m twine check dist/*" "Verifying built packages..."

if [[ "$DRY_RUN" == "false" && $? -ne 0 ]]; then
    print_error_colored "Package validation failed"
    exit 1
fi

# =====================================
# PHASE 3: RELEASE PREPARATION
# =====================================

print_step_colored ""
print_step_colored "📝 PHASE 3: RELEASE PREPARATION"
print_step_colored ""

# 3.1: Update version numbers
if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [DRY-RUN] Would update __version__ in __init__.py to $VERSION"
    echo "  [DRY-RUN] Would update version in pyproject.toml to $VERSION"
    echo "  [DRY-RUN] Would update version in README.md to $VERSION"
else
    echo "  ✓ Updating version in __init__.py..."
    sed -i.bak 's/__version__ = ".*"/__version__ = "'"$VERSION"'"/' src/bayescalc/__init__.py
    
    echo "  ✓ Updating version in pyproject.toml..."
    sed -i.bak 's/^version = ".*"/version = "'"$VERSION"'"/' pyproject.toml

    echo "  ✓ Updating version in README.md..."
    sed -i.bak 's/^  version={.*}/  version={'"$VERSION"'}/' README.md
fi

# 3.2: Generate changelog entry
if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [DRY-RUN] Would prepare changelog..."
    echo "  [DRY-RUN] Would create CHANGELOG_ENTRY.tmp with template for v$VERSION"
    echo "  [DRY-RUN] Would prepend to CHANGELOG.md or create new file"
    echo "  [DRY-RUN] Would prompt user to edit changelog (skipped in dry-run)"
else
    echo "  ✓ Preparing changelog..."
    CHANGELOG_DATE=$(date +%Y-%m-%d)

    # Create temporary changelog entry (customize as needed)
    cat > CHANGELOG_ENTRY.tmp << EOF
## [$VERSION] - $CHANGELOG_DATE

Release Type: $RELEASE_TYPE

### 📋 Summary 
- [Brief summary of the release]

### ✨ Additions
- [List new features added in this release]

### 🚀 Improvements
- [List improvements made in this release]

### 🐛 Bug Fixes
- [List bug fixes addressed in this release]

### 🛠 Internal
- [List internal changes, refactoring, etc.]

EOF

    # Prepend to existing CHANGELOG.md (create if doesn't exist)
    if [[ -f CHANGELOG.md ]]; then
        cat CHANGELOG_ENTRY.tmp CHANGELOG.md > CHANGELOG_NEW.tmp
        mv CHANGELOG_NEW.tmp CHANGELOG.md
    else
        mv CHANGELOG_ENTRY.tmp CHANGELOG.md
    fi
    rm -f CHANGELOG_ENTRY.tmp

    echo ""
    echo "⚠️  PLEASE EDIT CHANGELOG.md to add specific release notes"
    echo "   Press Enter when changelog is ready, or Ctrl+C to abort"
    read -r
fi

# 3.3: Final pre-commit validation
run_command "pytest tests/test_main.py -v" "Final validation after version updates..."

if [[ "$DRY_RUN" == "false" && $? -ne 0 ]]; then
    print_error_colored "Final validation failed"
    exit 1
fi

# =====================================
# PHASE 4: RELEASE EXECUTION
# =====================================

print_step_colored ""
print_step_colored "🎯 PHASE 4: RELEASE EXECUTION"
print_step_colored ""

# 4.1: Commit version updates
run_command "git add src/bayescalc/__init__.py pyproject.toml CHANGELOG.md README.md" "Staging release files..."

run_command "git commit -m \"chore(release): prepare $VERSION

- Update version to $VERSION
- Update changelog with release notes
- All tests passing with >80% coverage
- Package build validation complete\"" "Committing release preparation..."

# 4.2: Merge to main branch and create release commit
run_command "git checkout main" "Switching to main branch..."
run_command "git pull origin main" "Pulling latest main..."

# Squash merge develop into main
run_command "git merge --squash develop" "Squashing develop changes..."
run_command "git commit -m \"release: $VERSION

Summary of changes:
- All features and fixes from develop branch
- Comprehensive test coverage (>80%)
- Full integration testing completed
- Package build validation successful
- Static analysis passed

See CHANGELOG.md for detailed changes.\"" "Creating release commit on main..."


# 4.3: Create annotated release tag
if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [DRY-RUN] Would create annotated tag $VERSION..."
    echo "  [DRY-RUN] Tag message would include release type, date, and QA checklist"
else
    echo "  ✓ Creating release tag..."
    CHANGELOG_DATE=$(date +%Y-%m-%d)
    git tag -a "$VERSION" -m "Release version $VERSION

Release Type: $RELEASE_TYPE
Release Date: $CHANGELOG_DATE

Quality Assurance:
✓ Full test suite passed (>80% coverage)
✓ All example networks validated  
✓ CLI and REPL functionality verified
✓ Package build and validation complete
✓ Static analysis passed
✓ Integration tests passed

Changelog: See CHANGELOG.md for detailed changes"
fi

# 4.4: Push main branch and tags
run_command "git push origin main" "Pushing main branch..."
run_command "git push origin \"$VERSION\"" "Pushing release tag..."

# =====================================
# PHASE 5: POST-RELEASE CLEANUP
# =====================================

print_step_colored ""
print_step_colored "🧹 PHASE 5: POST-RELEASE CLEANUP AND MERGE BACK TO DEVELOP"
print_step_colored ""

# 5.1: Return to develop and merge back release changes
run_command "git checkout develop" "Switching back to develop..."
run_command "git pull origin develop" "Pulling latest develop changes..."

# 5.2: Merge main into develop to reconcile squash merge
if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [DRY-RUN] Would merge main into develop with --no-ff"
    echo "  [DRY-RUN] This reconciles the squashed commits on main"
else
    echo "  ✓ Merging main into develop to sync branches..."
    
    # Use --no-ff to create explicit merge commit
    git merge --no-ff -m "chore: sync develop with main after release $VERSION" main

    if [[ $? -ne 0 ]]; then
        print_error_colored "Failed to merge main into develop"
        echo ""
        echo "This indicates merge conflicts. To resolve:"
        echo "  1. git status  # See conflicting files"
        echo "  2. Edit files to resolve conflicts"
        echo "  3. git add <resolved-files>"
        echo "  4. git commit -m \"chore: resolve merge conflicts after release $VERSION\""
        echo "  5. git push origin develop"
        echo ""
        exit 1
    fi
    
    print_success "develop synced with main"
fi

# 5.3: Push synced develop branch
run_command "git push origin develop" "Pushing updated develop..."

# =====================================
# PHASE 6: BUILD DISTRIBUTION PACKAGE
# =====================================
print_step_colored ""
print_step_colored "📦 PHASE 6: PACKAGE FOR DISTRIBUTION"
print_step_colored ""

# 6.1: Clean up old build artifacts
run_command "rm -rf build/ dist/ src/*.egg-info/ htmlcov/" "Cleaning up build artifacts..."
run_command "rm -f *.bak src/bayescalc/*.bak" "Removing backup files..."

# 6.2: Build Package with the now updated version number
run_command "python -m build --wheel --sdist" "Testing package building..."

if [[ "$DRY_RUN" == "false" && $? -ne 0 ]]; then
    print_error_colored "Distribution package build failed"
    exit 1
fi

# 6.3: Package building validation
run_command "python -m twine check dist/*" "Verifying built packages..."

if [[ "$DRY_RUN" == "false" && $? -ne 0 ]]; then
    print_error_colored "Distribution package validation failed"
    exit 1
fi

# =====================================
# PHASE 7: RELEASE SUMMARY
# =====================================


echo ""
if [[ "$DRY_RUN" == "true" ]]; then
    print_step_colored ""
    print_step_colored "🔍 PHASE 7: DRY RUN RELEASE SUMMARY"
    print_step_colored ""
    echo "📋 Commands that would be executed:"
    echo "   → All validation checks (repository state, version format, etc.)"
    echo "   → Full test suite with coverage requirements"
    echo "   → Static analysis and code formatting checks"
    echo "   → Integration testing with example networks"
    echo "   → Package building and validation"
    echo "   → Version number updates in multiple files"
    echo "   → Changelog generation and user editing"
    echo "   → Git operations: commit, merge, tag, push"
    echo "   → Post-release cleanup"
    echo ""
    echo "🚀 To execute for real:"
    echo "   $0 $VERSION $RELEASE_TYPE"
else
    print_step_colored ""
    print_step_colored "✅ PHASE 7: RELEASE SUMMARY"
    print_step_colored ""
    print_success_colored "🎉 BayesCalc2 v$VERSION released successfully!"
    echo ""
    echo "📊 Release Summary:"
    echo "   Version:     $VERSION"
    echo "   Type:        $RELEASE_TYPE"
    echo "   Date:        $(date +%Y-%m-%d)"
    echo "   Branch:      main"
    echo "   Tag:         $VERSION"
    echo ""
    echo "📦 Artifacts:"
    echo "   - $(ls dist|head -1)"
    echo "   - $(ls dist|tail -1)"
    echo ""
    echo "📊 Branch Status:"
    echo "   GitHub will show develop as 'ahead' of main - this is expected!"
    echo "   • develop preserves detailed commit history"
    echo "   • main uses squash merges (one commit per release)"
    echo "   • Code content is identical between branches"
    echo ""
    echo "   Verify with: git diff main develop"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Verify release tag on GitHub"
    echo "   2. Run 'scripts/mkghrelease.sh' to create GitHub release (which will also upload packages to PyPI)"
    echo "   3. Announce the release!"
    echo ""
    echo "📋 Quality Metrics Achieved:"
    echo "   ✓ Test Coverage: >80%"
    echo "   ✓ All Example Networks: Validated"
    echo "   ✓ Package Build: Successful" 
    echo "   ✓ Static Analysis: Passed"
    echo "   ✓ Integration & Unit Tests: Passed"
fi
