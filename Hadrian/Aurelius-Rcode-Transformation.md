# Overview

PFA is produced by Aurelius in four stages: (1) a model is converted into a list-of-lists data structure, (2) code is written in R syntax and wrapped in `expression`, (3) `pfa.config` gathers all pieces of the scoring engine and produces a list-of-lists corresponding to the final PFA file, and (4) `json` converts the list-of-lists to a serialized JSON string or output file.

At no point does Aurelius check the validity of the resulting PFA file; use Hadrian, Titus, or Titus-in-Aurelius (`pfa.engine`) for this crucial test.

The "code written in R syntax" cannot use arbitrary R functions. Only unary and binary operators (e.g. `+`, `-`, `==`, `<`, which are functions in R and PFA) are automatically converted to their counterparts. Functions called in prefix notation (e.g. `log(x)`, `print(x)`) must use PFA function names. Moreover, indexes, if used, start at zero (PFA convention), not one (R convention).

Some valid R syntax is "overloaded" with new meanings to supply information needed by PFA, such as type annotations. For instance, a function must be notated like this:

```R
function(x = avro.double, y = avro.string -> avro.boolean) {
  (x > 5  &&  y == "hello")
}
```

This allows PFA to know that `x` is a number, `y` is a string, and that the function returns a boolean. Apart from these differences, writing R code for PFA conversion is like writing executable R code.

Aurelius automatically identifies whether symbols (variable references) are local variables, cells, pools, function names, or unknown. If unknown, Aurelius searches for a variable in the current R scope with that name and uses its value as a substitution. This allows you to write:

```R
threshold <- 5
pfaExpression <- pfa.expr(quote(if (x < threshold) 0 else 1))
print(json(pfaExpression))
[1] {"if": {"<": ["x", 5]}, "then": 0, "else" 1}
```

to hard-code a `threshold` in the PFA expression. The replacement is assumed to already be in list-of-lists format, so if you're substituting code, convert it with `pfa.expr` first. (The number `5` in this example is so simple that its list-of-lists format is also `5`. Note that strings in PFA's list-of-lists are `list("hello")` rather than `"hello"` to avoid confusion with a variable named `hello`.)

Any type annotations encountered in the R code are treated as R expressions, evaluated immediately. For instance,

```R
gettype <- function() avro.array(avro.int)
pfaExpression <- pfa.expr(quote(new(gettype(), "[]")))
```

calls the `gettype()` function to generate the type annotation in list-of-lists format. Think of the R-to-PFA process as compilation: a compiler evaluates types during compilation and generates code that evaluates values at runtime. The same is true in the R-to-PFA conversion.

# JSON as lists-of-lists

Aurelius uses the following _subset_ of R's data structures to represent JSON.

| R data structure | JSON equivalent |
|:-----------------|:----------------|
| NULL | null |
| TRUE | true |
| FALSE | false |
| scalar number | number (integer or floating-point) |
| character vector | string |
| unnamed list | JSON array (ordered, surrounded in square brackets) |
| named list | JSON object (unordered pairs in curly brackets) |

Note that data frames, environments, and non-scalars (vectors of length > 1) have no equivalent in Aurelius's JSON representation. If the `json` function encounters an unrecognized object, it will raise an error.

# Avro schema specification

All types in PFA are encoded in [Avro schemas](https://avro.apache.org/docs/1.7.7/spec.html), which are also embedded in JSON. You could create type specifications by producing the corresponding JSON in list-of-lists form or you can use the following convenience functions.

| Avro type | JSON | Aurelius generator |
|:----------|:-----|:-------------------|
| null | `"null"` | `avro.null` |
| boolean | `"boolean"` | `avro.boolean` |
| int | `"int"` | `avro.int` |
| long | `"long"` | `avro.long` |
| float | `"float"` | `avro.float` |
| double | `"double"` | `avro.double` |
| string | `"string"` | `avro.string` |
| bytes | `"bytes"` | `avro.bytes` |
| array | `{"type": "array", "items": "int"}` | `avro.array(avro.int)` |
| map | `{"type": "map", "values": "int"}` | `avro.map(avro.int)` |
| fixed | `{"type": "fixed", "name": "SomeName", "namespace": "com.wowzers", "size": 16}` | `avro.fixed(16, "SomeName", "com.wowzers")` |
| enum | `{"type": "enum", "name": "SomeName", "namespace": "com.wowzers", "symbols": ["one", "two", "three"]}` | `avro.enum(list("one", "two", "three"), "SomeName", "com.wowzers")` |
| record | `{"type": "record", "name": "SomeName", "namespace": "com.wowzers", "fields": [{"name": "one", "type": "int"}, {"name": "two", "type": "double"}, {"name": "three", "type": "string"}]}` | `avro.record(list(one = avro.int, two = avro.double, three = avro.string), "SomeName", "com.wowzers")` |
| union | `["null", "int", "string"]` | `avro.union(avro.null, avro.int, avro.string)` |

The `name` and `namespace` parameters are optional. If a `name` is not provided, Aurelius will generate a unique name.

# Code transformations

R code passed to `pfa.expr` must be wrapped in [R's `quote` function](https://stat.ethz.ch/R-manual/R-devel/library/base/html/substitute.html) and R code passed to arguments of `pfa.config` must be wrapped in [R's `expression` function](https://stat.ethz.ch/R-manual/R-devel/library/base/html/expression.html). The `quote` function only takes a single expression, but `expression` takes any number of expressions as comma-separated arguments. (Remember to put commas in the top level of your code!) The `quote` and `expression` functions are needed to keep R from evaluating the code right away.

The table below shows how each expression is transformed.

| R code | PFA equivalent | Interpretation |
|:-------|:---------------|:---------------|
| `NULL`, `TRUE`, `FALSE` | `null`, `true`, `false` | literal null and boolean |
| `12`, `3.14` | `12`, `3.14` | literal numbers |
| `new(avro.double, 3)` | `{"double": 3}` | ensure floating-point |
| `"hello"` | `{"string": "hello"}` | literal string |
| `new(avro.array(avro.int), "[]")` | `{"type": {"type": "array", "items": "int"}, "value": []}` | complex literal from JSON string |
| **FIXME** | `{"base64": "AH9AJhY="}` | literal Base64 |
| `myvar` | `"myvar"` | variable reference |
|         | `{"cell": "myvar"}` | cell reference |
|         | `{"pool": "myvar"}` | pool reference |
|         | `{"fcn": "myvar"}` | function reference |
| `anyfunc()`, `anyfunc(x)` | `{"anyfunc": []}`, `{"anyfunc": ["x"]}` | function calls |
| `new(avro.array(avro.int), x, y, z)` | `{"type": {"type": "array", "items": "int"}, "new": ["x", "y", "z"]}` | create array from variables |
| `new(avro.map(avro.int), field1 = x, field2 = y)` | `{"type": {"type": "map", "values": "int"}, "new": {"field1": "x", "field2": "y"}}` | create map or record from variables |
| `{ 1; 2; 3 }` | `{"do": [1, 2, 3]}` | grouping or limiting scope (returns value of last expression) |
| `x <- 3` | `{"let": {"x": 3}}` | initial assignment |
|          | `{"set": {"x": 3}}` | subsequent reassignment |
| `some[thing]` or `some[[thing]]` | `{"attr": "some", "path": ["thing"]}` | dereferencing variable |
|                 | `{"cell": "some", "path": ["thing"]}` | dereferencing cell |
|                 | `{"pool": "some", "path": ["thing"]}` | dereferencing pool |
| `function(. = avro.int) { 3.14 }` | `{"params": [], "ret": "int", "do": 3.14}` | zero-parameter function |
| `function(x = avro.int -> avro.double) { x + 0.1 }` | `{"params": [{"x": "int"}], "ret": "double", "do": {"+": ["x", 0.1]}}` | general function |
| `some <<- 3` | `{"cell", "to": 3}` | direct cell assignment |
| `some[thing] <<- 3` | `{"cell", "path": ["thing"], "to": 3}` | direct cell structure assignment |
|                     | `{"pool", "path": ["thing"], "to": 3}` | direct pool structure assignment |
| `some <<- function(old = avro.int -> avro.int) old + 1` | `{"cell": "some", "to": {"params": [{"old": "int"}], "ret": "int", "do": {"+": ["old", 1]}}` | cell transaction update |
| `some[thing] <<- function(old = avro.int -> avro.int) old + 1 <- 0` | `{"pool": "some", "path": ["thing"], "to": {"params": [{"old": "int"}], "ret": "int", "do": {"+": ["old", 1]}, "init": 0}` | pool transaction update with initializer |
| **FIXME** | `{"pool": "some", "del": "thing"}` | remove item from pool |
| `if (predicate) result` | `{"if": "predicate", "then": "result"}` | if-then |
| `if (predicate) result else alternate` | `{"if": "predicate", "then": "result", "else": "alternate"}` | if-then-else |
| `while (predicate) loopbody` | `{"while": "predicate", "do": "loopbody"}` | while loop |
| **FIXME** | `{"do": "loopbody", "until": "posttest"}` | post-test loop |
| `for (i in start:end) loopbody` | `{"for": {"i": "start"}, "while": {"<=": ["i", "end"]}, "step": {"i": {"+": ["i", 1]}}, "do": "loopbody"}` | for loop (special case) |
| `for (x in myArray) loopbody` | `{"foreach": "x", "in": "myArray", "do": "loopbody"}` | loop over array elements |
| `for (k.v in myMap) loopbody` | `{"forkey": "k", "forval": "v", "in": "myMap", "do": "loopbody"}` | loop over key-value pairs of map |
| **FIXME** | `{"cast": "myvar", "cases": [{"as": "int", "named": "x", "do": "x"}, {"as": "string", "named": "x", "do": {"a.len": "x"}}]}` | type-safe down-casting |
| **FIXME** | `{"upcast": "myvar", "as": "double"}` | up-casting |
| `if (!is.null(x <- myvar)) result else alternate` | `{"ifnotnull": {"x": "myvar"}, "then": "result", "else": "alternate"}` | type-safe null check |
| **FIXME** | `{"pack": [{"byte": 12}, {"unsigned short": 12}]}` | serialization to bytes |
| **FIXME** | `{"unpack": "myvar", "format": [{"x": "byte"}, {"y": "unsigned short"}], "then": "result", "else": "alternate"}` | deserialization from bytes |
| **FIXME** | `{"doc": "random text"}` | comments in JSON |
| `stop("some reason")` | `{"error": "some reason"}` | user-defined error |
| `try(expression)` | `{"try": "expression"}` | catch exceptions and return null instead |
| `log("message")` | `{"log": "message"}` | write to log file (if any) |
| `print("message")` | |

# Non-code elements

The `pfa.config` function wraps up everything involved in a scoring engine into one PFA file. Its parameters are the following.

| Name | Type | Description |
|:-----|:-----|:------------|
| input | Avro list-of-lists | input schema **(required)** |
| output | Avro list-of-lists | output schema **(required)** |
| action | R expression | what the scoring engine does for each input **(required)** |
| name | string | optional name |
| method | "map", "emit", "fold" | general behavior |
| begin | R expression | what the scoring engine does at startup |
| end | R expression | what the scoring engine does at shutdown |
| fcns | named list of R expressions, each encoding one function | user-defined functions available to action, begin, end, and merge |
| zero | JSON as list-of-lists | initial tally for method = "fold" |
| merge | R expression | what the scoring engine does to combine intermediate results from distributed folds |
| cells | named list of PFA cells (see below) | global variables |
| pools | named list of PFA pools (see below) | global environments |
| randseed | integer | seed controlling _all_ random numbers in the scoring engine |
| doc | string | optional documentation for the PFA file |
| version | integer | optional version number for the PFA file |
| metadata | named list of strings | optional parameters that are machine-mineable |
| options | JSON object as list-of-lists | implementation-specific compilation/runtime options that can be overridden by the executable environment |
| env | R environment | R variables used for substituting unknown symbols |

The `pfa.cell` function wraps up everything needed to describe a PFA cell (global variable). Its parameters are the following.

| Name | Type | Default | Description |
|:-----|:-----|:--------|:------------|
| type | Avro as list-of-lists | **(required)** | data type of the global variable |
| init | JSON as list-of-lists | **(required)** | initial value, usually from a converted R model |
| source | "embedded", "json" | "embedded" | if "embedded", init is the actual value; if "json", init is a URL pointing to a file containing the actual value |
| shared | logical | FALSE | if TRUE, share the global variable across linked scoring engines |
| rollback | logical | FALSE | if TRUE, roll back the global variable if processing a record raises an uncaught exception |

The `pfa.pool` function wraps up everything needed to describe a PFA pool (global environment: a mutable map of variables). Its parameters are the following.

| Name | Type | Default | Description |
|:-----|:-----|:--------|:------------|
| type | Avro as list-of-lists | **(required)** | data type of the environment |
| init | JSON as list-of-lists | **(required)** | initial value, usually from a converted R model, always a JSON object (named list) |
| source | "embedded", "json" | "embedded" | if "embedded", init is the actual value; if "json", init is a URL pointing to a file containing the actual value |
| shared | logical | FALSE | if TRUE, share the environment across linked scoring engines |
| rollback | logical | FALSE | if TRUE, roll back the environment if processing a record raises an uncaught exception |