# Simple Transformation

Find specific pattern in golang code and replace it with another code.

### Scenario

1. Parse golang source file by running `asty` with docker container.
2. Create transform that searches for `print` calls and replaces it with call to `log.Print` with same arguments.
3. Apply transform to create new AST.
4. Use `asty` to generate golang source code from new AST.

### Motivation

This approach is good to implement simple automatic code refactoring tools.