# Load Command Usage

## Overview
The `load` command allows you to dynamically load a new Bayesian network from a file without restarting the REPL session.

## Syntax
```
load(filename)
```

## Features
- **Tab Completion**: File paths support tab completion for easy navigation
- **Automatic Reload**: All internal state (queries, inference engine, completers) are automatically updated
- **Error Handling**: Clear error messages for missing or invalid files
- **Path Expansion**: Supports `~` for home directory expansion

## Examples

### Basic Usage
```
>> load(examples/rain_sprinkler_grass.net)
Successfully loaded network from: examples/rain_sprinkler_grass.net
Variables (3): GrassWet, Rain, Sprinkler
```

### Using Tab Completion
```
>> load(ex<TAB>         # Press TAB to complete
>> load(examples/<TAB>  # Press TAB to see available .net files
>> load(examples/rain_sprinkler_grass.net)
```

### Loading from Different Directories
```
>> load(~/Documents/my_network.net)
>> load(../other_project/network.net)
>> load(/absolute/path/to/network.net)
```

### Error Handling
```
>> load(nonexistent.net)
Error: Network file not found: nonexistent.net

>> load(invalid.net)
Error: Error parsing network file 'invalid.net': ...
```

## Use Cases

1. **Experimentation**: Switch between different network configurations to compare results
2. **Iterative Development**: Edit your network file externally and reload to test changes
3. **Teaching**: Demonstrate different network structures in a single session
4. **Debugging**: Test edge cases by loading various network configurations

## Notes

- The previous network state is completely replaced
- All queries and computations reference the new network after loading
- File paths are relative to the current working directory where BayesCalc2 was launched
- Only `.net` files appear in tab completion suggestions (directories also shown for navigation)
