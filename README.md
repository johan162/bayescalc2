# BayesCalc2

[![PyPI version](https://badge.fury.io/py/bayescalc2.svg)](https://badge.fury.io/py/bayescalc2)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Bayesian network calculator designed for learning, teaching, and research in probabilistic reasoning. This tool allows you to define Bayesian networks, calculate probabilities, and perform various probabilistic operations using an efficient variable-elimination algorithm that scales well with network complexity.

## Features

- **Efficient Inference**: Uses variable elimination algorithm instead of exponentially-growing joint probability tables
- **Interactive REPL**: Command-line interface with tab completion and command history
- **Batch Processing**: Execute multiple queries from files or command strings
- **Rich Query Language**: Support for conditional probabilities, arithmetic expressions, and independence tests
- **Information Theory**: Built-in entropy, mutual information, and conditional entropy calculations
- **Network Analysis**: Graph structure analysis with parent/child relationships
- **Network Visualization**: Generate publication-quality network diagrams with CPT tables (PDF, PNG, SVG)
- **Educational Focus**: Clear output formatting ideal for learning and teaching

## Installation

### Requirements

- Python 3.10 or higher
- NumPy >= 2.3.3
- prompt_toolkit >= 3.0.0
- graphviz >= 0.20.0 (for visualization)

### Install from PyPI

```bash
pip install bayescalc2
```

For visualization support, also install graphviz system package:

```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
# Download from https://graphviz.org/download/
```

### Install from Source

```bash
git clone https://github.com/your-username/bayescalc2.git
cd bayescalc2
pip install -e .
```

## Quick Start

```bash
# Download an example network
wget https://raw.githubusercontent.com/your-username/bayescalc2/main/examples/rain_sprinkler_grass.net

# Launch interactive mode
bayescalc rain_sprinkler_grass.net

# Try some queries
>> P(Rain)
>> P(Rain|GrassWet=True)
>> entropy(Rain)
>> exit
```

## Usage

BayesCalc2 can be used in two modes:

### 1. Interactive Mode

```bash
bayescalc network_file.net
```

This launches an interactive REPL where you can enter probability queries and commands.

### 2. Batch Mode

```bash
bayescalc network_file.net --batch commands.txt
```

or

```bash
bayescalc network_file.net --cmd "P(Rain|GrassWet=Yes);printCPT(Rain)"
```

## Network File Format

Create a Bayesian network definition in a .net file:

```
# Example network definition
boolean Rain
variable Sprinkler {On, Off}
variable GrassWet {Yes, No}

# CPT definitions
Rain {
    P(True) = 0.2
    # P(False) will be auto-filled
}

Sprinkler | Rain {
    P(On | True) = 0.01
    P(On | False) = 0.4
    # P(Off | parent) auto-filled
}

GrassWet | Rain, Sprinkler {
    P(Yes | True, On) = 0.99
    P(Yes | True, Off) = 0.8
    P(Yes | False, On) = 0.9
    # Remaining CPTs auto-completed
}
```

## Available Commands

### Probability Queries
- `P(A)` - Marginal probability
- `P(A|B)` - Conditional probability  
- `P(A,B|C)` - Joint conditional probability
- `P(A|B)*P(B)/P(A)` - Arithmetic expressions

### Network Analysis
- `printCPT(X)` - Display conditional probability table
- `printJPT()` - Display joint probability table
- `parents(X)` - Show parent variables
- `children(X)` - Show child variables
- `showGraph()` - Display network structure
- `visualize(file.pdf)` - Generate network visualization with CPT tables
- `load(file.net)` - Load a different network file

### Independence Testing
- `isindependent(A,B)` - Test marginal independence
- `iscondindependent(A,B|C)` - Test conditional independence

### Information Theory
- `entropy(X)` - Shannon entropy
- `conditional_entropy(X|Y)` - Conditional entropy
- `mutual_information(X,Y)` - Mutual information

### Visualization Examples

```bash
# Generate PDF with CPT tables
>> visualize(network.pdf)

# Generate PNG without CPT tables
>> visualize(simple_network.png, show_cpt=False)

# Generate SVG with horizontal layout
>> visualize(network.svg, rankdir=LR)
```

## Examples

The `examples/` directory contains various Bayesian networks demonstrating different use cases:

- `rain_sprinkler_grass.net` - Classic sprinkler example
- `medical_test.net` - Medical diagnosis scenario
- `student_network.net` - Academic performance model
- `asia_chest_clinic.net` - Medical expert system

## Use Cases

- **Education**: Teaching probabilistic reasoning and Bayesian networks
- **Research**: Prototyping and testing Bayesian models
- **Analysis**: Exploring conditional dependencies in data
- **Validation**: Verifying hand-calculated probability results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/your-username/bayescalc2.git
cd bayescalc2
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"  # Quotes needed for zsh shell
python -m pytest tests/
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## Support

- **Documentation**: See `docs/user_guide.md` for detailed usage instructions
- **Developer guide**: See `docs/developer_guide.md` for how to get started to contribute and overview of key dev practices and algorithms.
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/your-username/bayescalc2/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/your-username/bayescalc2/discussions)

## Citation

If you use BayesCalc2 in academic work, please cite:

```bibtex
@software{bayescalc2,
  title={BayesCalc2: A Bayesian Network Calculator},
  author={Johan Persson},
  year={2025},
  url={https://github.com/johan162/bayescalc2},
  version={2.0.0}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.