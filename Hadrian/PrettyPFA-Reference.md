## General comments

Although PrettyPFA provides a C-like syntax for PFA, the PFA language is different enough from mainstream procedural languages that the syntax must have some differences.

An earlier project, `titus.producer.expression`, attempted to transform Python into PFA, but the differences are big enough that the correspondence can't be one-to-one, and the use of familiar Python syntax to do something unfamiliar was misleading.  It helps that the PrettyPFA syntax is talor-made for PFA semantics, but that also means that it's a new syntax with rules that have to be learned.

### Semicolons and curly brackets

The most significant difference is that PFA contains no statements, only expressions.  Statements are a sequence of commands with no return value; expressions are a tree function calls, each of which has a return value.  (This makes PFA more composable--- simpler to edit algorithmically.)

Most C-like languages use semicolons to end statements and curly brackets to wrap sequences of statements (such as the body of an `if` statement).  Since the final curly bracket is the end of a statement, it implicitly acts like a semicolon.  For instance, the two `if` statements in

```javascript
// this is C
if (something) {
    do_something();
}
if (something_else) {
    do_something_else();
}
```

are separate statements: you don't need to put an explicit semicolon at the end of the first one to indicate that it's different from the second one.  However, in PrettyPFA, you do:

```javascript
// this is PrettyPFA
if (something) {
    do_something()
};
if (something_else) {
    do_something_else()
}
```

Why?  Because each `if` expression represents a value like `3` or `(x+4)` or `do_something()`.  If you just want to evaluate them sequentially, as in the example above, you need to separate them with semicolons.  However, you might instead want to use them as expressions:

```javascript
(if (x > 0) 1 else -1) * something
```

Since the `if` block might be in the middle of an equation, it shouldn't implicitly end the expression.

Another rule that differs from some C-like languages is that semicolons only separate expressions--- the last expression in a sequence doesn't need a semicolon.  Ending the last expression with a semicolon isn't an error (it's removed by the parser), but using them consistently as separators, rather than line terminators, can help you remember that blocks with curly brackets need them, too.

### Whitespace

PrettyPFA is whitespace-insensitive apart from section headers and comments.

### Comments

Comments start with a double slash (`//`) and end with a carriage return, just like modern C comments.

## Global document structure

A PrettyPFA document is split into sections, each of which has different rules.  The syntax of these sections resembles PFA in YAML:

```yaml
name: SquareRoot
input: double
output: union(double, null)
action:
  if (input >= 0.0)
    m.sqrt(input)
  else
    null
```

The section name must start a new line (unindented) and end in a colon (no space).  The following are all of the possible sections:

Section name | Required? | Format | Description
:----------- | :-------- | :----- | :----------
name | no | string | Name given to the scoring engine.  If not provided, a generic name will be assigned.
types | no | sequence of type assignments | The only section with no PFA analogue; used to declare commonly used types once, which can reappear throughout the engine.
input | required | type declaration | Defines the input type for the scoring engine.
output | required | type declaration | Defines the output type for the scoring engine.
method | no (default: map) | map, emit, or fold | Defines the method used to score inputs.
begin | no | expressions | Sequence of expressions to be evaluated before encountering any data.
action | required | expressions | Sequence of expressions to be evaluated on each input datum.
end | no | expressions | Sequence of expressions to be evaluated after all data (if such a time exists).
fcns | no | function declarations | User-defined functions that can be used in any expressions (including other functions).
zero | only for fold engines | JSON datum | Starting value for a fold engine's tally.
merge | only for fold engines | expressions | Method to combine partial tallies.
cells | no | cell declarations | Type declaration and initial values for named global variables.
pools | no | pool declarations | Type declaration and initial values for namespaces of unnamed global variables.
randseed | no | number | Used to seed random number generators used in all functions that make use of pseudorandom numbers.
doc | no | string | Human-readable comment that is stored in the PFA document (unlike PrettyPFA comments).
version | no | integer | Numerical version number for the scoring engine.
metadata | no | JSON map of strings | Other facts about the scoring engine.
options | no | JSON map of objects | Execution options that may be overridden by the scoring engine container.

### Types section

Avro does not allow named types (records, enums, and fixed) to be defined multiple times.  After the first time, the type can only be referred to by name.  Although these one-time declarations can be scattered throughout the document, it's simpler to put them all in one place.

Also, it can be useful to assign labels to other types, so that they can be more easily changed in the future.  For instance, the first version of a scoring engine might have labels defined by arbitrary strings, while a later version uses enumeration constants.  By declaring

```javascript
LabelType = string
```

in the `types` section, it can be changed to

```javascript
LabelType = enum([firstCase, secondCase, thirdCase])
```

without having to change all of the function signatures that use it.

The syntax of the types section is a sequence of assignments, with a new type name on the left and its definition on the right, separated by semicolons.  For instance:

```javascript
types:
  ArrayOfStrings = array(string);
  MyRecord = record(field1: int, field2: double);
  EitherOne = union(ArrayOfStrings, MyRecord)
```

As usual, the last one doesn't need to have a semicolon, though it can.

Since named types can include their name in their declaration, the assignment is optional.

```javascript
types:
  MyRecord = record(field1: int, field2: double)
```

is equivalent to

```javascript
types:
  MyRecord = record(MyRecord, field1: int, field2: double)
```

which is equivalent to

```yaml
types:
  record(MyRecord, field1: int, field2: double)
```

### Input and output sections

These are required, and they are simply a type specification.  They can use types defined in the `types` section, even if that section appears after `input` or `output`.

```yaml
input: type-specification
output: type-specification
```

### Method section

Just as in PFA, there are only three options: `map`, `emit`, and `fold`.  The default is `map`.

### Begin, action, and end sections

The `begin` and `end` sections are optional, but `action` is required.  Each contains either a single expression or a sequence of expressions.  The syntax of expressions is defined below.

### Fcns section

The `fcns` section is a sequence of function declarations, separated by semicolons.  Each declaration has the function name on the left (without the "u." namespace qualifier) and a function declaration on the right.  The function declaration syntax is exactly the same as for inline functions.

Here is an example:

```javascript
fcns:
  myfunc = fcn(arg1: int, arg2: int -> string)
    if (arg1 > 0)
      s.number(arg2)
    else
      "negative"
```

This defines `myfunc`, which can be used elsewhere as `u.myfunc`.  It has two arguments, `arg1` and `arg2`, both of which are integers.  The return value (specified by `->` inside the parameter list) is a string.

The function body must be enclosed by curly brackets if it contains multiple expressions; the example above does not.  (In most C-like languages, functions always require curly brackets, unlike `if`, `while`, and other constructs, but PrettyPFA is more uniform.)

Be sure to separate multiple functions with semicolons, even if they do use curly brackets:

```javascript
fcns:
  squared = fcn(x: double -> double) { x**2 };
  cubed   = fcn(x: double -> double) { x**3 };
  sqrroot = fcn(x: double -> double) { m.sqrt(x) }
```

### Zero and merge

The `zero` and `merge` sections are required for fold engines, and must not be present in map or emit engines.  Here is an example of a fold engine that computes a mean over distributed data:

```javascript
name: DistributedMean
input: double
output: record(Pair, numer: double, denom: double)
method: fold
zero: {numer: 0.0, denom: 0.0}
action:
  new(Pair, numer: tally.numer + input,
            denom: tally.denom + 1.0)
merge:
  new(Pair, numer: tallyOne.numer + tallyTwo.numer,
            denom: tallyOne.denom + tallyTwo.denom)
```

A distributed processor would send this scoring engine to a cluster of computers that each hold a part of the dataset, evaluate the `action` over that part of the data, collect the partial results, and evaluate `merge` to combine the partial data.

Although the `zero` section is a JSON object, it can be expressed with relaxed rules (keys in the JSON object do not need to be quoted, for instance).  See the section on JSON expressions below for details.

### Cells and pools

The `cells` and `pools` sections have a similar syntax.  They declare global variables (`cells`) or namespaces (`pools`) that can be used in any expression.  These sections are each a sequence of semicolon-separated assignments.  The right-hand side of the assignment is the cell or pool's initial value and the left-hand side is a declaration that includes the name, type, and any flags.

```javascript
cells:
  someNumber(double) = 3.14;

  someRecord(record(field1: int,
                    field2: double,
                    field3: string)) = {
    field1: 1,
    field2: 2.2,
    field3: "three"
  };

  somethingElse(type: PreviouslyDeclaredType,
                shared: true) = []

types:
  PreviouslyDeclaredType = array(int)
```

The parenthesized arguments must contain a type declaration, which may or may not be prefixed by `type:`.  They may contain `shared: true` or `rollback: true` (which are mutually exclusive).  The default values for `shared` and `rollback` are both `false`.

The initializer of a pool is a map of names to values of the specified type, and this map may be empty.

```javascript
cells:
  someCell(int) = 12

pools:
  somePool(int) = {one: 12, two: 12, three: 12}
```

### Randseed section

The `randseed` section is simply an integer.  This integer seeds all random numbers used in the calculation, so setting this value ensures that the scoring engine operation will be deterministic.

If multiple scoring engine instances are created, they have random number seeds that differ, yet are seeded by this seed (as per the PFA specification).  This is to avoid the possibility of scoring engines doing redundant work.

### Doc, version, metadata, and options sections

The `doc` section is simply a string, the `version` is simply an integer, and `metadata` is a JSON map of strings.  They have no impact on the operation of the scoring engine.

The `options` section requests the scoring engine to be run in a particular mode.  For instance, the `timeout` option specifies the number of milliseconds that an `action` is allowed to run before being canceled.  The scoring engine container can override any of these options (as per the PFA specification).

## Type specifications

Type specifications in PFA are Avro schema.  PrettyPFA provides a simpler way to express types.

The primitives are simply strings with no quotes.

Avro/PFA type | equivalent PrettyPFA
:------------ | :-------------------
`"null"` or `{"type": "null"}` | `null`
`"boolean"` or `{"type": "boolean"}` | `boolean`
`"int"` or `{"type": "int"}` | `int`
`"long"` or `{"type": "long"}` | `long`
`"float"` or `{"type": "float"}` | `float`
`"double"` or `{"type": "double"}` | `double`
`"bytes"` or `{"type": "bytes"}` | `bytes`
`"string"` or `{"type": "string"}` | `string`

Array, map, and union constructors are expressed like function calls with parentheses.  Arrays and maps are functions of one argument, while a union has two or more.

Avro/PFA type | equivalent PrettyPFA
:------------ | :-------------------
`{"type": "array", "items": X}` | `array(X)`
`{"type": "map", "values": X}` | `map(X)`
`[X, Y, ...]` | `union(X, Y, ...)`

Records are expressed as functions of `fieldName: fieldType` pairs.  The record name, which is required in Avro and PFA, is optional in PrettyPFA (a unique value will be generated).  The name may appear anywhere in the list (as long as it doesn't have a key and colon before it), but the beginning or end is a better choice than the middle.

Avro/PFA type | equivalent PrettyPFA
:------------ | :-------------------
`{"type": "record", "name": "RECORD_NAME", "fields": [{"name": "NAME", "type": TYPE}, ...]}` | `record(NAME: TYPE, ...)`
 | or `record(RECORD_NAME, NAME: TYPE, ...)` | `{"type": "record", "name": "RECORD_NAME", "namespace": "NAMESPACE", "fields": [{"name": "NAME", "type": TYPE}, ...]}` | `record(NAMESPACE.RECORD_NAME, NAME: TYPE, ...)`

The first argument of an enumeration type is an array of enumeration values and the optional second argument is the name (with namespace).  Note that the PrettyPFA symbols do no have quotes.

Avro/PFA type | equivalent PrettyPFA
:------------ | :-------------------
`{"type": "enum", "name": "NAME", "symbols": ["ONE", "TWO", "THREE", ...]}` | `enum([ONE, TWO, THREE, ...])` | or `enum([ONE, TWO, THREE, ...], NAME)`

The first argument of a fixed type is the size of the fixed byte array and the optional second argument is the name (with namespace).

Avro/PFA type | equivalent PrettyPFA
:------------ | :-------------------
`{"type": "fixed", "name": "NAME", "size": SIZE}` | `fixed(SIZE)` | or `fixed(SIZE, NAME)`

## JSON in PrettyPFA

Some functions require data to be expressed as JSON.  While literal JSON is allowed, some JSON restrictions can be relaxed.

Strings do not need to be quoted if they consist of alphanumeric characters (including underscores and periods, as long as the first character is not a period).  This applies to string values within the JSON object and keys of JSON mappings.

## Expressions in PrettyPFA

### Literal values and symbol refernces

Most literal values are the same in PFA and PrettyPFA.  The main exception is that strings can simply be strings, since symbols do not have quotes.

type | PFA example | PrettyPFA equivalent
:--- | :---------- | :-------------------
null literal | `null` | `null`
boolean literal | `true` | `true`
boolean literal | `false` | `false`
integer literal | `3` | `3`
double literal | `3.14` | `3.14`
symbol reference | `"something"` | `something`
string literal | `{"string": "something"}` or `["something"]` | `"something" or 'something'`

Less common types of values can be created as though they were function calls.

type | PFA example | PrettyPFA equivalent
:--- | :---------- | :-------------------
integer | `{"int": 3}` | `int(3)`
long | `{"long": 3}` | `long(3)`
float | `{"float": 3.14}` | `float(3.14)`
double | `{"double": 3.14}` | `double(3.14)`
string | `{"string": "hello"}` | `string("hello")`
bytes (in Base64) | `{"bytes": "aGVsbG8="}` | `bytes("aGVsbG8=")`
anything else | `{"type": {"type": "array", "items": "int"}, "value": [1, 2, 3]}` | `json(array(int), [1, 2, 3])`

The `json` function takes a type as its first argument and a (loosely interpreted) JSON value as its second.  It can only be used to create constants.

### Implicit resolution of symbol namespace

In PFA, local variables, cells, pools, and functions all live in separate namespaces and the PFA author must specify the namespace when referencing a symbol.  PrettyPFA checks to see which symbols are already defined and infers the namespace.

type | PFA example | PrettyPFA equivalent
:--- | :---------- | :-------------------
local variable | `"something"` | `something`
cell reference | `{"cell": "something"}` | `something`
pool reference | `{"pool": "something"}` | `something`
function reference | `{"fcn": "u.something"}` | `u.something`

The function table is checked first, then the cells, then the pools, and if no match is found, the symbol is assumed to be a local variable.

### Binary and unary operators

Simple operations, such as addition and subtraction, are functions in PFA but binary or unary operators in most languages.  In order of precedence, from least binding to most binding, they are:

operation | PFA example | PrettyPFA equivalent
:-------- | :---------- | :-------------------
logical or | `{"||": ["P", "Q"]}` | `P || Q`
logical xor | `{"^^": ["P", "Q"]}` | `P ^^ Q`
logical and | `{"&&": ["P", "Q"]}` | `P && Q`
logical not | `{"!": "P"}` | `!P`
equality | `{"==": ["X", "Y"]}` | `X == Y`
inequality | `{"!=": ["X", "Y"]}` | `X != Y`
less than | `{"<": ["X", "Y"]}` | `X < Y`
less or equal | `{"<=": ["X", "Y"]}` | `X <= Y`
greater than | `{">": ["X", "Y"]}` | `X > Y`
greater or equal | `{">=": ["X", "Y"]}` | `X >= Y`
bitwise or | `{"|": ["A", "B"]}` | `A | B`
bitwise xor | `{"^": ["A", "B"]}` | `A ^ B`
bitwise and | `{"&": ["A", "B"]}` | `A & B`
addition and subtraction | `{"+": ["x", "y"]}` | `x + y`
  | `{"-": ["x", "y"]}` | `x - y`
multiplication and division | `{"*": ["x", "y"]}` | `x * y`
 | `{"/": ["x", "y"]}` | `x / y` (floating-point)
 | `{"//": ["x", "y"]}` | `x idiv y` (integer)
 | `{"%": ["x", "y"]}` | `x % y` (modulo)
 | `{"%%": ["x", "y"]}` | `x %% y` (remainder)
unary minus and bitwise not | `{"u-": "x"}` | `-x`
 | `{"~": "A"}` | `~A`
power | `{"**": ["x", "p"]}` | `x**p`

### Grouping with parentheses

Parentheses group expressions to override the order of precedence, as in most C-like languages.

### Function calls

Functions are called using parenthsized argument lists, following the custom of C-like languages.  This is true of PFA library functions and user-defined functions.  The function names must always be fully qualified, including user-defined functions, which always begin with "`u.`".

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"u.myFunc": [1, "x", ["hello"]]}` | `u.myFunc(1, x, "hello")`
`{"model.cluster.closest": ["datum", {"cell": "clusters"}, {"fcn": "metric.simpleEuclidean"}]}` | `model.cluster.closest(datum, clusters, metric.simpleEuclidean)`
`{"m.pi": []}` | `m.pi()`

### New arrays, maps, and records

Arrays, maps, and records are complex objects that can be constructed with the `json` function if constant but not if they must be constructed from other expressions.  The `new` function exists for this purpose.

The syntax of the `new` function depends on the type of object ot be created.

type | PFA example | PrettyPFA equivalent
:--- | :---------- | :-------------------
array | `{"type": {"type": "array", "items": X}, "new": ["a", "b", "c"]}` | `new(array(X), a, b, c)`
map | `{"type": {"type": "map", "values": X}, "new": {"one": "a", "two": "b", "three": "c"}}` | `new(map(X), one: a, two: b, three: c)`
record | `{"type": "MyRecord", "new": {"one": "a", "two": "b", "three": "c"}}` | `new(MyRecord, one: a, two: b, three: c)`

### Extracting from arrays, maps, and records

There are two ways to extract data from a map or record: dot notation and bracket notation.  Dot notation extracts fields by name, delimited by periods, and can only be used if the field name isn't computed at runtime (as is always the case for records).  Bracket notation takes an arbitrary expression or sequence of expressions between square brackets, as long as the expressions evaluate to strings.

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"attr": "mapOrRecord", "path": [["aField"]]}` | `mapOrRecord.aField`
 | `mapOrRecord["aField"]`
`{"attr": "deepMapOrRecord", "path": [["a"], ["b"], ["c"]]}` | `deepMapOrRecord.a.b.c`
 | `deepMapOrRecord["a", "b", "c"]`
 | `deepMapOrRecord["a"]["b"]["c"]`
`{"attr": "mapOrRecord", "path": [{"f": "x"}]}` | `mapOrRecord[f(x)]`

Data can only be extracted from arrays by square brackets.  In this case, the expressions must evaluate to integers.

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"attr": "myArray", "path": [3]}` | `myArray[3]`
`{"attr": "deepArray", "path": [3, 4, 5]}` | `deepArray[3, 4, 5]`
 | `deepArray[3][4][5]`
`{"attr": "myArray", "path": [{"f": "x"}]}` | `myArray[f(x)]`

Naturally, records containing arrays, maps containing records, or any combination can be deeply extracted with brackets.

All of the above applies equally to cells and pools, though the `"attr"` in the generated PFA is replaced with `"cell"` or `"pool"`.

### Assignment and reassignment

The declaration and first assignment of a local variable takes a different form than subsequent reassignments in PFA.  In the first assignment, the variable's type is derived from the expression that initializes it.  In subsequent assignments, the type of the right-hand side is checked against the variable's type.

In PrettyPFA, the first assignment is denoted with a `var` keyword, and subsequent assignments have no `var` keyword.

assignment | PFA example | PrettyPFA equivalent
:--------- | :---------- | :-------------------
first | `{"let": {"x": 12}}` | `var x = 12`
subsequent | `{"set": {"x": 13}}` | `x = 13`

Multiple variables can be declared or assigned at the same time, either to swap values or to run independent calculations in parallel.  These are separated by commas in PrettyPFA.

assignment | PFA example | PrettyPFA equivalent
:--------- | :---------- | :-------------------
first | `{"let": {"x": 12, "y": ["hello"]}}` | `var x = 12, y = "hello"`
subsequent | `{"set": {"x": 13, "y": ["there"]}}` | `x = 13, y = "there"`
swap | `{"set": {"a": "b", "b": "a"}}` | `a = b, b = a`

### Modifying arrays, maps, and records

All structures in PFA are immutable, so it is not possible to modify one item in an array, one value in a map, or one field in a record.  It is possible, however, to create a copy of the original structure that differs by one element.

In most languages, an expression like the following would mean to modify an element in-place.

```javascript
myRecord["myField"] = newValue
```

Since parts of a structure cannot be modified in-place in PFA, this is instead an expression whose return value is the new structure that differs by one element.  For instance, the following prints both the original and the modified structure:

```javascript
var modified = (input["myField"] = 123);
log(input, modified)
```

Since the values of symbols can be replaced, here is a fragment that replaces fields of a record, discarding the original:

```javascript
var rec = json(record(one: int, two: double, three: string),
                 {one: 0, two: 0.0, three: ""});
rec = (rec["one"] = 1);
rec = (rec["two"] = 2.2);
rec = (rec["three"] = "THREE");
rec
```

For shallow (one level deep) replacements like the above, there is a special `update` function, which is more concise and looks less odd:

```javascript
var rec = json(record(Output, one: int, two: double, three: string),
                 {one: 0, two: 0.0, three: ""});
rec = update(rec, one: 1);
rec = update(rec, two: 2.2);
rec = update(rec, three: "THREE");
rec
```

The pseudo-assignment syntax can also appear as a return value at the end of a function or at the end of an `action`.  Here's an example of this sort of usage:
```python
>>> import titus.prettypfa as prettypfa
>>> engine, = prettypfa.engine(r'''
... input: record(Something, firstLevel: map(array(int)))
... output: Something
... action:
...   input["firstLevel", "secondLevel", 1] = 999
... ''')
... 
>>> print engine.action({"firstLevel": {"secondLevel": [1, 2, 3]}})
{'firstLevel': {'secondLevel': [1, 999, 3]}}
```

Note that the level of object that gets returned depends on whether the substructure was reached in one set of brackets or two.  The `action` below differs only in brackets, but the result is that a modified `"secondLevel"` object is returned, rather than a `"firstLevel"`.

```python
>>> engine, = prettypfa.engine(r'''
... input: record(Something, firstLevel: map(array(int)))
... output: map(array(int))
... action:
...   input["firstLevel"]["secondLevel", 1] = 999
... ''')
... 
>>> print engine.action({"firstLevel": {"secondLevel": [1, 2, 3]}})
{'secondLevel': [1, 999, 3]}
```

For the purpose of deep modifications, a sequence of dot-extractions counts as one bracket:

```python
>>> engine, = prettypfa.engine(r'''
... input: record(Something, firstLevel: map(map(int)))
... output: Something
... action:
...   input.firstLevel.secondLevel.thirdLevel = 999
... ''')
... 
>>> print engine.action({"firstLevel": {"secondLevel": {"thirdLevel": 1}}})
{'firstLevel': {'secondLevel': {'thirdLevel': 999}}}
```

### Updating cells and pools

The value of a cell or a pool item can be updated in-place in a way that is like variable assignment:

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"cell": "something", "to": 123}` | `something = 123`

And parts of it can be updated in a way that is like structure manipulation:

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"cell": "something", "path": [["field"], 2], "to": 123}` | `something["field", 2] = 123`
`{"pool": "space", "path": [["something"], ["field"], 2], "to": 123}` | `space["something", "field", 2] = 123`

These examples immediately modify the whole cell or the pool item and also return the new value.  The replacement is one atomic transaction: if two scoring engines attempt to change the same shared cell or pool, one will modify it first and the other will modify it afterward.

Sometimes, that could lead to inconsistent results.  If, for instance, the goal is to increment a value in a cell, a naive approach would be to query the cell's value in one transaction and change it in the next.  If another scoring engine modifies it in between, then it will not be correctly incremented.  In that case, we must send a callback function to lock the cell for an extended transaction.

The way to do this is to use a define an extended transaction in a function and pass that function to the cell or pool with a `to` keyword.  For instance:

```javascript
cells:
  counter(int) = 0
action:
  counter to fcn(old: int -> int) old + 1
```

The function may be declared inline, as in the above example, or it may be a named user-defined function:

```javascript
cells:
  counter(int) = 0
action:
  counter to u.increment
fcns:
  increment = fcn(old: int -> int) old + 1
```

The requirement is that the function accepts one argument, the old value of the cell, and returns the new value of the cell.  It can take as many steps as it needs to do so, and no other scoring engines will be able to modify the cell while it's working.

Substructure can be changed the same way.  The following increments the third integer of an array:

```javascript
cells:
  counter(array(int)) = [0, 0, 0, 0, 0]
action:
  counter[2] to fcn(old: int -> int) old + 1
```

Since pools are namespaces containing values, they are always modified as substructure.  However, the pool item you wish to replace might not exist yet, so pool modifiers must also have an `init` keyword:

```javascript
pools:
  counter(int) = {}
action:
  counter["key"] to fcn(old: int -> int) old + 1 init 0
```

The `init` quantity is a simple expression, not a function.

### Anonymous blocks

Although it's usually not necessary, it's possible to nest a sequence of expressions within a single expression by enclosing them in curly brackets.

There are two (rare) reasons for doing this: (1) to define local variables with a limited scope, and (2) to expand a slot that expects one simple expression into a block with temporary variables.  Here is an example of the second case: the right-hand side of an assignment is usually an equation, but if some temporary work needs to be done, it can be wrapped in curly brackets:

```python
var result = {
  var tmp = 0;
  tmp = tmp + 1;
  tmp
}
```

The PFA that is generated by this uses the `do` form:

```javascript
{"do": [{"let": {"tmp": 0}}, {"set": {"tmp": {"+": ["tmp", 1]}}}, "tmp"]}
```

### Conditionals

#### Simple if-then

The simplest `if` statement has one predicate and one consequent.

PFA example | PrettyPFA equivalent | return type
:---------- | :------------------- | :----------
`{"if": {">": ["x", 0]}, "then": {"f": "x"}}` | `if (x > 0) f(x)` | `null`

#### If-then-else

An `else` clause additionally provides an alternative, and the return value is either the consequent or the alternate.

PFA example | PrettyPFA equivalent | return type
:---------- | :------------------- | :----------
`{"if": {">": ["x", 0]}, "then": 1, "else": 2}` | `if (x > 0) 1 else 2` | `int`
`{"if": {">": ["x", 0]}, "then": 1, "else": {"string": "hello"}}` | `if (x > 0) 1 else "hello"` | `union(int, string)`

#### If-then-elseif-else

A chain of cascading conditions is represented by `else if`.  (A final `else` clause is optional, but without it, the return type is `null`.)

```javascript
if (x < 0)
  -1
else if (x == 0)
  0
else
  1
```

These do not resolve to nested `if` expressions in PFA, but to a flat `cond` block:

```javascript
{"cond": [{"if": {"<": ["x", 0]}, "then": -1},
          {"if": {"==": ["x", 0]}, "then": 0}],
 "else": 1}
```

### Loops

#### While loops (pretest)

While loops should be familiar: they have a test condition and a body.  Setting a `timeout` in the `options` section can prevent runaway loops.

```javascript
while (x > m.pi())
  x = x - 2*m.pi()
```

The PFA generated by this example is:

```javascript
{"while": {">": ["x", {"m.pi": []}]},
 "do": [
    {"set": {"x": {"-": ["x", {"*": [2, {"m.pi": []}]}]}}}
 ]}
```

#### Do-until (posttest)

Do-until loops are the post-test version of a `while` loop (and they continue until the test-condition becomes `true`, not while it is `true`).

```javascript
do
  x = x - 2*m.pi()
until (x < m.pi())
```

The PFA generated by this example is:

```javascript
{"do": [
  {"set": {"x": {"-": ["x", {"*": [2, {"m.pi": []}]}]}}}
 ],
  "until": {"<": ["x", {"m.pi": []}]}}
```

#### For loops with dummy variables

For loops should also be familiar.  This example emits Fibonacci numbers up to a given number of iterations.

```javascript
var a = 1, b = 1;
for (i = 0;  i < numIterations;  i = i + 1) {
  emit(a);
  a = b, b = a + b;
}
```

The PFA generated by this example is:

```javascript
{"for":   {"i": 0},
 "while": {"<": ["i", "numIterations"]},
 "step":  {"i": {"+": ["i", 1]}},
 "do": [
   {"emit": "a"},
   {"set": {"a": "b",
            "b": {"+": ["a", "b"]}}}
 ]}
```

The initializer and updator can act on multiple variables, as they do in C.  This example emits Fibonacci numbers up to a maximum value.

```javascript
for (a = 1, b = 1;  a < maxValue;  a = b, b = a + b)
  emit(a)
```

The PFA generated by this example is:

```javascript
{"for":   {"a": 1, "b": 1},
 "while": {"<": ["a", "maxValue"]},
 "step":  {"a": "b", "b": {"+": ["a", "b"]}},
 "do": [
   {"emit": ["a"]}
 ]}
```

#### Foreach loops over arrays and maps

Although a for loop could be used to define a dummy index that walks over an array, it is simpler to use the `foreach` version.

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"foreach": "x", "in": "myArray", "do": {"f": "x"}, "seq": false}` | `foreach (x: myArray) f(x)`
`{"foreach": "x", "in": "myArray", "do": {"f": "x"}, "seq": true}` | `foreach (x: myArray, seq: true) f(x)`

The `seq: true` form ensures that iteration is sequential (not parallelized), so variables declared outside the loop can be modified within it.

There is a variant of this syntax for iterating over the key, value pairs of a map:

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"forkey": "k", "forval": "v", "in": "myMap", "do": {"f": ["k", "v"]}}` | `foreach (k, v: myMap) f(k, v)`

### Defining functions

Functions are declared with an `fcn` keyword, a parenthesized list of argument name, argument type pairs, ending in a return type, followed by the function body, which must be enclosed in curly brackets if it involves more than one expression.  Here is an example:

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"params": [{"x": "int"}], "ret": "int", "do": [{"+": ["x", 1]}]}` | `fcn(x: int -> int) x + 1`

Functions may be defined inline, such as in the argument list of a function that takes a callback as an argument.  They can also be declared in the `fcns` section, where they are given a name that can be referenced multiple times.

Variables in an enclosing scope may be referenced within the function as free variables, but they cannot be modified (read-only closures).

### Partially applied functions

Another way to make functions is to apply arguments to an existing function.  That is, if `u.fcn3arg` is a function of three arguments, `x`, `y`, and `z`, the following are references to functions of 2 and 1 argument, respectively:

PFA example | PrettyPFA equivalent | number of arguments
:---------- | :------------------- | :------------------
`{"fcn": "u.fcn3arg", "fill": {"z": 3}}` | `u.fcn3arg(z: 3)` | 2 (`x` and `y`)
`{"fcn": "u.fcn3arg", "fill": {"y": 2, "z": 3}}` | `u.fcn3arg(y: 2, z: 3)` | 1 (just `x`)

It is important to note that `u.fcn3arg(1, 2, 3)` is a function call--- it evaluates the function and returns the result--- whereas `u.fcn3arg(x: 1, y: 2, z: 3)` is a function reference--- it is passed as an argument to something that may or may not call the function.  The key-value pairs in a partially applied function may be in any order.

This partial application may be used on user-defined functions or functions from the standard library.  For instance, it is sometimes useful to refer to the `m.atan2` of a triangle with one side fixed `m.atan2(y: 1.0)`.

### Calling functions specified at runtime

Although the PFA language makes widespread use of callbacks and operations on functions, it does not have first-class functions because these can be hard to implement in limited environments.  Some of the effects of first-class functions are simulated with inline function declarations and partially applied functions, but this leaves open another common need: the ability to choose a function to call at runtime.

For the purposes of small scoring engines, this ability can be provided through enumerations with names that match user-defined functions.  For instance, the following calls one of three functions on the number two:

```javascript
input: enum([linear, square, cube])
output: int
action:
  apply(input, 2)
fcns:
  linear = fcn(x: int -> int) x;
  square = fcn(x: int -> int) x**2;
  cube = fcn(x: int -> int) x**3
```

Since the input to the `apply` has an enumeration type, it can check all possible values for type consistency before runtime.  The generated PFA is given below.

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"call": "input", "args": [2]}` | `apply(input, 2)`

### General casting

Casting, or changing the type of an expression, can either make the type more general (upcasting) or more specific (downcasting).

Upcasting is the simple case: it is just a function call:

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"upcast": "x", "as": ["int", "string"]}` | `upcast(union(int, string), x)`

While upcasting is always safe, general downcasting is a back door to escape type-checking: a value that is asserted to have a certain type might not have that type at runtime, which would cause a runtime error.

Instead of casting in a way that simply asserts a type, PFA splits the program flow into branches, one for each possible type.  This will never cause a runtime error because a branch that assumes a given type will only be executed if the value has that type.

```javascript
cast(input) {
  as(x: int)
    s.concat(s.number(x), " is an integer")
  as(x: string)
    s.concat(x, " is a string")
}
```

In order for the `cast` expression to have a return value, every possible case must be covered, so that some branch is evaluated.  If that behavior is unnecessary, a `cast` can be declared as `partial` and the return type is `null`.

```javascript
cast(input, partial: true) {
  as(x: int)
    do_something(x)
}
```

The PFA generated by this example is:

```javascript
{"cast": "input",
 "cases": [
   {"as": "int", "named": "x", "do": [
     {"do_something": "x"}
   ]}],
 "partial": false}
```

### Missing value downcasting: ifnotnull

Since `null` is used as a missing value, one frequently needs to unpack a union of something and `null` (nullable), often for several variables at a time.  This would become tedius with the `cast`-`as` syntax.

The `ifnotnull` syntax is provided as a shortcut.  Given three variables, `xornull`, `yornull`, `zornull`, which are all nullable, the following expression evaluates the consequent if they are all non-null and the `else` clause if any are `null`.

```javascript
ifnotnull(x: xornull, y: yornull, z: zornull)
  do_something(x, y, z)
else
  default_value()
```

Without an `else` clause, this form returns `null`.  It is just like an `if` statement except that the body of the consequent receives `x`, `y`, `z` that are not nullable.  If, for instance, `xornull` is `union(double, null)`, then `x` is `double`.

The PFA generated by this example is:

```javascript
{"ifnotnull": {"x": "xornull", "y": "yornull", "z": "zornull"},
 "then": [
   {"do_something": ["x", "y", "z"]}
 ],
 "else": [
   {"default_value": []}
 ]}
```

### Missing value upcasting: if-else or try

The opposite of `ifnotnull` would turn a non-nullable type like `double` to a nullable one like `union(double, null)`.  A simple `if`-`else` statement would do that:

```javascript
if (condition(x))
  x
else
  null
```

The return type of the above is `union(double, null)` to allow for the possibility of encountering either branch.

However, if the reason for returning a nullable type is because an error might be encountered, use the `try` keyword.  The following returns `something(x)` if there were no exceptions in `something` and `null` if an exception was raised.

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"try": {"something": "x"}}` | `try something(x)`

A traditional try-catch block can be constructed by combining PrettyPFA's `try` with a `cast` or `ifnotnull` block.  The following catches all errors:

```javascript
ifnotnull(success: try something(x))
  do_success(success)
else
  do_failure()
```

And the following catches errors with error messages `"empty array"` and `"n < 0"`:

```javascript
ifnotnull(success: try("empty array", "n < 0") something(x))
  do_success(success)
else
  do_failure()
```

### Doc, error, and log

There are a few more special forms.

  * The `doc` form is an expression that does nothing and returns `null`.  It can be used to insert comments that are carried into the PFA document (unlike PrettyPFA comments).
  * The `error` form raises a user-defined exception.  It takes a string-based error message as argument.
  * The `log` form sends output to a log and returns `null`.  It takes arbitrarily many positional arguments (expressions to be logged) and an optional `namespace: "SomeWord"` argument for log filtering.

PFA example | PrettyPFA equivalent
:---------- | :-------------------
`{"doc": "This is nice."}` | `doc("This is nice.")`
`{"error": "This is broken!"}` | `error("This is broken!")`
`{"log": [["This is worth noting:"], "x", "y", "z"]}` | `log("This is worth noting:", x, y, z)`
`{"log": ["x", "y", "z"], "namespace": "DEBUG"}` | `log(x, y, z, namespace: "DEBUG")`







