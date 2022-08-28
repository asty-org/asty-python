# Advanced Matching

Search for pattern in golang code with special matching state machine to reduce nesting in code structures.

### Scenario

1. Loads pattern from JSON file. Pattern has same structure as AST.
   Pattern matches call to `print` function anywhere in the code with string constant anywhere 
   deeply nested in its parameters.
2. Parse golang source file by running `asty` with docker container.
3. Create matcher from pattern.
4. Apply matcher to parsed AST.
5. Prints matched results.

### Motivation

With this approach we can search for big complicated patterns in golang code.
It relies on DSL similar to jsonschema. May require further features and capabilities development.
Basically, you can think of it as a sequence of nested visitors.

### Pattern

```json5
{
  "NodeType": "MatchRule", // This matches `Rules` anywhere in the AST.
  "Name": "call", // Matched results will be presented under name `call`
  "Rules": [
    {
      "NodeType": "CallExpr", // Match `CallExpr`.
      "Fun": { // Simple nodes will be presented in the parent result 
               // under name of attribute. In this case `fun`
        "NodeType": "Ident", // Match `Ident` with name `print`.
        "Name": "print"
      },
      "Args": [
        {
          "NodeType": "MatchRule", // Match `Rules` anywhere in the arguments.
          "Name": "constant", // Matched results will be presented under 
                              // name `constant`.
          "Rules": [
            {
              "NodeType": "BasicLit", // Match `BasicLit` with type `string`.
              "Kind": "STRING"
            }
          ]
        }
      ]
    }
  ]
}
```

### Iterating result

```python
for result in match:
    for call in result['call']:
        ... # Do something with call itself
        # call.node - matched call node
        # call.pattern - pattern rule that matched call
        for fun in call['fun']:
            ... # Here we have name of the function
        for args in call['args']:
            ... # Here we have arguments of the function
            # But only those where we have value matched
            for const in args['constant']:
                ... # Do something with const
```
