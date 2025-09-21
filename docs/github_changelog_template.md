# Release Notes for v2.0.0

## Summary

Bayescalc2 is a bayesion inference engine allowing a Bayesian network specified to be
investigated using standard mathematical notation. 

```
python -m bayescalc.main examples/medical.net 
>> ls 
Variable | Type       | States       
----------------------------------- 
Sick     | Boolean    | True, False  
Test     | Boolean    | True, False 
>> P(Sick|Test)
  P() = 0.137881
>> P(Test|Sick)*P(Sick)
  = 0.009500
```

Bayescalc2 is a complete rewrite of Bayescalc with a new inference engined based on variable elimination
rather than complete JPT (Joint Probability Table) which grows exponentially in size with variables 
and states. In this way Bayescalc2 is slightly slower but can handle more variables in tractable time and
memory.

The variable elimination algorithm is described in details in **Appendix A** in the **Developers Guide**

Another main improvement is that instead of the purpose built Tab-completion mechanism in Bayescalc 
we use the standard 
`prompt_toolkit` library which also provides a command history mechanism.

## ✨  Features


**Multi-value variables**


## 🚀 Improvements

**Command line history**

**Documentation restructure**
- The documentation is now stored under `docs/` directory and have a newly written "User Guide".

**More example BN**
- Additional example of Bayesian Networks are included under the `exmples/` directory

## 🐛 Bug Fixes
- None (no-reported bugs)

## 🛠  Build system
- Renamed main entry point to `bayescalc.main`


## 📚 Documentation
- Major rehaul


**Full Changelog**: 