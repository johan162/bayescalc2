# API Reference

This section provides detailed API documentation for BayesCalc2's internal modules.

## Overview

BayesCalc2 is organized into several key modules:

### Core Components

- **[Network Model](network_model.md)**: Core data structures for Bayesian networks
    - `BayesianNetwork`: Main network container
    - `Variable`: Network variable with domain
    - `CPT`: Conditional probability table
    - `Factor`: Probability factor for inference

- **[Parser](parser.md)**: Parses `.net` files into network structures
    - `Parser`: Main parser class
    - AST node types for network definition elements

- **[Lexer](lexer.md)**: Tokenizes `.net` files
    - `Lexer`: Main lexer class
    - `Token`: Token representation
    - `TokenType`: Token type enumeration

### Inference Engine

- **[Inference](inference.md)**: Probability computation engine
    - `Inference`: Main inference class
    - Variable elimination algorithm
    - Factor operations (multiply, marginalize, normalize)

### Query Processing

- **[Query Parser](queries.md)**: Parses and executes probability queries
    - `QueryParser`: Main query parser
    - Support for `P(A|B)` syntax
    - Boolean shorthand handling

- **[Expression Parser](expression_parser.md)**: Evaluates arithmetic expressions
    - `ExpressionParser`: Expression evaluator
    - Support for `P(A) * P(B) / P(C)` syntax

### Interactive Components

- **[REPL](repl.md)**: Interactive shell interface
    - `REPL`: Main REPL class
    - Command-line interface with history and completion

- **[Commands](commands.md)**: Command handlers
    - `CommandHandler`: Command execution
    - Built-in commands (ls, printCPT, visualize, etc.)

- **[Completer](completer.md)**: Tab completion
    - `BayesCalcCompleter`: Auto-completion engine
    - Variable, command, and domain value completion

### Batch Processing

- **[Batch Runner](batch.md)**: Non-interactive command execution
    - Batch file processing
    - Command execution without REPL

## Architecture

The system follows a pipeline architecture:

```
Input (.net file) → Lexer → Parser → BayesianNetwork
                                            ↓
                                    Inference Engine
                                            ↑
                                     Query Parser ← User Query
```

### Network Definition Pipeline

1. **Lexer** (`lexer.py`): Tokenizes input text into tokens
2. **Parser** (`parser.py`): Builds AST and creates network model
3. **BayesianNetwork** (`network_model.py`): Stores network structure and CPTs

### Query Execution Pipeline

1. **QueryParser** (`queries.py`): Parses probability query syntax
2. **Inference** (`inference.py`): Computes probability using variable elimination
3. **ExpressionParser** (`expression_parser.py`): Evaluates arithmetic on probabilities

### Interactive Mode

1. **REPL** (`repl.py`): Main interactive loop
2. **CommandHandler** (`commands.py`): Executes user commands
3. **BayesCalcCompleter** (`completer.py`): Provides tab completion

## Usage Patterns

### Loading a Network

```python
from bayescalc.lexer import Lexer
from bayescalc.parser import Parser

# Read network file
with open('network.net', 'r') as f:
    net_str = f.read()

# Parse network
lexer = Lexer(net_str)
tokens = lexer.tokenize()
parser = Parser(tokens)
network = parser.parse()
```

### Running Inference

```python
from bayescalc.inference import Inference

# Create inference engine
inference = Inference(network)

# Query probability
query_vars = [('Rain', 'True')]
evidence = [('GrassWet', 'Yes')]
result = inference.query(query_vars, evidence)

print(f"P(Rain=True | GrassWet=Yes) = {result:.4f}")
```

### Using the REPL

```python
from bayescalc.repl import REPL

# Create and run REPL
repl = REPL(network)
repl.run()  # Interactive session
```

### Batch Processing

```python
from bayescalc.batch import run_batch

# Execute commands from file
run_batch(network, 'commands.txt')
```

## Key Classes

### BayesianNetwork

Central data structure holding:
- Variables and their domains
- Conditional probability tables
- Network topology

### Variable

Represents a random variable:
- Name
- Domain (possible values)
- Parent variables
- CPT (conditional probability table)

### Inference

Implements variable elimination:
- Factor creation from CPTs
- Factor multiplication
- Marginalization (summing out variables)
- Normalization

### QueryParser

Handles query syntax:
- Parse `P(A|B)` notation
- Boolean shorthand (`Rain` → `Rain=True`)
- Evidence specification

## Testing

All modules include comprehensive test suites in the `tests/` directory:

- `test_lexer.py`: Lexer tokenization tests
- `test_parser.py`: Parser and network construction tests
- `test_network_model.py`: Data model tests
- `test_inference.py`: Inference algorithm tests
- `test_queries.py`: Query parsing tests
- `test_commands.py`: Command execution tests
- `test_repl_e2e.py`: End-to-end REPL tests

Run tests with:
```bash
pytest tests/
```

## Extension Points

### Adding New Commands

Register in `CommandHandler._initialize_command_registry()`:

```python
def _initialize_command_registry(self):
    self.command_registry = {
        'mycommand': self.cmd_mycommand,
        # ...
    }

def cmd_mycommand(self, args: List[str]) -> None:
    """Execute my custom command."""
    # Implementation
```

### Custom Inference Algorithms

Subclass `Inference` and override `query()` method:

```python
from bayescalc.inference import Inference

class CustomInference(Inference):
    def query(self, query_vars, evidence):
        # Custom implementation
        pass
```

### Custom Query Syntax

Extend `QueryParser` to support new syntax:

```python
from bayescalc.queries import QueryParser

class ExtendedQueryParser(QueryParser):
    def parse(self, query_str):
        # Handle custom syntax
        pass
```

## API Documentation

For detailed API documentation of each module, see the individual module pages in the sidebar.
