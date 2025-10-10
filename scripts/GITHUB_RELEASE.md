# GitHub Release Script Documentation

## Overview

`mkghrelease.sh` automates GitHub release creation using the `gh` CLI tool. It's designed to be run **after** `mkrelease.sh` completes and all GitHub Actions workflows pass.

## Installation Prerequisites

### Install GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
sudo apt-add-repository https://cli.github.com/packages
sudo apt update
sudo apt install gh

# Fedora
sudo dnf install gh

# Windows
winget install --id GitHub.cli
```

### Authenticate with GitHub

```bash
# Interactive authentication
gh auth login

# Select: GitHub.com
# Select: HTTPS
# Authenticate with: Login with a web browser
# Follow the prompts
```

### Verify Installation

```bash
gh --version
# Should show: gh version 2.0.0 or higher

gh auth status
# Should show: Logged in to github.com as <username>
```

## Usage

### Basic Release Creation

```bash
# After mkrelease.sh completes:
./scripts/mkghrelease.sh
```

This will:
1. Check prerequisites
2. Verify no workflows are running
3. Extract release notes from CHANGELOG.md
4. Open editor for you to review/edit notes
5. Create GitHub release with artifacts
6. Upload wheel and sdist files

### Pre-release Creation

```bash
# For release candidates (auto-detected from tag):
./scripts/mkghrelease.sh
# Tag v1.0.0-rc1 → automatically marked as pre-release

# Force pre-release regardless of tag:
./scripts/mkghrelease.sh --pre-release
```

### Dry Run (Preview)

```bash
# See what would be done without executing:
./scripts/mkghrelease.sh --dry-run
```

## Complete Workflow Example

```bash
# Step 1: Create release on local/GitHub
./scripts/mkrelease.sh v1.0.0 major

# Step 2: Wait for CI to complete
gh run list --branch main
# Or watch in real-time:
gh run watch

# Step 3: Verify CI passed
gh run list --branch main --limit 1

# Step 4: Create GitHub release
./scripts/mkghrelease.sh

# Step 5: Verify release
gh release view v1.0.0
# Or visit: https://github.com/johan162/bayescalc2/releases/tag/v1.0.0
```

## Release Notes Editing

The script extracts release notes from CHANGELOG.md and opens your editor:

### Default Editor Priority

1. `$EDITOR` environment variable
2. `$VISUAL` environment variable
3. `nano` (fallback)

### Set Your Preferred Editor

```bash
# In ~/.bashrc or ~/.zshrc
export EDITOR=vim
# or
export EDITOR=code  # VS Code
# or
export EDITOR=nano
```

### Release Notes Format

The script extracts the section matching your tag from CHANGELOG.md:

```markdown
## [v1.0.0] - 2025-10-10

### 📋 Summary
Major refactor with new inference algorithm...

### ✨ Additions
- New load() command
- Graph visualization

### 🚀 Improvements
- Faster inference engine
- Better error messages
```

You can edit this before the release is created.

## Troubleshooting

### Error: "gh is not installed"

```bash
# Install gh CLI (see Installation Prerequisites above)
brew install gh  # macOS
```

### Error: "Not authenticated with GitHub"

```bash
gh auth login
# Follow the prompts
```

### Error: "There are N workflow(s) currently running"

```bash
# Wait for workflows to complete
gh run list --branch main

# Watch in real-time
gh run watch
```

### Error: "Latest workflow did not succeed"

```bash
# Check workflow status
gh run list --branch main --limit 5

# View specific run details
gh run view <run-id>

# Fix the issue and re-run workflows
```

### Error: "Release v1.0.0 already exists"

```bash
# Option 1: Delete and recreate
gh release delete v1.0.0
./scripts/mkghrelease.sh

# Option 2: Create new version
./scripts/mkrelease.sh v1.0.1 patch
./scripts/mkghrelease.sh
```

### Error: "Wheel file not found for version X.Y.Z"

```bash
# Rebuild the package
./scripts/mkbld.sh

# Or re-run release script
./scripts/mkrelease.sh v1.0.0 major
```

### Error: "Must be on 'main' branch"

```bash
git checkout main
git pull origin main
./scripts/mkghrelease.sh
```

## Pre-release vs Stable Release

### Automatic Detection

The script automatically determines release type:

| Tag Format | Release Type | Example |
|------------|--------------|---------|
| `vX.Y.Z-rcN` | Pre-release | `v1.0.0-rc1`, `v2.1.0-rc5` |
| `vX.Y.Z` | Stable | `v1.0.0`, `v2.1.0` |

### Force Pre-release

```bash
# Override automatic detection
./scripts/mkghrelease.sh --pre-release
# Even v1.0.0 will be marked as pre-release
```

## Artifacts Uploaded

For each release, the script uploads:

1. **Wheel file**: `bayescalc2-X.Y.Z-py3-none-any.whl`
   - Binary distribution
   - Fast installation
   - Platform independent

2. **Source distribution**: `bayescalc2-X.Y.Z.tar.gz`
   - Complete source code
   - Includes all files from MANIFEST.in
   - For building from source

Both files are validated for:
- Correct version number in filename
- Minimum file size (> 1KB)
- Existence in `dist/` directory

## Integration with PyPI

After creating GitHub release, optionally upload to PyPI:

```bash
# Test PyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Production PyPI
python -m twine upload dist/*
```

## Script Exit Codes

- `0` - Success
- `1` - Error (validation failed, prerequisites not met, etc.)
- `130` - User aborted (Ctrl+C or empty release notes)

## Environment Variables

None required. The script uses:
- `$EDITOR` or `$VISUAL` - For editing release notes
- Git repository context (branch, tags, etc.)

## Files Created/Modified

### Temporary Files
- `.github_release_notes.tmp` - Extracted release notes (deleted after use)

### No Permanent Changes
The script does NOT modify:
- Git repository (no commits, tags, or branch changes)
- Source code
- CHANGELOG.md
- Version files

All changes should be done via `mkrelease.sh` before running this script.

## Security Considerations

- Requires GitHub authentication via `gh auth`
- Uses existing git tags (no new tags created)
- Only uploads files from `dist/` directory
- Validates artifact names match tag version

## Best Practices

1. **Always run mkrelease.sh first**
   ```bash
   ./scripts/mkrelease.sh v1.0.0 major
   ```

2. **Wait for CI to complete**
   ```bash
   gh run watch
   ```

3. **Review artifacts before release**
   ```bash
   ls -lh dist/
   ```

4. **Use dry-run for first-time releases**
   ```bash
   ./scripts/mkghrelease.sh --dry-run
   ```

5. **Keep CHANGELOG.md updated**
   - Script extracts notes from here
   - Better notes = better release documentation

## See Also

- [scripts/mkrelease.sh](mkrelease.sh ) - Create the release (run first)
- [scripts/mkbld.sh](mkbld.sh ) - Build and test the package
- [scripts/README.md](README.md ) - Complete scripts documentation
- [GitHub CLI documentation](https://cli.github.com/manual/)
