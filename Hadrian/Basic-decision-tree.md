# Basic decision tree

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import csv
    >>> import math
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

And download the [Iris dataset](https://github.com/opendatagroup/hadrian/wiki/data/iris.csv).

## The basic form

The simplest algorithm for walking a decision tree is formed by combining `model.tree.simpleWalk` with `model.tree.simpleTest`. More complex variants are for non-binary trees, missing values, and compound predicates.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Input = record(Input,
                 sepal_length: double,
                 sepal_width: double,
                 petal_length: double,
                 petal_width: double);

  TreeNode = record(TreeNode,
                    field: enum([sepal_length, sepal_width, petal_length, petal_width]),
                    operator: string,
                    value: double,
                    pass: union(string, TreeNode),
                    fail: union(string, TreeNode))

input: Input
output: string
cells:
  // empty tree to satisfy type constraint; will be filled in later
  tree(TreeNode) = {field: "sepal_length", operator: "", value: 0.0, pass: {string: ""}, fail: {string: ""}}
action:
  model.tree.simpleWalk(input, tree, fcn(d: Input, t: TreeNode -> boolean) {
    model.tree.simpleTest(d, t)
  })
''')
```

## Producing a model

Titus has an implementation of CART in `titus.producer.cart` with many features (numerical and categorical splits, different impurity criteria, etc.), but we'll use a simple implementation here and reuse most of the code for the [random forest example](Basic-random-forest).

```python
class Datum(object):
    def __init__(self, sepal_length, sepal_width, petal_length, petal_width, truth):
        self.sepal_length = float(sepal_length)
        self.sepal_width = float(sepal_width)
        self.petal_length = float(petal_length)
        self.petal_width = float(petal_width)
        self.truth = truth.replace("Iris-", "")

def attemptSplit(field, data):
    bestGain = None
    bestSplit = None
    values = sorted(set(getattr(x, field) for x in data))
    splits = [(low + high)/2.0 for low, high in zip(values[:-1], values[1:])]
    for split in splits:
        gainPass = 0.0
        gainFail = 0.0
        for truth in "setosa", "versicolor", "virginica":
            numer = sum(x.truth == truth for x in data if getattr(x, field) < split)
            denom = sum(getattr(x, field) < split for x in data)
            if numer > 0.0:
                p = numer / float(denom)
                gainPass -= p * math.log(p, 2)
            numer = sum(x.truth == truth for x in data if getattr(x, field) >= split)
            denom = sum(getattr(x, field) >= split for x in data)
            if numer > 0.0:
                p = numer / float(denom)
                gainFail -= p * math.log(p, 2)
        gain = gainPass + gainFail
        if bestGain is None or gain > bestGain:
            bestGain = gain
            bestSplit = split
    return bestGain, bestSplit

def predominant(data):
    setosa = sum(x.truth == "setosa" for x in data)
    versicolor = sum(x.truth == "versicolor" for x in data)
    virginica = sum(x.truth == "virginica" for x in data)
    if setosa > versicolor and setosa > virginica:
        return "setosa"
    elif versicolor > setosa and versicolor > virginica:
        return "versicolor"
    else:
        return "virginica"

def ispure(data):
    setosa = sum(x.truth == "setosa" for x in data)
    versicolor = sum(x.truth == "versicolor" for x in data)
    virginica = sum(x.truth == "virginica" for x in data)
    if setosa == 0 and versicolor == 0:
        return True
    elif setosa == 0 and virginica == 0:
        return True
    elif versicolor == 0 and virginica == 0:
        return True
    else:
        return False

def makeTree(data):
    bestGain = None
    bestField = None
    bestSplit = None
    for field in "sepal_length", "sepal_width", "petal_length", "petal_width":
        gain, split = attemptSplit(field, data)
        if bestGain is None or gain > bestGain:
            bestGain = gain
            bestField = field
            bestSplit = split
    dataPass = [x for x in data if getattr(x, bestField) < bestSplit]
    dataFail = [x for x in data if getattr(x, bestField) >= bestSplit]
    if ispure(dataPass):
        branchPass = {"string": predominant(dataPass)}
    else:
        branchPass = makeTree(dataPass)
    if ispure(dataFail):
        branchFail = {"string": predominant(dataFail)}
    else:
        branchFail = makeTree(dataFail)
    return {"TreeNode": {"field": bestField,
                         "operator": "<",
                         "value": bestSplit,
                         "pass": branchPass,
                         "fail": branchFail}}

iris = csv.reader(open("iris.csv"))
iris.next()
dataset = [Datum(*x) for x in iris]

tree = makeTree(dataset)["TreeNode"]
```

The only thing here that depends on PFA is the form of the return value of the `makeTree` function.

## Insert the model into PFA

This tree is already correctly formatted for PFA, so just attach it.

```python
pfaDocument["cells"]["tree"]["init"] = tree
```

## Test it!

The tree-building algorithm above has no pruning and continues until all leaves are pure. Hence, it correctly labels 100% of the training dataset (because it's overtuned). Compare this with the [ruleset example](Basic-ruleset) (95%) and the [random forest example](Basic-random-forest) (typically 95%).

```python
engine, = PFAEngine.fromJson(pfaDocument)

iris = csv.reader(open("iris.csv"))
iris.next()

numer = 0
denom = 0
for sepal_length, sepal_width, petal_length, petal_width, truth in iris:
    result = engine.action({"sepal_length": sepal_length, "sepal_width": sepal_width, "petal_length": petal_length, "petal_width": petal_width})
    print result, "vs", truth.replace("Iris-", "")
    if result != truth.replace("Iris-", ""):
        numer += 1
    denom += 1

print "Fraction mislabeled:", float(numer) / float(denom)
```
