# BayesCalc2 AI Coding Instructions

## Architecture Overview

BayesCalc2 is a Bayesian network calculator with a **pipeline architecture**: `lexer.py` → `parser.py` → `network_model.py` → `inference.py`. The system supports both interactive REPL and batch processing modes.

### Core Components

- **Network Definition Pipeline**: `.net files` → `Lexer` (tokenization) → `Parser` (AST) → `BayesianNetwork` (data model)
- **Query Processing**: `QueryParser` handles `P(A|B)` syntax, `ExpressionParser` for arithmetic (`P(A)*P(B)/P(C)`)
- **Inference Engine**: Uses variable elimination algorithm in `inference.py` (NOT naive joint probability tables)
- **Interactive Shell**: `REPL` class with prompt_toolkit integration, tab completion via `completer.py`

## Key Patterns

### Network File Format (.net)
```
variable Rain {True, False}
Rain { P(True) = 0.2 }
GrassWet | Rain, Sprinkler {
    P(Yes | True, On) = 0.99
    # Missing probabilities auto-completed to sum to 1
}
```

### Testing Strategy
- Use `setUpClass()` for shared network setup across test methods
- Standard pattern: `Lexer(net_str) → Parser(tokens) → network → Inference(network)`
- Test files in `tests/` follow `test_*.py` naming convention
- Run tests with `python -m pytest tests/` from project root

### Boolean Variables Detection
Variables are automatically classified as Boolean if domain contains `{True, False}` or `{T, F}`. Access via `Variable.is_boolean` property.

## Development Workflows

### Adding New Commands
1. Register in `CommandHandler._initialize_command_registry()`
2. Implement handler method following naming convention `cmd_name → self.cmd_name`
3. Add to `completer.py` for tab completion support

### Network File Parsing
- Lexer tokenizes into `TokenType` enum values
- Parser uses recursive descent with `_consume()`, `_peek()`, `_advance()` methods
- Missing probabilities automatically normalized to sum to 1.0

### Query Execution Path
Interactive: `REPL.run()` → `QueryParser.parse_and_execute()` → `Inference.variable_elimination()`
Batch: `main()` → `run_batch()` → `execute_commands()` → same query path

## Critical Dependencies

- **prompt_toolkit**: Only imported in non-test environments (check `'pytest' not in sys.modules`)
- **numpy**: Used in inference calculations, not for basic probability operations
- Entry point: `bayescalc = "bayescalc.main:main"` in `pyproject.toml`

## Common Gotchas

- Factor operations in `inference.py` modify probability tables in-place
- REPL commands don't require parentheses: `printCPT Rain` works, but functions do: `entropy(Rain)`
- Variable names are case-sensitive throughout the system
- Tab completion only works in interactive mode, not batch processing

## File Organization

- Core logic: `src/bayescalc/` (avoid editing test files for business logic)
- Network examples: `examples/*.net` (good for testing parsing edge cases)
- Main entry: `src/bayescalc/main.py` handles argument parsing and mode selection