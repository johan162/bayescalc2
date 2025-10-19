# Examples

This page provides detailed examples of using BayesCalc2 for various probabilistic reasoning tasks.

## Medical Diagnosis

The medical diagnosis network demonstrates Bayesian reasoning about diseases and test results.

### Network Definition (`medical_test.net`)

```
variable Disease {Present, Absent}
variable TestResult {Positive, Negative}
variable Symptom {Severe, Mild, None}

Disease { P(Present) = 0.01 }

Symptom | Disease {
    P(Severe | Present) = 0.6
    P(Mild | Present) = 0.3
    P(None | Present) = 0.1
    P(Severe | Absent) = 0.01
    P(Mild | Absent) = 0.09
    P(None | Absent) = 0.9
}

TestResult | Disease {
    P(Positive | Present) = 0.95
    P(Negative | Present) = 0.05
    P(Positive | Absent) = 0.10
    P(Negative | Absent) = 0.90
}
```

### Example Queries

**Prior probability of disease:**
```
BayesCalc> P(Disease=Present)
P(Disease=Present) = 0.0100
```

**Probability with positive test:**
```
BayesCalc> P(Disease=Present|TestResult=Positive)
P(Disease=Present | TestResult=Positive) = 0.0876
```

**Probability with symptoms and positive test:**
```
BayesCalc> P(Disease=Present|TestResult=Positive, Symptom=Severe)
P(Disease=Present | TestResult=Positive, Symptom=Severe) = 0.8632
```

### Insights

- A positive test alone only raises disease probability to ~9% (from 1% prior)
- Combining positive test with severe symptoms raises probability to ~86%
- This demonstrates the importance of multiple evidence sources

## Weather Prediction

A classic Bayesian network example showing how rain and sprinklers affect grass wetness.

### Network Definition (`rain_sprinkler_grass.net`)

```
variable Rain {True, False}
variable Sprinkler {On, Off}
variable GrassWet {Yes, No}

Rain { P(True) = 0.2 }

Sprinkler | Rain {
    P(On | True) = 0.01
    P(On | False) = 0.4
}

GrassWet | Rain, Sprinkler {
    P(Yes | True, On) = 0.99
    P(Yes | True, Off) = 0.90
    P(Yes | False, On) = 0.85
    P(Yes | False, Off) = 0.05
}
```

### Example Queries

**Explaining away phenomenon:**
```
BayesCalc> P(Rain|GrassWet=Yes)
P(Rain=True | GrassWet=Yes) = 0.6203

BayesCalc> P(Rain|GrassWet=Yes, Sprinkler=On)
P(Rain=True | GrassWet=Yes, Sprinkler=On) = 0.2686
```

Learning the sprinkler was on "explains away" some of the evidence for rain.

## Student Network

Models student exam performance based on intelligence and exam difficulty.

### Network Definition (`student_network.net`)

```
variable Intelligence {High, Medium, Low}
variable Difficulty {Hard, Easy}
variable Grade {A, B, C}

Intelligence {
    P(High) = 0.3
    P(Medium) = 0.5
    P(Low) = 0.2
}

Difficulty { P(Hard) = 0.4 }

Grade | Intelligence, Difficulty {
    P(A | High, Hard) = 0.6
    P(B | High, Hard) = 0.3
    P(C | High, Hard) = 0.1
    
    P(A | High, Easy) = 0.9
    P(B | High, Easy) = 0.08
    P(C | High, Easy) = 0.02
    
    P(A | Medium, Hard) = 0.2
    P(B | Medium, Hard) = 0.5
    P(C | Medium, Hard) = 0.3
    
    P(A | Medium, Easy) = 0.5
    P(B | Medium, Easy) = 0.4
    P(C | Medium, Easy) = 0.1
    
    P(A | Low, Hard) = 0.05
    P(B | Low, Hard) = 0.25
    P(C | Low, Hard) = 0.7
    
    P(A | Low, Easy) = 0.2
    P(B | Low, Easy) = 0.4
    P(C | Low, Easy) = 0.4
}
```

### Example Queries

**Inferring intelligence from grade:**
```
BayesCalc> P(Intelligence|Grade=A)
P(Intelligence=High | Grade=A) = 0.5368
P(Intelligence=Medium | Grade=A) = 0.3473
P(Intelligence=Low | Grade=A) = 0.1159
```

**Effect of knowing difficulty:**
```
BayesCalc> P(Intelligence=High|Grade=A, Difficulty=Hard)
P(Intelligence=High | Grade=A, Difficulty=Hard) = 0.7568
```

A grade of 'A' on a hard exam is stronger evidence of high intelligence.

## Asia Chest Clinic

A more complex medical diagnosis network from the Bayesian network literature.

### Network Structure

- **Visit to Asia**: Binary variable
- **Tuberculosis**: Influenced by Asia visit
- **Smoking**: Binary variable
- **Lung Cancer**: Influenced by smoking
- **Bronchitis**: Influenced by smoking
- **TuberculosisOrCancer**: Logical OR of tuberculosis and lung cancer
- **X-Ray Result**: Influenced by TuberculosisOrCancer
- **Dyspnoea**: Influenced by TuberculosisOrCancer and bronchitis

### Example Queries

```
BayesCalc> load examples/asia_chest_clinic.net
Network loaded successfully.

BayesCalc> P(LungCancer|Dyspnoea=Yes, XRayResult=Abnormal)
P(LungCancer=Yes | Dyspnoea=Yes, XRayResult=Abnormal) = 0.1025

BayesCalc> P(LungCancer|Dyspnoea=Yes, XRayResult=Abnormal, Smoking=Yes)
P(LungCancer=Yes | Dyspnoea=Yes, XRayResult=Abnormal, Smoking=Yes) = 0.1217
```

## Boolean Shorthand

BayesCalc2 supports convenient shorthand for Boolean variables:

```
variable Rain {True, False}

Rain { P(True) = 0.2 }
```

Query with shorthand:
```
BayesCalc> P(Rain)        # Same as P(Rain=True)
P(Rain=True) = 0.2000

BayesCalc> P(!Rain)       # Same as P(Rain=False)
P(Rain=False) = 0.8000
```

Conditional queries:
```
BayesCalc> P(Rain|GrassWet)  # Same as P(Rain=True|GrassWet=True)
P(Rain=True | GrassWet=True) = 0.6203
```

## Expression Evaluation

Combine multiple probabilities in arithmetic expressions:

```
BayesCalc> P(Rain) * P(Sprinkler)
0.0200

BayesCalc> P(Rain|GrassWet) / P(Rain)
3.1015

BayesCalc> 1 - P(Rain)
0.8000
```

## Network Visualization

Generate PDF diagrams of your networks:

```
BayesCalc> visualize network.pdf
Visualization saved to network.pdf

BayesCalc> visualize network.pdf --page-size=letter --scale=1.2
Visualization saved to network.pdf (letter size, 120% scale)
```

Supported page sizes: `a4`, `letter`, `legal`, `a3`, `tabloid`

## Batch Processing

Create a command file `analysis.txt`:

```
# Load network
load examples/medical_test.net

# Basic queries
P(Disease=Present)
P(TestResult=Positive)

# Conditional probabilities
P(Disease=Present|TestResult=Positive)
P(Disease=Present|TestResult=Positive, Symptom=Severe)

# Visualize
visualize medical_diagnosis.pdf

# Save results
# (Would need to redirect stdout in shell)
```

Run in batch mode:
```bash
bayescalc -b analysis.txt
```

## Advanced Analysis

### Information Theory

Calculate entropy and mutual information:

```
BayesCalc> entropy(Disease)
H(Disease) = 0.0808 bits

BayesCalc> mutualInformation(Disease, TestResult)
I(Disease; TestResult) = 0.0352 bits
```

### Network Inspection

```
BayesCalc> ls
Variables:
  - Disease: {Present, Absent}
  - TestResult: {Positive, Negative}
  - Symptom: {Severe, Mild, None}

BayesCalc> printCPT Disease
CPT for Disease:
P(Disease=Present) = 0.0100
P(Disease=Absent) = 0.9900

BayesCalc> printCPT TestResult
CPT for TestResult | Disease:
P(TestResult=Positive | Disease=Present) = 0.9500
P(TestResult=Negative | Disease=Present) = 0.0500
P(TestResult=Positive | Disease=Absent) = 0.1000
P(TestResult=Negative | Disease=Absent) = 0.9000
```

## Tips and Tricks

### 1. Use Tab Completion

In interactive mode, press Tab to complete:
- Variable names
- Command names
- Domain values

### 2. Auto-normalization

You don't need to specify all probabilities:

```
variable Coin {Heads, Tails}
Coin { P(Heads) = 0.5 }  # Tails automatically gets 0.5
```

### 3. Missing Probabilities

If you don't specify probabilities for some combinations, they're auto-normalized:

```
GrassWet | Rain, Sprinkler {
    P(Yes | True, On) = 0.99
    P(Yes | True, Off) = 0.90
    # Other combinations auto-normalized
}
```

### 4. Error Checking

BayesCalc2 validates your network definition:
- Probabilities must sum to 1.0
- All parent configurations must be covered
- Variable names must be unique
- Domain values must be unique within a variable

### 5. Performance

For large networks:
- Variable elimination is efficient (much better than joint tables)
- Order queries from most to least specific evidence
- Consider breaking very large networks into subnetworks

## More Examples

Explore the `examples/` directory for more networks:

- `alarm_network.net` - Home alarm system
- `car_starting.net` - Car troubleshooting
- `credit_approval.net` - Credit risk assessment
- `genetic_inheritance.net` - Genetic traits
- `heart_disease.net` - Cardiovascular diagnosis
- `marketing_funnel.net` - Customer conversion
- `monty_hall.net` - The famous probability puzzle
- `text_classification.net` - Document categorization

Each demonstrates different aspects of Bayesian reasoning!
