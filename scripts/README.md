# Build Scripts

This directory contains utility scripts for building, testing, and maintaining the BayesCalc2 project.

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
