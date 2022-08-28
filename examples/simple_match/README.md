# Simple Matching

Search for simple values in golang code with visitor and 
python pattern matching.

### Scenario

1. Parse golang source file by running `asty` with docker container.
2. Create visitor that searches for `fmt.Println` calls with first parameter as string constant.
3. Apply visitor to parsed AST and print found parameters.

### Motivation

With this approach you can find static patterns in AST that you can fit into single python match.
If you need to search for more complicated things you can use nested visitors or 
nested `match` in conjunction with `walk`. This is simple way of searching that works well for most of the cases.
However, for more advanced cases you code might become very complex and verbose. 