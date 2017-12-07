# Basic association rules

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import random
    >>> import json
    >>> from collections import Counter
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## The basic form

PFA has no dedicated library for [association rules](https://en.wikipedia.org/wiki/Association_rule_learning) because the scoring procedure is easy to express in terms of functional primitives. If you're building an association rule model with many rules, be sure to make the antecedent a map-lookup (constant time) rather than a loop through an array of rules (linear time).

Map keys in PFA are always strings (a restriction inherited from Avro and JSON), so you'll need a way to project your sets of antecedent items onto a string. Use `a.sort` to remove dependency on item order and `s.join` to make one string with a `DELIMITER` that is not in your item's alphabet. Then it simply becomes a matter of looking up a value in a map.

```python
DELIMITER = " - "

pfaDocument = titus.prettypfa.jsonNode('''
types:
  Item = string;
  Rule = record(Rule,
                consequent: array(Item),
                confidence: double)

input: array(Item)
output: Rule
cells:
  rules(map(Rule)) = {}
action:
  ifnotnull(rule: try rules[s.join(a.sort(input), <<DELIMITER>>)])
    rule
  else
    json(Rule, {consequent: [], confidence: 0.0})
''', DELIMITER = {"string": DELIMITER})
```

The French quotes (`<<` and `>>`) are a mechanism for inserting simple values into a PrettyPFA document. The values you insert have to be raw PFA (hence `{"string": " - "}` rather than just `" - "`).

## Producing a model

Like most models, association rules are much easier to score than to produce. You can use any tool to produce them as long as you make a JSON structure adhering to your chosen `Rule` declaration above. For the sake of providing a complete example, here's a simple association rule producer in Python.

```python
items = ["milk", "bread", "butter", "beer", "diapers"]
transactions = [random.sample(items, random.randint(1, len(items))) for x in xrange(10000)]

def pairsOfSubsets(transaction):
    for binary in xrange(2**0, 2**len(transaction) - 1):
        yield [transaction[i] for i in xrange(len(transaction)) if binary & 2**i != 0], \
              [transaction[i] for i in xrange(len(transaction)) if binary & 2**i == 0]

def makeHashable(set):
    return DELIMITER.join(sorted(set))

supports = Counter()
for transaction in transactions:
    for antecedent, consequent in pairsOfSubsets(transaction):
        supports[makeHashable(antecedent)] += 1
        supports[makeHashable(consequent)] += 1
    supports[makeHashable(transaction)] += 1

rules = {}
for transaction in transactions:
    numer = float(supports[makeHashable(transaction)])
    for antecedent, consequent in pairsOfSubsets(transaction):
        confidence = numer / supports[makeHashable(consequent)]
        rules[makeHashable(antecedent)] = {"consequent": consequent, "confidence": confidence}
```

## Insert the model into PFA

These rules already have the right structure for our `Rule` type, so we can just insert them into the PFA. We'll find out if it was the right structure when we try to make an engine out of it.

```python
pfaDocument["cells"]["rules"]["init"] = rules
```

## Test it!

```python
engine, = PFAEngine.fromJson(pfaDocument)

for transaction in transactions:
    for antecedent, consequent in pairsOfSubsets(transaction):
        print "{0:50s} -> {1}".format(json.dumps(antecedent), json.dumps(engine.action(antecedent)))

```
