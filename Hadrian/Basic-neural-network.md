# Basic neural network

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## The basic form

The `model.neural.simpleLayers` function assumes that the topology of the neural network is arranged in layers. We chose the `m.link.logit` activation function from the link function library.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Layer = record(Layer,
                 weights: array(array(double)),
                 bias: array(double))

input: array(double)
output: double
cells:
  neuralnet(array(Layer)) = []
action:
  var activation = model.neural.simpleLayers(input, neuralnet, fcn(x: double -> double) m.link.logit(x));
  m.link.logit(activation[0])
''')
```

## Producing a model

The model parameters for a layered neural network is just a set of transition matricies and bias vectors.

```python
neuralnet = [{"weights": [[ -6.0, -8.0],
                          [-25.0, -30.0]], "bias": [4.0, 50.0]},
             {"weights": [[-12.0, 30.0]], "bias": [-25.0]}]
```

## Insert the model into PFA

```python
pfaDocument["cells"]["neuralnet"]["init"] = neuralnet
```

## Test it!

```python
engine, = PFAEngine.fromJson(pfaDocument)

data_xor = [[0, 0],
            [1, 0],
            [0, 1],
            [1, 1]]
y = [0.0,
     1.0,
     1.0,
     0.0]

for i in range(4):
    print "{0:.3f} vs {1}".format(engine.action(data_xor[i]), y[i])
```
