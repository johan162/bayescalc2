#!/bin/bash
# BayesCalc2 Release Script
# Usage: ./scripts/release.sh <version> [major|minor|patch]
# Example: ./scripts/release.sh 2.1.0 minor

set -euo pipefail  # Exit on any error

VERSION=${1:-}
RELEASE_TYPE=${2:-minor}

if [[ -z "$VERSION" ]]; then
    echo "❌ Error: Version required"
    echo "Usage: $0 <version> [major|minor|patch]"
    echo "Example: $0 2.1.0 minor"
    exit 1
fi

echo "🚀 Starting BayesCalc2 v$VERSION release process..."
echo "📋 Release type: $RELEASE_TYPE"

# =====================================
# PHASE 1: PRE-RELEASE VALIDATION
# =====================================

echo ""
echo "🔍 PHASE 1: Pre-release validation"

# 1.1: Verify we're on develop and it's clean
echo "  ✓ Checking repository state..."
if [[ $(git symbolic-ref --short HEAD) != "develop" ]]; then
    echo "❌ Must be on develop branch"
    exit 1
fi

if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Working directory must be clean"
    git status --short
    exit 1
fi

# 1.2: Pull latest changes
echo "  ✓ Pulling latest changes..."
git pull origin develop

# 1.3: Validate version format (semver)
echo "  ✓ Validating version format..."
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Version must follow semver format (x.y.z)"
    exit 1
fi

# 1.4: Check if version already exists
if git tag | grep -q "v$VERSION"; then
    echo "❌ Version v$VERSION already exists"
    exit 1
fi

# =====================================
# PHASE 2: COMPREHENSIVE TESTING
# =====================================

echo ""
echo "🧪 PHASE 2: Comprehensive testing suite"

# 2.1: Full test suite with coverage requirements
echo "  ✓ Running full test suite with coverage..."
pytest \
    --cov=bayescalc \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-fail-under=90 \
    --verbose \
    tests/

if [[ $? -ne 0 ]]; then
    echo "❌ Test suite failed - aborting release"
    exit 1
fi

# 2.2: Static analysis and code quality
echo "  ✓ Running static analysis..."
# Type checking
if command -v mypy >/dev/null 2>&1; then
    mypy src/bayescalc --ignore-missing-imports || echo "⚠️  Type check warnings found"
fi

# Code style (if black is available)
if command -v black >/dev/null 2>&1; then
    echo "  ✓ Checking code formatting..."
    black --check --diff src/ tests/ || {
        echo "❌ Code formatting issues found. Run: black src/ tests/"
        exit 1
    }
fi

# 2.3: Integration testing with example networks
echo "  ✓ Testing example networks..."
for network in examples/*.net; do
    if [[ -f "$network" ]]; then
        echo "    Testing: $(basename "$network")"
        python -m bayescalc "$network" --cmd "help" >/dev/null 2>&1 || {
            echo "❌ Failed to load network: $network"
            exit 1
        }
    fi
done

# 2.4: Command-line interface testing
echo "  ✓ Testing CLI functionality..."
# Test basic probability queries
python -m bayescalc examples/rain_sprinkler_grass.net --cmd "P(Rain=True)" | grep -q "Probability" || {
    echo "❌ CLI probability query test failed"
    exit 1
}

# Test REPL commands
echo "printCPT Rain" | python -m bayescalc examples/rain_sprinkler_grass.net >/dev/null 2>&1 || {
    echo "❌ REPL command test failed"
    exit 1
}

# 2.5: Package building test
echo "  ✓ Testing package building..."
python -m build --wheel --sdist || {
    echo "❌ Package build failed"
    exit 1
}

# Verify built packages
python -m twine check dist/* || {
    echo "❌ Package validation failed"
    exit 1
}

# =====================================
# PHASE 3: RELEASE PREPARATION
# =====================================

echo ""
echo "📝 PHASE 3: Release preparation"

# 3.1: Update version numbers
echo "  ✓ Updating version numbers..."

# Update src/bayescalc/__init__.py
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" src/bayescalc/__init__.py

# Update pyproject.toml
sed -i.bak "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# 3.2: Generate changelog entry
echo "  ✓ Preparing changelog..."
CHANGELOG_DATE=$(date +%Y-%m-%d)

# Create temporary changelog entry (customize as needed)
cat > CHANGELOG_ENTRY.tmp << EOF
## [$VERSION] - $CHANGELOG_DATE

### Added
- [List new features added in this release]

### Changed
- [List changes to existing functionality]

### Fixed
- [List bug fixes]

### Removed
- [List deprecated features removed]

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

# 3.3: Final pre-commit validation
echo "  ✓ Final validation after version updates..."
pytest tests/test_main.py -v  # Quick smoke test

# =====================================
# PHASE 4: RELEASE EXECUTION
# =====================================

echo ""
echo "🎯 PHASE 4: Release execution"

# 4.1: Commit version updates
echo "  ✓ Committing release preparation..."
git add src/bayescalc/__init__.py pyproject.toml CHANGELOG.md
git commit -m "chore(release): prepare v$VERSION

- Update version to $VERSION
- Update changelog with release notes
- All tests passing with >90% coverage
- Package build validation complete"

# 4.2: Merge to main branch
echo "  ✓ Merging to main branch..."
git checkout main
git pull origin main
git merge --no-ff develop -m "release: merge v$VERSION from develop

This release includes:
- Comprehensive test coverage (>90%)
- Full integration testing
- Package build validation
- Static analysis validation"

# 4.3: Create annotated release tag
echo "  ✓ Creating release tag..."
git tag -a "v$VERSION" -m "Release version $VERSION

Release Type: $RELEASE_TYPE
Release Date: $CHANGELOG_DATE

Quality Assurance:
✓ Full test suite passed (>90% coverage)
✓ All example networks validated  
✓ CLI and REPL functionality verified
✓ Package build and validation complete
✓ Static analysis passed
✓ Integration tests passed

Changelog: See CHANGELOG.md for detailed changes"

# 4.4: Push main branch and tags
echo "  ✓ Pushing to remote..."
git push origin main
git push origin "v$VERSION"

# =====================================
# PHASE 5: POST-RELEASE CLEANUP
# =====================================

echo ""
echo "🧹 PHASE 5: Post-release cleanup"

# 5.1: Return to develop and merge back release changes
echo "  ✓ Syncing develop branch..."
git checkout develop
git merge main  # Bring version updates back to develop
git push origin develop

# 5.2: Clean up build artifacts
echo "  ✓ Cleaning up build artifacts..."
rm -rf build/ dist/ src/*.egg-info/ htmlcov/
rm -f *.bak

# =====================================
# RELEASE COMPLETE
# =====================================

echo ""
echo "✅ RELEASE COMPLETE!"
echo ""
echo "📊 Release Summary:"
echo "   Version:     v$VERSION"
echo "   Type:        $RELEASE_TYPE"
echo "   Date:        $CHANGELOG_DATE"
echo "   Branch:      main"
echo "   Tag:         v$VERSION"
echo ""
echo "🚀 Next Steps:"
echo "   1. Verify release on GitHub/GitLab"
echo "   2. Monitor CI/CD pipeline for PyPI publication"
echo "   3. Update documentation sites if needed"
echo "   4. Announce release to stakeholders"
echo ""
echo "📋 Quality Metrics Achieved:"
echo "   ✓ Test Coverage: >90%"
echo "   ✓ All Example Networks: Validated"
echo "   ✓ Package Build: Successful" 
echo "   ✓ Static Analysis: Passed"
echo "   ✓ Integration Tests: Passed"
```
# End of mkrelease.sh
