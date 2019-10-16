# Basic baseline models

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

## The basic form

A lot of different things could all be called "baseline models." [Z-scores](http://scoringengine.org/docs/library/#fcn:stat.change.zValue) and [Mahalanobis distances](http://scoringengine.org/docs/library/#fcn:model.reg.mahalanobis) would be trivial examples, as would [moving windows](http://scoringengine.org/docs/library/#fcn:stat.sample.updateWindow), [exponentially weighted moving averages](http://scoringengine.org/docs/library/#fcn:stat.sample.updateEWMA), [Holt-Winters](http://scoringengine.org/docs/library/#fcn:stat.sample.updateHoltWinters), etc. There are also many ways to post-process a baseline, such as [one-pass filters](http://scoringengine.org/docs/library/#fcn:stat.change.updateTrigger) to avoid repeated alerts for the same deviation. Since baseline models are simple, they are often coupled with segmentation for finer granularity. To segment a model, simply put it in a pool, rather than a cell.

The model we have chosen to demonstrate here is a [cumulative sum (CUSUM)](https://en.wikipedia.org/wiki/CUSUM), a fairly simple statistic, but one that relies on mutable state. Of the four cells used to organize the model parameters, only `cusum` is mutable (is assigned to).

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Gaussian = record(mu: double, sig: double)

input: double
output: double
cells:
  cusum(double, shared: true) = 0.0;
  reset(double) = 0.0;
  baseline(Gaussian) = {mu: 0.0, sig: 0.0};   // will be replaced by training
  alternate(Gaussian) = {mu: 0.0, sig: 0.0}
  
action:
  var baseLL = prob.dist.gaussianLL(input, baseline.mu, baseline.sig);
  var altLL = prob.dist.gaussianLL(input, alternate.mu, alternate.sig);
  cusum to fcn(old: double -> double)
    stat.change.updateCUSUM(altLL - baseLL, old, reset)
''')
```

New values can be assigned to cells and pools using the usual `=` operator, but here we use a `to` keyword with a function to update `cusum` in a transaction. The function takes the old value of `cusum` as input and returns the new value as `output`. PFA ensures that multiple scoring engines, if they operate on shared data, do not interleave "get" and "put" operations, thereby corrupting the data. The contents of the function defines one atomic transaction on the data.

## Producing a model

A CUSUM is trained by characterizing two distributions, a baseline and an alternate.

```python
baselineDataset = [random.gauss(10, 2) for x in range(1000)]
alternateDataset = [random.gauss(5, 4) for x in range(100)]
```

## Insert the model into PFA

```python
pfaDocument["cells"]["baseline"]["init"]["mu"] = float(numpy.mean(baselineDataset))
pfaDocument["cells"]["baseline"]["init"]["sig"] = float(numpy.std(baselineDataset))
pfaDocument["cells"]["alternate"]["init"]["mu"] = float(numpy.mean(alternateDataset))
pfaDocument["cells"]["alternate"]["init"]["sig"] = float(numpy.std(alternateDataset))
```

## Test it!

In this test, we feed the scoring engine the baseline data, which yields zero or low significance, followed by the alternate distribution, which quickly accumulates to high significance.

```python
engine, = PFAEngine.fromJson(pfaDocument)

for datum in baselineDataset:
    print engine.action(datum)

for datum in alternateDataset:
    print engine.action(datum)
```

Again, there are many ways to treat these outputs; you will probably want to write custom alert code.
