# Command Parsing Priority Fix

## Problem

The `load()` command was being incorrectly parsed as a mathematical expression instead of a command, resulting in the error:

```
>> load(examples/rain_sprinkler_grass.net)
Error: Error evaluating mathematical expression 'load(examples/rain_sprinkler_grass.net)': 
Invalid mathematical expression: load(examples/rain_sprinkler_grass.net). 
Error: name 'load' is not defined
```

## Root Cause

The REPL's execution flow was:

1. Check if input can be evaluated as an expression (`expression_parser.can_evaluate()`)
2. If yes, try to evaluate as mathematical expression
3. Otherwise, try to execute as a command

The `can_evaluate()` method returns `True` for any string containing parentheses (like function calls), which included commands like `load(filename)`.

## Solution

Changed the REPL's execution priority to:

1. **Check if input is a known command first** (`command_handler.is_command()`)
2. Execute as command if matched
3. Otherwise, check if it can be evaluated as an expression
4. Execute as expression if matched
5. Report error if neither

### Changes Made

#### 1. Added `is_command()` method to `CommandHandler` (commands.py)

```python
def is_command(self, command_str: str) -> bool:
    """Check if the given string looks like a command from the command registry."""
    command_str = command_str.strip()
    
    # Check if it's a command without arguments
    if command_str in self.alias_to_command:
        return True
    
    # Check if it matches command(args) pattern
    match = re.match(r"(\w+)\(", command_str)
    if match:
        command = match.group(1)
        return command in self.alias_to_command
    
    return False
```

#### 2. Updated REPL execution flow (repl.py)

```python
# Check if it's a known command first (before trying expression evaluation)
if self.command_handler.is_command(line):
    try:
        result = self.command_handler.execute(line)
        print(result)
    except (ValueError, SyntaxError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
    continue

# Check if it can be evaluated as an expression (mathematical or probability)
if self.expression_parser.can_evaluate(line):
    # ... expression evaluation logic ...
```

## Benefits

1. **Commands work correctly**: `load()`, `printCPT()`, etc. are executed as commands
2. **No regression**: Probability queries like `P(A|B)` still work as expressions
3. **Clear precedence**: Commands have priority over expressions
4. **Better error messages**: Unknown commands get helpful error messages

## Testing

Added comprehensive tests in:
- `tests/test_command_priority.py` - Tests `is_command()` method
- `tests/test_load_integration.py` - Integration tests for REPL context
- All existing tests pass (22/22)

## Commands vs Expressions

After this fix:

| Input | Treated As | Reason |
|-------|-----------|---------|
| `load(file.net)` | Command | Matches command registry |
| `printCPT(Rain)` | Command | Matches command registry |
| `P(A)` | Expression | Not in command registry |
| `P(A) * P(B)` | Expression | Not in command registry |
| `log(0.5)` | Expression | Not in command registry |
| `entropy(X)` | Command | Matches command registry |
