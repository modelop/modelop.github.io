When you first look at an auto-generated PFA file, it often looks like this:

```
{"input": {"type": "record", "fields": [{"name": "x1", "type": "string"}, {"name": "x2",
"type": ["null", "double"]}], "name": "Input"}, "output": "Output", "action": [{"let":
{"derived": {"type": {"type": "record", "fields": [{"name": "x1", "type": "string"},
{"name": "x2", "type": "double"}], "name": "Derived"}, "new": {"x1": {"s.lower": [{"attr":
"input", "path": [{"string": "x1"}]}]}, "x2": {"u.imputeX2": [{"attr": "input", "path":
[{"string": "x2"}]}]}}}}}, {"let": {"scores": {"a.map": [{"cell": "forest"}, {"params":
[{"tree": "TreeNode"}], "ret": "string", "do": [{"model.tree.simpleWalk": ["derived",
"tree", {"params": [{"d": "Derived"}, {"node": "TreeNode"}], "ret": "boolean", "do":
[{"model.tree.simpleTest": ["d", "node"]}]}]}]}]}}}, {"let": {"winner": {"a.mode":
["scores"]}}}, {"let": {"breakdown": {"type": {"type": "map", "values": "double"}, "new":
{"bad": {"/": [{"a.count": ["scores", {"string": "bad"}]}, {"a.len": ["scores"]}]},
"good": {"/": [{"a.count": ["scores", {"string": "good"}]}, {"a.len": ["scores"]}]}}}}},
{"type": {"type": "record", "fields": [{"name": "winner", "type": "string"}, {"name":
"breakdown", "type": {"type": "map", "values": "double"}}], "name": "Output"}, "new":
{"winner": "winner", "breakdown": "breakdown"}}], "fcns": {"imputeX2": {"params":
[{"possiblyNull": ["null", "double"]}], "ret": "double", "do": [{"ifnotnull": {"x":
"possiblyNull"}, "then": {"do": [{"cell": "runningAverage", "to": {"params": [{"old":
"RunningAverage"}], "ret": "RunningAverage", "do": [{"stat.sample.updateEWMA": ["x", 0.1,
...
```

Technically, it's human-readable, but it isn't organized well enough to be practical. Fortunately, Titus provides some tools for navigating PFA and making sense of it.

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.8.3; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `json` and `titus.producer.tools`:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import json
    >>> import titus.producer.tools as t

and download [myModel.pfa](https://github.com/opendatagroup/hadrian/wiki/model/myModel.pfa). Also, verify that you can run the `pfainspector` script (it gets installed in your executable path when you install Titus).

## Direct inspection in Python

PFA documents are pure JSON, so you can load them with Python's `json` module.

```python
pfaDocument = json.load(open("myModel.pfa"))
```

This loads the JSON text into Python objects with the following substitutions:

| JSON type | Example | Python object | Example |
|:----------|:--------|:--------------|:--------|
| null | `null` | None | `None` |
| boolean | `true`, `false` | bool | `True`, `False` |
| number | `3`, `3.14` | int, long, float | `3`, `3.14` |
| string | `"hello"` | str | `'hello'` |
| array | `[1, 2, 3]` | list | `[1, 2, 3]` |
| object | `{"one": 1, "two": 2}` | dict | `{'one': 1, 'two': 2}` |

You can navigate these types using ordinary Python square brackets, like this:

```python
>>> pfaDocument["cells"]["forest"]["init"][29]["pass"] \
...                ["TreeNode"]["fail"]["TreeNode"]["value"]
{u'array': [u'three']}
```

or modify them like this:

```python
>>> pfaDocument["cells"]["forest"]["init"][29]["pass"] \
...                ["TreeNode"]["fail"]["TreeNode"]["value"] = \
...                    {"array": ["three", "four"]}
```

but that still isn't particularly convenient for deep objects. Also, finding a path involves many interactive steps, asking for the `.keys()` or `len()` at each level, to avoid flooding the output with huge PFA fragments.

## Navigation tools in Titus

The `titus.producer.tools` module (loaded as `t` here) has a `get` method that treats Python's JSON representation as a tree that can be traversed with a path from root to any element. The above example becomes

```python
>>> t.get(pfaDocument, ("cells", "forest", "init", 29, "pass", "TreeNode", \
                        "fail", "TreeNode", "value"))
```

or even

```python
>>> t.get(pfaDocument, "cells,forest,init,29,pass,TreeNode,fail,TreeNode,value")
```

There is a corresponding `assign` for assignment.

```python
t.assign(pfaDocument, "cells,forest,init,29,pass,TreeNode,fail,TreeNode,value", \
             {"array": ["three", "four"]})
```

Finding the relevant path is still an issue, so Titus has a `look` function for browsing.

```
>>> t.look(pfaDocument)
index                          data
------------------------------------------------------------
                               {
action                           "action": [
action,0                           {
action,0,let                         "let": {
action,0,let,derived                   "derived": {
action,0,let,derived,new                 "new": {
action,0,let,derived,new,x2                "x2": {
action,0,let,derived,new,x2...               "u.imputeX2": [
action,0,let,derived,new,x2...                 {...}
                                             ]
                                           },
action,0,let,derived,new,x1                "x1": {
action,0,let,derived,new,x1...               "s.lower": [
action,0,let,derived,new,x1...                 {...}
                                             ]
                                           }
                                         },
action,0,let,derived,type                "type": {
action,0,let,derived,type,f...             "fields": [{"type": "string", "name": "x1"}, {"type": "double", "name": "x2"}],
action,0,let,derived,type,type             "type": "record",
action,0,let,derived,type,name             "name": "Derived"
                                         }
                                       }
                                     }
                                   },
action,1                           {
action,1,let                         "let": {
```

This function gives tree-indexes on the left and content on the right, pretty-printed such that two levels of depth are inline, six levels of depth are exploded, and anything deeper is hidden in ellipsis (`...`). All of these parameters can be controlled.

```
>>> help(t.look)
Help on function look in module titus.producer.tools:

look(expr, maxDepth=8, inlineDepth=2, indexWidth=30, dropAt=True, stream=<open file '<stdout>', mode 'w'>)
    Print a JSON object on the screen in a readable way.
    
    maxDepth: maximum depth to show before printing ellipsis (...)
    inlineDepth: maximum depth to show on a single line
    indexWidth: width (in characters) of the index column on the left
    dropAt: don't show "@" keys
    stream: allows the output to be sent to a file or stream.
```

For very deep objects, it's often useful to call `look` once to find part of the path, copy it into a `get`, and then call `look` again to go deeper.

```
>>> t.look(t.get(pfaDocument, "cells,forest,init,29,pass"))
index                          data
------------------------------------------------------------
                               {
TreeNode                         "TreeNode": {
TreeNode,operator                  "operator": "<=",
TreeNode,field                     "field": "x2",
TreeNode,fail                      "fail": {
TreeNode,fail,TreeNode               "TreeNode": {
TreeNode,fail,TreeNode,oper...         "operator": "in",
TreeNode,fail,TreeNode,field           "field": "x1",
TreeNode,fail,TreeNode,fail            "fail": {"string": "bad"},
TreeNode,fail,TreeNode,value           "value": {"array": ["three", "four"]},
TreeNode,fail,TreeNode,pass            "pass": {"string": "good"}
                                     }
                                   },
TreeNode,value                     "value": {"double": 7.26247432127833},
TreeNode,pass                      "pass": {
TreeNode,pass,TreeNode               "TreeNode": {
TreeNode,pass,TreeNode,oper...         "operator": "in",
TreeNode,pass,TreeNode,field           "field": "x1",
TreeNode,pass,TreeNode,fail            "fail": {"string": "bad"},
TreeNode,pass,TreeNode,value           "value": {"array": ["three"]},
TreeNode,pass,TreeNode,pass            "pass": {"string": "good"}
                                     }
                                   }
                                 }
                               }
```

These tools are intended for interactive exploration of a PFA document. To find substructures in a way that doesn't depend on index (to be more robust against changes in the PFA document), use [JSON regular expressions](JSON-Regular-Expressions), the next topic.
