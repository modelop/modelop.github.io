# Segmentation

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import random
    >>> 
    >>> import numpy
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## Benefits of segmented models

Segmentation is a simple way to add flexibility to a model: the space of one or more features is partitioned into segments and submodels are independently trained for each segment.

Since the submodels can be scored independently, they can be distributed to different computers in a cluster, either because the full model is too large for any one computer or because the submodels' parameters can change, and changes among independent processors do not need to be kept consistent across the distributed cluster.

## Implementation in PFA

The easiest way to implement segmentation in PFA is to make a map of submodels. That is, if a submodel has type X, make a cell of type map(X) or make a pool of type X. If the submodel's parameters might change at runtime, the pool is a better choice since the granularity of change is at the level of each submodel, rather than the whole collection of submodels.

Here is an example of a simple z-score model, segmented by field `which`. After defining the `pfaDocument`, we generate a random dataset and fill the segments.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  SubModel = record(SubModel,
                    count: double,
                    mean: double,
                    variance: double)
input: record(which: string,
              x: double)
output: double
pools:
  submodels(SubModel) = {}
action:
  var submodel = submodels[input.which];
  stat.change.zValue(input.x, submodel, false)
''')

segments = ["s%02d" % i for i in xrange(100)]

dataset = [{"which": random.choice(segments), "x": random.gauss(0, 1)} for i in xrange(10000)]

def makeSubModel(segment):
    filtered = [datum["x"] for datum in dataset if datum["which"] == segment]
    if len(filtered) > 0:
        return {"count": len(filtered),
                "mean": float(numpy.mean(filtered)),
                "variance": float(numpy.var(filtered))}
    else:
        return None
                
submodels = dict((segment, makeSubModel(segment)) for segment in segments if makeSubModel(segment) is not None)

pfaDocument["pools"]["submodels"]["init"] = submodels

engine, = PFAEngine.fromJson(pfaDocument)

for datum in dataset:
    print engine.action(datum)
```

## Mutable submodels

The advantage of using a pool for segments is that concurrent scoring engines can update different items within a single pool at the same time, which can increase performance.

Here is an example of a segmented model that updates its state. In addition to the updator function, it needs an `init` to define the initial state, since it's possible that it will encounter new segments at runtime.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  SubModel = record(SubModel,
                    count: double,
                    mean: double,
                    variance: double)
input: record(which: string,
              x: double)
output: double
pools:
  submodels(SubModel, shared: true) = {}
action:
  var submodel = (submodels[input.which] to fcn(old: SubModel -> SubModel) {
    stat.sample.update(input.x, 1.0, old)
  } init {
    new(SubModel, count: 1.0, mean: input.x, variance: 0.0)
  });

  stat.change.zValue(input.x, submodel, false)
''')

segments = ["s%02d" % i for i in xrange(100)]

dataset = [{"which": random.choice(segments), "x": random.gauss(0, 1)} for i in xrange(100)]

def makeSubModel(segment):
    filtered = [datum["x"] for datum in dataset if datum["which"] == segment]
    if len(filtered) > 0:
        return {"count": len(filtered),
                "mean": float(numpy.mean(filtered)),
                "variance": float(numpy.var(filtered))}
    else:
        return None
                
submodels = dict((segment, makeSubModel(segment)) for segment in segments if makeSubModel(segment) is not None)

pfaDocument["pools"]["submodels"]["init"] = submodels

engine, = PFAEngine.fromJson(pfaDocument)

for datum in [{"which": random.choice(segments), "x": random.gauss(4, 1)} for i in xrange(1000)]:
    print engine.action(datum)
```

## When the segmentation key is not a string

In the above examples, we have assumed that the segmentation key is a string. In PFA, map keys and pool keys must be strings (a restriction inherited from Avro and JSON), so if your segmetnation key is not a string, you have two options: (1) turn it into a string and (2) use a ruleset of models.

The advantage of turning the segmentation key into a string is that maps and pools are implemented by trees and hashmaps, respectively, so you get logarithmic or constant-time lookup. If your segmentation key is a tuple of fields, you can join them with a delimiter. Be sure, however, that the delimiter does not appear in any of the subfields.

```python
delimiterExample, = titus.prettypfa.engine('''
input: record(a: string, b: string, c: string)
output: string
action: s.join(new(array(string), input.a, input.b, input.c), " - ")
''')
print delimiterExample.action({"a": "one", "b": "two", "c": "three"})
```

If a field is a number, you can bin it.

```python
binningExample, = titus.prettypfa.engine('''
input: double
output: string
action: s.number(cast.int(m.round((input - <<LOW>>) / (<<HIGH>> - <<LOW>>) * <<NUMBINS>>)))
''', LOW = 3, HIGH = 8, NUMBINS = 10)
print binningExample.action(4.5)
```

If your segmentation scheme is based on a series of predicates, the above won't work. In fact, it would be impossible to evaluate the rules without walking over the whole list, so a completely different approach is required. A straightforward way to do it is to use the primitives from the [`model.tree.*` library](http://scoringengine.org/docs/library/#lib:model.tree) to make a rule-set.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  SubModel = record(SubModel,
                    field: enum([x, y, z]),
                    operator: string,
                    value: double,
                    count: double,
                    mean: double,
                    variance: double);
input: record(x: double,
              y: double,
              z: double)
output: double
cells:
  submodels(array(SubModel)) = []
action:
  var index = a.index(submodels, fcn(submodel: SubModel -> boolean) {
    model.tree.simpleTest(input, submodel)
  });

  stat.change.zValue(input.x, submodels[index], false)
''')

pfaDocument["cells"]["submodels"]["init"] = [
    {"field": "y", "operator": ">", "value": 3, "count": 10, "mean": 5, "variance": 6.25},
    {"field": "z", "operator": "<=", "value": 8, "count": 9, "mean": 3, "variance": 4},
    {"field": "x", "operator": "alwaysTrue", "value": 0, "count": 12, "mean": 5, "variance": 9}
    ]

engine, = PFAEngine.fromJson(pfaDocument)
```

