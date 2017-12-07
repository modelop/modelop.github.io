# Basic nearest neighbors

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import random
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## The basic form

A nearest neighbor model is simply a codebook of training points that are used to estimate density (or other quantities) at runtime. In this (common) case, we want to find the nearest `K` elements and average them. In general, we could find the nearest `K` elements (or all elements within a ball of radius `R`) and perform some other kind of integration over them. The `Point` data type can contain anything you want to aggregate. It could be a record if you're willing to write a metric function over those records.

```python
K = 5

pfaDocument = titus.prettypfa.jsonNode('''
types:
  Point = array(double);
  Codebook = array(Point)
input: Point
output: Point
cells:
  codebook(Codebook) = []
action:
  model.neighbor.mean(model.neighbor.nearestK(<<K>>, input, codebook, metric.simpleEuclidean))
''', K = K)
```

The French quotes (`<<` and `>>`) are a mechanism for inserting simple values into a PrettyPFA document. The values you insert have to be raw PFA.

## Producing a model

With nearest neighbors, there's no model to produce: just dump a bunch of points (usually from a training set, not randomly generated).

```python
def randomPoint():
    return [random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1)]

codebook = [randomPoint() for x in xrange(1000)]
```

## Insert the model into PFA

```python
pfaDocument["cells"]["codebook"]["init"] = codebook
```

## Test it!

```python
engine, = PFAEngine.fromJson(pfaDocument)

for point in codebook:
    print "{0:70s} -> {1}".format(point, engine.action(point))
```

Try setting `K` = 1 to see that it reproduces the input datum.
