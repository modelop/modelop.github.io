## Motivation

PFA is sufficiently expressive to implement a wide variety of scoring engines, but model producers tend to be more complex. Ordinarily, one would produce a model with some non-PFA tool, such as R, Scikit-Learn, or MLlib, and then convert the resulting model into a PFA scoring engine afterward. This production process is overseen by a data analyst and should be in a dynamic language for flexibility. The final scoring engine is scaled out, sometimes to such a degree that it cannot be fully overseen by a human operator, and should be in a static language like PFA. The model-producing and model-execution environments are different because they have different needs.

However, sometimes you want to mix the two environments, at least partially. Data preprocessing applied to model training must be exactly the same as data preprocessing applied to the online scoring engine, and a good way to ensure exact reproducibility is to use exactly the same code. [Titus has tools](Preprocessing-in-Titus) for applying the same preprocessing expressions to Numpy arrays and PFA, but sometimes you even want to use the same workflow, such as Hadoop ([Hadrian-MR](Hadrian-MR)) or servlets ([Hadrian-GAE](Hadrian-GAE)). You want to run your model producer in the same way you'd run your PFA models, but you don't want to implement your training algorithm in PFA.

Antinous provides this functionality. It is a [Jython](http://www.jython.org/) library (Python for the JVM) that runs Python scripts anywhere that a PFA engine could run. Python is a dynamic language without the strictness or guarantees of PFA, which is good for model development. The only restriction that Antinous requires is that these Python scripts have a well-defined input and output schema and begin-action-end cycle, like PFA.

## Overview

Antinous is a library, not an application, the way that Hadrian is a library rather than an application. It provides functions to access Jython-masquerading-as-PFA, but it doesn't impose a particular workflow. Hadrian applications, such as Hadrian-Standalone, can include Antinous as a dependency rather than Hadrian as a dependency to get this additional ability. Hadrian-Standalone is an example of a Hadrian application with this feature, so we'll use it in the following examples.

## Before you begin...

Download the [pre-built Hadrian-Standalone JAR](Installation#case-2-you-want-to-use-pre-built-jar-files-for-one-of-the-hadrian-containers) with all dependencies, including Antinous. This article was tested with Hadrian 0.8.3; newer versions should work with no modification.

## Simple example

Consider a minimal PFA scoring engine, one that adds 100 to every input. (Or, not so minimal, since it does it by calling `emit`, rather than just mapping the `input + 100` expression.)

```json
{"input": "double",
 "output": "double",
 "method": "emit",
 "action": {"emit": {"+": ["input", 100]}}}
```

The equivalent Antinous Jython script is

```python
from antinous import *

input = double
output = double

def action(input):
    emit(input + 100)
```

We can run them both on numbers from 1 to 10 by calling Hadrian-Standalone like this:

    seq 1 10 | java -jar hadrian-standalone-TRUNK-jar-with-dependencies.jar -i json -o json test.pfa
    seq 1 10 | java -jar hadrian-standalone-TRUNK-jar-with-dependencies.jar -i json -o json test.py

When Hadrian-Standalone recognizes that `test.py` is not a PFA file, it passes the script to Antinous. Antinous runs the script in an embedded Jython interpreter and looks for five global variables: `input`, `output`, `begin`, `action`, and `end`. You can use any technique you want to assign these variables, but they must exist after the script has been evaluated once.

## Global variables

| Variable name | Interpreted meaning |
|:--------------|:--------------------|
| input | input schema (see below) |
| output | output schema (see below) |
| begin | callable function; return value ignored |
| action | callable function; return value ignored (use `emit`) |
| end | callable function; return value ignored |

The names of these variables should be familiar to you from PFA: `input` and `output` specify the kind of data the engine can handle and `begin`, `action`, `end` are called before, after, or on data in the data stream. If the data stream is infinite, `end` is never called.

## Input and output schema

The first line in the Jython script is `from antinous import *` to import some functions useful for constructing a schema. You could write the `input` and `output` schemas as Avro AVSC literals (JSON documents describing an Avro type), translating `null` to `None`, `true` to `True`, and `false` to `False` for Python. However, you can also build them as nested functions.

| Avro type | AVSC style | Function-call style |
|:----------|:-----------|:--------------------|
| null | `"null"` (string) or `{"type": "null"}` | `None` (Python built-in) or `null` (a singleton object imported from `antinous`) |
| boolean | `"boolean"` or `{"type": "boolean"}` | `boolean` |
| int | `"int"` or `{"type": "int"}` | `int` (Python's built-in integer type function) |
| long | `"long"` or `{"type": "long"}` | `long` (Python's built-in long type function) |
| float | `"float"` or `{"type": "float"}` | `float` (Python's built-in floating type function) |
| double | `"double"` or `{"type": "double"}` | `double` |
| bytes | `"bytes"` or `{"type": "bytes"}` | `bytes` (Python's built-in bytes type function) |
| string | `"string"` or `{"type": "string"}` | `string` |
| array of X | `{"type": "array", "items": X}` for some type X | `array(X)` for some type X |
| map of X | `{"type": "map", "values": X}` for some type X | `map(X)` for some type X; overshadows Python's built-in `map` (see below) |
| fixed bytes with size S | `{"type": "fixed", "name": N, "namespace": NS, "size": S}` (NS string is optional, N string is required) | `fixed(S, FQN)` (FQN fully qualified name string is optional) |
| enumeration with symbols S | `{"type": "enum", "name": N, "namespace": NS, "symbols": S}` (NS is optional, N is required, S is an array of strings) | `enum(S, FQN)` (FQN is optional, S is an array of strings) |
| record with fields F1=T1, F2=T2, ... | `{"type": "record", "name": N, "namespace": NS, "fields": [{"name": F1, "type": T1}, ...]}` | `record({F1: T1, ...}, FQN)` (FQN is optional, F1... are strings, T1... are types |
| union of T1, T2, ... | `[T1, T2, ...]` | `union(T1, T2, ...)` |

These two styles of type specification can be arbitrarily mixed. For instance, you could choose not to import `antinous` and express all of your types as AVSC, such as

```python
input = {"type": "record",
         "name": "MyRecord",
         "fields": [{"name": "one", "type": "int"},
                    {"name": "two", "type": "double"},
                    {"name": "three", "type": "string"}]}
output = ["null", "string"]
```

Or you could use the function-call style exclusively (which resembles [PrettyPFA](PrettyPFA-Reference#type-specifications)).

```python
from antinous import *
input = record(one = int, two = double, three = string)
output = union(null, string)
```

Or you could use both in the same schema.

```python
from antinous import *
input = record(one = "int", two = "double", three = {"type": "string"})
output = [None, string]
```

Antinous begins by recursively walking through the type specifications, normalizing them to AVSC form for Avro.

*Note:* it is unfortunate that Antinous's `map` type builder shadows Python's built-in `map` function. You could avoid this by

   * importing Antinous in a namespace (`import antinous` and call functions like `antinous.map`, rather than `from antinous import *`),
   * renaming `map` before importing Antinous, like `pymap = map; from antinous import *`, or
   * by reimplementing `map`: `def pymap(f, iterable): return [f(x) for x in iterable]`.

## Begin/action/end and emit/log

As with PFA, the `begin` method (if it exists) is called before processing the data stream, `action` is called on each datum, and `end` (if it exists) is called after the end of all data (if such a time exists). The return values of all three functions are ignored, so all Antinous Jython engines are implicitly emit-engines.

When an Antinous Jython engine begins, it has the `emit` and `log` (as in logfile) functions in the global scope, even if you don't `from antinous import *`. The `emit` function sends Python data to the output sink and the `log` function sends messages to the logfile processor (if it exists). The `emit` function expects data to be translatable to the output schema and the `log` function expects one or two strings (message or message and namespace).

The `action` method is called with one argument, the input (which, unlike PFA, you don't have to name "input"), and the `begin` and `end` methods are called with no arguments.

## Data translation

The main thing Antinous does is translate data between PFA and Jython. Jython has its own data model, using, for example, the Java class `PyList` for Python lists, whereas PFA uses `PFAArray` for PFA arrays.

When data is passed from a Hadrian application into a Jython script (as an argument to `action`), it is translated like this:

| Avro type | PFA type | Jython type | Python type |
|:----------|:---------|:------------|:------------|
| null | `null` | `Py.None` | `None` |
| boolean | `java.lang.Boolean` | `Py.True` or `Py.False` | `True` or `False` |
| int (32-bit) | `java.lang.Integer` | `PyInteger` | `int` (arbitrary precision) |
| long (64-bit) | `java.lang.Long` | `PyLong` | `long` (arbitrary precision) |
| float (32-bit) | `java.lang.Float` | `PyFloat` | `float` (64-bit) |
| double (64-bit) | `java.lang.Double` | `PyFloat` | `float` (64-bit) |
| string | `java.lang.String` | `PyUnicode` | `unicode` (abstract Unicode string) |
| bytes | `Array[Byte]` | `PyString` | `str` (raw string made using `array.array.tostring` |
| array | `PFAArray` (custom Hadrian) | `PyList` | `list` |
| map | `PFAMap` (custom Hadrian) | `PyDictionary` | `dict` |
| fixed | `PFAFixed` (custom Hadrian) | `JythonFixed` (custom Antinous) | object with an `__str__` method to get raw bytes |
| enum | `PFAEnumSymbol` (custom Hadrian) | `JythonEnumSymbol` (custom Antinous) | object with `__str__` and `__unicode__` methods to get symbol name |
| record | `PFARecord` (custom Hadrian) | `JythonRecord` (custom Antinous) | object with `__getattr__` for `object.attr` access |
| union | `AnyRef` | `PyObject` | `object` |

When data is passed from a Jython script back to the Hadrian application (as an argument to the `emit` function), it is translated like this:

| Avro type | Python type | Jython type | PFA type |
|:----------|:------------|:------------|:---------|
| null | `None` | `Py.None` | `null` |
| boolean | `True` or `False` | `Py.True` or `Py.False` | `java.lang.Boolean` |
| int | `int` or `long` | `PyInteger` or `PyLong` | `java.lang.Integer` |
| long | `int` or `long` | `PyInteger` or `PyLong` | `java.lang.Long` |
| float | `int`, `long`, or `float` | `PyInteger`, `PyLong`, or `PyFloat` | `java.lang.Float` |
| double | `int`, `long`, or `float` | `PyInteger`, `PyLong`, or `PyFloat` | `java.lang.Double` |
| string | `str` or `unicode` | `PyString` or `PyUnicode` | `java.lang.String` |
| bytes | `str` or `unicode` | `PyString` or `PyUnicode` | `Array[Byte]` |
| array | `list` or `tuple` | `PyList` or `PyTuple` | `PFAArray` (custom Hadrian) |
| map | `dict` | `PyDictionary` | `PFAMap` (custom Hadrian) |
| fixed | `JythonFixed`, `str`, or `unicode` | `JythonFixed` (custom Antinous), `PyString`, or `PyUnicode` | `PFAFixed` (custom Hadrian) |
| enum | `JythonEnumSymbol`, `str`, or `unicode` | `JythonFixed` (custom Antinous), `PyString`, or `PyUnicode` | `PFAEnumSymbol` (custom Hadrian) |
| record | `JythonRecord`, `dict` with the appropriate items (`__getitem__`), or `object` with the appropriate attributes (`__getattr__`) | `JythonRecord` (custom Antinous), `PyDictionary`, or `PyObject` | `PFARecord` |
| union | `object` | `PyObject` | `AnyRef` |

## Mutable state

One of the benefits of PFA is a well-controlled mutable state (cells and pools). Antinous does not explicitly define an equivalent for Jython scripts because the Python language already has ways of persisting state. However, the state of an Antinous Jython engine is not as well-controlled as in PFA.

To persist state in an Antinous Jython script, simply define some global variables. For instance,

```python
from antinous import *

input = double
output = double

total = 0.0

def action(x):
    global total
    total = total + x
    emit(total)
```

accumulates a total, emitting it every time. The `global` keyword is needed to inform Python to replace `total` in the global namespace. As another example,

```python
from antinous import *

input = double
output = array(double)

collection = []

def action(x):
    collection.append(x)
    emit(collection)
```

accumulates a list, emitting it every time. Here, the `global` keyword is not needed because the only `collection` is in the global namespace and we're not attempting to assign to it from a local namespace. We're just changing its value in place.

If you have multiple Antinous Jython engines running, there is no way to make their state shared, as there is in PFA.

Reverting an Antinous Jython engine to its initial state is also fragile. The Hadrian `PFAEngine` interface defines a `revert()` method that is supposed to make the engine exactly as it was after initialization and before the `begin` method. This re-initialization is exact for PFA engines and approximate for Antinous Jython engines.

After Antinous executes the Jython script once, it attempts to copy all objects from the global namespace by pickling them. ([Pickling](https://docs.python.org/3/library/pickle.html) is native Python serialization.) If an object is not pickleable, a reference to its initial value is saved instead. When the `revert()` method is called, Antinous repopulates the global namespace by unpickling its serialized copies and rebinding its referenced copies.

Thus, pickleable objects are exactly restored to their initial values, since the serialized form is sequestered in an immutable string and it encapsulates all of the object's deep structure. Non-pickleable, immutable objects such as functions and lambda expressions are re-attached to their original names, just in case `action` changed those names in the course of processing. (I know that you can assign attributes to functions, making them technically mutable, but you _wouldn't_ do that, would you?)

The unhandled case is that of non-pickleable, mutable objects. These are re-attached to their original names, but if `action` changed them in-place, then _they will not be restored_ by `revert()`. An object that contains a non-pickleable object is non-pickleable, which means that nested functions or lambda expressions will break the intended meaning of `revert()`. Consider the following:

```python
from antinous import *

input = double
output = double

good1 = {"a": 12, "b": 12}              # contains normal Python data
good2 = lambda y: y                     # Python function
bad = {"a": lambda y: y, "b": 12}       # Python data containing a function

def action(x):
    global good2
    emit(good2(good1["b"] + bad["b"]))  # make the output depend on everything

    good1["b"] = x                      # change good1 in-place
    good2 = lambda y: y + x             # rebind good2
    bad["a"] = lambda y: y + x          # change bad in-place
    bad["b"] = x                        # both items
```

The global object named `good1` is restored by `revert()` because it is pickleable--- it contains normal Python data. The global object `good2` is also restored by `revert()` because it would never be changed in place (though it may be rebound, as in the example). But the global object `bad` is incorrectly restored by `revert()` because it is not pickleable and its references are changed in-place. After a `revert()`, the keys `"a"` and `"b"` in `bad` will have the value of their last `action`, not the initial state.

Note that Hadrian-MR reducers make extensive use of `revert()` to guarantee independence of reduced keys. Mixed global data in an Antinous Jython reducer would lead to unexpected results.

## Loading libraries in Jython

Since Antinous executes scripts using Jython, any pure-Python libraries may be loaded if `sys.path` is correctly set. Also, any Java libraries may be loaded using

```python
from com.groupid.artifactid.package import ClassName
```

syntax. (See [Jython documentation](http://www.jython.org/jythonbook/en/1.0/JythonAndJavaIntegration.html#using-java-within-jython-applications) for details.) You can even load Hadrian using an experimental `pfainterface` package in Antinous:

```python
from antinous import *
from com.opendatagroup.antinous.pfainterface import PFAEngineFactory

input = double
output = double

pfaEngineFactory = PFAEngineFactory()

preprocessing = pfaEngineFactory.engineFromJson('''
{"input": "double",
 "output": "double",
 "action": {"m.log10": {"/": ["input", %g]}}}
''' % (1.0/127.0))

def action(x):
    y = preprocessing.action(x)
    emit(y)
```

This could be useful for ensuring that model-producer preprocessing is exactly the same as PFA preprocessing. (It also illustrates a deeply nested relationship: Hadrian PFA is running within Jython, which is running within Hadrian as though it were PFA.)

What you cannot load, however, are any natively compiled extensions for the C implementation of Python, such as Numpy. These are incompatible with the Java platform.

## JythonEngine in Scala code

To access Antinous in Scala code (to make an Antinous-aware Hadrian application, for instance), find the `JythonEngine` class in package `com.opendatagroup.antinous.engine`. This class satisfies the [`PFAEngine`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.jvmcompiler.PFAEngine) interface so that it can run anywhere a `PFAEngine` can run. PFA methods that don't make sense for Jython (such as `callGraph`, `snapshot`, anything involving cells or pools) simply raise `NotImplementedError`.

The `JythonEngine` companion object ("static methods" for the `JythonEngine` class) include

   * `factoryFromPython(in: InputStream, fileName: Option[String]): () => JythonEngine`
     
     Given a Python script in an `InputStream` (with an optional `fileName` for error reporting), create a zero-argument Scala function that produces executable `JythonEngines`.
     
   * `factoryFromPython(in: String, fileName: Option[String]): () => JythonEngine`
   * `factoryFromPython(in: java.io.File, fileName: Option[String]): () => JythonEngine`
     
     Same for input from strings and Java `File` objects.
     
   * `fromPython(in: AnyRef, fileName: String = "<string>", multiplicity: Int = 1): Seq[JythonEngine]`
     
     Create one or a collection of `JythonEngines` without the possibility of making future siblings.

**Example:** If you have some Scala code that makes `PFAEngines` like this:

```scala
val engines: Seq[PFAEngine] =
    if (suffix == ".pfa"  ||  suffix == ".json")
        PFAEngine.fromJson(source, multiplicity = numberOfEngines)
    else if (suffix == ".yaml")
        PFAEngine.fromYaml(source, multiplicity = numberOfEngines)
```

add the following:

```scala
    else if (suffix == ".py")
        JythonEngine.fromPython(source, multiplicity = numberOfEngines)
```

and `import com.opendatagroup.antinous.engine.JythonEngine`.
