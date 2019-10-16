This page provides an introduction to using Titus. It deliberately mirrors the [Hadrian Basic Use](Hadrian-Basic-Use) page.

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.8.3; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `json` and `PFAEngine`:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import json
    >>> from titus.genpy import PFAEngine

## Simplest possible scoring engines

Let's start with an engine that merely adds 10 to each input. That's something we can write inline.

```python
>>> engine, = PFAEngine.fromJson('''
... {"input": "double",
...  "output": "double",
...  "action": {"+": ["input", 10]}}
... ''')
```

For convenience, we could have written it in YAML (all of Titus's unit tests are written this way).

```python
>>> engine, = PFAEngine.fromYaml('''
... input: double
... output: double
... action: {"+": [input, 100]}
... ''')
```

Notice the comma (`,`) after `engine`. The `PFAEngine.fromJson` and `PFAEngine.fromYaml` functions produce a collection of `PFAEngine` objects from one PFA file (pass `multiplicity = 4` and drop the comma to see that). The comma makes the left-hand side a one-element tuple, effectively unpacking the singleton list. These scoring engines can run in parallel and share memory. For now, though, we're only interested in one scoring engine.

By virtue of having created an engine, the PFA has been fully validated. If the PFA is not valid, you would see

   * a `ValueError` because the JSON wasn't valid;
   * a `yaml.scanner.ScannerError` because the YAML wan't valid;
   * [`PFASyntaxException`](http://modelop.github.io//hadrian/titus-0.8.3/titus.errors.PFASyntaxException.html) if Titus could not build an [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) of the PFA from the JSON, for instance if a JSON field name is misspelled;
   * [`PFASemanticException`](http://modelop.github.io//hadrian/titus-0.8.3/titus.errors.PFASemanticException.html) if Titus could not build Python code from the AST, for instance if data types don't match;
   * [`PFAInitializationException`](http://modelop.github.io//hadrian/titus-0.8.3/titus.errors.PFAInitializationException.html) if Titus could not create a scoring engine instance, for instance if the cell/pool data are incorrectly formatted.

Now run the scoring engine on some sample input:

```python
>>> print engine.action(3.14)
103.14
```

You should only ever see one of the following exceptions at runtime

   * [`PFARuntimeException`](http://modelop.github.io//hadrian/titus-0.8.3/titus.errors.PFARuntimeException.html) if a PFA library function encountered an exceptional case, such as `a.max` of an empty list.
   * [`PFAUserException`](http://modelop.github.io//hadrian/titus-0.8.3/titus.errors.PFAUserException.html) if the PFA has explicit `{"error": "my error message"}` directives.
   * [`PFATimeoutException`](http://modelop.github.io//hadrian/titus-0.8.3/titus.errors.PFATimeoutException.html) if the PFA has some `"options": {"timeout": 1000}` set and a calculation takes too long.

### Emit-type engines

Of the three types of PFA scoring engine (map, emit, and fold), emit requires special attention in scoring. Map and fold engines yield results as the return value of the function (and fold do so cumulatively), but emit engines always return `None`. The only way to get results from them is by passing a callback function.

```python
>>> engine2, = PFAEngine.fromYaml('''
... input: double
... output: double
... method: emit
... action:
...   - if:
...       ==: [{"%": [input, 2]}, 0]
...     then:
...       - emit: input
...       - emit: {/: [input, 2]}
... ''')
... 
>>> def newEmit(x):
...     print "output:", x
... 
>>> engine2.emit = newEmit
>>> 
>>> for x in range(1, 5+1):
...     print "input:", x
...     engine2.action(x)
input: 1
input: 2
output: 2.0
output: 1.0
input: 3
input: 4
output: 4.0
output: 2.0
input: 5
```

## Titus Data Format

Data passed to Titus (or received from Titus) must take the following form.

| Avro type | Type in Titus | Example |
|:----------|:--------------|:--------|
| null | NoneType | `None` |
| boolean | bool | `True`, `False` |
| int | int or long | `3` |
| long | int or long | `3L` |
| float | int, long, or float | `3.14` |
| double | int, long, or float | `3.14` |
| string | str or unicode (Python 2) | `"hello"` |
| bytes | str (Python 2) | `"\x00\x01\x02"` |
| array | list or tuple | `[1, 2, 3]` |
| map | dict | `{"one": 1, "two": 2}` |
| record | dict | `{"x": 1, "y": "hello"}` |
| fixed | str (Python 2) | `"\x00\x01\x02"` |
| enum | str or unicode (Python 2) | `"third"` |
| union | untagged object | `3`, `"hello"`, or `None` |
|       | tagged object | `{"int": 3}`, `{"string": "hello"}`, or `None` |

Titus functions are designed to accept unions in tagged or untagged form and produce unions in tagged form. The [Python Avro library](https://pypi.python.org/pypi/avro/1.7.7) produces tagged unions and unicode strings and the [fastavro library](https://pypi.python.org/pypi/fastavro/0.9.5) produces untagged unions and raw strings.

## Snapshots

Snapshots are representations of a PFA engine's state at a moment in time. They are only relevant if the engine has a mutable state. Let's start by making a mutable scoring engine and filling it with some state.

```python
>>> engine4, = PFAEngine.fromYaml('''
... input: int
... output: {type: array, items: int}
... cells:
...   history:
...     type: {type: array, items: int}
...     init: []
... action:
...   cell: history
...   to: {a.append: [{cell: history}, input]}
... ''')
... 
>>> engine4.action(1)
[1]
>>> engine4.action(2)
[1, 2]
>>> engine4.action(3)
[1, 2, 3]
>>> engine4.action(4)
[1, 2, 3, 4]
>>> engine4.action(5)
[1, 2, 3, 4, 5]
```

The `snapshot` method locks the scoring engine and turns the state of the engine into a new AST that could be immediately serializxed as a PFA file.

```python
>>> engine4.snapshot()
EngineConfig(name=Engine_3,
    method=map,
    inputPlaceholder="int",
    outputPlaceholder={"items": "int", "type": "array"},
    begin=[],
    action=[CellTo(u'history', [], Call(u'a.append', [CellGet(u'history', []), Ref(u'input')]))],
    end=[],
    fcns={},
    zero=None,
    merge=None,
    cells={u'history': Cell({"items": "int", "type": "array"}, '[1, 2, 3, 4, 5]', False, False, 'embedded')},
    pools={},
    randseed=None,
    doc=None,
    version=None,
    metadata={},
    options={})
```

To get the values, dig into the [`EngineConfig`](http://modelop.github.io//hadrian/titus-0.8.3/titus.pfaast.EngineConfig.html) object to get the `init` of the relevant cell or pool. Then use `json.loads` to convert the serialized form into an object.

```python
>>> json.loads(engine4.snapshot().cells["history"].init)
[1, 2, 3, 4, 5]
```

### Abstract Syntax Tree

The PFA AST is an immutable tree structure built from the serialized JSON, stored in `engine.config`, which is an [`EngineConfig`](http://modelop.github.io//hadrian/titus-0.8.3/titus.pfaast.EngineConfig.html). You can query anything about the original PFA file in a structured way through this AST. For instance,

```python
>>> engine.config.action[0]
Call(u'+', [Ref(u'input'), LiteralInt(100)])

>>> engine.config.action[0].__class__.__name__
'Call'

>>> engine.config.input.avroType
"double"
```

There are also a few methods for recursively walking over the AST. The `collect` method applies a partial function to all nodes in the tree and produces a list of matches. For instance, to get all `Expressions` (function calls like "+", symbol references like "input", and literal values like "100"), do

```python
>>> from titus.pfaast import Expression
>>> def pf(x): return x
... 
>>> pf.isDefinedAt = lambda x: isinstance(x, Expression)
>>> 
>>> engine.config.collect(pf)
[Call(u'+', [Ref(u'input'), LiteralInt(100)]), Ref(u'input'), LiteralInt(100)]
```

The function object (`pf` in this case) must have another function associated with it to define the domain, making it a partial function in analogy with Scala's [`PartialFunction` class](http://blog.bruchez.name/2011/10/scala-partial-functions-without-phd.html).

You can also build new scoring engines by passing a replacement function. This one turns instances of 100 into 999. You can do quite a lot just by crafting the right partial function.

```python
>>> from titus.pfaast import LiteralInt
>>> def pf(x): return LiteralInt(999)
... 
>>> pf.isDefinedAt = lambda x: isinstance(x, LiteralInt) and x.value == 100
>>> 
>>> engine.config.replace(pf)
EngineConfig(name=Engine_1,
    method=map,
    inputPlaceholder="double",
    outputPlaceholder="double",
    begin=[],
    action=[Call(u'+', [Ref(u'input'), LiteralInt(999)])],
    end=[],
    fcns={},
    zero=None,
    merge=None,
    cells={},
    pools={},
    randseed=None,
    doc=None,
    version=None,
    metadata={},
    options={})
```

In fact, this is how Titus generates code in general. A `walk` over the tree checks for semantic errors while calling a `Task` at each node. Usually, this `Task` is to create Python code, but it could be anything. This small example generates Lisp.

```python
>>> from titus.pfaast import *
>>> from titus.datatype import *
>>> from titus.options import EngineOptions
>>> from titus.signature import PFAVersion
>>> 
>>> class LispCode(TaskResult): pass
... 
>>> class LispFunction(LispCode):
...     def __init__(self, car, cdr):
...         self.car = car
...         self.cdr = cdr
...     def __repr__(self):
...         return "(" + self.car + " " + " ".join(repr(x) for x in self.cdr) + ")"
... 
>>> class LispSymbol(LispCode):
...     def __init__(self, name):
...         self.name = name
...     def __repr__(self):
...         return self.name
... 
>>> class GenerateLisp(Task):
...     def __call__(self, context, engineOptions):
...         if isinstance(context, Call.Context):
...             return LispFunction(context.fcn.name, context.args)
...         elif isinstance(context, Ref.Context):
...             return LispSymbol(context.name)
...         elif isinstance(context, LiteralInt.Context):
...             return LispSymbol(str(context.value))
... 
>>> symbolTable = SymbolTable(None, {}, {}, {}, True, False)
>>> symbolTable.put("input", AvroDouble())
>>> engine.config.action[0].walk(GenerateLisp(), symbolTable, FunctionTable.blank(), \
...                              EngineOptions({}, {}), PFAVersion(0, 8, 1))[1]
... 
(+ input 100)
>>> 
>>> engine6, = PFAEngine.fromYaml('''
... input: double
... output: double
... action: {+: [{/: [input, 2]}, {m.sqrt: input}]}
... ''')
... 
>>> engine6.config.action[0].walk(GenerateLisp(), symbolTable, FunctionTable.blank(), \
...                               EngineOptions({}, {}), PFAVersion(0, 8, 1))[1]
... 
(+ (/ input 2) (m.sqrt input))
```