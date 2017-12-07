# Basic random forest

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import random
    >>> import csv
    >>> import math
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

And download the [Iris dataset](https://github.com/opendatagroup/hadrian/wiki/data/iris.csv).

## The basic form

Scoring a random forest involves scoring every tree and reporting the most frequent result (`a.mode` for the majority vote). The tree-scoring process is identical to the [decision tree example](Basic-decision-tree) It's also common to report the fraction of trees that gave each class of score (use `a.count` and `a.len` to compute a fraction).

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
  forest(array(TreeNode)) = []
action:
  var scores = a.map(forest, fcn(tree: TreeNode -> string) {
    model.tree.simpleWalk(input, tree, fcn(d: Input, t: TreeNode -> boolean) {
      model.tree.simpleTest(d, t)
    })
  });
  a.mode(scores)    // majority vote
''')
```

## Producing a model

The following code is a literal copy of the decision tree builder with tweaks to turn it into a random forest. The CART decision tree algorithm optimizes its choice of field to split on and the cut point; random forests randomize the choice of field and optimize the cut point for that field. They also stop building after a certain depth (to make an ensemble of weak classifiers).

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
    if bestGain is None:
        return 0.0, 0.0
    else:
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

def makeTree(data, depth):
    field = random.choice(["sepal_length", "sepal_width", "petal_length", "petal_width"])
    gain, split = attemptSplit(field, data)
    dataPass = [x for x in data if getattr(x, field) < split]
    dataFail = [x for x in data if getattr(x, field) >= split]
    if depth == 0:
        branchPass = {"string": predominant(dataPass)}
        branchFail = {"string": predominant(dataFail)}
    else:
        branchPass = makeTree(dataPass, depth - 1)
        branchFail = makeTree(dataFail, depth - 1)
    return {"TreeNode": {"field": field,
                         "operator": "<",
                         "value": split,
                         "pass": branchPass,
                         "fail": branchFail}}

iris = csv.reader(open("iris.csv"))
iris.next()
dataset = [Datum(*x) for x in iris]

forest = [makeTree(dataset, 5)["TreeNode"] for x in xrange(100)]
```

## Insert the model into PFA

Just as with the [decision tree example](Basic-decision-tree), the trees are already formatted for PFA.

```python
pfaDocument["cells"]["forest"]["init"] = forest
```

## Test it!

Depending on how your random number generator is seeded, this forest correctly identifies about 95% of the Iris dataset. Compare with the [ruleset example](Basic-ruleset) (95%) and overtrained [decision tree example](Basic-decision-tree) (100%).

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
