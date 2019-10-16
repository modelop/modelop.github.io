# Basic naïve bayes

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## The basic form

The [`model.naive.*` library](http://scoringengine.org/docs/library/#lib:model.naive) consists of functions that compute log likelihoods of one-dimensional distributions. These must be normalzed and compared to find the class with the most likely distribution for a given input.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Distribution = record(Distribution,
                        logLikelihoods: array(double),
                        class: string);

input: array(int)
output: string
cells:
  model(array(Distribution)) = []
action:
  var classLL = a.map(model, fcn(dist: Distribution -> double) {
    model.naive.multinomial(input, dist.logLikelihoods)
  });
  var norm = a.logsumexp(classLL);
  var index = a.argmax(a.map(classLL, fcn(x: double -> double) m.exp(x - norm)));
  model[index, "class"]
''')
```

## Producing a model

```python
model = [
    {"logLikelihoods": [0.05,     0.35,     0.2,      0.4],      "class": "A"},
    {"logLikelihoods": [0.444445, 0.444445, 0.055556, 0.055556], "class": "B"},
    {"logLikelihoods": [0.05,     0.05,     0.45,     0.45],     "class": "C"}
    ]
```

## Insert the model into PFA

```python
pfaDocument["cells"]["model"]["init"] = model
```

## Test it!

```python
engine, = PFAEngine.fromJson(pfaDocument)

data = [[0, 3, 0, 3],
        [0, 1, 2, 1],
        [1, 3, 2, 4],
        [4, 3, 1, 0],
        [4, 5, 0, 1],
        [1, 0, 5, 4],
        [0, 1, 4, 5]]
y = ["A", "A", "A", "B", "B", "C", "C"]

for i in range(len(data)):
    print "{0} vs {1}".format(engine.action(data[i]), y[i])
```
