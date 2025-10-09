## [v1.0.0-rc1] - 2025-10-09

### Added
- Added `load()` command to load a network while in interactive mode
- Added graphic visualization of network graph (PNG, PDF, SVG) format
- Updated network syntax with `boolean` keyword for boolean variables
- Developer guide documentation improvements
- User guide documentation improvements

### Fixed
- All lint and type checking warnings 

### Internal
- Added unit tests to pass >= 80% code coverage
- Updated and build and release scripts
- Updated CI/CD Github actions and pipelines
- Added PyPi upload
- Added build script for automatic code coverage badge updated

## [0.1.0] - 2025-09-30

- Complete rewrite with new inference engine based on a variable elimination algorithm
- Use prompt_toolkit which gives both Tab-completion (with pop-up window) and command history
