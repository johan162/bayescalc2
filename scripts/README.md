# Build Scripts

This directory contains utility scripts for building, testing, releasing, and maintaining the BayesCalc2 project.

## Scripts Overview

### `mkbld.sh` - Main Build Script

The primary build script that runs the complete build pipeline:

```bash
./scripts/mkbld.sh [OPTIONS]
```

**Pipeline Steps:**
1. Run tests with coverage (≥80% required)
2. Update coverage badge in README.md (local only)
3. Run flake8 static analysis
4. Run mypy type checking
5. Check code formatting with black
6. Clean previous builds
7. Build package (wheel + source distribution)
8. Validate package with twine

**Options:**
- `--dry-run` - Show commands without executing them
- `--help` - Display help message

**Requirements:**
- Python 3.10+
- Virtual environment activated (`.venv/bin/activate`)
- All dev dependencies installed (`pip install -e ".[dev]"`)

**Output:**
- Test coverage report: `htmlcov/index.html`
- Coverage XML: `coverage.xml`
- Built packages: `dist/`

### `update_coverage_badge.sh` - Coverage Badge Updater

Automatically updates the coverage badge in README.md based on actual test coverage.

```bash
./scripts/update_coverage_badge.sh
```

**What it does:**
1. Reads line coverage from `coverage.xml` (line-rate attribute)
2. Converts decimal to percentage (rounded to nearest integer)
3. Determines badge color based on coverage:
   - 90%+ → brightgreen
   - 80-89% → darkgreen
   - 70-79% → yellowgreen
   - 60-69% → yellow
   - 50-59% → orange
   - <50% → red
4. Updates the coverage badge URL in `README.md`

**Requirements:**
- `coverage.xml` must exist (run tests with `--cov-report=xml`)
- `README.md` must contain a coverage badge

**Example Output:**
```
📊 Coverage line-rate: 0.8272
📊 Coverage percentage: 83%
🎨 Badge color: green
✅ Updated coverage badge in README.md to 83%
✅ Verification successful: Badge updated to 83%
🎉 Coverage badge update complete!
```

**Badge Format:**
```markdown
[![Coverage](https://img.shields.io/badge/coverage-83%25-green.svg)](https://github.com/johan162/bayescalc2)
```

### `mkrelease.sh` - Release Automation Script

Automates the complete release process from develop to main branch.

```bash
./scripts/mkrelease.sh <version> [release_type] [OPTIONS]
```

**Arguments:**
- `<version>` - Version tag (e.g., `v1.0.0`, `v2.1.0-rc1`)
- `[release_type]` - Optional: `major`, `minor`, `patch` (for changelog)

**Options:**
- `--dry-run` - Preview release steps without executing
- `--help` - Display help message

**What it does:**
1. Validates version format and prerequisites
2. Runs complete build pipeline (`mkbld.sh`)
3. Updates version in `__init__.py` and `pyproject.toml`
4. Updates or creates CHANGELOG entry
5. Commits changes on develop
6. Merges develop → main (squash merge)
7. Creates and pushes release tag
8. Syncs main back to develop
9. Cleans up build artifacts

**Requirements:**
- On `develop` branch with clean working directory
- All tests passing
- Version format: `vX.Y.Z` or `vX.Y.Z-rcN`

**Example:**
```bash
# Create release candidate
./scripts/mkrelease.sh v1.0.0-rc1 minor

# Create stable release
./scripts/mkrelease.sh v1.0.0 major

# Preview what would happen
./scripts/mkrelease.sh v1.0.1 patch --dry-run
```

### `mkghrelease.sh` - GitHub Release Creator

Creates GitHub releases using the `gh` CLI tool. **Run after `mkrelease.sh` and GitHub Actions complete.**

```bash
./scripts/mkghrelease.sh [OPTIONS]
```

**Options:**
- `--help` - Display help message
- `--pre-release` - Force marking as pre-release
- `--dry-run` - Preview without creating release

**What it does:**
1. Validates `gh` CLI is installed and authenticated
2. Checks no workflows are currently running
3. Identifies latest tag on main branch
4. Validates tag format and artifacts in `dist/`
5. Extracts release notes from CHANGELOG.md
6. Opens editor for you to review/edit notes
7. Creates GitHub release with wheel and sdist
8. Automatically determines pre-release status from tag

**Pre-release Detection:**
- Tags ending with `-rc1`, `-rc2`, etc. → Automatically marked as pre-release
- Other tags (e.g., `v1.0.0`) → Stable release
- Use `--pre-release` to force pre-release status

**Requirements:**
- GitHub CLI (`gh`) version 2.0.0+ installed
- Authenticated with GitHub (`gh auth login`)
- On `main` branch
- `mkrelease.sh` completed successfully
- All GitHub Actions workflows passed

**Example:**
```bash
# After mkrelease.sh completes and CI passes:
./scripts/mkghrelease.sh

# Force as pre-release
./scripts/mkghrelease.sh --pre-release

# Preview what would be created
./scripts/mkghrelease.sh --dry-run
```

**Artifacts uploaded:**
- `bayescalc2-X.Y.Z-py3-none-any.whl` (wheel)
- `bayescalc2-X.Y.Z.tar.gz` (source distribution)

## Usage Workflows

### Development Workflow

```bash
# Make code changes
vim src/bayescalc/commands.py

# Run full build pipeline
./scripts/mkbld.sh

# Check coverage report
open htmlcov/index.html
```

### Before Committing

```bash
# Verify everything passes
./scripts/mkbld.sh

# Review changes (including updated coverage badge)
git status
git diff README.md

# Commit
git add .
git commit -m "feat: add new feature with tests"
```

### Complete Release Workflow

```bash
# 1. Development on develop branch
git checkout develop
# ... make changes, add features ...

# 2. Build and test
./scripts/mkbld.sh

# 3. Commit changes
git add .
git commit -m "feat: add new feature"
git push origin develop

# 4. Create release (merges to main, creates tag)
./scripts/mkrelease.sh v1.0.0 major

# 5. Wait for GitHub Actions to complete
# Check: gh run list --branch main

# 6. Create GitHub release
./scripts/mkghrelease.sh

# 7. Verify release
gh release view v1.0.0
# Or visit: https://github.com/johan162/bayescalc2/releases

# 8. Optional: Upload to PyPI
python -m twine upload dist/*
```

### Release Candidate Workflow

```bash
# Create RC release
./scripts/mkrelease.sh v1.0.0-rc1 minor

# Wait for CI to pass
gh run watch

# Create pre-release on GitHub (auto-detected as pre-release)
./scripts/mkghrelease.sh

# Test the RC...
# If issues found, fix and create rc2:
./scripts/mkrelease.sh v1.0.0-rc2 minor
./scripts/mkghrelease.sh

# When ready for stable:
./scripts/mkrelease.sh v1.0.0 minor
./scripts/mkghrelease.sh
```

### CI/CD Integration

The `mkbld.sh` script automatically detects CI environments (`$CI` or `$GITHUB_ACTIONS`) and:
- Disables color output
- Skips coverage badge update (CI should not modify README)
- Generates XML coverage report for external services

## Maintenance

### Adding New Build Steps

Edit `mkbld.sh` and add your step using the `execute_cmd` function:

```bash
execute_cmd "your_command_here" "Description of what it does"
```

### Updating Coverage Thresholds

Edit the badge color mapping in `update_coverage_badge.sh`:

```bash
if [ "$coverage_percent" -ge 90 ]; then
    badge_color="brightgreen"
# ... etc
```

### Troubleshooting

**Problem: "coverage.xml not found"**
```bash
# Solution: Generate coverage report first
pytest --cov=src/bayescalc --cov-report=xml
./scripts/update_coverage_badge.sh
```

**Problem: "Badge not found in README.md"**
- Ensure README.md contains the coverage badge
- Pattern: `https://img.shields.io/badge/coverage-XX%25-COLOR.svg`

**Problem: "sed: command not found" or syntax errors**
- Script handles both macOS and Linux sed syntax
- Requires bash 3.2+

## Script Dependencies

### System Dependencies
- bash (≥3.2)
- sed
- grep
- bc (for decimal calculations)
- git

### Python Dependencies
- pytest
- pytest-cov
- flake8
- mypy
- black
- build
- twine

## Best Practices

1. **Always run `mkbld.sh` before pushing** to ensure all checks pass
2. **Keep coverage ≥80%** - builds fail below this threshold
3. **Review coverage report** after adding new features
4. **Don't manually edit coverage badge** - let the script update it
5. **Use `--dry-run`** to preview build steps without executing

## Related Documentation

- [Developer Guide](../docs/developer_guide.md) - Architecture and contribution guidelines
- [User Guide](../docs/user_guide.md) - End-user documentation
- [GitHub Workflows](../.github/workflows/) - CI/CD configuration
