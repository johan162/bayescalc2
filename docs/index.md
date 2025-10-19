# BayesCalc2

**A powerful Bayesian network calculator with interactive REPL**

BayesCalc2 is a command-line tool for defining, analyzing, and querying Bayesian networks. It provides an intuitive syntax for specifying probabilistic relationships and a rich set of commands for probability inference.

## Features

- 🔢 **Bayesian Network Definition**: Simple, human-readable `.net` file format
- 🧮 **Probability Queries**: Natural syntax like `P(Rain|GrassWet)` 
- 📊 **Network Visualization**: Generate PDF diagrams of your networks
- 🔍 **Advanced Inference**: Variable elimination algorithm for efficient computation
- 💻 **Interactive REPL**: Tab completion, command history, and helpful feedback
- 📝 **Batch Processing**: Run multiple commands from script files
- 🔗 **Boolean Shorthand**: Concise syntax for binary variables (`Rain` vs `Rain=True`)

## Quick Start

### Installation

```bash
pip install bayescalc2
```

Or install from source:

```bash
git clone https://github.com/ljp/bayescalc2.git
cd bayescalc2
pip install -e .
```

### Your First Network

Create a simple network file `rain.net`:

```
variable Rain {True, False}
variable Sprinkler {On, Off}
variable GrassWet {Yes, No}

Rain { P(True) = 0.2 }
Sprinkler { P(On) = 0.1 }

GrassWet | Rain, Sprinkler {
    P(Yes | True, On) = 0.99
    P(Yes | True, Off) = 0.90
    P(Yes | False, On) = 0.85
    P(Yes | False, Off) = 0.05
}
```

### Run Interactive Mode

```bash
bayescalc rain.net
```

Then query probabilities:

```
BayesCalc> P(Rain|GrassWet=Yes)
P(Rain=True | GrassWet=Yes) = 0.6203
```

### Batch Mode

Create a command file `queries.txt`:

```
P(Rain)
P(GrassWet=Yes|Rain=True)
visualize output.pdf
```

Run it:

```bash
bayescalc rain.net -b queries.txt
```

## Documentation

- **[User Guide](user_guide.md)**: Complete guide to using BayesCalc2
- **[Developer Guide](developer_guide.md)**: Architecture and development workflows
- **[Examples](examples.md)**: Sample networks and use cases
- **[API Reference](api/index.md)**: Detailed API documentation

## Example Networks

BayesCalc2 includes several example networks:

- **Medical Diagnosis**: Disease testing with false positives/negatives
- **Weather Prediction**: Rain, sprinkler, and grass wetness
- **Student Performance**: Exam results based on intelligence and difficulty
- **Asia Chest Clinic**: Medical diagnosis network from literature
- **Monty Hall Problem**: Classic probability puzzle

See the [Examples](examples.md) page for detailed explanations.

## Architecture

BayesCalc2 uses a pipeline architecture:

```
.net files → Lexer → Parser → BayesianNetwork → Inference Engine
                                        ↓
                            QueryParser ← User Queries
```

Key components:

- **Lexer**: Tokenizes `.net` files
- **Parser**: Builds abstract syntax tree and network model
- **BayesianNetwork**: Data model for variables, domains, and CPTs
- **Inference**: Variable elimination algorithm for probability computation
- **REPL**: Interactive shell with tab completion

## Contributing

Contributions are welcome! Please see the [Developer Guide](developer_guide.md) for:

- Setting up the development environment
- Running tests
- Code style guidelines
- Architecture overview

## License

BayesCalc2 is released under the MIT License. See [LICENSE](https://github.com/ljp/bayescalc2/blob/main/LICENSE) for details.
