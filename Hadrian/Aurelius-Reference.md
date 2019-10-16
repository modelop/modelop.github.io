### avro.array

Constructs a list-of-lists Avro schema for the array type.

**Usage:** `avro.array(items)`


**Examples:**

```R
avro.array(avro.int)
avro.array(avro.string)
```

### avro.boolean

Constructs a list-of-lists Avro schema for the boolean (logical) type.

**Usage:** `avro.boolean`



### avro.bytes

Constructs a list-of-lists Avro schema for the bytes (unstructured byte array) type.

**Usage:** `avro.bytes`



### avro.double

Constructs a list-of-lists Avro schema for the double (floating-point numeric with 64-bit precision) type.

**Usage:** `avro.double`



### avro.enum

Constructs a list-of-lists Avro schema for the enum (set of symbols) type.

**Usage:** `avro.enum(symbols, name = NULL, namespace = NULL)`

   * **symbols:** list of string-valued symbol names
   * **name:** required name (if missing, uniqueEnumName is invoked)
   * **namespace:** optional namespace

**Examples:**

```R
avro.enum(list("one", "two", "three"))
```

### avro.fixed

Constructs a list-of-lists Avro schema for the fixed (byte array with fixed size) type.

**Usage:** `avro.fixed(size, name = NULL, namespace = NULL)`

   * **size:** size of the byte array
   * **name:** required name (if missing, uniqueFixedName is invoked)
   * **namespace:** optional namespace

**Examples:**

```R
avro.fixed(6, "MACAddress")
```

### avro.float

Constructs a list-of-lists Avro schema for the float (floating-point numeric with 32-bit precision) type.

**Usage:** `avro.float`



### avro.fromFrame

Convenience function for creating an Avro input schema from a data frame

**Usage:** `avro.fromFrame(dataFrame, exclude = list(), name = NULL, namespace = NULL)`

   * **dataFrame:** a data.frame object
   * **exclude:** set of field names to exclude
   * **name:** required name of the record (if not specified, uniqueRecordName will be invoked)
   * **namespace:** optional namespace of the record

**Examples:**

```R
avro.fromFrame(dataFrame)
```

### avro.fullName

Yields the full type name (with namespace) of an Avro list-of-lists

**Usage:** `avro.fullName(type)`


**Examples:**

```R
avro.fullName(avro.record(list(), "MyRecord"))                   # "MyRecord"
avro.fullName(avro.record(list(), "MyRecord", "com.wowzers"))    # "com.wowzers.MyRecord"
```

### avro.int

Constructs a list-of-lists Avro schema for the int (integer numeric with 32-bit precision) type.

**Usage:** `avro.int`



### avro.long

Constructs a list-of-lists Avro schema for the long (integer numeric with 64-bit precision) type.

**Usage:** `avro.long`



### avro.map

Constructs a list-of-lists Avro schema for the map type.

**Usage:** `avro.map(values)`


**Examples:**

```R
avro.map(avro.int)
avro.map(avro.string)
```

### avro.null

Constructs a list-of-lists Avro schema for the null type (type with only one value).

**Usage:** `avro.null`



### avro.record

Constructs a list-of-lists Avro schema for the record type.

**Usage:** `avro.record(fields, name = NULL, namespace = NULL)`

   * **fields:** named list of field names and schemas
   * **name:** required name (if missing, uniqueRecordName is invoked)
   * **namespace:** optional namespace

**Examples:**

```R
avro.record(list(one = avro.int, two = avro.double, three = avro.string))
```

### avro.string

Constructs a list-of-lists Avro schema for the string (UTF-8) type.

**Usage:** `avro.string`



### avro.type

Inspects an R object and produces the corresponding Avro type name

**Usage:** `avro.type(obj)`


**Examples:**

```R
avro.type("hello")           # "string"
avro.type(factor("hello"))   # "string"
avro.type(3.14)              # "double"
avro.type(3)                 # "int"
```

### avro.typemap

Convenience function for ensuring that Avro type schemas are declared exactly once. It returns a function that yields a full type declaration the first time it is invoked and just a name on subsequent times.

**Usage:** `avro.typemap(...)`


**Examples:**

```R
tm <- avro.typemap(
    MyType1 = avro.record(list(one = avro.int, two = avro.double, three = avro.string), MyType1),
    MyType2 = avro.array(avro.double)
)
tm("MyType1")           # produces the whole declaration
tm("MyType1")           # produces just "MyType1"
tm("MyType2")           # produces the whole declaration
tm("MyType2")           # produces the declaration again because this is not a named type
```

### avro.union

Constructs a list-of-lists Avro schema for the tagged union type.

**Usage:** `avro.union(...)`


**Examples:**

```R
avro.union(avro.null, avro.int)         # a way to make a nullable int
avro.union(avro.double, avro.string)    # any set of types can be unioned
```

### json

Convert a list-of-lists structure into a JSON string in memory or a JSON file on disk.

**Usage:** `json(x, fileName = NULL, newline = TRUE, spaces = TRUE, sigfigs = NULL, stringsAsIs = FALSE)`

   * **x:** The structure to convert.
   * **fileName:** If NULL (default), return an in-memory JSON string; if a fileName string, write to a file without incurring in-memory overhead.
   * **newline:** If TRUE (default), end the string/file with a newline.
   * **spaces:** If TRUE (default), include spaces after commas and colons for readability.
   * **sigfigs:** If NULL (default), represent numbers with full precision; if an integer, represent numbers with that many significant digits.
   * **stringsAsIs:** If FALSE (default), process strings to escape characters that need to be escaped in JSON; if TRUE, pass strings as-is for speed, possibly creating invalid JSON.

**Examples:**

```R
cat(json(pfaDocument))
json(pfaDocument, fileName = "myModel.pfa")
```

### json.array

Convenience function for making a (possibly empty) unnamed list, which converts to a JSON array.

**Usage:** `json.array(...)`


**Examples:**

```R
json.array()
json.array(1, TRUE, "THREE")
```

### json.map

Convenience function for making a (possibly empty) named list, which converts to a JSON object.

**Usage:** `json.map(...)`


**Examples:**

```R
json.map()
json.map(one = 1, two = TRUE, three = "THREE")
```

### pfa.cell

Creates a list-of-lists representing a PFA cell.

**Usage:** `pfa.cell(type, init, source = "embedded", shared = FALSE, rollback = FALSE)`

   * **type:** cell type, which is an Avro schema as list-of-lists (created by avro.* functions)
   * **init:** cell initial value, which is a list-of-lists, usually converted from a model
   * **source:** if "embedded", the init is the data structure, if "json", the init is a URL string pointing to an external JSON file
   * **shared:** if TRUE, the cell is shared across scoring engine instances
   * **rollback:** if TRUE, the cell’s value would be rolled back if an uncaught exception is encountered

**Examples:**

```R
pfa.cell(avro.double, 12)
```

### pfa.config

Create a complete PFA document as a list-of-lists. Composing with the json function creates a PFA file on disk.

**Usage:** `pfa.config(input, output, action, name = NULL, method = NULL, begin = NULL, end = NULL, fcns = NULL, zero = NULL, merge = NULL, cells = NULL, pools = NULL, randseed = NULL, doc = NULL, version = NULL, metadata = NULL, options = NULL, env = parent.frame())`

   * **input:** input schema, which is an Avro schema as list-of-lists (created by avro.* functions)
   * **output:** output schema, which is an Avro schema as list-of-lists (created by avro.* functions)
   * **action:** R commands wrapped as an expression (see R’s built-in expression function)
   * **name:** optional name for the scoring engine (string)
   * **method:** "map", "emit", "fold", or NULL (for "map")
   * **begin:** R commands wrapped as an expression
   * **end:** R commands wrapped as an expression
   * **fcns:** named list of R commands, wrapped as expressions
   * **zero:** list-of-lists representing the initial value for a "fold“s tally
   * **merge:** R commands wrapped as an expression
   * **cells:** named list of cell specifications (see the pfa.cell function)
   * **pools:** named list of pool specifications (see the pfa.cell function)
   * **randseed:** optional random number seed (integer) for ensuring that the scoring engine is deterministic
   * **doc:** optional model documentation string
   * **version:** optional model version number (integer)
   * **metadata:** optional named list of strings to store model metadata
   * **options:** optional list-of-lists to specify PFA options
   * **env:** environment for resolving unrecognized symbols as substitutions

**Examples:**

```R
pfa.config(avro.double, avro.double, expression(input + 10))
```

### pfa.engine

Create an executable PFA scoring engine in R by calling Titus through rPython. If this function is successful, then the PFA is valid (only way to check PFA validity in R).

**Usage:** `pfa.engine(config, tempFile = NULL)`

   * **config:** list-of-lists representing a complete PFA document
   * **tempFile:** if NULL, generate the PFA as a string in memory and pass it without touching disk; if a string, save the PFA document in a temporary file and have Python load it from that file

**Examples:**

```R
pfa.engine(pfaDocument)   # where pfaDocument is created by pfa.config
```

### pfa.expr

Convert a quoted R expression into a list-of-lists that can be inserted into PFA

**Usage:** `pfa.expr(expr, symbols = list(), cells = list(), pools = list(), fcns = list(), env = parent.frame())`

   * **expr:** quoted R expression (e.g. quote(2 + 2))
   * **symbols:** list of symbol names that would be in scope when evaluating this expression
   * **cells:** list of cell names that would be in scope when evaluating this expression
   * **pools:** list of pool names that would be in scope when evaluating this expression
   * **fcns:** list of function names that would be in scope when evaluating this expression
   * **env:** environment for resolving unrecognized symbols as substitutions

**Examples:**

```R
pfa.expr(quote(2 + 2))
```

### pfa.gbm.buildOneTree

Builds one tree extracted by pfa.gbm.extractTree.

**Usage:** `pfa.gbm.buildOneTree(tree, categoricalLookup, whichNode, valueNeedsTag = TRUE, dataLevels = NULL, fieldTypes = NULL)`

   * **tree:** FIXME
   * **categoricalLookup:** FIXME
   * **whichNode:** FIXME
   * **valueNeedsTag:** FIXME
   * **dataLevels:** FIXME
   * **fieldTypes:** FIXME

**Examples:**

```R
FIXME
```

### pfa.gbm.extractTree

Extracts a tree from a forest made by the gbm library.

**Usage:** `pfa.gbm.extractTree(gbm, whichTree = 1)`

   * **gbm:** an object of class "gbm"
   * **whichTree:** FIXME

**Examples:**

```R
FIXME
```

### pfa.glm.extractParams

Extract generalized linear model parameters from the glm library

**Usage:** `pfa.glm.extractParams(fit)`


**Examples:**

```R
FIXME
```

### pfa.glmnet.extractParams

Extract generalized linear model net parameters from the glm library

**Usage:** `pfa.glmnet.extractParams(cvfit, lambdaval = "lambda.1se")`

   * **cvfit:** an object of class "cv.glmnet"
   * **lambdaval:** FIXME

**Examples:**

```R
FIXME
```

### pfa.glmnet.inputType

describeme

**Usage:** `pfa.glmnet.inputType(params, name = NULL, namespace = NULL)`


**Examples:**

```R
someExamples
```

### pfa.glmnet.modelParams

describeme

**Usage:** `pfa.glmnet.modelParams(params)`


**Examples:**

```R
someExamples
```

### pfa.glmnet.predictProb

describeme

**Usage:** `pfa.glmnet.predictProb(params, input, model)`


**Examples:**

```R
someExamples
```

### pfa.glmnet.regressionType

describeme

**Usage:** `pfa.glmnet.regressionType(params)`


**Examples:**

```R
someExamples
```

### pfa.pool

Creates a list-of-lists representing a PFA pool.

**Usage:** `pfa.pool(type, init, source = "embedded", shared = FALSE, rollback = FALSE)`

   * **type:** pool type, which is an Avro schema as list-of-lists (created by avro.* functions)
   * **init:** pool initial value, which is a list-of-lists, usually converted from a model
   * **source:** if "embedded", the init is the data structure, if "json", the init is a URL string pointing to an external JSON file
   * **shared:** if TRUE, the pool is shared across scoring engine instances
   * **rollback:** if TRUE, the pool’s value would be rolled back if an uncaught exception is encountered

**Examples:**

```R
pfa.pool(avro.double, json.map(one = 1.1, two = 2.2, three = 3.3))
```

### pfa.randomForest.buildOneTree

Builds one tree extracted by pfa.randomForest.extractTree.

**Usage:** `pfa.randomForest.buildOneTree(tree, whichNode, valueNeedsTag, dataLevels, fieldTypes = NULL)`

   * **tree:** FIXME
   * **whichNode:** FIXME
   * **valueNeedsTag:** FIXME
   * **dataLevels:** FIXME
   * **fieldTypes:** FIXME

**Examples:**

```R
FIXME
```

### pfa.randomForest.extractTree

Extracts a tree from a forest made by the randomForest library.

**Usage:** `pfa.randomForest.extractTree(forest, whichTree = 1, labelVar = FALSE)`

   * **forest:** an object of class "randomForest"
   * **whichTree:** FIXME
   * **labelVar:** FIXME

**Examples:**

```R
FIXME
```

### uniqueEngineName

Convenience or internal function for generating engine names; each call results in a new name.

**Usage:** `uniqueEngineName()`


**Examples:**

```R
uniqueEngineName()
```

### uniqueEnumName

Convenience or internal function for generating enum names; each call results in a new name.

**Usage:** `uniqueEnumName()`


**Examples:**

```R
uniqueEnumName()
```

### uniqueFixedName

Convenience or internal function for generating fixed names; each call results in a new name.

**Usage:** `uniqueFixedName()`


**Examples:**

```R
uniqueFixedName()
```

### uniqueRecordName

Convenience or internal function for generating record names; each call results in a new name.

**Usage:** `uniqueRecordName()`


**Examples:**

```R
uniqueRecordName()
```

### uniqueSymbolName

Convenience or internal function for generating symbol names; each call results in a new name.

**Usage:** `uniqueSymbolName(symbols)`


**Examples:**

```R
uniqueSymbolName()
```

### unjson

Convert a JSON string in memory or a JSON file on disk into a list-of-lists structure.

**Usage:** `unjson(x)`


**Examples:**

```R
unjson("{\\"one\\": 1, \\"two\\": true, \\"three\\": \\"THREE\\"}")
unjson(file("myModel.pfa"))
```

