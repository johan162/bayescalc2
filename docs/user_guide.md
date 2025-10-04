# BayesCalc2 User Guide

A comprehensive guide to using the Bayesian Network Calculator for learning, teaching, and research.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Network File Format](#network-file-format)
4. [Usage Walkthrough](#usage-walkthrough)
5. [Appendix A: Complete Command Reference](#appendix-a-complete-command-reference)
6. [Appendix B: Visualization Guide](#appendix-b-visualization-guide)
7. [Appendix C: Mathematical Background](#appendix-c-mathematical-background)

---

## Overview

### Purpose

BayesCalc2 is an educational and research tool designed to:

- **Learn Bayesian Networks**: Understand probabilistic relationships through hands-on experimentation
- **Teach Probability**: Provide an interactive environment for exploring conditional probability, independence, and inference
- **Research Support**: Rapid prototyping and analysis of small to medium-sized Bayesian networks
- **Validate Calculations**: Double-check manual probability calculations and reasoning

### Key Features

- **Interactive REPL**: Real-time probability queries with tab completion
- **Batch Processing**: Script multiple commands for automated analysis
- **Rich Query Language**: Support for conditional probabilities, arithmetic expressions, and logical operations
- **Information Theory**: Built-in entropy, mutual information, and conditional entropy calculations
- **Network Analysis**: Independence testing, graph visualization, and structural queries
- **Educational Focus**: Clear output formatting and helpful error messages

### Limitations

**Network Size**: Optimized for networks with fewer than 15-20 variables. Performance degrades with larger networks due to exponential complexity.

**Exact Inference Only**: Uses exact algorithms (variable elimination). No approximate inference methods like sampling or variational approaches.

**Static Networks**: No support for dynamic Bayesian networks, temporal reasoning, or online learning.

**Discrete Variables Only**: Continuous variables are not supported. All variables must have finite, discrete domains.

**No Parameter Learning**: Network structure and parameters must be specified manually. No learning from data.

---

## Installation

### Standard Installation

The graph visualization makes use of `graphviz` so this must be installed first:

- **MacOS:** `brew install graphviz`
- **Linux Fedore:** `sudo dnf install grphviz`
- **Ubuntu:** `sudo apt-get install graphviz`

The simplest way to install BayesCalc2:

```bash
pip install bayescalc2
```

This installs the package globally and makes the `bayescalc` command available system-wide.

### Development Installation

For development or if you want to modify the source code:

```bash
# Clone the repository
git clone https://github.com/johan162/bayescalc2.git 
cd bayescalc2

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Virtual Environment Setup

To create an isolated environment (recommended):

```bash
# Create virtual environment
python -m venv bayescalc-env

# Activate it
source bayescalc-env/bin/activate  # On Windows: bayescalc-env\Scripts\activate

# Install BayesCalc2
pip install bayescalc2

# Deactivate when done
deactivate
```

### Replicating the Development Environment

To exactly replicate the development environment:

```bash
# Clone the repository
git clone https://github.com/your-repo/bayescalc2.git
cd bayescalc2

# Create virtual environment with Python 3.10+
python -m venv .venv
source .venv/bin/activate

# Install dev dependencies from `pyproject.toml`:
pip install -e ".[dev]"

# Verify installation
bayescalc --help
```

### Requirements

- **Python**: 3.10 or higher
- **Dependencies**: 
  - `prompt_toolkit >= 3.0.0` (for interactive REPL)
  - `numpy >= 2.3.3` (for numerical computations)
  - `graphviz` (for network visualization)

---

### Usage
```txt
usage: main.py [-h] [-b BATCH_FILE | --cmd CMD_STRING] network_file

A Bayesian Network Calculator.

positional arguments:
  network_file          Path to the Bayesian network definition file (*.net or *.jpt).

options:
  -h, --help            show this help message and exit
  -b, --batch BATCH_FILE
                        Path to a file with commands to execute in batch mode.
  --cmd CMD_STRING      A string of commands to execute, separated by semicolons.
```
---

## Network File Format

### EBNF Grammar

```ebnf
(* Bayesian Network Definition Grammar *)

network          = { statement } ;
statement        = variable_decl | cpt_block ;
variable_decl    = "variable" identifier [ domain_spec ] ;
boolean_decl     = "boolean" identifier ;
domain_spec      = "{" identifier_list "}" ;
identifier_list  = identifier { "," identifier } ;

cpt_block        = identifier [ "|" parent_list ] "{" { cpt_entry } "}" ;
parent_list      = identifier_list ;
cpt_entry        = "P(" assignment_list ")" "=" number ;
assignment_list  = assignment { "," assignment } ;
assignment       = identifier [ "=" identifier ] ;

identifier       = letter { letter | digit | "_" } ;
number          = [ "-" ] digit { digit } [ "." { digit } ] ;
letter          = "A" | ... | "Z" | "a" | ... | "z" ;
digit           = "0" | ... | "9" ;

(* Comments start with # and continue to end of line *)
comment         = "#" { any_character } newline ;
```

### File Structure

A network file consists of two main sections:

1. **Variable Declarations**: Define variables and their possible values
2. **CPT Blocks**: Specify conditional probability tables

### Variable Declarations

#### Basic Syntax
```
variable VariableName {value1, value2, ...}
```

#### Boolean Variables (Shorthand)
```
boolean BooleanVar  # Automatically gets domain {True, False}
```

#### Examples
```
# Explicit domain specification
variable Weather {Sunny, Rainy, Cloudy}
variable Grade {A, B, C, D, F}

# Boolean variables (implicit True/False domain)
variable Raining
variable StudyHard
```

### CPT (Conditional Probability Table) Blocks

#### Root Variables (No Parents)
```
VariableName {
    P(value1) = probability1
    P(value2) = probability2
    # Remaining probabilities auto-completed to sum to 1.0
}
```

#### Variables with Parents
```
ChildVariable | Parent1, Parent2 {
    P(child_value | parent1_value, parent2_value) = probability
    # Specify probabilities for each parent combination
}
```

### Complete Examples

#### Simple Rain-Sprinkler Network
```
# Weather affects both sprinkler and grass
variable Rain {True, False}
variable Sprinkler {True, False} 
variable GrassWet {True, False}

# Prior probability of rain
Rain {
    P(True) = 0.2
    # P(False) = 0.8 (auto-completed)
}

# Sprinkler depends on rain (less likely when raining)
Sprinkler | Rain {
    P(True | True) = 0.01   # Rarely use sprinkler when raining
    P(True | False) = 0.4   # More likely when not raining
}

# Grass wetness depends on both rain and sprinkler
GrassWet | Rain, Sprinkler {
    P(True | True, True) = 0.99    # Almost certain when both
    P(True | True, False) = 0.8    # Likely with just rain
    P(True | False, True) = 0.9    # Likely with just sprinkler
    P(True | False, False) = 0.1   # Unlikely with neither
}
```

#### Student Performance Network
```
# Multi-valued variables example
variable Difficulty {Easy, Medium, Hard}
variable Intelligence {Low, Medium, High}
variable Grade {A, B, C, D, F}
variable SAT {Low, Medium, High}

# Course difficulty prior
Difficulty {
    P(Easy) = 0.3
    P(Medium) = 0.5
    # P(Hard) = 0.2 (auto-completed)
}

# Student intelligence prior  
Intelligence {
    P(Low) = 0.2
    P(Medium) = 0.6
    P(High) = 0.2
}

# Grade depends on both difficulty and intelligence
Grade | Difficulty, Intelligence {
    # Easy course, Low intelligence
    P(A | Easy, Low) = 0.1
    P(B | Easy, Low) = 0.2
    P(C | Easy, Low) = 0.4
    P(D | Easy, Low) = 0.2
    P(F | Easy, Low) = 0.1
    
    # Easy course, Medium intelligence  
    P(A | Easy, Medium) = 0.3
    P(B | Easy, Medium) = 0.4
    P(C | Easy, Medium) = 0.2
    P(D | Easy, Medium) = 0.08
    P(F | Easy, Medium) = 0.02
    
    # ... (continue for all combinations)
}

# SAT correlates with intelligence
SAT | Intelligence {
    P(High | High) = 0.8
    P(Medium | High) = 0.15
    P(Low | High) = 0.05
    
    P(High | Medium) = 0.3
    P(Medium | Medium) = 0.5
    P(Low | Medium) = 0.2
    
    P(High | Low) = 0.05
    P(Medium | Low) = 0.25
    P(Low | Low) = 0.7
}
```

### Format Rules and Tips

#### Comments
- Use `#` for line comments
- Comments can appear on separate lines or at the end of statements
- Useful for documenting network structure and assumptions

#### Probability Specifications
- **Auto-completion**: You don't need to specify all probabilities. The system will auto-complete missing values to ensure each conditional distribution sums to 1.0
- **Boolean shortcuts**: For boolean variables, you can use `T`/`F` or `True`/`False`
- **Decimal precision**: Use appropriate decimal precision (e.g., `0.33` vs `0.333333`)

#### Common Patterns
```
# Root node with uniform distribution
UniformVariable {
    # All values get equal probability automatically
}

# Boolean variable with bias
BiasedCoin {
    P(True) = 0.7  # P(False) = 0.3 automatically
}

# Deterministic relationship  
Effect | Cause {
    P(True | True) = 1.0   # Always happens
    P(True | False) = 0.0  # Never happens otherwise
}
```

---

## Usage Walkthrough

This section walks through a complete session using BayesCalc2, from loading a network to performing various analyses.

### Starting BayesCalc2

#### Interactive Mode
```bash
# Start with a network file
bayescalc examples/rain_sprinkler_grass.net

# You'll see:
Bayesian Network Calculator (using prompt_toolkit)
Type 'help' for a list of commands, 'exit' to quit.
>> 
```

#### Batch Mode
```bash
# Execute a single command
bayescalc network.net --cmd "P(Rain|GrassWet=True);showGraph()"

# Run multiple commands from file
bayescalc network.net --batch commands.txt
```

### Example Session: Weather Analysis

Let's work through analyzing the rain-sprinkler-grass network:

```
>> # First, let's explore the network structure
>> ls
Variable    | Type       | States
-----------|------------|------------------
Rain        | Discrete   | True, False
Sprinkler   | Discrete   | True, False  
GrassWet    | Discrete   | True, False

>> # View the network structure
>> showGraph()
Rain
├── Sprinkler
└── GrassWet
Sprinkler
└── GrassWet

>> # Check what affects grass wetness
>> parents(GrassWet)
Parents of GrassWet: {Rain, Sprinkler}

>> # Look at the conditional probability table
>> printCPT(GrassWet)
Child    | Parents           | Probability
---------|-------------------|-------------
GrassWet | Rain=True, Sprinkler=True  | 0.99
GrassWet | Rain=True, Sprinkler=False | 0.80
GrassWet | Rain=False, Sprinkler=True | 0.90
GrassWet | Rain=False, Sprinkler=False| 0.10
```

### Basic Probability Queries

```
>> # What's the probability of rain?
>> P(Rain=True)
0.2

>> # What if we observe wet grass?
>> P(Rain=True | GrassWet=True)
0.358

>> # Joint probability
>> P(Rain=True, Sprinkler=False)
0.198

>> # Multiple conditions
>> P(Rain=True | GrassWet=True, Sprinkler=False)
0.571
```

### Arithmetic with Probabilities

```
>> # Bayes' rule calculation
>> P(Rain=True | GrassWet=True) * P(GrassWet=True) / P(Rain=True)
0.894

>> # Probability of at least one cause
>> P(Rain=True) + P(Sprinkler=True) - P(Rain=True, Sprinkler=True)
0.398

>> # Conditional independence check numerically
>> P(Rain=True | Sprinkler=True) - P(Rain=True)
0.0
```

### Independence Analysis

```
>> # Are rain and sprinkler independent?
>> isindependent(Rain, Sprinkler)
True

>> # Are rain and grass conditionally independent given sprinkler?
>> iscondindependent(Rain, GrassWet | Sprinkler)
False

>> # Verify with probabilities
>> P(Rain=True | GrassWet=True, Sprinkler=True)
0.111
>> P(Rain=True | Sprinkler=True) 
0.2
```

### Information Theory Analysis

```
>> # How much uncertainty is in each variable?
>> entropy(Rain)
0.722

>> entropy(GrassWet)
0.971

>> # How much does observing grass reduce rain uncertainty?
>> conditional_entropy(Rain | GrassWet)
0.639

>> # Mutual information between variables
>> mutual_information(Rain, GrassWet)
0.083
```

### Advanced Queries

```
>> # Compare different scenarios
>> P(GrassWet=True | Rain=True)
0.82

>> P(GrassWet=True | Sprinkler=True)
0.918

>> # Find most likely explanation
>> P(Rain=True, Sprinkler=False | GrassWet=True)
0.321

>> P(Rain=False, Sprinkler=True | GrassWet=True)
0.358

>> # The sprinkler scenario is more likely!
```

### Batch Processing Example

Create a file `analysis.txt`:
```
# Weather network analysis script
showGraph()
P(Rain=True)
P(GrassWet=True | Rain=True)
P(GrassWet=True | Sprinkler=True)  
isindependent(Rain, Sprinkler)
mutual_information(Rain, GrassWet)
printCPT(Sprinkler)
```

Run it:
```bash
bayescalc rain_sprinkler_grass.net --batch analysis.txt
```

### Error Handling and Debugging

```
>> # Invalid variable name
>> P(InvalidVar=True)
Error: Variable 'InvalidVar' not found

>> # Invalid value
>> P(Rain=Maybe)
Error: Value 'Maybe' not in domain of variable 'Rain'

>> # Syntax error
>> P(Rain=True |)
Error: Expected variable name after '|'

>> # Check variable domains when in doubt
>> ls
```

### Pro Tips for Effective Usage

1. **Start with structure**: Use `showGraph()` and `ls` to understand the network
2. **Validate with simple queries**: Check marginal probabilities make sense
3. **Use tab completion**: Type partial variable names and press Tab
4. **Save complex queries**: Use batch files for repeated analysis
5. **Verify with multiple approaches**: Cross-check independence with conditional probabilities
6. **Build incrementally**: Start with small networks, add complexity gradually

---

## Appendix A: Complete Command Reference

### Initialization

#### `load`

**Purpose**: Load a new network from a file

**Syntax**: `load(filename)`

#### Features
- **Tab Completion**: File paths support tab completion for easy navigation
- **Automatic Reload**: All internal state (queries, inference engine, completers) are automatically updated
- **Error Handling**: Clear error messages for missing or invalid files
- **Path Expansion**: Supports `~` for home directory expansion

#### Basic Usage
```
>> load(examples/rain_sprinkler_grass.net)
Successfully loaded network from: examples/rain_sprinkler_grass.net
Variables (3): GrassWet, Rain, Sprinkler
```

#### Notes

- The previous network state is completely replaced
- All queries and computations reference the new network after loading
- File paths are relative to the current working directory where BayesCalc2 was launched
- Only `.net` files appear in tab completion suggestions (directories also shown for navigation)


### Probability Queries

#### Basic Probability Syntax
- `P(Variable=Value)` - Marginal probability
- `P(Variable)` - Full distribution over variable (when supported)
- `P(A=a, B=b)` - Joint probability
- `P(A=a | B=b)` - Conditional probability
- `P(A=a | B=b, C=c)` - Multiple conditions

#### Arithmetic Expressions
- `P(A) * P(B|A)` - Multiplication
- `P(A) + P(B) - P(A,B)` - Addition/subtraction  
- `P(A|B) / P(A)` - Division
- `(P(A) + P(B)) * 0.5` - Parentheses and constants

### Network Structure Commands

#### `showGraph()`

**Purpose**: Display ASCII representation of network structure

**Output**: Tree-like visualization showing parent-child relationships

**Example**:
```
>> showGraph()
Temp
├── JohnRun
├── MaryRun
└── Meet
```

### `visualize(output_file)`

See: **Appendix C**

#### `parents(Variable)`

**Purpose**: List parent variables of specified variable

**Parameters**: Variable name

**Returns**: Set of parent variable names

**Example**: 
```
>> parents(GrassWet)
Parents of GrassWet: {Rain, Sprinkler}
```

#### `children(Variable)`  

**Purpose**: List child variables of specified variable

**Parameters**: Variable name

**Returns**: Set of child variable names

**Example**:
```
>> children(Rain)
Children of Rain: {Sprinkler, GrassWet}
```

#### `ls` / `vars`

**Purpose**: List all variables with their types and domains

**Aliases**: `ls`, `vars`

**Output**: Formatted table of variable information

**Example**:
```
>> ls
Variable    | Type       | States
-----------|------------|------------------
Rain        | Discrete   | True, False
Weather     | Discrete   | Sunny, Rainy, Cloudy
```


### Probability Tables

#### `printCPT(Variable)`

**Purpose**: Display conditional probability table for specified variable

**Parameters**: Variable name

**Output**: Three-column table (Child | Parents | Probability)

**Example**:
```
>> printCPT(GrassWet)
Child    | Parents           | Probability
---------|-------------------|-------------
GrassWet | Rain=True, Sprinkler=True  | 0.99
GrassWet | Rain=True, Sprinkler=False | 0.80
GrassWet | Rain=False, Sprinkler=True | 0.90
GrassWet | Rain=False, Sprinkler=False| 0.10
```

#### `printJPT()`

**Purpose**: Display complete joint probability table

**Warning**: Exponentially large for big networks

**Output**: All possible variable assignments with probabilities

**Use**: Small networks only (< 10 variables recommended)

### Independence Testing

#### `isindependent(Variable1, Variable2)`

**Purpose**: Test marginal independence between two variables

**Parameters**: Two variable names

**Returns**: `True` if independent, `False` otherwise

**Mathematical Test**: P(A,B) = P(A) × P(B)

**Example**:
```
>> isindependent(Rain, Sprinkler)
True
```

#### `iscondindependent(Variable1, Variable2 | ConditioningSet)`

**Purpose**: Test conditional independence

**Syntax**: `iscondindependent(A, B | C, D, ...)`

**Returns**: `True` if conditionally independent

**Mathematical Test**: P(A,B|C) = P(A|C) × P(B|C)

**Example**:
```
>> iscondindependent(Rain, GrassWet | Sprinkler)
False
```

### Information Theory

#### `entropy(Variable)`

**Purpose**: Compute Shannon entropy of variable

**Formula**: H(X) = -∑ P(x) log₂ P(x)

**Units**: bits

**Range**: [0, log₂(|domain|)]

**Example**:
```
>> entropy(Rain)
0.722  # bits
```

#### `conditional_entropy(Variable1 | Variable2)`

**Purpose**: Compute conditional entropy

**Syntax**: `conditional_entropy(X | Y)`

**Formula**: H(X|Y) = -∑∑ P(x,y) log₂ P(x|y)

**Interpretation**: Average uncertainty in X given Y

**Example**:
```
>> conditional_entropy(Rain | GrassWet)
0.639
```

#### `mutual_information(Variable1, Variable2)`

**Purpose**: Compute mutual information between variables

**Formula**: I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)

**Range**: [0, min(H(X), H(Y))]

**Interpretation**: Information shared between variables

**Example**:
```
>> mutual_information(Rain, GrassWet)
0.083
```

### Advanced Probability Commands

#### `marginals(N)`

**Purpose**: Generate marginal probabilities for N variables

**Parameters**: Number of variables to include

**Output**: All marginal probability combinations

**Use**: Systematic probability analysis

#### `condprobs(N, M)`  

**Purpose**: Generate conditional probabilities

**Parameters**: N variables conditioned on M variables

**Output**: All conditional probability combinations

**Use**: Systematic conditional analysis

### Utility Commands

#### `help`

**Purpose**: Display help message with command summary

**Aliases**: `help`, `?`

**Output**: Formatted command reference

#### `exit`

**Purpose**: Exit the interactive session

**Aliases**: `exit`, `quit`, Ctrl-C, Ctrl-D

### Command Syntax Rules

#### Variable Names
- Case-sensitive
- Must match exactly as defined in network file
- Tab completion available

#### Boolean Values
- `True`/`False` (recommended)
- `T`/`F` (shorthand)
- Case-sensitive

#### Arithmetic Operators
- `+` Addition
- `-` Subtraction  
- `*` Multiplication
- `/` Division
- `()` Parentheses for grouping

#### Conditional Syntax
- `|` separates condition variables
- `,` separates multiple variables
- `=` assigns values to variables

---

## Appendix B: Visualization Guide

### Overview

BayesCalc2 now supports generating visual representations of Bayesian networks with optional CPT (Conditional Probability Table) displays. This feature uses graphviz to create publication-quality visualizations in multiple formats.

### Installation

#### 1. Install Python Package

The graphviz Python package is included in BayesCalc2's dependencies:

```bash
pip install bayescalc2
```

Or if installing from source:

```bash
pip install -e ".[dev]"
```

#### 2. Install Graphviz System Package

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


### Usage

#### Basic Command

```
visualize(output_file)
```

#### Command Syntax

```
visualize(output_file, format=FORMAT, show_cpt=BOOL, layout=LAYOUT, rankdir=DIR, page_size=SIZE, scale=FACTOR)
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
- `page_size`: PDF page size (`A3`, `A4`, `A5`, or custom size as `WxH` in mm, e.g. `297x210`) - PDF only
- `scale`: Scale factor for the graph (float, e.g. `1.0`, `0.8`, `2.0`) - PDF only

#### PDF Page Size and Scale

When generating PDF output, you can control the page size and scaling:

- `page_size`: Choose from standard sizes (`A3`, `A4`, `A5`) or specify custom dimensions in millimeters (`WxH`, e.g. `210x148`).
- `scale`: Adjusts the overall size of the graph on the page. Use values less than 1.0 to shrink, greater than 1.0 to enlarge.

**Examples:**

```bash
>> visualize(network.pdf, page_size=A4, scale=0.8)
>> visualize(network.pdf, page_size=297x210, scale=1.2)
```

If omitted, defaults are `page_size=None` (Graphviz default) and `scale=1.0` (no scaling).

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

#### Using the Alias

The command has a short alias `viz`:

```bash
>> viz(network.pdf)
Network visualization saved to: network.pdf
```

### Output Examples

#### With CPT Tables (`show_cpt=True`)

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

#### Without CPT Tables (`show_cpt=False`)

Shows only variable names and network structure (useful for large networks or presentations).

### Layout Comparison

#### dot (default)
Best for Bayesian networks - creates hierarchical tree layout respecting parent-child relationships.

#### neato
Force-directed layout - good for showing network connectivity patterns.

#### fdp
Similar to neato but uses different force model - useful for larger networks.

#### circo
Circular layout - good for visualizing networks with cyclic structures or for aesthetic purposes.

### Tab Completion

The visualize command supports tab completion:

```bash
>> visualize(<TAB>
network.pdf    network.png    network.svg    network_simple.pdf

>> visualize(network.pdf, <TAB>
format=pdf    format=png    format=svg    show_cpt=True    show_cpt=False    
layout=dot    layout=neato  layout=fdp    rankdir=TB       rankdir=LR
```

### Use Cases

#### 1. Documentation
Generate diagrams for papers, reports, or documentation:
```bash
>> visualize(paper_figure.pdf, show_cpt=False, rankdir=LR)
```

#### 2. Teaching
Create educational materials showing both structure and probabilities:
```bash
>> visualize(lecture_slide.png, show_cpt=True)
```

#### 3. Debugging
Quickly visualize network structure during development:
```bash
>> viz(debug.svg, show_cpt=False)
```

#### 4. Presentations
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

---

## Appendix C: Mathematical Background

### Bayesian Networks Fundamentals

#### Definition
A Bayesian network is a probabilistic graphical model representing conditional dependencies between random variables through a directed acyclic graph (DAG).

**Components**:
1. **Graph Structure**: Nodes represent variables, edges represent direct dependencies
2. **Parameters**: Conditional probability tables (CPTs) quantify relationships

#### Joint Probability Factorization
For variables X₁, X₂, ..., Xₙ with parents Pa(Xᵢ):

**P(X₁, X₂, ..., Xₙ) = ∏ᵢ P(Xᵢ | Pa(Xᵢ))**

This factorization enables efficient representation and computation.

### Independence Relations

#### Marginal Independence
Variables A and B are independent if:
**P(A, B) = P(A) × P(B)**

Equivalently: **P(A | B) = P(A)** and **P(B | A) = P(B)**

#### Conditional Independence  
Variables A and B are conditionally independent given C if:
**P(A, B | C) = P(A | C) × P(B | C)**

Equivalently: **P(A | B, C) = P(A | C)**

#### d-Separation
Graph-theoretic criterion for reading independence relations:
- **Chain**: A → B → C, A and C are independent given B
- **Fork**: A ← B → C, A and C are independent given B  
- **Collider**: A → B ← C, A and C are dependent given B

### Inference Algorithms

#### Variable Elimination
BayesCalc2 uses variable elimination for exact inference:

1. **Eliminate** variables not in query in reverse topological order
2. **Sum out** variables by marginalizing joint distributions  
3. **Normalize** final result

**Complexity**: Exponential in tree-width of moral graph

#### Query Types Supported
- **Marginal**: P(X = x)
- **Conditional**: P(X = x | E = e) 
- **Joint**: P(X₁ = x₁, X₂ = x₂, ...)
- **MAP**: Most probable assignment (partially supported)

### Information Theory Measures

#### Shannon Entropy
Measures uncertainty/information content:
**H(X) = -∑ₓ P(x) log₂ P(x)**

**Properties**:
- H(X) ≥ 0 (non-negative)
- H(X) = 0 iff X is deterministic  
- H(X) ≤ log₂|X| (maximized by uniform distribution)

#### Conditional Entropy
Expected entropy of X given Y:
**H(X|Y) = ∑ᵧ P(y) H(X|Y=y) = -∑ₓ,ᵧ P(x,y) log₂ P(x|y)**

**Chain Rule**: H(X,Y) = H(X) + H(Y|X) = H(Y) + H(X|Y)

#### Mutual Information
Information shared between variables:
**I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)**

**Alternative form**: I(X;Y) = ∑ₓ,ᵧ P(x,y) log₂[P(x,y)/(P(x)P(y))]

**Properties**:
- I(X;Y) ≥ 0 (non-negative)
- I(X;Y) = 0 iff X ⊥ Y (independence)
- I(X;Y) = I(Y;X) (symmetric)

### Computational Complexity

#### Network Size Limitations
- **Variables**: Practical limit ~15-20 variables
- **Domain Size**: Product of all domain sizes affects complexity
- **Tree Width**: Determines inference complexity

#### Exponential Blowup
Joint probability table size: **∏ᵢ |Domain(Xᵢ)|**

For n binary variables: **2ⁿ** entries

#### Optimization Strategies
1. **Variable Ordering**: Affects intermediate factor sizes
2. **Caching**: Store computed factors for reuse
3. **Lazy Evaluation**: Compute only needed probabilities

### Practical Considerations

#### Numerical Precision
- **Underflow**: Very small probabilities may underflow
- **Log Space**: Consider log-probabilities for stability  
- **Normalization**: Ensure probabilities sum to 1.0

#### Model Validation
- **CPT Consistency**: Each conditional distribution sums to 1
- **Acyclicity**: Graph must be directed and acyclic
- **Completeness**: All parent combinations must be specified

#### Common Patterns

**Naive Bayes**: All features conditionally independent given class
```
Class → Feature1
Class → Feature2  
Class → Feature3
```

**Markov Chain**: Sequential dependence
```
X₁ → X₂ → X₃ → X₄
```

**Tree**: Hierarchical structure with single paths
```
Root → Child1 → Grandchild1
Root → Child2 → Grandchild2
```

---

## Conclusion

BayesCalc2 provides a powerful yet accessible platform for exploring Bayesian networks. This guide covers the essential concepts and practical usage patterns needed to effectively use the tool for learning, teaching, and research.

For additional support:
- Check the `examples/` directory for more network files
- Use the built-in `help` command for quick reference  
- Consult the source code for implementation details

Happy exploring with Bayesian networks!