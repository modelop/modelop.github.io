# Basic Gaussian Process

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.8.0; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import numpy
    >>> from sklearn import gaussian_process
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## Introduction

This document presents an example of how to use Gaussian Processes in
PFA, and how to compare results with the corresponding Scikit-Learn
function.

## Simplest example

First, let's make a Gaussian Process in Scikit-Learn.

Same function as the [Scikit-Learn documentation](http://scikit-learn.org/stable/modules/gaussian_process.html).
```python
def f(x):
    return x * numpy.sin(x)
```

Make 100 training x points of order pi.
```python
X = numpy.random.normal(3, 3, 100).reshape((100, 1))
```

Make 100 training y points.
```python
y = f(X)
```

Create a Gaussian Process object with a kernel proportional to exp(-x**2), with weight 0.1.
```python
gp = gaussian_process.GaussianProcess(corr="squared_exponential", theta0=0.1)
```

Fit it to our training data.
```python
gp.fit(X, y)
```

Make a prediction dataset and predict the value on it.
```python
x_pred = numpy.random.normal(3, 3, 100).reshape((100, 1))
y_pred = gp.predict(x_pred)
```

In PFA, we use the [`model.reg.gaussianProcess`](http://dmg.org/pfa/docs/library/#fcn:model.reg.gaussianProcess) function from the regression library, which coincidentally has the same signature as interpolation functions like `interp.linear`. This is so that the same training set can be used for interpolation or for a Gaussian Process, which is like a fancy interpolation.

The choice of "squared exponential" kernel corresponds to [`m.kernel.rbf`](http://dmg.org/pfa/docs/library/#fcn:m.kernel.rbf) in PFA. This function was introduced (and named) for use in SVM models, but it can be used anywhere. Even the metrics from the [`metric.*`](http://dmg.org/pfa/docs/library/#lib:metric) library, or user-defined functions, are fair game.

First, make a skeleton PFA document (in PrettyPFA) with all code applied but no model parameters.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  InterpolationPoint =
    record(InterpolationPoint,
           x: double,
           "to": double)
input: double
output: double
cells:
  table(array(InterpolationPoint)) = []
action:
  model.reg.gaussianProcess(input, table, null, m.kernel.rbf(gamma: <<theta0>>))
''', theta0=0.1)
```

Now fill it with the training data.
```python
pfaDocument["cells"]["table"]["init"] = [{"x": float(xi), "to": float(yi)} for xi, yi in zip(X, y)]
```

And create a scoring engine.
```python
engine, = PFAEngine.fromJson(pfaDocument)
```

Now we can compare the SciKit-Learn result with PFA. The small numerical differences can be traced to differences in the Cholesky, QR decomposition and linear solvers used by Scipy (Scikit-Learn) and Numpy (Titus). This case, which has no uncertainties in the training data, is the least numerically robust.

```python
for xi, yi in zip(x_pred, y_pred):
    pfaValue = engine.action(float(xi))
    print xi, yi, pfaValue, pfaValue - float(yi)
```

## Adding uncertainties to the training data

In Scikit-Learn, we add uncertainties to the training data by introducing a "nugget," another array whose value is (uncertainty in y / y)**2.

```python
def f(x):
    return x * numpy.sin(x)

X = numpy.random.normal(3, 3, 100).reshape((100, 1))
```

Create uncertainties and jiggle the y data by those uncertainties.
```python
ey = numpy.array([0.2] * len(X))
y = numpy.random.normal(f(X).reshape(100), ey)
```

```python
gp = gaussian_process.GaussianProcess(corr="squared_exponential", theta0=0.1, nugget=(ey/y)**2)
gp.fit(X, y)
x_pred = numpy.random.normal(3, 3, 100).reshape((100, 1))
y_pred = gp.predict(x_pred)
```

Now PFA's `InterpolationPoint` records include a `sigma` field for each uncertainty.
```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  InterpolationPoint =
    record(InterpolationPoint,
           x: double,
           "to": double,
           sigma: double)
input: double
output: double
cells:
  table(array(InterpolationPoint)) = []
action:
  model.reg.gaussianProcess(input, table, null, m.kernel.rbf(gamma: <<theta0>>))
''', theta0=0.1)
```

Now fill it with the training data.
```python
pfaDocument["cells"]["table"]["init"] = [{"x": float(xi), "to": float(yi), "sigma": float(eyi)} for xi, yi, eyi in zip(X, y, ey)]
engine, = PFAEngine.fromJson(pfaDocument)
```

In this case, the differences between Scikit-Learn and PFA are at the level of machine precision (1e-12).
```python
for xi, yi in zip(x_pred, y_pred):
    pfaValue = engine.action(float(xi))
    print xi, yi, pfaValue, pfaValue - float(yi)
```

## Vector regressors and regressands

The above cases all used one-dimensional regressors (X) and one-dimensional regressands (y). However, Scikit-Learn also supports the vector-regressor case and PFA supports all four cases (scalar-scalar, vector-scalar, scalar-vector, vector-vector). The `model.reg.gaussianProcess` has four signatures.

```python
def f(x1, x2, x3):
    return x1 * numpy.sin(x2) + x3

X = numpy.random.normal(3, 3, 300).reshape((100, 3))
```

Create uncertainties and jiggle the y data by those uncertainties.
```python
ey = numpy.array([0.2] * len(X))
y = numpy.random.normal(f(X[:,0], X[:,1], X[:,2]).reshape(100), ey)
```

```python
gp = gaussian_process.GaussianProcess(corr="squared_exponential", theta0=0.1, nugget=(ey/y)**2)
gp.fit(X, y)
x_pred = numpy.random.normal(3, 3, 300).reshape((100, 3))
y_pred = gp.predict(x_pred)
```

Now PFA's `InterpolationPoint` records include a `sigma` field for each uncertainty.
```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  InterpolationPoint =
    record(InterpolationPoint,
           x: array(double),
           "to": double,
           sigma: double)
input: array(double)
output: double
cells:
  table(array(InterpolationPoint)) = []
action:
  model.reg.gaussianProcess(input, table, null, m.kernel.rbf(gamma: <<theta0>>))
''', theta0=0.1)
```

Now fill it with the training data.
```python
pfaDocument["cells"]["table"]["init"] = [{"x": xi.tolist(), "to": float(yi), "sigma": float(eyi)} for xi, yi, eyi in zip(X, y, ey)]
engine, = PFAEngine.fromJson(pfaDocument)
```

In this case, the differences between Scikit-Learn and PFA are at the level of machine precision (1e-12).
```python
for xi, yi in zip(x_pred, y_pred):
    pfaValue = engine.action(xi.tolist())
    print xi, yi, pfaValue, pfaValue - float(yi)
```

## Using a given Kriging value

All of the above models had `null` in the slot for `krigingWeight`. This instructs `model.reg.gaussianProcess` to perform universal Kriging, but we could instead supply a specific value. In Scikit-Learn, this is `beta0`.

```python
def f(x):
    return x * numpy.sin(x)

X = numpy.random.normal(3, 3, 100).reshape((100, 1))
ey = numpy.array([0.2] * len(X))
y = numpy.random.normal(f(X).reshape(100), ey)
gp = gaussian_process.GaussianProcess(corr="squared_exponential", theta0=0.1, nugget=(ey/y)**2, beta0=1.0)
gp.fit(X, y)
x_pred = numpy.random.normal(3, 3, 100).reshape((100, 1))
y_pred = gp.predict(x_pred)

pfaDocument = titus.prettypfa.jsonNode('''
types:
  InterpolationPoint =
    record(InterpolationPoint,
           x: double,
           "to": double,
           sigma: double)
input: double
output: double
cells:
  table(array(InterpolationPoint)) = []
action:
  model.reg.gaussianProcess(input, table, <<beta0>>, m.kernel.rbf(gamma: <<theta0>>))
''', theta0=0.1, beta0=1.0)

pfaDocument["cells"]["table"]["init"] = [{"x": float(xi), "to": float(yi), "sigma": float(eyi)} for xi, yi, eyi in zip(X, y, ey)]
engine, = PFAEngine.fromJson(pfaDocument)

for xi, yi in zip(x_pred, y_pred):
    pfaValue = engine.action(float(xi))
    print xi, yi, pfaValue, pfaValue - float(yi)
```

## Sending the model to Hadrian

As always, a PFA model tested in Titus can be sent to Hadrian for large-scale production. The Hadrian implementation of `model.reg.gaussianProcess` is much more highly optimized, in that it only fits the training data once.

```python
import json
json.dump(pfaDocument, open("gaussianProcess.pfa", "w"))
```
