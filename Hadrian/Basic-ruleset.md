# Basic ruleset

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.2; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import csv
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

And download the [Iris dataset](https://github.com/opendatagroup/hadrian/wiki/data/iris.csv).

## The basic form

Rulesets are not fundamentally different from decision trees, but they're usually not as deeply nested (often, they're only one level of hierarchy) and they're usually made by hand. Here's an example of a ruleset evaluated using half of the tree-scoring suite (tests with no walking).

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Input = record(Input,
                 sepal_length: double,
                 sepal_width: double,
                 petal_length: double,
                 petal_width: double);

  Comparison = record(Comparison,
                      field: enum([sepal_length, sepal_width, petal_length, petal_width]),
                      operator: string,
                      value: double);

  Rule = record(Rule,
                comparisons: array(Comparison),
                result: string)

input: Input
output: union(null, string)
cells:
  ruleset(array(Rule)) = []
action:
  var index = a.index(ruleset, fcn(rule: Rule -> boolean) {
    model.tree.compoundTest(input, "and", rule["comparisons"],
      fcn(d: Input, t: Comparison -> boolean) model.tree.simpleTest(d, t))
  });

  if (index == -1)   // it is possible to fail all rules
    null
  else
    ruleset[index, "result"]
''')
```

## Insert a model into PFA

For a model, I'll use the same four rules as [Tutorial 1](Tutorial-Small-Model-Titus).

```python
pfaDocument["cells"]["ruleset"]["init"] = [
    {"comparisons": [{"field": "petal_length", "operator": "<", "value": 2.5}], "result": "setosa"},
    {"comparisons": [{"field": "petal_length", "operator": ">=", "value": 2.5},
                     {"field": "petal_length", "operator": "<", "value": 4.8}], "result": "versicolor"},
    {"comparisons": [{"field": "petal_length", "operator": ">=", "value": 4.8},
                     {"field": "petal_width", "operator": "<", "value": 1.7}], "result": "versicolor"},
    {"comparisons": [{"field": "petal_length", "operator": ">=", "value": 4.8},
                     {"field": "petal_width", "operator": ">=", "value": 1.7}], "result": "virginica"}
    ]
```

## Test it!

These four rules correctly label 95% of the Iris dataset. Compare to the (overtrained) [decision tree example](Basic-decision-tree) (100%) and the [random forest example](Basic-random-forest) (typically 95%).

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
