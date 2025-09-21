As a math student and I want to create a Python program to investigate Bayesian networks. This should be a Bayesian network calculator useful for learning and teaching that I can query with standard mathematical notations.

Implement a Python program in a structured way. Priority readability before speed. Use standard libraries such as numpy when possible.
For lexical analysis and building if AST use standard libraries as far as possible.

# Core Components of the Bayesian Network Calculator
Should be structured into several modules under the `src/` directory. A suggested file structure could be:

1. lexer.py: Tokenizes the input string.
2. parser.py: Parses the tokens into an Abstract Syntax Tree (AST) representing the network.
3. network_model.py: Defines data structures for variables, CPTs, and the overall Bayesian Network. Contains logic for CPT  auto-completion and validation.
4. inference.py: Implements exact inference algorithms (e.g., Variable Elimination).
5. queries.py: Handles parsing and executing probability queries.
6. commands.py: Implements other utility commands (independence tests, tables, info-theory, graph).
7. repl.py: Manages the interactive REPL mode.
8. batch.py: Handles batch mode execution.
9. main.py: Entry point for the application.


# Detailed specification

## A) Input Format and Grammar

The input format should be designed to be **human-readable**, **robust**, and **formally parsable**. Inspired by INI/JSON-like formats, but simpler for high readability and parsing.

The input format should support either Bayesian networks using "*.net" files or Joint Probability tables using the "*.jpt" format.

### Example Bayesian Network Format (Multi value variables)

```
# Example network definition
variable Rain {True, False}
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

If only boolean variables are used the specification can be simplified as

```
# Example network definition. Simpleified Boolean variables
variable Rain 
variable Sprinkler 
variable GrassWet 

# CPT definitions
Rain {
    P(T) = 0.2 # Could also be specified as P(1) = 0.2
    # P(False) will be auto-filled
}

Sprinkler | Rain {
    P(T | T) = 0.01
    P(T | T) = 0.4
    # P(F | parent) auto-filled
}

GrassWet | Rain, Sprinkler {
    P(T | T, T) = 0.99
    P(T | T, F) = 0.8
    P(T | F, T) = 0.9
    # Remaining CPTs auto-completed
}
```


#### Bayesian Network Formal Grammar (EBNF style)

For use with `*.net` input files.

```
<network>       ::= { <variable_decl> | <cpt_block> }

<variable_decl> ::= "variable" <identifier> "{" <value_list> "}"
<value_list>    ::= <identifier> { "," <identifier> }

<cpt_block>     ::= <identifier> [ "|" <parent_list> ] "{" { <cpt_entry> } "}"
<parent_list>   ::= <identifier> { "," <identifier> }

<cpt_entry>     ::= "P(" <value> [ "|" <condition_list> ] ")" "=" <probability>
<condition_list>::= <value> { "," <value> }

<probability>   ::= <float>
<float>         ::= DIGIT+ "." DIGIT+
<identifier>    ::= LETTER { LETTER | DIGIT | "_" }
<value>         ::= <identifier>
```

This grammar is compact, easy to parse, supports Boolean and multi-valued variables, and allows *partial specification* of CPTs.

### Example Joint Probability Table Format for Boolean variables

```
variable Sickness    # If yoiu are sick or not
variable Test        # The medicla test

Sickness, Test {
    FF = 0.12
    FT = 0.32
    TF = 0.18
    TT = 0.38
}
```

#### Joint Probability Table Format Formal Grammar (EBNF style)

For use with `*.jpt` input files.

```
<network>       ::= { <variable_decl> | <jpt_block> }

<variable_decl> ::= "variable" <identifier> 

<jpt_block>     ::= <identifier> [ "," <parent_list> ] "{" { <jpt_entry> } "}"

<jpt_entry>     ::= jpt_list "=" <probability>
<jpt_list>      ::= <jpt_value> { <jpt_value> }

<probability>   ::= <float>
<float>         ::= DIGIT+ "." DIGIT+
<identifier>    ::= LETTER { LETTER | DIGIT | "_" }
<jpt_value>     ::= <T|F>
```

***

## B) Commands Set

### Probability Queries

- `P(A)` – marginal probability.
- `P(A|B)` – conditional.
- `P(A,B)` – joint.
- `P(A|B,C)` – multi-conditionals.
- Arithmetic with probabilities (e.g., `P(A|B)*P(B)`).


### Independence Tests

- `isindependent(A,B)`
- `iscondindependent(A,B|C)`


### Tables

- `printCPT(X)` – CPT of node X.
- `printJPT()` – full joint probability table.
- `printContingency(A,B[,C,D])` – contingency table.


### Information-Theoretic

- `entropy(X)`
- `conditional_entropy(X|Y)`
- `mutual_information(X,Y)`
- `kl_divergence(P||Q)` if comparing models.


### Graph \& Structure

- `showGraph()` – ASCII graph of network.
- `parents(X)`
- `children(X)`

***

## C) Detailed Requirements 

### Input / Network Model

1. The system must parse the network specification defined by the custom grammar and give good error messages to helk the user
2. The parser must produce detailed and specific error messages on incorrect syntax or if probability values adds up incorrectly.
3. The input format must allow both Boolean and multi-valued nodes.
4. Each variable must have explicitly defined states.
5. CPT entries must only require minimal specification, with missing rows auto-completed.
6. Probabilities must be validated for correctness (range , rows sum to 1).
7. It must be possible to give long variable names.
8. Variables with no parents must support prior probability declarations.
9. Dependencies between variables must be clearly represented.

### Probability Computation

10. Must compute marginal probabilities of any variable.
11. Must compute conditional probabilities.
12. Must compute joint probabilities.
13. Must support basic probability arithmetic operations with symbolic commands.
14. Efficient inference must work up to ~15 Boolean or ~8 multi-valued variables.

### Queries

15. Support expressions like `P(A|B)` where A,B can be events or conjunctions.
16. Allow arithmetic expressions such as `P(A|B)*P(B)/P(A,B)`.
17. Implement independence checks (`isindependent`).
18. Implement conditional independence checks (`iscondindependent`).
19. Tab-style completiopn should be possible for both variable names, value names, and commands

### Commands / Outputs

20. `printCPT(X)` must output a CPT in readable tabular format.
21. `printJPT()` must print the full joint table.
22. `printContingency(A,B,C,D)` must handle up to 4 variables nicely formatted.
23. Graph visualization must support ASCII rendering.
24. Queries must show numeric results with 4–6 decimal precision.

### Information-Theoretic

25. Must compute entropy of a variable.
26. Must compute conditional entropy given another variable.
27. Must compute mutual information.
28. Must compute KL divergence between models or distributions.

### Execution Modes

29. Interactive REPL mode must allow iterative queries by user.
30. Batch mode must read a model and list of commands and output results directly.
31. Errors in batch mode must be clear and not interrupt entire processing.
32. REPL mode must support history of commands.
33. Both modes must be consistent on command execution.

### Testing / Quality

34. All functionality must be unit-testable.
35. Integration tests must validate full workflow from network definition → query → output.
36. Timing performance must be reasonable for networks within scope (8 multi-value, 15 Boolean).
37. Parser should be tested for robustness against malformed input.
38. The output of probability values must be consistent with exact values within floating-point tolerance.

### Usability

38. Must support comments (`#`).
39. Must not be sensitive to whitespace variations.
40. Must provide help command listing all supported operations in REPL.

***

## D) Possible Extensions

Keep these future extensions in mind while developing the code

- **Sampling methods**: Add approximate inference via Gibbs sampling when exact computation is infeasible.
- **Learning from data**: Extend input format to allow datasets and perform parameter learning (estimate CPTs from frequency counts).
- **Sensitivity analysis**: Show how output probability changes if input CPTs vary slightly.
- **Export formats**: Ability to export/import from standard Bayesian network formats like `.xdsl` or `.bif`.
- **Visualization**: Graphical (non-ASCII) output using libraries like `networkx` or `graphviz`.
- **Explanations**: Explain step-by-step how a probability was computed (useful for teaching).

***



