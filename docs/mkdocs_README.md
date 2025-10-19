# MkDocs Documentation Setup - Summary

## Overview

For Bayescalc2 we use a MkDocs documentation system with the Material theme and mkdocstrings for auto-generating API documentation from Python docstrings. The generated documentaton (HTML-format) is stored in the `gh_pages` branch of the repo and is mapped the URL [https://johan162.github.io/bayescalc2/](https://johan162.github.io/bayescalc2/).


## Files Used for the Documentation Setup

### Configuration Files

1. **`mkdocs.yml`** - Main MkDocs configuration
   - Material theme with dark/light mode toggle
   - Navigation structure with sections:
     - Home (landing page)
     - User Guide
     - Developer Guide  
     - Examples (detailed usage examples)
     - API Reference (auto-generated from code)
     - Changelog (symlinked from root)
   - mkdocstrings plugin for API docs
   - Markdown extensions (syntax highlighting, admonitions, tabs, etc.)

### Documentation Pages

2. **`docs/index.md`** - Landing page
   - Project overview and features
   - Quick start guide
   - Installation instructions
   - Links to other documentation sections
   - Architecture diagram

3. **`docs/examples.md`** - Comprehensive examples
   - Medical diagnosis network
   - Weather prediction (rain/sprinkler)
   - Student performance network
   - Asia chest clinic
   - Boolean shorthand examples
   - Expression evaluation
   - Batch processing
   - Network visualization
   - Tips and tricks

4. **`docs/api/index.md`** - API reference overview
   - Architecture explanation
   - Module organization
   - Usage patterns
   - Testing information
   - Extension points

5. **API Documentation Pages** (auto-generated with mkdocstrings):
   - `docs/api/network_model.md` - Core data structures
   - `docs/api/parser.md` - Network file parser
   - `docs/api/lexer.md` - Tokenizer
   - `docs/api/inference.md` - Inference engine
   - `docs/api/queries.md` - Query parser
   - `docs/api/expression_parser.md` - Expression evaluator
   - `docs/api/repl.md` - Interactive shell
   - `docs/api/commands.md` - Command handlers
   - `docs/api/completer.md` - Tab completion
   - `docs/api/batch.md` - Batch processing

6. **`docs/CHANGELOG.md`** - Symlink to root CHANGELOG.md

### Scripts

7. **`scripts/mkdocs.sh`** - Documentation build/deploy script
   - Commands:
     - `serve` - Start local dev server at http://127.0.0.1:8000
     - `build` - Build static site to `site/`
     - `deploy` - Deploy to GitHub Pages (gh-pages branch)
     - `clean` - Remove built site
   - Auto-detects and activates virtual environment
   - Creates CHANGELOG symlink automatically
   - Checks for required dependencies

### CI/CD

8. **`.github/workflows/docs.yml`** - Documentation workflow
   - Triggers on:
     - Push to `main` or `develop` branches
     - Pull requests to `main` or `develop`
     - Changes to docs, mkdocs.yml, or source code
     - Manual workflow dispatch
   - Jobs:
     - **build**: Build documentation and upload artifact
     - **deploy**: Deploy to GitHub Pages (only on main branch pushes)
   - Uses Python 3.11 with pip caching
   - Configures git for gh-pages deployment

## Documentation Structure

```
docs/
├── index.md                    # Landing page
├── user_guide.md              # Existing user guide
├── developer_guide.md         # Existing developer guide
├── examples.md                # New: Comprehensive examples
├── CHANGELOG.md               # Symlink to ../CHANGELOG.md
└── api/                       # API reference (auto-generated)
    ├── index.md               # API overview
    ├── network_model.md       # Core data structures
    ├── parser.md              # Network parser
    ├── lexer.md               # Tokenizer
    ├── inference.md           # Inference engine
    ├── queries.md             # Query parser
    ├── expression_parser.md   # Expression evaluator
    ├── repl.md                # Interactive REPL
    ├── commands.md            # Command handlers
    ├── completer.md           # Tab completion
    └── batch.md               # Batch processing
```

## Usage

### Local Development

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Start development server (with live reload)
./scripts/mkdocs.sh serve

# View at http://127.0.0.1:8000
```

### Building

```bash
# Build static site
./scripts/mkdocs.sh build

# Output in site/ directory
```

### Deployment

Documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch via the GitHub Actions workflow.

Manual deployment (maintainers only):
```bash
./scripts/mkdocs.sh deploy
```

This deploys to the `gh-pages` branch and makes the documentation available at:
**https://johan162.github.io/bayescalc2/**

## Features

### Material Theme
- Light/dark mode toggle (respects system preferences)
- Instant navigation
- Navigation tabs and sections
- Search with highlighting
- Code copy buttons
- Responsive design

### mkdocstrings
- Auto-generates API documentation from Python docstrings
- Shows source code
- Cross-references between modules
- Inheritance diagrams
- Type annotations

### Markdown Extensions
- Syntax highlighting with line numbers
- Admonitions (notes, warnings, tips)
- Tabbed content
- Task lists
- Emoji support
- Table of contents with permalinks
- Mermaid diagram support (for future use)

## Notes

### Warnings During Build

The following warnings appear during build but are non-critical:

1. **Unused pages**: `BayesCalcReq.md`, `github_changelog_template.md` and `mkdocs_README.md`  are not included in navigation (intentional)

2. **Missing links in developer_guide.md**:
   - `mkrelease.sh`, `mkbld.sh` - These are script references, not documentation links
   - `README.md` - Root README reference

These warnings don't affect the functionality of the documentation.

### Virtual Environment

The `mkdocs.sh` script automatically detects and activates the `.venv` virtual environment if it exists and you're not already in one.

### CHANGELOG Symlink

The script automatically creates a symlink from `docs/CHANGELOG.md` to `../CHANGELOG.md` so the changelog appears in the documentation without duplication.

## Next Steps

### Optional Improvements

1. **Fix developer_guide.md links**: Update broken links to scripts and sections
2. **Add more examples**: Expand the examples page with additional use cases
3. **Add docstrings**: Enhance Python docstrings for better API documentation
4. **Add diagrams**: Use Mermaid to add architecture diagrams
5. **Version documentation**: Use mike for versioned documentation (already configured in mkdocs.yml)
6. **Add tutorials**: Create step-by-step tutorials for common tasks

### GitHub Pages Setup

To enable GitHub Pages:

1. Go to repository Settings → Pages
2. Set Source to "Deploy from a branch"
3. Select `gh-pages` branch and `/ (root)` folder
4. Save

The documentation will be available at: https://johan162.github.io/bayescalc2/

## Testing

The documentation has been successfully built locally. To verify:

```bash
# Build completed successfully
./scripts/mkdocs.sh build

# Output shows:
# - Documentation built in ~2.6 seconds
# - Site generated in site/ directory
# - All pages rendered correctly
```


