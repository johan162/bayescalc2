# Network Visualization Feature

## Overview

BayesCalc2 now supports generating visual representations of Bayesian networks with optional CPT (Conditional Probability Table) displays. This feature uses graphviz to create publication-quality visualizations in multiple formats.

## Installation

### 1. Install Python Package

The graphviz Python package is included in BayesCalc2's dependencies:

```bash
pip install bayescalc2
```

Or if installing from source:

```bash
pip install -e ".[dev]"
```

### 2. Install Graphviz System Package

You also need the graphviz system binary:

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**Windows:**
Download from https://graphviz.org/download/ and add to PATH

## Usage

### Basic Command

```
visualize(output_file)
```

### Command Syntax

```
visualize(output_file, format=FORMAT, show_cpt=BOOL, layout=LAYOUT, rankdir=DIR)
```

**Parameters:**

- `output_file` (required): Output filename with or without extension
- `format`: Output format (`pdf`, `png`, `svg`, `jpg`) - default: determined from filename or `pdf`
- `show_cpt`: Include CPT tables in visualization (`True`/`False`) - default: `True`
- `layout`: Graph layout engine - default: `dot`
  - `dot`: Hierarchical layout (best for DAGs)
  - `neato`: Spring model layout
  - `fdp`: Force-directed placement
  - `circo`: Circular layout
  - `twopi`: Radial layout
- `rankdir`: Graph direction - default: `TB`
  - `TB`: Top to bottom
  - `LR`: Left to right
  - `BT`: Bottom to top
  - `RL`: Right to left

### Examples

#### Basic Visualization with CPT

```bash
>> load(examples/rain_sprinkler_grass.net)
>> visualize(network.pdf)
Network visualization saved to: network.pdf
```

#### PNG Without CPT Tables

```bash
>> visualize(simple_network.png, show_cpt=False)
Network visualization saved to: simple_network.png
```

#### SVG with Horizontal Layout

```bash
>> visualize(network.svg, rankdir=LR)
Network visualization saved to: network.svg
```

#### Custom Layout Engine

```bash
>> visualize(network.pdf, layout=neato)
Network visualization saved to: network.pdf
```

#### Multiple Options

```bash
>> visualize(exam_network.png, show_cpt=True, layout=dot, rankdir=LR, format=png)
Network visualization saved to: exam_network.png
```

### Using the Alias

The command has a short alias `viz`:

```bash
>> viz(network.pdf)
Network visualization saved to: network.pdf
```

## Output Examples

### With CPT Tables (`show_cpt=True`)

Nodes display:
- Variable name (header)
- Domain values
- Probability values for each state
- For conditional probabilities, shows parent conditions

Example node display:
```
┌─────────────────────┐
│      Rain           │
├─────────────────────┤
│   True, False       │
├──────────┬──────────┤
│ P(True)  │  0.2000  │
│ P(False) │  0.8000  │
└──────────┴──────────┘
```

### Without CPT Tables (`show_cpt=False`)

Shows only variable names and network structure (useful for large networks or presentations).

## Layout Comparison

### dot (default)
Best for Bayesian networks - creates hierarchical tree layout respecting parent-child relationships.

### neato
Force-directed layout - good for showing network connectivity patterns.

### fdp
Similar to neato but uses different force model - useful for larger networks.

### circo
Circular layout - good for visualizing networks with cyclic structures or for aesthetic purposes.

## Tab Completion

The visualize command supports tab completion:

```bash
>> visualize(<TAB>
network.pdf    network.png    network.svg    network_simple.pdf

>> visualize(network.pdf, <TAB>
format=pdf    format=png    format=svg    show_cpt=True    show_cpt=False    
layout=dot    layout=neato  layout=fdp    rankdir=TB       rankdir=LR
```

## Use Cases

### 1. Documentation
Generate diagrams for papers, reports, or documentation:
```bash
>> visualize(paper_figure.pdf, show_cpt=False, rankdir=LR)
```

### 2. Teaching
Create educational materials showing both structure and probabilities:
```bash
>> visualize(lecture_slide.png, show_cpt=True)
```

### 3. Debugging
Quickly visualize network structure during development:
```bash
>> viz(debug.svg, show_cpt=False)
```

### 4. Presentations
Generate clean, professional-looking network diagrams:
```bash
>> visualize(presentation.pdf, show_cpt=True, layout=dot, rankdir=TB)
```

## Troubleshooting

### Error: graphviz package not installed

Install the Python package:
```bash
pip install graphviz
```

### Error: failed to execute 'dot'

Install the graphviz system package (see Installation section above).

### Large CPT Tables

For variables with many parent combinations, the visualizer automatically truncates the CPT display to show only the first 8 entries, with a note indicating how many more exist.

### Graph Too Large

For large networks:
1. Use `show_cpt=False` to reduce node size
2. Try different layouts (`neato`, `fdp`) for better spacing
3. Use `rankdir=LR` for horizontal layout
4. Generate SVG format for scalable output

## Programmatic Use

For advanced users, the visualizer can be used programmatically:

```python
from bayescalc.visualizer import NetworkVisualizer

visualizer = NetworkVisualizer(network)
output_path = visualizer.generate_graph(
    output_file="custom_network",
    format="pdf",
    show_cpt=True,
    layout="dot",
    rankdir="TB"
)
print(f"Saved to: {output_path}")
```

## File Formats

- **PDF**: Best for documents and papers (vector format, scales perfectly)
- **PNG**: Good for web and presentations (raster format)
- **SVG**: Best for web and editing (vector format, editable)
- **JPG**: Compact raster format (lower quality)

## Tips

1. **Start simple**: First generate without CPT tables to see structure
2. **Iterate**: Try different layouts to find best visualization
3. **Choose format wisely**: Use PDF/SVG for publications, PNG for quick sharing
4. **Direction matters**: Top-bottom works well for small networks, left-right for wide ones
5. **Tab completion**: Use tab completion to discover options quickly
