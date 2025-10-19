# BayesCalc2 Developer Guide

Purpose: A guide for developers contributing to the BayesCalc2 Bayesian Network Calculator project.

## Table of Contents

0. [Setup for Development](#tldr-quick-setup-for-development
1. [Codebase Overview](#codebase-overview)
2. [Architecture and Design](#architecture-and-design)
3. [Testing Framework](#testing-framework)
4. [Writing Unit Tests](#writing-unit-tests)
5. [REPL Testing Helpers](#repl-testing-helpers)
6. [Code Quality Guidelines](#code-quality-guidelines)
7. [Development Workflow](#development-workflow)
8. [Pull Request Guidelines](#pull-request-guidelines)
9. [Debugging and Performance](#debugging-and-performance)
10. [Building the documentation](#building-the-documentation)
11. [Release Process](#release-process)
12. [Appendix A: Variable Elimination Algorithm](#appendix-a-variable-elimination-algorithm---detailed-implementation-guide)
13. [Appendix B: GitHub Release Script Documentation](#appendix-b-github-release-script-documentation)

---

## TLDR; Quick Setup for Development

Steps to clone the repo and setup a working virtusl environment.

### Installing Pre-reqs

#### `graphviz`:
The bayescalc2 is using graphviz via its Python bindings to create graph
visualizations.

- **MacOS:** `brew install graphviz`
- **Linux Fedore:** `sudo dnf install grphviz`
- **Ubuntu:** `sudo apt-get install graphviz`

### Setting up Python virtual environment (.venv)

1. Clone and create venv:
   ```bash
   git clone https://github.com/johan162/bayescalc2.git && cd bayescalc2
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install package in editable mode:
   ```bash
   pip install -e .
   ```

3. Install dev dependencies from `pyproject.toml`:
   ```bash
   pip install -e ".[dev]"
   ```

4. Verify installation:
   ```bash
   bayescalc --help
   python -c "import bayescalc; print(bayescalc.__file__)"
   ```

### Quick build guide

Once the local environment is setup and a code change has been made the primary build script `scripts/mkbld.sh` should be run. This script does the following checks

1. That code coverage is > 80%
2. That all tests passes
3. Run "flake8" static analysis with no errors  or warnings
4. Checks code formatting with "black"
5. Creates a PyPi distribution and validates with "twine"

The build script must have a successfull result before a commit can be made. 
The CI pipeline setup at GitHub will run the script as a pre-commit script that must pass.

---

## Codebase Overview

### Project Structure

```
bayescalc2/
├── src/bayescalc/         # Main package source code
├── scripts/               # Build scrippts  
├── tests/                 # Comprehensive test suite
├── examples/              # Sample network files
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
└── README.md              # Basic usage guide
```

### Core Modules

#### `src/bayescalc/`

**`network_model.py`** - Core Data Structures
- **Purpose**: Fundamental data structures for Bayesian networks
- **Key Classes**:
  - `Variable`: Represents random variables with discrete domains
  - `Factor`: Represents probability distributions (CPTs, joint tables)
  - `BayesianNetwork`: Main container for the entire network
- **Functionality**: Variable management, factor operations, network validation
- **Dependencies**: None (core module)

**`lexer.py`** - Tokenization
- **Purpose**: Converts raw network file text into tokens
- **Key Classes**:
  - `Token`: Individual lexical unit (identifier, number, symbol)
  - `TokenType`: Enumeration of token categories
  - `Lexer`: Main tokenization engine
- **Functionality**: String parsing, token classification, error reporting
- **Dependencies**: None

**`parser.py`** - Syntax Analysis
- **Purpose**: Converts tokens into network data structures
- **Key Classes**:
  - `Parser`: Recursive descent parser for network syntax
- **Functionality**: Variable declaration parsing, CPT block parsing, syntax validation
- **Dependencies**: `lexer.py`, `network_model.py`

**`inference.py`** - Probabilistic Reasoning
- **Purpose**: Exact inference algorithms for probability queries
- **Key Classes**:
  - `VariableElimination`: Main inference engine
- **Functionality**: Variable elimination, marginalization, conditioning
- **Dependencies**: `network_model.py`, `numpy`
- **Algorithms**: Variable elimination with optimal ordering

**`queries.py`** - Query Processing
- **Purpose**: Parse and execute probability queries
- **Key Classes**:
  - `QueryParser`: Parses P(A|B) syntax into structured queries
- **Functionality**: Query parsing, evidence handling, result formatting
- **Dependencies**: `lexer.py`, `parser.py`, `inference.py`

**`expression_parser.py`** - Arithmetic Expressions
- **Purpose**: Handle arithmetic operations with probabilities
- **Key Classes**:
  - `ExpressionParser`: Recursive descent parser for arithmetic
- **Functionality**: Mathematical expressions, operator precedence, probability arithmetic
- **Dependencies**: `queries.py`

**`commands.py`** - Command Handler
- **Purpose**: Interactive command processing and execution
- **Key Classes**:
  - `CommandHandler`: Central command dispatcher
- **Functionality**: Command routing, parameter parsing, output formatting
- **Key Commands**: `printCPT()`, `showGraph()`, `entropy()`, `isindependent()`
- **Dependencies**: All other modules

**`completer.py`** - Tab Completion
- **Purpose**: Interactive tab completion for the REPL
- **Key Classes**:
  - `PromptToolkitCompleter`: Integrates with prompt_toolkit
- **Functionality**: Variable name completion, command completion, context-aware suggestions
- **Dependencies**: `network_model.py`, `prompt_toolkit`

**`repl.py`** - Interactive Interface
- **Purpose**: Real-time interactive calculator interface
- **Key Classes**:
  - `REPL`: Main interactive loop and session management
- **Functionality**: User interaction, command routing, session state
- **Dependencies**: All modules, `prompt_toolkit`

**`batch.py`** - Batch Processing
- **Purpose**: Execute commands from files or command line
- **Key Classes**:
  - `BatchProcessor`: File-based command execution
- **Functionality**: Script execution, output collection, error handling
- **Dependencies**: `commands.py`

**`main.py`** - Entry Point
- **Purpose**: Application entry point and CLI argument processing
- **Key Functions**:
  - `main()`: Primary entry point
- **Functionality**: Argument parsing, mode selection, application bootstrap
- **Dependencies**: All modules

### Test Structure

#### `tests/`

The test suite is organized by functionality and includes comprehensive coverage:

**Core Component Tests:**
- `test_network_model.py` - Data structure tests
- `test_parser.py` - Syntax parsing tests  
- `test_lexer.py` - Tokenization tests (implicit)
- `test_inference.py` - Inference algorithm tests
- `test_queries.py` - Query processing tests

**Feature Tests:**
- `test_commands_queries.py` - Command execution tests
- `test_completer.py` - Tab completion tests
- `test_repl_e2e.py` - End-to-end REPL tests
- `test_main.py` - CLI interface tests

**Edge Case Tests:**
- `test_error_handling.py` - Error condition tests
- `test_numerical_edge_cases.py` - Numerical precision tests
- `test_parser_edge_cases.py` - Parsing edge cases
- `test_inference_edge_cases.py` - Inference edge cases

**Integration Tests:**
- `test_example_networks.py` - Full network validation
- `test_large_networks.py` - Performance and scalability
- `test_boolean_shorthand_*.py` - Boolean syntax variations

**Specialized Tests:**
- `test_command_argument_completion.py` - Tab completion regression tests
- `test_advanced_numerical_cases.py` - Complex probability calculations

---

## Architecture and Design

### Design Principles

#### Separation of Concerns
- **Parsing Layer**: `lexer.py` → `parser.py` (syntax)
- **Model Layer**: `network_model.py` (data structures)
- **Logic Layer**: `inference.py` → `queries.py` (algorithms)
- **Interface Layer**: `repl.py` → `commands.py` (user interaction)

#### Immutable Data Structures
- `Variable` and `Factor` are immutable (frozen dataclasses)
- Network modifications create new objects rather than mutating existing ones
- Enables safe concurrent access and easier debugging

#### Layered Architecture
```
┌─────────────────┐
│ Interface Layer │  repl.py, main.py, batch.py
├─────────────────┤
│ Command Layer   │  commands.py, completer.py
├─────────────────┤
│ Query Layer     │  queries.py, expression_parser.py
├─────────────────┤
│ Inference Layer │  inference.py
├─────────────────┤
│ Model Layer     │  network_model.py
├─────────────────┤
│ Parsing Layer   │  parser.py, lexer.py
└─────────────────┘
```

### Data Flow

#### Network Loading
1. **File Input** → `lexer.py` (tokenization)
2. **Tokens** → `parser.py` (AST construction)
3. **AST** → `network_model.py` (network instantiation)

#### Query Processing
1. **User Input** → `queries.py` (query parsing)
2. **Query Object** → `inference.py` (probability computation)
3. **Results** → `commands.py` (formatting and display)

#### Interactive Session
1. **User Input** → `repl.py` (session management)
2. **Commands** → `commands.py` (command dispatch)
3. **Results** → `repl.py` (output display)

### Key Design Patterns

#### Factory Pattern
- `BayesianNetwork.add_variable()` - creates `Variable` instances
- `Parser._parse_*()` methods - create network components

#### Strategy Pattern
- `CommandHandler.execute()` - selects appropriate command handler
- `VariableElimination` - implements inference strategy

#### Observer Pattern
- Test fixtures observe network state changes
- REPL observes command execution results

---

## Testing Framework

### Testing Philosophy

BayesCalc2 follows **comprehensive testing principles**:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Edge Case Tests**: Test boundary conditions and error scenarios
5. **Regression Tests**: Prevent known bugs from reoccurring

### Test Organization

#### Test Categories

**API Tests**: Test public interfaces and expected behavior
```python
def test_probability_query(self):
    # Test P(A=True) returns correct probability
    result = self.query_parser.parse_and_execute("P(Rain=True)")
    self.assertAlmostEqual(result, 0.2, places=3)
```

**REPL Tests**: Test interactive command execution
```python
def test_interactive_command(self):
    # Test command execution in REPL context
    result = self.command_handler.execute("printCPT(Rain)")
    self.assertIn("Probability", result)
```

**Error Tests**: Validate error handling
```python  
def test_invalid_variable_error(self):
    with self.assertRaises(ValueError) as cm:
        self.network.get_variable("NonExistent")
    self.assertIn("Variable 'NonExistent' not found", str(cm.exception))
```

#### Test Utilities

**`tests/test_utils.py`** provides helper functions:
- `parse_string()` - Create networks from string definitions
- Custom assertion methods for probability comparisons
- Network validation helpers

### Running Tests

#### Full Test Suite
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bayescalc --cov-report=html

# Run specific test file
pytest tests/test_network_model.py

# Run tests matching pattern
pytest -k "test_probability"
```

#### Test Selection
```bash
# Run only unit tests
pytest tests/test_network_model.py tests/test_parser.py

# Run integration tests
pytest tests/test_commands_queries.py tests/test_example_networks.py

# Run edge case tests
pytest tests/test_*edge_cases.py tests/test_error_handling.py
```

---

## Writing Unit Tests

### Test Structure Template

```python
"""
Test module for [component name].
"""
import unittest
from typing import Dict, List, Any

# Import the module being tested
from bayescalc.network_model import BayesianNetwork, Variable, Factor

class Test[ComponentName](unittest.TestCase):
    """Test cases for [ComponentName] class.""" 
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.network = BayesianNetwork()
        self.network.add_variable("TestVar", ("True", "False"))
        
    def tearDown(self):
        """Clean up after each test method."""
        # Usually not needed due to test isolation
        pass
    
    def test_[specific_functionality](self):
        """Test [specific functionality] works correctly."""
        # Arrange - Set up test data
        expected_result = "expected_value"
        
        # Act - Execute the functionality
        actual_result = self.network.some_method("TestVar")
        
        # Assert - Verify the results
        self.assertEqual(actual_result, expected_result)
        
    def test_[error_condition](self):
        """Test that [error condition] raises appropriate exception."""
        with self.assertRaises(ValueError) as context:
            self.network.invalid_operation()
        
        self.assertIn("expected error message", str(context.exception))

if __name__ == '__main__':
    unittest.main()
```

### Testing Best Practices

#### 1. Test Network Setup

**Use Test Utilities**:
```python
from tests.test_utils import parse_string

def setUp(self):
    network_def = """
    variable Rain {True, False}
    variable Sprinkler {True, False}
    
    Rain {
        P(True) = 0.2
    }
    
    Sprinkler | Rain {
        P(True | True) = 0.01
        P(True | False) = 0.4
    }
    """
    self.network = parse_string(network_def)
```

**Create Minimal Networks**:
```python
def setUp(self):
    # Minimal network for focused testing
    self.network = BayesianNetwork()
    self.network.add_variable("A", ("True", "False"))
    self.network.add_factor("A", [], {("True",): 0.3, ("False",): 0.7})
```

#### 2. Probability Testing

**Use Appropriate Precision**:
```python
def test_probability_calculation(self):
    result = self.network.query("P(Rain=True)")
    # Use places for decimal precision
    self.assertAlmostEqual(result, 0.2, places=3)
    
    # Or use delta for absolute tolerance
    self.assertAlmostEqual(result, 0.2, delta=0.001)
```

**Test Probability Properties**:
```python
def test_probability_normalization(self):
    """Test that probabilities sum to 1.0."""
    prob_true = self.network.query("P(Rain=True)")
    prob_false = self.network.query("P(Rain=False)")
    total = prob_true + prob_false
    self.assertAlmostEqual(total, 1.0, places=6)
```

#### 3. Command Testing

**Test Command Execution**:
```python
def test_print_cpt_command(self):
    """Test printCPT command produces expected output."""
    result = self.command_handler.execute("printCPT(Rain)")
    
    # Check for expected elements in output
    self.assertIn("Child", result)
    self.assertIn("Parents", result)
    self.assertIn("Probability", result)
    self.assertIn("Rain", result)
```

**Test Error Commands**:
```python
def test_invalid_command_error(self):
    """Test that invalid commands produce helpful errors."""
    with self.assertRaises(ValueError) as context:
        self.command_handler.execute("invalidCommand()")
    
    error_msg = str(context.exception)
    self.assertIn("Unknown command", error_msg)
```

#### 4. Parser Testing

**Test Valid Syntax**:
```python
def test_variable_declaration_parsing(self):
    """Test parsing of variable declarations."""
    tokens = self.lexer.tokenize("variable Test {A, B, C}")
    parser = Parser(tokens)
    network = parser.parse()
    
    self.assertIn("Test", network.variables)
    self.assertEqual(network.get_variable("Test").domain, ("A", "B", "C"))
```

**Test Invalid Syntax**:
```python
def test_syntax_error_handling(self):
    """Test that syntax errors are properly reported."""
    with self.assertRaises(SyntaxError) as context:
        tokens = self.lexer.tokenize("variable { }")  # Missing name
        Parser(tokens).parse()
    
    error_msg = str(context.exception)
    self.assertIn("Expected", error_msg)
    self.assertIn("line", error_msg)  # Should include line number
```

### Example: Complete Test Class

```python
"""
Tests for the Variable class in network_model.py
"""
import unittest
from bayescalc.network_model import Variable

class TestVariable(unittest.TestCase):
    """Test cases for Variable class."""
    
    def test_variable_creation(self):
        """Test basic variable creation."""
        var = Variable("TestVar", ("A", "B"))
        self.assertEqual(var.name, "TestVar")
        self.assertEqual(var.domain, ("A", "B"))
    
    def test_boolean_variable_detection(self):
        """Test detection of boolean variables."""
        bool_var = Variable("BoolVar", ("True", "False"))
        multi_var = Variable("MultiVar", ("A", "B", "C"))
        
        self.assertTrue(bool_var.is_boolean)
        self.assertFalse(multi_var.is_boolean)
    
    def test_variable_type_property(self):
        """Test var_type property returns correct values."""
        bool_var = Variable("BoolVar", ("True", "False"))
        multi_var = Variable("MultiVar", ("A", "B", "C"))
        
        self.assertEqual(bool_var.var_type, "Boolean")
        self.assertEqual(multi_var.var_type, "Multival")
    
    def test_variable_immutability(self):
        """Test that variables are immutable."""
        var = Variable("Test", ("A", "B"))
        
        # Should not be able to modify
        with self.assertRaises(AttributeError):
            var.name = "NewName"
        
        with self.assertRaises(AttributeError):
            var.domain = ("C", "D")
    
    def test_variable_repr(self):
        """Test string representation of variables."""
        var = Variable("Test", ("A", "B"))
        repr_str = repr(var)
        
        self.assertIn("Variable", repr_str)
        self.assertIn("Test", repr_str)
        self.assertIn("A", repr_str)
        self.assertIn("B", repr_str)

if __name__ == '__main__':
    unittest.main()
```

---

## REPL Testing Helpers

### Interactive Testing Philosophy

REPL (Read-Eval-Print Loop) testing ensures that interactive commands work correctly in realistic usage scenarios. BayesCalc2 provides specialized helpers for testing interactive functionality without requiring actual terminal interaction.

### Mock-Based REPL Testing

#### Test Infrastructure

**`tests/test_repl_e2e.py`** provides the foundation:

```python
"""
Example of REPL testing using mock objects.
"""
import unittest
from unittest.mock import MagicMock
from bayescalc.completer import PromptToolkitCompleter
from bayescalc.network_model import BayesianNetwork

class TestReplInteraction(unittest.TestCase):
    
    def setUp(self):
        # Create test network
        self.network = BayesianNetwork()
        self.network.add_variable("Rain", ("True", "False"))
        self.network.add_variable("Sprinkler", ("True", "False"))
        
        # Set up REPL components
        from bayescalc.commands import CommandHandler
        self.command_handler = CommandHandler(self.network)
        self.completer = PromptToolkitCompleter(self.network)
    
    def test_command_execution_sequence(self):
        """Test a sequence of interactive commands."""
        # Simulate user typing commands
        commands = [
            "ls",
            "P(Rain=True)",
            "printCPT(Rain)",
            "showGraph()"
        ]
        
        results = []
        for cmd in commands:
            try:
                result = self.command_handler.execute(cmd)
                results.append(result)
            except Exception as e:
                self.fail(f"Command '{cmd}' failed: {e}")
        
        # Verify results
        self.assertIn("Variable", results[0])  # ls output
        self.assertIsInstance(results[1], float)  # probability value
        self.assertIn("Probability", results[2])  # CPT output
        self.assertIn("Rain", results[3])  # graph output
```

### Tab Completion Testing

#### Mock Document Objects

```python
class MockDocument:
    """Mock prompt_toolkit document for testing completion."""
    
    def __init__(self, text_before_cursor: str):
        self.text_before_cursor = text_before_cursor
        self.text_after_cursor = ""
        self.text = text_before_cursor
        self.cursor_position = len(text_before_cursor)
    
    def get_word_before_cursor(self, WORD=False):
        """Extract word before cursor for completion."""
        if not self.text_before_cursor:
            return ""
        
        # Simple word extraction (can be enhanced)
        parts = self.text_before_cursor.split()
        return parts[-1] if parts else ""

class MockCompletion:
    """Mock completion object."""
    
    def __init__(self, text: str):
        self.text = text
        self.start_position = 0

def test_variable_name_completion(self):
    """Test completion of variable names."""
    doc = MockDocument("P(R")
    completions = list(self.completer.get_completions(doc, None))
    
    # Should suggest "Rain"
    completion_texts = [c.text for c in completions]
    self.assertIn("ain", completion_texts)  # Completing "R" → "Rain"
```

### Command Testing Helpers

#### Command Execution Testing

```python
def execute_command_safely(self, command: str):
    """Execute command and return result or error."""
    try:
        return self.command_handler.execute(command), None
    except Exception as e:
        return None, str(e)

def test_command_error_handling(self):
    """Test that commands handle errors gracefully."""
    # Test invalid variable
    result, error = self.execute_command_safely("P(InvalidVar=True)")
    self.assertIsNone(result)
    self.assertIn("Variable 'InvalidVar' not found", error)
    
    # Test invalid syntax
    result, error = self.execute_command_safely("P(Rain=)")
    self.assertIsNone(result)
    self.assertIn("syntax", error.lower())
```

#### Interactive Session Simulation

```python
class MockReplSession:
    """Simulate a complete REPL session."""
    
    def __init__(self, network: BayesianNetwork):
        self.network = network
        self.command_handler = CommandHandler(network)
        self.session_history = []
    
    def execute(self, command: str):
        """Execute command and store in history."""
        try:
            result = self.command_handler.execute(command)
            self.session_history.append((command, result, None))
            return result
        except Exception as e:
            self.session_history.append((command, None, str(e)))
            raise
    
    def get_history(self):
        """Return session history for analysis."""
        return self.session_history

def test_full_session_workflow(self):
    """Test a complete user workflow."""
    session = MockReplSession(self.network)
    
    # Simulate user workflow
    workflow = [
        ("ls", "should list variables"),
        ("P(Rain=True)", "should return probability"),
        ("P(Rain=True | Sprinkler=True)", "should handle conditioning"),
        ("entropy(Rain)", "should calculate entropy"),
        ("showGraph()", "should display graph")
    ]
    
    for command, description in workflow:
        try:
            result = session.execute(command)
            self.assertIsNotNone(result, f"Command '{command}' failed: {description}")
        except Exception as e:
            self.fail(f"Workflow step '{command}' failed: {e}")
```

### Completion Testing Patterns

#### Testing Command Completion

```python
def test_command_name_completion(self):
    """Test completion of command names."""
    test_cases = [
        ("prin", ["printCPT"]),
        ("show", ["showGraph"]),
        ("isen", ["isindependent"]),
        ("entro", ["entropy"])
    ]
    
    for prefix, expected in test_cases:
        doc = MockDocument(prefix)
        completions = list(self.completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]
        
        for exp in expected:
            # Check if any completion contains expected text
            self.assertTrue(
                any(exp in comp for comp in completion_texts),
                f"Expected '{exp}' in completions for '{prefix}': {completion_texts}"
            )
```

#### Testing Context-Aware Completion

```python
def test_context_aware_completion(self):
    """Test completion respects command context."""
    # Inside printCPT(), should complete variable names
    doc = MockDocument("printCPT(R")
    completions = list(self.completer.get_completions(doc, None))
    
    # Should suggest variable names, not command names
    completion_texts = [c.text for c in completions]
    self.assertTrue(any("ain" in comp for comp in completion_texts))  # "Rain"
    
    # Outside commands, should complete command names
    doc = MockDocument("prin")
    completions = list(self.completer.get_completions(doc, None))
    completion_texts = [c.text for c in completions]
    self.assertTrue(any("tCPT" in comp for comp in completion_texts))  # "printCPT"
```

### Integration Test Helpers

#### End-to-End Workflow Testing

```python
def create_test_workflow(self):
    """Create a standard test workflow for REPL testing."""
    return [
        # Basic exploration
        "ls",
        "showGraph()",
        
        # Simple queries
        "P(Rain=True)",
        "P(Sprinkler=True)",
        
        # Conditional queries
        "P(Rain=True | Sprinkler=True)",
        
        # Table display
        "printCPT(Rain)",
        "printCPT(Sprinkler)",
        
        # Analysis commands
        "entropy(Rain)",
        "isindependent(Rain, Sprinkler)",
        
        # Graph analysis
        "parents(Sprinkler)",
        "children(Rain)"
    ]

def test_standard_workflow(self):
    """Test standard user workflow executes without errors."""
    session = MockReplSession(self.network)
    workflow = self.create_test_workflow()
    
    for i, command in enumerate(workflow):
        try:
            result = session.execute(command)
            self.assertIsNotNone(result, f"Step {i+1}: '{command}' returned None")
        except Exception as e:
            self.fail(f"Step {i+1}: '{command}' failed with: {e}")
```

---

## Code Quality Guidelines

### Python Style Guidelines

#### PEP 8 Compliance
- **Line Length**: Maximum 100 characters (slightly more than standard 79 for readability)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized according to PEP 8 (standard library, third-party, local)
- **Naming Conventions**:
  - Functions and variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
  - Private members: `_leading_underscore`

#### Example Code Structure
```python
"""
Module docstring describing purpose and usage.
"""
from typing import Dict, List, Optional, Tuple
import os
import sys

import numpy as np
from prompt_toolkit import PromptSession

from .network_model import BayesianNetwork, Variable
from .utils import validate_probability

# Module-level constants
DEFAULT_PRECISION = 4
MAX_VARIABLES = 20

class ExampleClass:
    """Class docstring describing purpose and usage."""
    
    def __init__(self, network: BayesianNetwork):
        """Initialize with a Bayesian network."""
        self.network = network
        self._cache: Dict[str, float] = {}
    
    def public_method(self, variable_name: str) -> Optional[float]:
        """
        Public method with clear docstring.
        
        Args:
            variable_name: Name of the variable to process
            
        Returns:
            Computed probability or None if not found
            
        Raises:
            ValueError: If variable_name is invalid
        """
        if not variable_name:
            raise ValueError("Variable name cannot be empty")
        
        # Implementation here
        return self._compute_probability(variable_name)
    
    def _private_method(self, data: List[float]) -> float:
        """Private helper method."""
        return sum(data) / len(data) if data else 0.0
```

### Documentation Standards

#### Docstring Format
Use **Google-style docstrings** for consistency:

```python
def complex_function(network: BayesianNetwork, 
                    variables: List[str],
                    evidence: Dict[str, str] = None) -> Dict[str, float]:
    """
    Compute marginal probabilities for multiple variables.
    
    This function performs variable elimination to compute the marginal
    probability distribution for each variable in the provided list,
    optionally conditioned on evidence.
    
    Args:
        network: The Bayesian network to query
        variables: List of variable names to compute marginals for
        evidence: Optional evidence as variable->value mapping
        
    Returns:
        Dictionary mapping variable names to their marginal probabilities
        
    Raises:
        ValueError: If any variable name is not found in the network
        RuntimeError: If inference fails due to numerical issues
        
    Example:
        >>> network = create_rain_network()
        >>> marginals = compute_marginals(network, ["Rain", "Sprinkler"])
        >>> print(marginals["Rain"])
        0.2
    """
```

#### Type Hints
Use comprehensive type hints:

```python
from typing import Dict, List, Optional, Tuple, Union, Any

# Specific type hints
def process_probabilities(probs: Dict[Tuple[str, ...], float]) -> List[float]:
    """Process probability dictionary."""
    return list(probs.values())

# Union types for flexibility
def parse_value(value: Union[str, float, int]) -> float:
    """Parse various input types to float."""
    return float(value)

# Optional for nullable values
def find_variable(name: str) -> Optional[Variable]:
    """Find variable by name, return None if not found."""
    return self.variables.get(name)
```

### Error Handling Best Practices

#### Specific Exception Types
```python
# Custom exception hierarchy
class BayesCalcError(Exception):
    """Base exception for BayesCalc errors."""
    pass

class NetworkError(BayesCalcError):
    """Errors related to network structure."""
    pass

class QueryError(BayesCalcError):
    """Errors in query processing."""
    pass

class InferenceError(BayesCalcError):
    """Errors during probabilistic inference."""
    pass

# Usage in code
def add_variable(self, name: str, domain: Tuple[str, ...]) -> None:
    """Add variable to network."""
    if name in self.variables:
        raise NetworkError(f"Variable '{name}' already exists")
    
    if len(domain) < 2:
        raise NetworkError(f"Variable '{name}' must have at least 2 values")
    
    self.variables[name] = Variable(name, domain)
```

#### Informative Error Messages
```python
def validate_probability_query(self, query: str) -> None:
    """Validate probability query syntax."""
    if not query.startswith("P("):
        raise QueryError(
            f"Invalid query '{query}': must start with 'P('. "
            f"Example: P(Rain=True) or P(A|B=b)"
        )
    
    if not query.endswith(")"):
        raise QueryError(
            f"Invalid query '{query}': missing closing parenthesis. "
            f"Check for balanced parentheses in '{query}'"
        )
```

### Performance Guidelines

#### Efficient Data Structures
```python
# Use tuples for immutable keys
probability_cache: Dict[Tuple[str, ...], float] = {}

# Use sets for membership testing
variable_names: Set[str] = set(network.variables.keys())
if "Rain" in variable_names:  # O(1) lookup
    process_variable("Rain")

# Use list comprehensions for transformations
probabilities = [factor.get_probability(assignment) 
                for assignment in all_assignments]
```

#### Caching Strategies
```python
from functools import lru_cache

class BayesianNetwork:
    @lru_cache(maxsize=1000)
    def _compute_marginal(self, variable: str, evidence_tuple: Tuple[Tuple[str, str], ...]) -> float:
        """Cached marginal computation."""
        # Convert evidence tuple back to dict for processing
        evidence = dict(evidence_tuple) if evidence_tuple else {}
        return self._perform_inference(variable, evidence)
    
    def compute_marginal(self, variable: str, evidence: Dict[str, str] = None) -> float:
        """Public interface with caching."""
        evidence_tuple = tuple(sorted(evidence.items())) if evidence else ()
        return self._compute_marginal(variable, evidence_tuple)
```

### Testing Quality Standards

#### Comprehensive Test Coverage
```python
def test_all_edge_cases(self):
    """Test comprehensive edge cases for probability computation."""
    test_cases = [
        # (description, input, expected_output, should_raise)
        ("zero probability", {"A": 0.0, "B": 1.0}, 0.0, None),
        ("one probability", {"A": 1.0, "B": 0.0}, 1.0, None),
        ("negative probability", {"A": -0.1, "B": 1.1}, None, ValueError),
        ("probabilities sum > 1", {"A": 0.6, "B": 0.6}, None, ValueError),
        ("empty probabilities", {}, None, ValueError),
    ]
    
    for description, input_data, expected, should_raise in test_cases:
        with self.subTest(description=description):
            if should_raise:
                with self.assertRaises(should_raise):
                    self.network.set_probabilities(input_data)
            else:
                result = self.network.compute_probability(input_data)
                self.assertAlmostEqual(result, expected, places=6)
```

#### Test Data Management
```python
class NetworkTestBase(unittest.TestCase):
    """Base class for network tests with common fixtures."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test networks used across multiple tests."""
        cls.simple_network = cls._create_simple_network()
        cls.complex_network = cls._create_complex_network()
    
    @staticmethod
    def _create_simple_network():
        """Create simple test network."""
        network_def = """
        variable A {True, False}
        variable B {True, False}
        
        A { P(True) = 0.5 }
        B | A { 
            P(True | True) = 0.8
            P(True | False) = 0.2
        }
        """
        return parse_string(network_def)
    
    def setUp(self):
        """Set up fresh instances for each test."""
        # Copy networks to avoid test interference
        self.network = self._copy_network(self.simple_network)
```

---

## Development Workflow

### Environment Setup

#### Development Environment
```bash
# Clone repository
git clone https://github.com/johan162/bayescalc2.git
cd bayescalc2

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
# pip install pytest pytest-cov black flake8 mypy

# Verify installation
bayescalc examples/rain_sprinkler_grass.net --cmd "P(Rain=True)"
```

#### IDE Configuration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"]
}
```

### Git Workflow

#### Branch Naming Convention
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes
- `refactor/component-name` - Code refactoring
- `docs/documentation-update` - Documentation changes

#### Commit Message Format
```
<type>(<scope>): <description>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(inference): add variable elimination caching

Implement LRU cache for variable elimination results to improve
performance for repeated queries on the same network.

- Add @lru_cache decorator to _eliminate_variable method
- Update tests to verify caching behavior
- Add performance benchmark for cached vs uncached queries

Closes #123
```

### Code Quality Checks

#### Pre-commit Hooks
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        args: [--line-length=100]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --ignore=E203,W503]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

#### Manual Quality Checks
```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Run tests with coverage
pytest --cov=bayescalc --cov-report=term-missing --cov-fail-under=90

```

### Continuous Integration

#### GitHub Actions Workflow (`.github/workflows/test.yml`):
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=bayescalc --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

## Pull Request Guidelines

### PR Requirements Checklist

#### Before Submitting
- [ ] **Rebase to latest develop**: `git rebase origin/develop`
- [ ] **All tests pass**: `pytest` exits with 0
- [ ] **Code coverage maintained**: No decrease in overall coverage
- [ ] **Style checks pass**: `black`, `flake8`, `mypy` all pass
- [ ] **Documentation updated**: User guide and docstrings updated if needed
- [ ] **CHANGELOG updated**: Add entry describing changes

#### PR Content Requirements

**1. Comprehensive Test Coverage**
Every PR must include tests that cover:
- **Happy path**: Normal operation scenarios
- **Edge cases**: Boundary conditions and corner cases  
- **Error conditions**: Invalid inputs and error handling
- **Integration**: How changes interact with existing code

**2. Test Coverage Examples**
```python
# For a new command implementation
class TestNewCommand(unittest.TestCase):
    
    def test_normal_operation(self):
        """Test command works with valid inputs."""
        pass
    
    def test_edge_cases(self):
        """Test boundary conditions."""
        pass
    
    def test_error_handling(self):
        """Test invalid inputs raise appropriate errors."""
        pass
    
    def test_integration_with_existing_commands(self):
        """Test new command works with existing functionality."""
        pass
```

### PR Description Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)

## Testing
Describe the testing strategy and coverage:

### New Tests Added
- List new test files/methods
- Describe test scenarios covered
- Note any integration tests

### Test Coverage
- Current coverage: X%
- Coverage after changes: Y%
- Critical paths tested: [list]

## Performance Impact
- [ ] No performance impact
- [ ] Performance improvement (describe)
- [ ] Potential performance regression (describe mitigation)

## Documentation
- [ ] Code comments updated
- [ ] Docstrings updated
- [ ] User guide updated (if user-facing changes)
- [ ] CHANGELOG.md updated

## Checklist
- [ ] Rebased to latest develop
- [ ] All tests pass locally
- [ ] Code style checks pass
- [ ] No decrease in test coverage
- [ ] Documentation updated
- [ ] Self-review completed
```

### Review Process

#### Code Review Criteria

**Functionality**
- Does the code solve the intended problem?
- Are all requirements addressed?
- Are edge cases handled appropriately?

**Code Quality**
- Is the code readable and well-structured?
- Are naming conventions followed?
- Is the code DRY (Don't Repeat Yourself)?

**Testing**
- Is test coverage comprehensive?
- Do tests actually validate the intended behavior?
- Are tests maintainable and clear?

**Documentation**
- Are docstrings complete and accurate?
- Is user-facing documentation updated?
- Are complex algorithms explained?

#### Required Approvals
- **1 Reviewer Minimum**: For small changes and bug fixes
- **2 Reviewers Required**: For new features and breaking changes
- **Maintainer Approval**: Required for all changes to core inference logic

### Merge Requirements

#### Automated Checks Must Pass
- All CI tests pass on all supported Python versions
- Code coverage remains above threshold (90%)
- Style and type checks pass
- No security vulnerabilities detected

#### Manual Verification
- Code review approval from required reviewers
- Functional testing on example networks
- Performance regression testing (for core changes)
- Documentation review (for user-facing changes)

---

## Debugging and Performance

### Debugging Strategies

#### Logging Configuration
```python
import logging

# Configure logging for development
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bayescalc_debug.log'),
        logging.StreamHandler()
    ]
)

# Use in modules
logger = logging.getLogger(__name__)

class VariableElimination:
    def eliminate_variable(self, variable: str) -> None:
        logger.debug(f"Eliminating variable: {variable}")
        logger.debug(f"Current factors: {[f.name for f in self.factors]}")
        
        # Implementation
        
        logger.info(f"Successfully eliminated {variable}")
```

#### Debug Helper Functions
```python
def debug_network_state(network: BayesianNetwork) -> None:
    """Print detailed network state for debugging."""
    print(f"Network has {len(network.variables)} variables:")
    for var_name, var in network.variables.items():
        print(f"  {var_name}: {var.domain}")
    
    print(f"Network has {len(network.factors)} factors:")
    for factor in network.factors:
        print(f"  {factor.name}: {len(factor.probabilities)} entries")

def debug_probability_computation(network: BayesianNetwork, query: str) -> None:
    """Debug probability computation step-by-step."""
    print(f"Computing: {query}")
    
    # Parse query
    query_obj = network.parse_query(query)
    print(f"Parsed query: {query_obj}")
    
    # Show elimination order
    elimination_order = network.get_elimination_order(query_obj)
    print(f"Elimination order: {elimination_order}")
    
    # Step through elimination
    for step, variable in enumerate(elimination_order):
        print(f"Step {step + 1}: Eliminating {variable}")
        # ... detailed elimination logging
```

### Performance Optimization

#### Profiling Code
```python
import cProfile
import pstats
from functools import wraps

def profile_function(func):
    """Decorator to profile function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # Top 20 functions
    return wrapper

# Usage
@profile_function
def compute_complex_query(network, query):
    return network.compute_probability(query)
```

#### Performance Benchmarks
```python
import time
from typing import List, Tuple

def benchmark_inference(network: BayesianNetwork, queries: List[str]) -> List[Tuple[str, float]]:
    """Benchmark inference performance on multiple queries."""
    results = []
    
    for query in queries:
        start_time = time.time()
        try:
            result = network.compute_probability(query)
            end_time = time.time()
            duration = end_time - start_time
            results.append((query, duration))
            print(f"{query}: {duration:.4f}s")
        except Exception as e:
            print(f"{query}: ERROR - {e}")
            results.append((query, -1))
    
    return results

# Example usage
queries = [
    "P(Rain=True)",
    "P(Rain=True | Sprinkler=True)",
    "P(GrassWet=True | Rain=False, Sprinkler=False)"
]
benchmark_results = benchmark_inference(network, queries)
```

#### Memory Optimization
```python
import sys
from typing import Dict, Any

def analyze_memory_usage(network: BayesianNetwork) -> Dict[str, Any]:
    """Analyze memory usage of network components."""
    analysis = {}
    
    # Variable memory
    var_sizes = {name: sys.getsizeof(var) for name, var in network.variables.items()}
    analysis['variables'] = {
        'count': len(network.variables),
        'total_size': sum(var_sizes.values()),
        'individual_sizes': var_sizes
    }
    
    # Factor memory
    factor_sizes = {}
    for factor in network.factors:
        size = sys.getsizeof(factor.probabilities)
        factor_sizes[factor.name] = {
            'probability_table_size': size,
            'entry_count': len(factor.probabilities)
        }
    
    analysis['factors'] = factor_sizes
    analysis['total_estimated_size'] = (
        analysis['variables']['total_size'] + 
        sum(f['probability_table_size'] for f in factor_sizes.values())
    )
    
    return analysis
```

---

## Building the Documentation

The project uses [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/) for documentation.

Install documentation dependencies:
```bash
pip install -e ".[docs]"
```

Build and serve documentation locally:
```bash
# Start development server (http://127.0.0.1:8000)
./scripts/mkdocs.sh serve

# Build static site to site/
./scripts/mkdocs.sh build

# Deploy to GitHub Pages (maintainers only)
./scripts/mkdocs.sh deploy

# Clean built documentation
./scripts/mkdocs.sh clean
```

The documentation is automatically built by the `docs.yml` GitHub workflow. It is built for each push (and PR) on `develop` and `main` branches. A new site is deployed only when a push to the `main` branch is made. The site is then pushed to the `gh-pages` branch which is automatically mapped to GitHub pages on [johan162.github.io/bayescalc2](https://johan162.github.io/bayescalc2).


---

## Release Process

### Version Management

#### Semantic Versioning
BayesCalc2 follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)


### Release Checklist

#### Pre-Release
- [ ] All tests pass on all supported Python versions
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are updated consistently
- [ ] Performance benchmarks show no regressions
- [ ] Security scan passes

#### Git Flow and Release Strategy

BayesCalc2 follows a simplified **Git Flow** branching strategy with continuous integration principles:

#### Branching Model Diagrams

To make the workflow clearer, here are separate diagrams for each major proces.

**1. High-Level Overview**

This diagram shows the main relationship between the `develop` and `main` branches. Features are integrated into `develop`.

```
main   <------------------ develop
                              ^
                              |
                              '---- feature/bugfix/refactor/etc.
```

**2. Feature/Bugfix/Refactor Branch Workflow**

Feature/bugfix/refactor branches are for developing new features and bugfixes. They are created from `develop` and merged back into `develop`.

```
           (start work)
develop ------------------.----------------------------------.------------>
                           \                                / (merge PR)
                            `---( feature/new-feature )----`
                                (commit 1) (commit 2)
```


### Branch Types and Purposes

**`main` Branch** (Production)
- **Purpose**: Stable, production-ready code
- **Protection**: Direct pushes forbidden, only PRs from release branches
- **Tags**: All releases tagged here (v1.0.0, v1.1.0, etc.)
- **Deployments**: Automatic PyPI releases triggered from tags

**`develop` Branch** (Integration)  
- **Purpose**: Integration branch for feature development
- **Source**: All feature branches merge here first
- **Target**: Release branches created from here
- **CI**: Continuous testing on every push

**Feature Branches** (`feature/*`)
- **Purpose**: Individual feature development
- **Naming**: `feature/descriptive-name` (e.g., `feature/tab-completion`)
- **Source**: Branch from `develop`
- **Target**: Merge back to `develop` via PR (or direct merge))
- **Lifetime**: Short-lived (days to weeks)

**Bugfix Branches** (`bugfix/*`)
- **Purpose**: Individual bugfix development
- **Naming**: `bugfix/bug-description` (e.g., `bugfix/missing-option-check`)
- **Source**: Branch from `develop`
- **Target**: Merge back to `develop` via PR (or direct merge)
- **Lifetime**: Short-lived (days to weeks)


#### Standard Release Process

**Simplified Direct Release** - Stringent quality controls with streamlined workflow.

**Prerequisites:**
- All planned features merged to `develop` branch
- No known critical bugs
- Documentation updated for new features
- All tests passing on latest `develop` by passing the build script `scripts/mkbld.sh`

**Release Scripts** 

The release process is a two-step stage process

#### Release step 1: Createing a release tag
Running the git release script  `scripts/mkrelease.sh` while on the `develop` branch.
   This will merge back and squash all changes on develop to main, tag the release, and finally
   merge back changes from main onto develop. 

Usage: 

`./scripts/mkrelease.sh <version> [major|minor|patch] [--dry-run] [--help]`

```
$ ./scripts/mkrelease.sh 2.1.0 minor
$ ./scripts/mkrelease.sh 2.1.0 minor --dry-run
$ ./scripts/mkrelease.sh --help
```


**Quality Gates Enforced:**
- ✅ **80%+ test coverage** requirement
- ✅ **All example networks** must load and execute
- ✅ **CLI and REPL** functionality validation
- ✅ **Package building** and validation via twine
- ✅ **Static analysis** and code formatting checks
- ✅ **Integration testing** with real network files
- ✅ **Version consistency** across all files
- ✅ **Clean repository state** required
- ✅ **Semver compliance** validation
- ✅ **Duplicate version** prevention

#### Release step 2: Creating a GitHub Release

After a succesful run of the git/branch release script it is time to create the GitHub release. using the script `scripts/mkghrelease.sh`. This will use the latest tag created and name a new release with this name. The GitHub release will be made with an updated release note and the latest artifacts. Due to the CI/CD workflow this will also trigger a release to be pushed to PyPI with the given version number.

Usage:

`./scripts/mkghrelease.sh [--dry-run] [--help] [--pre-release]`

```
$ ./scripts/mkghrelease.sh
$ ./scripts/mkghrelease.sh --dry-run
$ ./scripts/mkghrelease.sh --help
$ ./scripts/mkghrelease.sh --pre-release
```

**Quality Gates Enforced:**
- ✅ **Authenticated** That the user is authenticated to use `gh`
- ✅ **Running workflows** Checks that no workflows are currently running
- ✅ **Auto-naming** Identifies the latest tag on main branch
- ✅ **Tag validation** Validates tag format (vX.Y.Z or vX.Y.Z-rcN)
- ✅ **Artifact validation** Validates artifacts in dist/ directory
- ✅ **Release creation** Creates GitHub release with artifacts and release notes


### Post-Release

#### Verification
- [ ] PyPI package installs correctly
- [ ] Documentation site updated
- [ ] GitHub release created with notes
- [ ] Announcement posted (if major release)

#### Monitoring
- Monitor for bug reports
- Track download statistics
- Gather user feedback
- Plan next release cycle

---

# Appendix A: Variable Elimination Algorithm - Detailed Implementation Guide

This appendix provides a comprehensive, step-by-step explanation of the Variable Elimination algorithm as implemented in BayesCalc2, complete with worked examples and implementation details.

## Algorithm Overview

Variable Elimination is an exact inference algorithm for Bayesian networks that computes marginal and conditional probabilities by systematically eliminating variables through factor operations. The algorithm transforms a complex joint probability computation into a sequence of simpler factor manipulations.

### Core Concept

Instead of computing the full joint probability table (which grows exponentially), Variable Elimination works with **factors** - smaller probability tables that are combined and reduced as needed. This approach is much more efficient for most practical networks.

### Mathematical Foundation

For a Bayesian network with variables X₁, X₂, ..., Xₙ, the joint probability factors as:

**P(X₁, X₂, ..., Xₙ) = ∏ᵢ P(Xᵢ | Parents(Xᵢ))**

To compute a conditional probability P(Q | E) where Q are query variables and E is evidence:

**P(Q | E) = P(Q, E) / P(E) = ∑_{hidden} ∏ᵢ P(Xᵢ | Parents(Xᵢ)) / ∑_Q ∑_{hidden} ∏ᵢ P(Xᵢ | Parents(Xᵢ))**

Variable elimination computes this efficiently by eliminating hidden variables in a strategic order.

## Step-by-Step Algorithm

### Phase 1: Network Preparation

**Input**: Query variables Q, Evidence E, Bayesian Network BN
**Output**: Conditional probability distribution P(Q | E)

1. **Extract Factors**: Convert CPTs to Factor objects
2. **Apply Evidence**: Reduce factors by incorporating observed values
3. **Identify Variables**: Determine which variables need elimination
4. **Order Selection**: Choose elimination order (affects efficiency)

### Phase 2: Variable Elimination Loop

For each variable X to eliminate:
1. **Collect Factors**: Find all factors containing X
2. **Join Factors**: Multiply factors together  
3. **Marginalize**: Sum out X from the joined factor
4. **Replace**: Substitute new factor for old ones

### Phase 3: Final Computation

1. **Join Remaining**: Multiply all remaining factors
2. **Normalize**: Convert to conditional probabilities

## Detailed Example: Rain-Sprinkler-GrassWet Network

Let's work through computing **P(Rain | GrassWet=True)** step by step.

### Network Definition

```
Variables:
- Rain ∈ {True, False}
- Sprinkler ∈ {True, False}  
- GrassWet ∈ {True, False}

Structure:
Rain → Sprinkler
Rain → GrassWet
Sprinkler → GrassWet

CPTs:
P(Rain=True) = 0.2
P(Rain=False) = 0.8

P(Sprinkler=True | Rain=True) = 0.01
P(Sprinkler=True | Rain=False) = 0.4
P(Sprinkler=False | Rain=True) = 0.99
P(Sprinkler=False | Rain=False) = 0.6

P(GrassWet=True | Rain=True, Sprinkler=True) = 0.99
P(GrassWet=True | Rain=True, Sprinkler=False) = 0.8
P(GrassWet=True | Rain=False, Sprinkler=True) = 0.9
P(GrassWet=True | Rain=False, Sprinkler=False) = 0.1
P(GrassWet=False | Rain=True, Sprinkler=True) = 0.01
P(GrassWet=False | Rain=True, Sprinkler=False) = 0.2
P(GrassWet=False | Rain=False, Sprinkler=True) = 0.1
P(GrassWet=False | Rain=False, Sprinkler=False) = 0.9
```

### Phase 1: Preparation

**Step 1.1: Extract Initial Factors**

```python
Factor₁: φ₁(Rain)
Variables: [Rain]
Probabilities: {
    (True,): 0.2,
    (False,): 0.8
}

Factor₂: φ₂(Sprinkler, Rain)
Variables: [Sprinkler, Rain]
Probabilities: {
    (True, True): 0.01,
    (True, False): 0.4,
    (False, True): 0.99,
    (False, False): 0.6
}

Factor₃: φ₃(GrassWet, Rain, Sprinkler)
Variables: [GrassWet, Rain, Sprinkler]
Probabilities: {
    (True, True, True): 0.99,
    (True, True, False): 0.8,
    (True, False, True): 0.9,
    (True, False, False): 0.1,
    (False, True, True): 0.01,
    (False, True, False): 0.2,
    (False, False, True): 0.1,
    (False, False, False): 0.9
}
```

**Step 1.2: Apply Evidence (GrassWet=True)**

We reduce Factor₃ by eliminating rows where GrassWet ≠ True:

```python
Factor₃': φ₃'(Rain, Sprinkler)  # GrassWet eliminated by evidence
Variables: [Rain, Sprinkler]
Probabilities: {
    (True, True): 0.99,     # was (True, True, True)
    (True, False): 0.8,     # was (True, True, False)
    (False, True): 0.9,     # was (True, False, True)
    (False, False): 0.1     # was (True, False, False)
}
```

**Step 1.3: Identify Variables to Eliminate**

- Query variables: {Rain}
- Evidence variables: {GrassWet}
- Variables to eliminate: {Sprinkler}

### Phase 2: Variable Elimination

**Step 2.1: Eliminate Sprinkler**

**Collect factors containing Sprinkler:**
- Factor₂: φ₂(Sprinkler, Rain)
- Factor₃': φ₃'(Rain, Sprinkler)

**Join Factor₂ and Factor₃':**

The join operation multiplies factors. For each combination of Rain and Sprinkler values:

```python
# Join: φ₄(Rain, Sprinkler) = φ₂(Sprinkler, Rain) × φ₃'(Rain, Sprinkler)

φ₄(True, True) = φ₂(True, True) × φ₃'(True, True)
                = 0.01 × 0.99 = 0.0099

φ₄(True, False) = φ₂(False, True) × φ₃'(True, False)  
                 = 0.99 × 0.8 = 0.792

φ₄(False, True) = φ₂(True, False) × φ₃'(False, True)
                 = 0.4 × 0.9 = 0.36

φ₄(False, False) = φ₂(False, False) × φ₃'(False, False)
                  = 0.6 × 0.1 = 0.06

Factor₄: φ₄(Rain, Sprinkler)
Variables: [Rain, Sprinkler]
Probabilities: {
    (True, True): 0.0099,
    (True, False): 0.792,
    (False, True): 0.36,
    (False, False): 0.06
}
```

**Sum out Sprinkler from Factor₄:**

The marginalization operation sums over all values of the eliminated variable:

```python
# Marginalize: φ₅(Rain) = ∑_{Sprinkler} φ₄(Rain, Sprinkler)

φ₅(True) = φ₄(True, True) + φ₄(True, False)
         = 0.0099 + 0.792 = 0.8019

φ₅(False) = φ₄(False, True) + φ₄(False, False)
          = 0.36 + 0.06 = 0.42

Factor₅: φ₅(Rain)
Variables: [Rain]
Probabilities: {
    (True,): 0.8019,
    (False,): 0.42
}
```

### Phase 3: Final Computation

**Step 3.1: Join Remaining Factors**

Remaining factors: Factor₁ (φ₁(Rain)) and Factor₅ (φ₅(Rain))

```python
# Join: φ₆(Rain) = φ₁(Rain) × φ₅(Rain)

φ₆(True) = φ₁(True) × φ₅(True) = 0.2 × 0.8019 = 0.16038
φ₆(False) = φ₁(False) × φ₅(False) = 0.8 × 0.42 = 0.336

Factor₆: φ₆(Rain)  # Unnormalized
Variables: [Rain]
Probabilities: {
    (True,): 0.16038,
    (False,): 0.336
}
```

**Step 3.2: Normalize**

```python
# Normalization: Convert to conditional probabilities
total = 0.16038 + 0.336 = 0.49638

P(Rain=True | GrassWet=True) = 0.16038 / 0.49638 ≈ 0.323
P(Rain=False | GrassWet=True) = 0.336 / 0.49638 ≈ 0.677
```

### Final Result

**P(Rain | GrassWet=True) = {True: 0.323, False: 0.677}**

This means that given the grass is wet, there's approximately a 32.3% chance it rained and a 67.7% chance it didn't rain.

## Implementation Details

### Factor Data Structure

```python
@dataclass
class Factor:
    variables: Tuple[Variable, ...]
    probabilities: Dict[Tuple[str, ...], float] = field(default_factory=dict)
    
    def __post_init__(self):
        # Ensure probabilities are normalized for each parent configuration
        self._validate_probabilities()
```

### Join Operation Implementation

```python
def _join_factors(self, factor1: Factor, factor2: Factor) -> Factor:
    """Join two factors by multiplication."""
    # Union of variables
    vars1 = set(factor1.variables)
    vars2 = set(factor2.variables)
    new_vars = tuple(vars1.union(vars2))
    
    # Create mapping from new variable order to old orders
    map1 = [new_vars.index(v) for v in factor1.variables]
    map2 = [new_vars.index(v) for v in factor2.variables]
    
    new_factor = Factor(new_vars)
    
    # Generate all possible assignments to new variables
    domains = [v.domain for v in new_vars]
    for assignment in product(*domains):
        # Extract sub-assignments for each original factor
        ass1 = tuple(assignment[i] for i in map1)
        ass2 = tuple(assignment[i] for i in map2)
        
        # Multiply probabilities (default to 1.0 if not present)
        prob1 = factor1.probabilities.get(ass1, 1.0)
        prob2 = factor2.probabilities.get(ass2, 1.0)
        new_factor.probabilities[assignment] = prob1 * prob2
    
    return new_factor
```

### Marginalization Implementation

```python
def _sum_out(self, factor: Factor, var_to_eliminate: Variable) -> Factor:
    """Sum out (marginalize) a variable from a factor."""
    if var_to_eliminate not in factor.variables:
        return factor
    
    # New variables exclude the eliminated variable
    var_index = list(factor.variables).index(var_to_eliminate)
    new_vars = tuple(v for v in factor.variables if v != var_to_eliminate)
    
    new_factor = Factor(new_vars)
    
    # Sum over all values of the eliminated variable
    for old_assignment, prob in factor.probabilities.items():
        # Create new assignment by removing the eliminated variable's value
        new_assignment = tuple(
            old_assignment[i] for i in range(len(old_assignment)) 
            if i != var_index
        )
        
        # Accumulate probability
        current_prob = new_factor.probabilities.get(new_assignment, 0.0)
        new_factor.probabilities[new_assignment] = current_prob + prob
    
    return new_factor
```

## Optimization Strategies

### Elimination Order Selection

The order in which variables are eliminated significantly affects performance. BayesCalc2 uses a simple heuristic:

```python
def _select_elimination_order(self, variables_to_eliminate: Set[str]) -> List[str]:
    """Select elimination order using min-fill heuristic."""
    return sorted(
        variables_to_eliminate,
        key=lambda var: sum(1 for f in self.factors if var in f.variable_names)
    )
```

**Better heuristics** (for future implementation):
- **Min-fill**: Choose variable that adds fewest edges to moral graph
- **Min-width**: Choose variable that results in smallest factor size
- **Weighted min-fill**: Consider both factor size and number of factors

### Complexity Analysis

**Time Complexity**: O(n × d^w) where:
- n = number of variables
- d = maximum domain size
- w = treewidth of elimination order

**Space Complexity**: O(d^s) where s = size of largest intermediate factor

**Practical Considerations**:
- Networks with tree structure: polynomial time
- Networks with cycles: potentially exponential
- Good elimination order crucial for performance

## Common Implementation Pitfalls

### 1. Factor Alignment Issues

**Problem**: Variables in different orders between factors
```python
# Wrong - assumes same variable order
factor1_vars = [A, B]  
factor2_vars = [B, A]  # Different order!
result = factor1.prob[0] * factor2.prob[0]  # Incorrect alignment
```

**Solution**: Use variable mapping
```python
# Correct - map variables properly
map1 = [new_vars.index(v) for v in factor1.variables]
map2 = [new_vars.index(v) for v in factor2.variables]
```

### 2. Evidence Handling Errors

**Problem**: Not properly reducing factors with evidence
```python
# Wrong - evidence not applied consistently
if var_name in evidence and assignment[var_idx] != evidence[var_name]:
    continue  # Skip inconsistent assignments
```

**Solution**: Normalize evidence values consistently
```python
# Correct - handle T/F vs True/False
def normalize_value(value):
    if value in ["T", "True"]: return "True"
    if value in ["F", "False"]: return "False"  
    return value
```

### 3. Numerical Precision Issues

**Problem**: Floating point errors accumulate
```python
# May have precision issues
if total_probability == 1.0:  # Exact comparison problematic
```

**Solution**: Use appropriate tolerances
```python
# Better - use epsilon for comparisons
if abs(total_probability - 1.0) < 1e-9:
```

## Testing Variable Elimination

### Unit Test Structure

```python
def test_variable_elimination_step_by_step(self):
    """Test each step of variable elimination."""
    # Setup
    network = self.create_rain_sprinkler_network()
    inference = Inference(network)
    
    # Test factor extraction
    factors = inference._extract_factors()
    self.assertEqual(len(factors), 3)
    
    # Test evidence reduction  
    evidence = {"GrassWet": "True"}
    reduced_factors = inference._apply_evidence(factors, evidence)
    
    # Verify evidence was applied correctly
    grass_factor = next(f for f in reduced_factors if "GrassWet" in f.variable_names)
    self.assertTrue(all("True" in str(assignment) for assignment in grass_factor.probabilities.keys()))
    
    # Test variable elimination
    result = inference.variable_elimination(["Rain"], evidence)
    
    # Verify normalization
    total_prob = sum(result.probabilities.values())
    self.assertAlmostEqual(total_prob, 1.0, places=6)
```

### Integration Tests

```python
def test_inference_against_hand_calculation(self):
    """Verify inference results match hand calculations."""
    known_results = {
        "P(Rain=True | GrassWet=True)": 0.323,
        "P(Rain=False | GrassWet=True)": 0.677,
        "P(Sprinkler=True | GrassWet=True)": 0.429,
        "P(Sprinkler=False | GrassWet=True)": 0.571
    }
    
    for query, expected in known_results.items():
        result = self.inference.compute_probability(query)
        self.assertAlmostEqual(result, expected, places=3, 
                             msg=f"Failed for query: {query}")
```

This detailed implementation guide provides everything needed to understand, modify, and extend the Variable Elimination algorithm in BayesCalc2. The step-by-step example demonstrates the algorithm's mechanics, while the implementation details show how theory translates to working code.

---

# APPENDIX B: GitHub Release Script Documentation

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

In the `scripts/` directory:

- `mkrelease.sh` - Create the release (run first)
- `mkbld.sh` - Build and test the package
- `README.md` - Complete scripts documentation


For using `gh` CLI:

- [GitHub CLI documentation](https://cli.github.com/manual/)
