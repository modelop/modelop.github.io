## Motivation

Often, you want a PFA scoring engine to exactly reproduce the preprocessing (or postprocessing) steps involved in model-production. For instance, if you normalize vectors before building k-means clusters, you must normalize the data using the same offset and scale while scoring.

PFA preprocessing steps are expressed using PFA functions, but the model producer may use its own language to express them. If you're building models in Python/Numpy, you're probably preprocessing the training data as Python lists or Numpy arrays.

The [`titus.producer.transformation.Transformation`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.transformation.Transformation.html) class is intended to help coordinate offline (producer) transformations in Python/Numpy with online (scoring) transformations in PFA.

## Before you begin...

Download and install [Titus](Installation#case-4-you-want-to-install-titus-in-python) and [Numpy](http://www.numpy.org/).  This article was tested with Titus 0.8.3 and Numpy 1.8.2; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `numpy`, `titus.producer.transformation`, and some Avro types for generating PFA output:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import numpy as np
    >>> from titus.producer.transformation import Transformation
    >>> from titus.datatype import AvroArray, AvroMap, AvroDouble, AvroRecord, AvroField

## Dataset formats

For the purposes of the `Transformation` class, a dataset is a rectangular table of numbers or strings. It may or may not have column names. Although this is similar to R data.frames, Pandas DataFrames, and SQL tables, the `Transformation` class expects tables without columns names to be in the form of Numpy 2-D arrays and tables with column names to be [Numpy record arrays](http://docs.scipy.org/doc/numpy/user/basics.rec.html) or Python dictionaries of equal-length Numpy 1-D arrays.

For instance, a table without column names would look like

    >>> dataFrame1 = np.random.normal(0.0, 1.0, (100, 3))

and a table with column names would look like

    >>> dataFrame2 = np.core.records.fromarrays((np.random.normal(0, 1, 100),
                                                 np.random.normal(0, 1, 100),
                                                 np.random.normal(0, 1, 100)),
                                                names="x, y, z")

or

    >>> dataFrame3 = {"x": np.random.normal(0, 1, 100),
                      "y": np.random.normal(0, 1, 100),
                      "z": np.random.normal(0, 1, 100)}

Transformations can accept any of these forms and it outputs the same type it received.

## Defining a transformation

Perhaps the most common type of transformation is just an offset and scaling of the inputs.

    >>> means = dataFrame1.mean(axis=0)
    >>> stdevs = dataFrame1.std(axis=0)
    >>> t1 = Transformation("(_0 - {means[0]})/{stdevs[0]}".format(**vars()),
                            "(_1 - {means[1]})/{stdevs[1]}".format(**vars()), 
                            "(_2 - {means[2]})/{stdevs[2]}".format(**vars()))

But any transformation from the N column input to an M column output is possible. The following takes each of the three input columns (`_0`, `_1`, and `_2`, because they are unnamed) to two output columns (which will be named `_0` and `_1`).

    >>> t2 = Transformation("_0**2 + _1 * m.sin(_2)", "_0**2 + _1 * m.cos(_2)")

Strings are parsed as [PrettyPFA](PrettyPFA-Reference), though an expression built from PFA AST instances (e.g. built using [`titus.reader.jsonToAst`](http://modelop.github.io//hadrian/titus-0.8.3/titus.reader.jsonToAst.html) or [`titus.reader.yamlToAst`](http://modelop.github.io//hadrian/titus-0.8.1/titus.reader.yamlToAst.html)) would also work.

Expressions using named columns are somewhat easier to read.

    >>> t3 = Transformation(xprime="x**2 + y * m.sin(z)", yprime="x**2 + y * m.cos(z)")

## Applying a transformation to Numpy arrays

Before training a model, you can preprocess your Numpy arrays using the `transform` method.

    >>> normalized = t1.transform(dataFrame1)
    >>> dataFrame2Prime = t3.transform(dataFrame2)
    >>> dataFrame3Prime = t3.transform(dataFrame3)

Although the transformations were expressed in PrettyPFA, those expressions were converted to Python/Numpy so that fast, vectorized Numpy functions are called, not Titus's PFA engine.

## Converting a transformation to PFA

The `Transformation` class has three methods to create a PFA snippet. The `expr` method creates a PFA expression that can be embedded in a larger calculation (as an argument in model input, for instance), though it is limited to one data column. The `let` method creates a PFA "let" block that defines several new variables at once. The `new` method creates a PFA "new" expression that creates an array, a map, or a record. Your choice depends on how you need the data formatted.

This is what the normalization `t1` looks like as PFA. Since it has unnamed columns, the data type for `new` is probably `AvroArray(AvroDouble())`.

```python
>>> t1.expr("_0")
{'/': [{'-': ['_0', -0.08392950604]}, 0.985158554796]}
>>> t1.expr("_1")
{'/': [{'-': ['_1', -0.113170895046]}, 1.11869880821]}
>>> t1.expr("_2")
{'/': [{'-': ['_2', 0.0375438926037]}, 0.958713316426]}
>>> 
>>> t1.let()
{'let': {'_0': {'/': [{'-': ['_0', -0.08392950604]}, 0.985158554796]},
         '_2': {'/': [{'-': ['_2', 0.0375438926037]}, 0.958713316426]},
         '_1': {'/': [{'-': ['_1', -0.113170895046]}, 1.11869880821]}}}
>>> 
>>> t1.new(AvroArray(AvroDouble()))
{'new': [{'/': [{'-': ['_0', -0.08392950604]}, 0.985158554796]},
         {'/': [{'-': ['_1', -0.113170895046]}, 1.11869880821]},
         {'/': [{'-': ['_2', 0.0375438926037]}, 0.958713316426]}],
 'type': {'items': 'double', 'type': 'array'}}
```

This is what the transformation `t3` looks like. Since it has named columns, the data type for `new` is probably `AvroMap(AvroDouble())` (if a record type is not defined) or an `AvroRecord` (if it is).

```python
>>> t3.expr("xprime")
{'+': [{'**': ['x', 2]}, {'*': ['y', {'m.sin': ['z']}]}]}
>>> t3.expr("yprime")
{'+': [{'**': ['x', 2]}, {'*': ['y', {'m.cos': ['z']}]}]}
>>> 
>>> t3.let()
{'let': {'xprime': {'+': [{'**': ['x', 2]}, {'*': ['y', {'m.sin': ['z']}]}]},
         'yprime': {'+': [{'**': ['x', 2]}, {'*': ['y', {'m.cos': ['z']}]}]}}}
>>> 
>>> t3.new(AvroMap(AvroDouble()))
{'new': {'xprime': {'+': [{'**': ['x', 2]}, {'*': ['y', {'m.sin': ['z']}]}]},
         'yprime': {'+': [{'**': ['x', 2]}, {'*': ['y', {'m.cos': ['z']}]}]}},
 'type': {'values': 'double', 'type': 'map'}}
>>> 
>>> recType = AvroRecord([AvroField("xprime", AvroDouble()),
...                       AvroField("yprime", AvroDouble())], "Prime")
... 
>>> t3.new(recType)
{'new': {'xprime': {'+': [{'**': ['x', 2]}, {'*': ['y', {'m.sin': ['z']}]}]},
         'yprime': {'+': [{'**': ['x', 2]}, {'*': ['y', {'m.cos': ['z']}]}]}},
 'type': 'Prime'}
```

These PFA expressions are ready to be inserted into a PFA document.

## Complete example

Suppose we want to normalize an input dataset, perform k-means clustering, and then produce a scoring engine that does the same normalization before using those clusters to classify. Here is how you would do that. Start by importing the relevant libraries.

    >>> import json
    >>> import titus.producer.kmeans as k
    >>> import titus.producer.tools as t

Next, transform `dataFrame1` by a mean-shift and standard deviation scaling. This is the same as above (same variable names, too), repeated here for completeness.

    >>> means = dataFrame1.mean(axis=0)
    >>> stdevs = dataFrame1.std(axis=0)
    >>> t1 = Transformation("(_0 - {means[0]})/{stdevs[0]}".format(**vars()),
                            "(_1 - {means[1]})/{stdevs[1]}".format(**vars()), 
                            "(_2 - {means[2]})/{stdevs[2]}".format(**vars()))
    >>> normalized = t1.transform(dataFrame1)

Now perform k-means as usual, but use `normalized` as the input dataset.

    >>> kmeans = k.KMeans(5, normalized)
    >>> kmeans.optimize(k.moving())

Look at the default PFA document that the `KMeans` object provides. The problem with it is that it assumes an input vector that has already been normalized, like its training data.

```
>>> pfaDocument = kmeans.pfaDocument("Cluster", map(str, range(5)))
>>> t.look(pfaDocument["action"])
index                          data
------------------------------------------------------------
                               [
0                                {
0,attr                             "attr": {
0,attr,model.cluster.closest         "model.cluster.closest": [
0,attr,model.cluster.closest,0         "input",
0,attr,model.cluster.closest,1         {"cell": "clusters"},
0,attr,model.cluster.closest,2         {
0,attr,model.cluster.closes...           "params": [
0,attr,model.cluster.closes...             {"datum": {"items": "double", "type": "array"}},
0,attr,model.cluster.closes...             {"clusterCenter": {"items": "double", "type": "array"}}
                                         ],
0,attr,model.cluster.closes...           "ret": "double",
0,attr,model.cluster.closes...           "do": [
0,attr,model.cluster.closes...             {
0,attr,model.cluster.closes...               "metric.euclidean": [{"fcn": "metric.absDiff"}, "datum", "clusterCenter"]
                                           }
                                         ]
                                       }
                                     ]
                                   },
0,path                             "path": [{"string": "id"}]
                                 }
                               ]
```

The problem is at index `"0,attr,model.cluster.closest,0"`, where the input argument to `model.cluster.closest` is `input`. We want that to be a transformation.

We can make the transformation like this.

```python
>>> preprocessed = t1.new(AvroArray(AvroDouble()),
                          _0={"attr": "input", "path": [0]},
                          _1={"attr": "input", "path": [1]},
                          _2={"attr": "input", "path": [2]})
>>> print json.dumps(preprocessed)
{"new": [{"/": [{"-": [{"attr": "input", "path": [0]}, -0.08392950604]}, 0.985158554796]},
         {"/": [{"-": [{"attr": "input", "path": [1]}, -0.113170895046]}, 1.11869880821]},
         {"/": [{"-": [{"attr": "input", "path": [2]}, 0.0375438926037]}, 0.958713316426]}],
 "type": {"items": "double", "type": "array"}}
```

where the `_0`, `_1`, and `_2` substitutions pull the individual elements out of the `input` array.

Finally, we replace the content at index `"0,attr,model.cluster.closest,0"` with our transformed expression.

```python
>>> t.assign(pfaDocument["action"], "0,attr,model.cluster.closest,0", preprocessed)
```

and look at the result. This is suitable for testing in Titus or writing out as JSON for Hadrian. Improperly preprocessed vectors tend to skew results toward a single cluster.

```
>>> t.look(pfaDocument["action"], maxDepth=10)
index                          data
------------------------------------------------------------
                               [
0                                {
0,attr                             "attr": {
0,attr,model.cluster.closest         "model.cluster.closest": [
0,attr,model.cluster.closest,0         {
0,attr,model.cluster.closes...           "new": [
0,attr,model.cluster.closes...             {
0,attr,model.cluster.closes...               "/": [
0,attr,model.cluster.closes...                 {
0,attr,model.cluster.closes...                   "-": [
0,attr,model.cluster.closes...                     {"attr": "input", "path": [0]},
0,attr,model.cluster.closes...                     -0.08392950604
                                                 ]
                                               },
0,attr,model.cluster.closes...                 0.985158554796
                                             ]
                                           },
0,attr,model.cluster.closes...             {
0,attr,model.cluster.closes...               "/": [
0,attr,model.cluster.closes...                 {
0,attr,model.cluster.closes...                   "-": [
0,attr,model.cluster.closes...                     {"attr": "input", "path": [1]},
0,attr,model.cluster.closes...                     -0.113170895046
                                                 ]
                                               },
0,attr,model.cluster.closes...                 1.11869880821
                                             ]
                                           },
0,attr,model.cluster.closes...             {
0,attr,model.cluster.closes...               "/": [
0,attr,model.cluster.closes...                 {
0,attr,model.cluster.closes...                   "-": [
0,attr,model.cluster.closes...                     {"attr": "input", "path": [2]},
0,attr,model.cluster.closes...                     0.0375438926037
                                                 ]
                                               },
0,attr,model.cluster.closes...                 0.958713316426
                                             ]
                                           }
                                         ],
0,attr,model.cluster.closes...           "type": {"items": "double", "type": "array"}
                                       },
0,attr,model.cluster.closest,1         {"cell": "clusters"},
0,attr,model.cluster.closest,2         {
0,attr,model.cluster.closes...           "params": [
0,attr,model.cluster.closes...             {"datum": {"items": "double", "type": "array"}},
0,attr,model.cluster.closes...             {"clusterCenter": {"items": "double", "type": "array"}}
                                         ],
0,attr,model.cluster.closes...           "ret": "double",
0,attr,model.cluster.closes...           "do": [
0,attr,model.cluster.closes...             {
0,attr,model.cluster.closes...               "metric.euclidean": [{"fcn": "metric.absDiff"}, "datum", "clusterCenter"]
                                           }
                                         ]
                                       }
                                     ]
                                   },
0,path                             "path": [{"string": "id"}]
                                 }
                               ]
```
