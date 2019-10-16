# Motivation

[PMML is similar to PFA](http://dmg.org/pfa/docs/motivation/#flexibility-and-safety) in that both file formats are meant to encapsulate statistical models for transport between systems. But whereas PMML encodes one of several predefined models, PFA provides tools to encode new models by composing primitives. Therefore, any PMML model can be converted into PFA, but some PFA models can't be converted into PMML.

Converting a specific PMML model into PFA is easy: look up the corresponding functions, read the PMML's XML, and write the PFA's JSON. However, a script that converts _any_ PMML into the corresponding PFA is hard to write (about as hard as implementing PMML, for the same reasons).

Titus has a stub implementation of a general PMML to PFA converter that supports preprocessing transformations and decision trees. It could be expanded to include other models by adding the appropriate translations, one model type at a time. This document shows how to use Titus's converter, assuming that your input PMML satisfies the coverage.

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.8.3; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `pmmlToNode`, `PFAEngine`, and `look`:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from titus.pmml.reader import pmmlToNode
    >>> from titus.genpy import PFAEngine
    >>> from titus.producer.tools import look

The `titus.pmml.reader` module has several functions for converting PMML:

   * `pmmlToJson` returns a JSON string, already serialized and ready for transmission
   * `pmmlToNode` returns a Python structure representing the JSON, which is more convenient for examination and manipulation
   * `pmmlToAst` returns an [EngineConfig](http://modelop.github.io//hadrian/titus-0.8.3/titus.pfaast.EngineConfig.html#titus.pfaast.EngineConfig) (PFA abstract syntax tree), which is convenient for context-sensitive traversals or transformations.

## Trivial PMML document

The simplest PMML document allowed by [its specification](http://dmg.org/pmml/v4-2-1/GeneralStructure.html) is

```xml
>>> pmmlDocument = '''
<PMML version="4.2">
    <Header copyright=""/>
    <DataDictionary>
        <DataField name="x" optype="continuous" dataType="double" />
    </DataDictionary>
</PMML>
'''
```

though it's not clear what such a document ought to do. The `pmmlToNode` function converts it into a scoring engine that asserts an input schema but produces nothing:

```python
>>> look(pmmlToNode(pmmlDocument))
index                          data
------------------------------------------------------------
                               {
name                             "name": "Engine_1",
input                            "input": {
input,fields                       "fields": [{"type": "double", "name": "x"}],
input,type                         "type": "record",
input,name                         "name": "DataDictionary"
                                 },
output                           "output": "null",
method                           "method": "map",
action                           "action": [null]
                               }
```

## Basic transformations

To make the PMML do something, we should give it a model. The simplest model is a baseline z-score, which transforms data by subtracting a mean and dividing by a variance.

```xml
>>> pmmlDocument = '''
<PMML version="4.2">
    <Header copyright=""/>
    <DataDictionary>
        <DataField name="x" optype="continuous" dataType="double" />
    </DataDictionary>
    <BaselineModel>
        <TestDistributions field="x" testStatistic="zValue">
            <Baseline>
                <GaussianDistribution mean="1" variance="4"/>
            </Baseline>
        </TestDistributions>
    </BaselineModel>
</PMML>
'''
```

This translates to a PFA document that performs the two transformations.

```python
>>> pfaDocument = pmmlToNode(pmmlDocument)
>>> look(pfaDocument)
index                          data
------------------------------------------------------------
                               {
name                             "name": "Engine_2",
input                            "input": {
input,fields                       "fields": [{"type": "double", "name": "x"}],
input,type                         "type": "record",
input,name                         "name": "DataDictionary"
                                 },
output                           "output": "double",
method                           "method": "map",
action                           "action": [
action,0                           {
action,0,/                           "/": [
action,0,/,0                           {
action,0,/,0,-                           "-": [
action,0,/,0,-,0                           {
action,0,/,0,-,0,attr                        "attr": "input",
action,0,/,0,-,0,path                        "path": [{"string": "x"}]
                                           },
action,0,/,0,-,1                           1.0
                                         ]
                                       },
action,0,/,1                           {"m.sqrt": [4.0]}
                                     ]
                                   }
                                 ]
                               }
>>> 
>>> engine, = PFAEngine.fromJson(pfaDocument)
>>> engine.action({"x": 1})
0.0
>>> engine.action({"x": 2})
0.5
>>> engine.action({"x": 3})
1.0
>>> engine.action({"x": 4})
1.5
>>> engine.action({"x": 5})
2.0
```

PMML preprocessing transformations are converted into chains of PFA function applications. Most of PMML's built-in functions are supported (exceptions are date conversions and aggregations).

```xml
>>> pmmlDocument = '''
<PMML version="4.2">
    <Header copyright=""/>
    <DataDictionary>
        <DataField name="x" optype="continuous" dataType="double" />
    </DataDictionary>
    <BaselineModel>
        <LocalTransformations>
            <DerivedField name="y" optype="continuous" dataType="double">
                <Apply function="min">
                    <FieldRef field="x"/>
                    <Constant dataType="double">0</Constant>
                </Apply>
            </DerivedField>
        </LocalTransformations>
        <TestDistributions field="y" testStatistic="zValue">
            <Baseline>
                <GaussianDistribution mean="0" variance="1"/>
            </Baseline>
        </TestDistributions>
    </BaselineModel>
</PMML>
'''
```

```python
>>> pfaDocument = pmmlToNode(pmmlDocument)
>>> look(pfaDocument)
index                          data
------------------------------------------------------------
                               {
name                             "name": "Engine_3",
input                            "input": {
input,fields                       "fields": [{"type": "double", "name": "x"}],
input,type                         "type": "record",
input,name                         "name": "DataDictionary"
                                 },
output                           "output": "double",
method                           "method": "map",
action                           "action": [
action,0                           {
action,0,let                         "let": {
action,0,let,y                         "y": {
action,0,let,y,min                       "min": [
action,0,let,y,min,0                       {
action,0,let,y,min,0,attr                    "attr": "input",
action,0,let,y,min,0,path                    "path": [{"string": "x"}]
                                           },
action,0,let,y,min,1                       0.0
                                         ]
                                       }
                                     }
                                   },
action,1                           {
action,1,/                           "/": [
action,1,/,0                           {"-": ["y", 0.0]},
action,1,/,1                           {"m.sqrt": [1.0]}
                                     ]
                                   }
                                 ]
                               }
>>> 
>>> engine, = PFAEngine.fromJson(pfaDocument)
>>> engine.action({"x": 3})
0.0
>>> engine.action({"x": 2})
0.0
>>> engine.action({"x": 1})
0.0
>>> engine.action({"x": 0})
0.0
>>> engine.action({"x": -1})
-1.0
>>> engine.action({"x": -2})
-2.0
>>> engine.action({"x": -3})
-3.0
```

PMML's `<DefineFunction>` tags become user-defined functions in PFA.

```xml
>>> pmmlDocument = '''
<PMML version="4.2">
    <Header copyright=""/>
    <DataDictionary>
        <DataField name="x" optype="continuous" dataType="double" />
    </DataDictionary>
    <TransformationDictionary>
        <DefineFunction name="square">
            <ParameterField name="a" dataType="double"/>
            <Apply function="*">
                <FieldRef field="a"/>
                <FieldRef field="a"/>
            </Apply>
        </DefineFunction>
    </TransformationDictionary>
    <BaselineModel>
        <LocalTransformations>
            <DerivedField name="y" optype="continuous" dataType="double">
                <Apply function="square">
                    <FieldRef field="x"/>
                </Apply>
            </DerivedField>
        </LocalTransformations>
        <TestDistributions field="y" testStatistic="zValue">
            <Baseline>
                <GaussianDistribution mean="0" variance="1"/>
            </Baseline>
        </TestDistributions>
    </BaselineModel>
</PMML>
'''
```

```python
>>> pfaDocument = pmmlToNode(pmmlDocument)
>>> look(pfaDocument)
index                          data
------------------------------------------------------------
                               {
name                             "name": "Engine_4",
input                            "input": {
input,fields                       "fields": [{"type": "double", "name": "x"}],
input,type                         "type": "record",
input,name                         "name": "DataDictionary"
                                 },
output                           "output": "double",
method                           "method": "map",
action                           "action": [
action,0                           {
action,0,let                         "let": {
action,0,let,y                         "y": {
action,0,let,y,u.square                  "u.square": [
action,0,let,y,u.square,0                  {
action,0,let,y,u.square,0,attr               "attr": "input",
action,0,let,y,u.square,0,path               "path": [{"string": "x"}]
                                           }
                                         ]
                                       }
                                     }
                                   },
action,1                           {
action,1,/                           "/": [
action,1,/,0                           {"-": ["y", 0.0]},
action,1,/,1                           {"m.sqrt": [1.0]}
                                     ]
                                   }
                                 ],
fcns                             "fcns": {
fcns,square                        "square": {
fcns,square,params                   "params": [{"a": "double"}],
fcns,square,ret                      "ret": "double",
fcns,square,do                       "do": [
fcns,square,do,0                       {"*": ["a", "a"]}
                                     ]
                                   }
                                 }
                               }
>>> 
>>> engine, = PFAEngine.fromJson(pfaDocument)
>>> engine.action({"x": 0})
0.0
>>> engine.action({"x": 1})
1.0
>>> engine.action({"x": 2})
4.0
>>> engine.action({"x": 3})
9.0
>>> engine.action({"x": 4})
16.0
```

## Tree models

PMML decision trees can also be converted into the corresponding PFA structure.

```xml
>>> pmmlDocument = '''
<PMML version="4.2">
    <Header copyright=""/>
    <DataDictionary>
        <DataField name="x" optype="continuous" dataType="double" />
        <DataField name="y" optype="continuous" dataType="integer" />
        <DataField name="z" optype="categorical" dataType="string" />
    </DataDictionary>
    <TreeModel functionName="categorical" splitCharacteristic="binarySplit">
        <Node>
            <True/>
            <Node>
                <SimplePredicate field="x" operator="lessThan" value="1"/>
                <Node score="leaf-1">
                    <SimplePredicate field="z" operator="equal" value="hello"/>
                </Node>
                <Node score="leaf-2">
                    <SimplePredicate field="z" operator="notEqual" value="hello"/>
                </Node>
            </Node>
            <Node>
                <SimplePredicate field="x" operator="greaterOrEqual" value="1"/>
                <Node score="leaf-3">
                    <SimplePredicate field="z" operator="equal" value="hello"/>
                </Node>
                <Node score="leaf-4">
                    <SimplePredicate field="z" operator="notEqual" value="hello"/>
                </Node>
            </Node>
        </Node>
    </TreeModel>
</PMML>
'''
```

```python
>>> pfaDocument = pmmlToNode(pmmlDocument)
>>> look(pfaDocument)
index                          data
------------------------------------------------------------
                               {
name                             "name": "Engine_5",
input                            "input": {
input,fields                       "fields": [{"type": "double", "name": "x"}, {"type": "int", "name": "y"}, {"type": "string", "name": "z"}],
input,type                         "type": "record",
input,name                         "name": "DataDictionary"
                                 },
output                           "output": "string",
method                           "method": "map",
action                           "action": [
action,0                           {
action,0,model.tree.simpleWalk       "model.tree.simpleWalk": [
action,0,model.tree.simpleW...         "input",
action,0,model.tree.simpleW...         {"cell": "modelData"},
action,0,model.tree.simpleW...         {
action,0,model.tree.simpleW...           "params": [
action,0,model.tree.simpleW...             {"d": "DataDictionary"},
action,0,model.tree.simpleW...             {
action,0,model.tree.simpleW...               "t": {
action,0,model.tree.simpleW...                 "fields": [...],
action,0,model.tree.simpleW...                 "type": "record",
action,0,model.tree.simpleW...                 "name": "TreeNode"
                                             }
                                           }
                                         ],
action,0,model.tree.simpleW...           "ret": "boolean",
action,0,model.tree.simpleW...           "do": [
action,0,model.tree.simpleW...             {"model.tree.simpleTest": ["d", "t"]}
                                         ]
                                       }
                                     ]
                                   }
                                 ],
cells                            "cells": {
cells,modelData                    "modelData": {
cells,modelData,type                 "type": "TreeNode",
cells,modelData,init                 "init": {
cells,modelData,init,operator          "operator": "<",
cells,modelData,init,field             "field": "x",
cells,modelData,init,fail              "fail": {
cells,modelData,init,fail,T...           "TreeNode": {"operator": "==", "field": "z", "fail": {"string": "leaf-4"}, "value": {"string": "hello"}, "pass": {"string": "leaf-3"}}
                                       },
cells,modelData,init,value             "value": {"double": 1.0},
cells,modelData,init,pass              "pass": {
cells,modelData,init,pass,T...           "TreeNode": {"operator": "==", "field": "z", "fail": {"string": "leaf-2"}, "value": {"string": "hello"}, "pass": {"string": "leaf-1"}}
                                       }
                                     },
cells,modelData,shared               "shared": false,
cells,modelData,rollback             "rollback": false
                                   }
                                 }
                               }
>>> engine, = PFAEngine.fromJson(pfaDocument)
>>> engine.action({"x": 0.9, "y": 0, "z": "hello"})
u'leaf-1'
>>> engine.action({"x": 0.9, "y": 0, "z": "goodbye"})
u'leaf-2'
>>> engine.action({"x": 1.1, "y": 0, "z": "hello"})
u'leaf-3'
>>> engine.action({"x": 1.1, "y": 0, "z": "goodbye"})
u'leaf-4'
```

Implementing additional models would simply require a traversal over the appropriate PMML XML tags and conversion to the corresponding PFA JSON. The infrastructure in `titus.pmml.*` provides a glue for such conversions, to convert PMML preprocessing transformations and PMML models in the same framework.
