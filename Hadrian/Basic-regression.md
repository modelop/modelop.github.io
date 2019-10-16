# Basic regression

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import numpy
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## The basic form

Regression models are sometimes difficult to produce, but they are always simple to score. You only need a constant term, coefficients vector, and maybe a link function (for scoring engines built from logistic regression, for instance).

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Regression = record(Regression,
                      const: double,
                      coeff: array(double))
input: array(double)
output: double
cells:
  regression(Regression) = {const: 0.0, coeff: []}
action:
  model.reg.linear(input, regression)
''')
```

## Producing a model

Numpy can compute ordinary least squares linear regressions.

```python
x1data = numpy.random.uniform(-1, 1, 1000); x1data.sort()
x2data = numpy.random.uniform(-1, 1, 1000); x2data.sort()
x3data = numpy.random.uniform(-1, 1, 1000); x3data.sort()
x4data = numpy.random.uniform(-1, 1, 1000); x4data.sort()
x5data = numpy.random.uniform(-1, 1, 1000); x5data.sort()
ydata = numpy.array(range(1000)) + numpy.random.uniform(-0.1, 0.1, 1000)

A = numpy.vstack([numpy.ones(1000), x1data, x2data, x3data, x4data, x5data]).T

allcoeff = numpy.linalg.lstsq(A, ydata)[0]
const = float(allcoeff[0])
coeff = allcoeff[1:].tolist()
```

## Insert the model into PFA

```python
pfaDocument["cells"]["regression"]["init"] = {"const": const, "coeff": coeff}
```

## Test it!

```python
engine, = PFAEngine.fromJson(pfaDocument)

for x1, x2, x3, x4, x5, y in zip(x1data, x2data, x3data, x4data, x5data, ydata):
    print "{0} vs {1}".format(engine.action([x1, x2, x3, x4, x5]), y)
```
