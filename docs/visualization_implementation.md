# Visualization Feature Implementation Summary

## Overview

Added comprehensive network visualization capability to BayesCalc2 using graphviz, allowing users to generate publication-quality Bayesian network diagrams with optional CPT tables.

## Files Created

### 1. `src/bayescalc/visualizer.py`
New module implementing network visualization:
- **NetworkVisualizer** class for generating visualizations
- Support for multiple output formats (PDF, PNG, SVG, JPG)
- Multiple layout engines (dot, neato, fdp, circo, twopi)
- Optional CPT table display alongside nodes
- Configurable graph direction (TB, LR, BT, RL)
- Automatic CPT truncation for large tables
- Error handling for missing dependencies

### 2. `tests/test_visualizer.py`
Comprehensive test suite:
- Tests for all output formats
- Tests for different layout engines
- Tests for command integration
- Tests for error handling
- Graceful skipping when graphviz not installed

### 3. `docs/visualization_guide.md`
Complete user documentation:
- Installation instructions
- Usage examples
- Parameter reference
- Layout comparison
- Troubleshooting guide
- Use cases and tips

## Files Modified

### 1. `src/bayescalc/commands.py`
- Added `_handle_visualize()` method for command parsing
- Added visualize command to registry with alias `viz`
- Flexible argument parsing for options (format, show_cpt, layout, rankdir)
- Helpful error messages for missing dependencies

### 2. `src/bayescalc/completer.py`
- Added `visualize(` and `viz(` to command list
- Implemented file path completion for output files
- Implemented option completion (format=, show_cpt=, layout=, rankdir=)
- Suggests common filenames when tab pressed

### 3. `pyproject.toml`
- Added `graphviz>=0.20.0` to dependencies

### 4. `README.md`
- Added visualization to features list
- Added graphviz to requirements
- Added installation instructions for graphviz system package
- Added visualization examples section
- Added visualize command to available commands list

## Key Features

### 1. Multiple Output Formats
- **PDF**: Vector format, best for documents
- **PNG**: Raster format, good for web/presentations
- **SVG**: Vector format, editable
- **JPG**: Compressed raster format

### 2. Layout Engines
- **dot** (default): Hierarchical layout for DAGs
- **neato**: Spring model layout
- **fdp**: Force-directed placement
- **circo**: Circular layout
- **twopi**: Radial layout

### 3. Customization Options
- **show_cpt**: Toggle CPT table display
- **rankdir**: Graph direction (TB/LR/BT/RL)
- **layout**: Choose layout engine
- **format**: Output file format

### 4. Smart CPT Display
- Automatically shows domain information
- Displays prior probabilities for root nodes
- Shows conditional probabilities with parent conditions
- Truncates large CPT tables (shows first 8 entries)
- Indicates number of hidden entries

## Usage Examples

### Basic
```bash
>> visualize(network.pdf)
```

### Without CPT Tables
```bash
>> visualize(simple.png, show_cpt=False)
```

### Horizontal Layout
```bash
>> visualize(network.svg, rankdir=LR)
```

### Custom Layout Engine
```bash
>> visualize(network.pdf, layout=neato)
```

### Multiple Options
```bash
>> visualize(output.png, format=png, show_cpt=True, layout=dot, rankdir=TB)
```

## Tab Completion

Full tab completion support:
- Filename suggestions
- Format options
- Layout options
- Boolean parameters

```bash
>> visualize(<TAB>
network.pdf    network.png    network.svg

>> visualize(out.pdf, <TAB>
format=pdf    show_cpt=True    layout=dot    rankdir=TB
```

## Error Handling

### Missing Python Package
```
Error: graphviz package not installed.
Install it with: pip install graphviz
```

### Missing System Package
```
Error: failed to execute 'dot'
Install graphviz system package:
  macOS: brew install graphviz
  Ubuntu: sudo apt-get install graphviz
```

### Invalid Parameters
```
Error: Invalid format 'xyz'. Valid formats: pdf, png, svg, jpg
Error: Invalid layout 'abc'. Valid layouts: dot, neato, fdp, circo, twopi
```

## Testing

All tests include proper skip logic for missing dependencies:
- Tests skip gracefully if graphviz Python package not installed
- Tests skip gracefully if graphviz system binary not installed
- No test failures due to missing optional dependencies

### Test Coverage
- Format generation (PDF, PNG, SVG)
- Layout engines (dot, neato, fdp, circo)
- With/without CPT tables
- Command registration
- Command execution
- Error handling
- Invalid parameters

## Documentation

### User Guide
- `docs/visualization_guide.md`: Complete user guide
  - Installation steps
  - Usage examples
  - Parameter reference
  - Layout comparison
  - Troubleshooting
  - Tips and best practices

### README Updates
- Added to features list
- Added to requirements
- Added to installation section
- Added usage examples
- Added to available commands

## Dependencies

### Runtime
- **graphviz** (Python package): >=0.20.0
- **graphviz** (system package): Required for rendering

### System Package Installation

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**Windows:**
Download from https://graphviz.org/download/

## Command Integration

The visualize command is fully integrated:
- Registered in command registry
- Has alias `viz` for convenience
- Recognized by `is_command()` method
- Tab completion support
- Help system integration

## Benefits

1. **Publication Quality**: Generate diagrams for papers and documentation
2. **Educational**: Visual learning aid with CPT tables visible
3. **Debugging**: Quick visualization of network structure
4. **Flexible**: Multiple formats and layout options
5. **Easy to Use**: Simple command with sensible defaults
6. **Well Documented**: Comprehensive guide with examples

## Future Enhancements (Optional)

Potential future improvements:
- Color coding for different node types
- Highlighting specific paths or variables
- Interactive HTML output
- Custom node styling options
- Legend generation
- Multi-page output for large networks
