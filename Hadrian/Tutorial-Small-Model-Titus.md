# Tutorial 1: small model in Titus (Python)

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `PFAEngine` to verify the installation:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from titus.genpy import PFAEngine

Also download the [Iris dataset](https://github.com/opendatagroup/hadrian/wiki/data/iris.csv).

## Small model

To get started, let's assume you have some extremely simple model to convert to PFA. Usually, models are built algorithmically, but building one manually will help us focus on the core functionality. Model building algorithms are diverse and specialized.

Suppose, for instance, that you want to convert this decision tree to PFA:

<center>
<img src="https://github.com/opendatagroup/hadrian/wiki/images/IrisDataDecisionTreeDepth3.png" vspace="20">
</center>

and score it with the Iris dataset. There are several ways we can do this:

   1. express the decision tree splits as PFA code (if-statements);
   2. express the decision tree splits as model data and write PFA code to walk over that model data;
   3. express the decision tree splits as a PFA tree, such that the tree-walking library functions recognize them and know how to walk over them.

Usually, we would only consider the third option, but the progression illustrates some basic facts about PFA.

## Model as code

This method is like hard-coding a model in a traditional programming language: we'll be writing code like the following.

```C
if (petal_length_cm < 2.5)
    return "setosa";
else if (petal_length_cm < 4.8)
    return "versicolor";
else if (petal_width_cm < 1.7)
    return "versicolor";
else
    return "virginica";
```

Unlike the C syntax above, PFA is entirely expressed in JSON. Below is an example of how to do that with Titus on a Python prompt. The if-statements are in the "action" section; the "input" and "output" define the form of the data that this scoring engine expects and produces. (The format for declaring PFA data types is exactly the same as [Avro](https://avro.apache.org/docs/1.7.7/spec.html), a well-known serialization library that declares schemas in JSON.)

```python
pfaDocument = {
    "input": {"type": "record",
              "name": "Iris",
              "fields": [
                  {"name": "sepal_length_cm", "type": "double"},
                  {"name": "sepal_width_cm", "type": "double"},
                  {"name": "petal_length_cm", "type": "double"},
                  {"name": "petal_width_cm", "type": "double"},
                  {"name": "class", "type": "string"}
              ]},
    "output": "string",
    "action": [
        {"if": {"<": ["input.petal_length_cm", 2.5]},
         "then": {"string": "Iris-setosa"},
         "else":
             {"if": {"<": ["input.petal_length_cm", 4.8]},
              "then": {"string": "Iris-versicolor"},
              "else":
                  {"if": {"<": ["input.petal_width_cm", 1.7]},
                  "then": {"string": "Iris-versicolor"},
                  "else": {"string": "Iris-virginica"}}
             }
        }
    ]}
engine, = PFAEngine.fromJson(pfaDocument)
```

Be careful to include a comma (`,`) after the word `engine`. This is to unpack the list of scoring engines that `PFAEngine.fromJson` returns: you may ask for a collection of scoring engines with `multiplicity=N` and the function always returns a list for consistency. The comma is a convenient way of [unpacking a singleton list in Python](http://stackoverflow.com/a/303697/1623645).

If this function returns without error, then the PFA is valid and the engine was built. You can execute the engine like this:

```python
engine.action({"sepal_length_cm": 5.1, "sepal_width_cm": 3.5,
               "petal_length_cm": 1.4, "petal_width_cm": 0.2,
               "class": "Iris-setosa"})
```

and like this:

```python
import csv

dataset = csv.reader(open("iris.csv"))
fields = dataset.next()

numCorrect = 0.0
numTotal = 0.0
for datum in dataset:
    asRecord = dict(zip(fields, datum))
    if engine.action(asRecord) == asRecord["class"]:
        numCorrect += 1.0
    numTotal += 1.0

print "accuracy", numCorrect/numTotal
```

A JSON-based syntax is not particularly easy to write by hand, but it is more convenient to generate automatically. This is important because most data mining models are built by programs, not by hand. Below is an example of randomly generating an if-statement tree:

```python
import random

classes = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]
fields = ["sepal_length_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"]

def makeTree(depth):
    if depth == 0:
        return {"string": random.choice(classes)}
    else:
        field = random.choice(fields)
        split = abs(random.gauss(3.46, 1.97))
        return {"if": {"<": ["input." + field, split]},
                "then": makeTree(depth - 1),
                "else": makeTree(depth - 1)}

pfaDocument["action"] = makeTree(5)
engine, = PFAEngine.fromJson(pfaDocument)
```

Most of the above code is choosing the fields and split points; the PFA is built by making a Python dictionary with three keys: `"if"`, `"then"`, and `"else"`. If you were generating C code, you'd have to worry about generating parentheses, curly brackets, and semicolons, and the script would be easily broken by future changes.

But not everything is built algorithmically; some parts of a PFA document, such as pre- and post-processing, are usually written by hand. For these parts, there are compilers that turn human-readable code into PFA. The most useful have been R-to-PFA (in Aurelius) and PrettyPFA (in Titus). Below is an example of building the small model in PrettyPFA.

```python
import titus.prettypfa

pfaDocument = titus.prettypfa.jsonNode('''
input: record(sepal_length_cm: double,
              sepal_width_cm: double,
              petal_length_cm: double,
              petal_width_cm: double)
output: string
action:
  if (input.petal_length_cm < 2.5)
    "Iris-setosa"
  else if (input.petal_length_cm < 4.8)
    "Iris-versicolor"
  else if (input.petal_width_cm < 1.7)
    "Iris-versicolor"
  else
    "Iris-virginica"
''')
engine, = PFAEngine.fromJson(pfaDocument)
```

It still has the main "input," "output," "action" structure of a PFA document, but the data types are more simply expressed and the code looks like C. Fairly complex PFA models have been built this way, combining human-readable programming with automated metaprogramming to gain from the advantages of each.

However, there's still one thing wrong with our example: the model is expressed as code, which mixes procedural algorithms ("if not this, then that, or that...") and declarative model parameters ("cut petal length at 2.5, petal width at 1.7..."). In real cases, we move model parameters to their own section for flexibility and scalability.

## Model as data

Imagine trying to express a large decision tree as if-statements, or worse yet, a random forest: the code section would become very large. That's not a problem for code generation because we can use our `makeTree` function to generate arbitrarily large trees, but it is a problem for compiling it as bytecode. Some compilers would take too long or use too much memory to compile a huge code block; others (like Java) have built-in limitations on the size of the code block (64 kilobytes). Adding pre- or post-processing code around the large block would be cumbersome. And finally, the model would be immutable because PFA code is not allowed to modify itself (for security reasons).

The solution to this is to put the declarative model data in a non-code section of the PFA. In practice, this section is usually the largest: a typical PFA file has one or two lines of code and gigabytes of model data. Below is an example for our small model.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: record(sepal_length_cm: double,
              sepal_width_cm: double,
              petal_length_cm: double,
              petal_width_cm: double)
output: string
types:
  Rules = array(record(field: string,
                       cut: double,
                       result: string))
cells:
  rules(Rules) = [
    {field: "petal_length_cm", cut: 2.5, result: "Iris-setosa"},
    {field: "petal_length_cm", cut: 4.8, result: "Iris-versicolor"},
    {field: "petal_width_cm", cut: 1.7, result: "Iris-versicolor"},
    {field: "none", cut: -1, result: "Iris-virginica"}
  ]

action:
  var result = "";

  for (index = 0; result == ""; index = index + 1) {
    var rule = rules[index];

    var fieldValue =
      if (rule.field == "sepal_length_cm") input.sepal_length_cm
      else if (rule.field == "sepal_width_cm") input.sepal_width_cm
      else if (rule.field == "petal_length_cm") input.petal_length_cm
      else if (rule.field == "petal_width_cm") input.petal_width_cm
      else -1.0;

    if (rule.field == "none"  ||  fieldValue < rule.cut)
      result = rule.result;
  };

  result
''')
engine, = PFAEngine.fromJson(pfaDocument)
```

All of the information about which fields to split on and what cut points to use are in a JSON data structure called "rules". Like everything in PFA, the rules have a well-defined data type: an array (ordered sequence) of records (objects) with a "field" (string), "cut" (double), and a "result" (string). The code walks over this structure to interpret and apply these rules, but all of the choices are stored in the declarative structure.

Typically, one would write a PrettyPFA "skeleton" that has all of the human-authored code and an empty spot where the model parameters would go, then fill it up algorithmically. For instance, if we had set

```
  rules(Rules) = []
```

above, we could fill it with Python code like the following.

```python
pfaDocument["cells"]["rules"]["init"] = [
    {"field": "petal_length_cm", "cut": 2.5, "result": "Iris-setosa"},
    {"field": "petal_length_cm", "cut": 4.8, "result": "Iris-versicolor"},
    {"field": "petal_width_cm", "cut": 1.7, "result": "Iris-versicolor"},
    {"field": "none", "cut": -1, "result": "Iris-virginica"}
  ]
```

Another feature of model data is that it is mutable. Anything in the "cells" (global variables) section or "pools" (global environments or namespaces) section can be changed at runtime with PFA code. This makes the same section useful for intermediate values, such as moving windows, moving averages, and cumulative sums. PFA makes no distinctions between "model parameters" and "intermediate values," what they mean is determined entirely by how you use them.

At this point, PFA is beginning to look like a general purpose programming language, but it is curtailed in specific ways to aid in statistical modeling.

   * _All_ persistent state is confined to the "cells" and "pools" sections.
   * _All_ data, including model parameters and intermediate values like moving windows are rigorously typed and replaceable but not in-place mutable.
   * The functions available for programming are limited to those that perform calculations; they cannot manipulate the larger system, including the data stream. (Data must be fed into a PFA model, as in the Python for-loop examples above.)

It is better to think of PFA as a domain specific mini-language focused on data transformations. PFA by itself is unrestrictive, but whenever you encode a specific model in it, the data types you define make it restrictive. That is, the JSON that you insert into a cell or pool has to satisfy the form that you specify, and the code is type-checked to ensure that it can work with anything of that form.

The example given above was simplified for pedagogical reasons; a more realistic version might look like the following:

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Input = record(sepal_length_cm: double,
                 sepal_width_cm: double,
                 petal_length_cm: double,
                 petal_width_cm: double);

  Output = string;

  Rule = union(record(Decision,
                      field: enum([slen, swid, plen, pwid], Fields),
                      cut: double,
                      result: Output),
               Output);

input: Input
output: Output
cells:
  rules(array(Rule)) = [
    {Decision: {field: plen, cut: 2.5, result: "Iris-setosa"}},
    {Decision: {field: plen, cut: 4.8, result: "Iris-versicolor"}},
    {Decision: {field: pwid, cut: 1.7, result: "Iris-versicolor"}},
    {string: "Iris-virginica"}
  ]

action:
  var result = "";

  for (index = 0; result == ""; index = index + 1)
    cast(rules[index]) {
      as(decision: Decision) {
        var fieldValue =
          if (decision.field == Fields@slen) input.sepal_length_cm
          else if (decision.field == Fields@swid) input.sepal_width_cm
          else if (decision.field == Fields@plen) input.petal_length_cm
          else input.petal_width_cm;

        if (fieldValue < decision.cut)
          result = decision.result;
      }

      as(output: Output) {
        result = output;
      }
    };

  result
''')
engine, = PFAEngine.fromJson(pfaDocument)
```

Here, the `Output` type is declared in one place, so that it can be replaced and changes propagate through PFA's type inference. A `Rule` has two cases that was kludged by `{field: "none", cut: -1, result: "Iris-virginica"}` the first time but is better handled here: it is a union of a `Decision` type and an `Output` type (data values can be either of these two). The `field` is an enumeration to ensure that unhandled values are never allowed. The PFA code has to handle both cases of the union: it does so using a `cast-as` structure, which ensures that a variable can never be incorrectly cast. (This is equivalent to type-safe pattern matching, and the same mechanism is used to handle missing data.)

But now that we've seen some of PFA's generality, you may be thinking, "I just want to score a standard tree model. Do I really have to write the program myself?" The answer is "No."

## Model in a library call

PFA has hundreds of functions for handling typical statistical calculations, and these calls are factorized into small pieces so that they can be interchanged in a variety of ways. The "action" section for a typical PFA file contains one or two lines of code (depending on how many pre- and post-processing steps there are).

You can search for relevant functions using the [scoringengine.org function library page](http://scoringengine.org/docs/library/) or by leafing through the [PFA specification (PDF)](http://github.com/scoringengine/pfa/blob/master/pfa-specification.pdf?raw=true).

Decision trees are handled by functions in the `model.tree.*` library; our tutorial example boils down to the PFA code below.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Input = record(sepal_length_cm: double,
                 sepal_width_cm: double,
                 petal_length_cm: double,
                 petal_width_cm: double);

  Output = string;

  TreeNode = record(TreeNode,
                    field: enum([sepal_length_cm, sepal_width_cm,
                                 petal_length_cm, petal_width_cm]),
                    operator: string,
                    value: double,
                    pass: union(TreeNode, Output),
                    fail: union(TreeNode, Output))

input: Input
output: Output
cells:
  tree(TreeNode) =
    {field: "petal_length_cm",
     operator: "<",
     value: 2.5,
     pass: {string: "Iris-setosa"},
     fail: {TreeNode:
       {field: "petal_length_cm",
        operator: "<",
        value: 4.8,
        pass: {string: "Iris-versicolor"},
        fail: {TreeNode:
          {field: "petal_width_cm",
           operator: "<",
           value: 1.7,
           pass: {string: "Iris-versicolor"},
           fail: {string: "Iris-virginica"}
          }}
       }}
    }

action:
  model.tree.simpleWalk(input, tree, fcn(d: Input, t: TreeNode -> boolean) {
    model.tree.simpleTest(d, t)
  })
''')
engine, = PFAEngine.fromJson(pfaDocument)
```

The rules are encoded in a data structure with specific field names: "field" (enum), "operator" (string), "value" (double), "pass" (another `TreeNode` or the `Output`), and "fail" (another `TreeNode` or the `Output`). The use of unions allows us to build a finite tree: every walk through the tree is guaranteed to end on some `Output`.

The code is a one-line expression (expanded to three lines for clarity) involving two library functions:

   * `model.tree.simpleWalk` is an algorithm for walking down a tree by repeatedly applying a test function at each node. If the test function yields `true`, it follows the "pass" branch, and if the test function yields `false`, it follows the "fail" branch. This function requires our data structure to have "pass" and "fail" fields, but it does not preclude additional fields.
   * `model.tree.simpleTest` is an algorithm for testing a tree node. It requires our data structure to have "field", "operator", and "value" branches, but does not preclude additional fields.

To use these two functions together, we need a data structure with all five fields. If you want, you can add additional fields, either to store metadata from the model-building phase (e.g. partial scores at each tree node) or to use them in the scoring process (e.g. returning a partial score if a field value is missing). You could put linear regressions or other models on the leaves if you wish: they don't have to be strings. (In fact, a regression tree would require numerical leaves, and a multivariate regression tree would require arrays of numbers at each leaf.)

You could replace the `model.tree.simpleTest` with a `model.tree.compoundTest`, a `model.tree.surrogateTest`, or a user-defined function. You could replace the `model.tree.simpleWalk` with a `model.tree.missingWalk` or a user-defined function. Complexity is opt-in.

## Next steps

Naturally, this flexibility can be bewildering: where should you start? How would you know that a `model.tree.simpleWalk` and a `model.tree.simpleTest` should be glued together like the above to produce a standard decision tree? To answer these questions, we provide a "Basic models" section on the Hadrian wiki. Most of the standard models that might be covered in a data mining course are demonstrated there, using Titus and PrettyPFA.

If, on the other hand, you're interested in building models with Aurelius in R (without delving into their internals) or productionalizing them with Hadrian on the JVM, see the second and third tutorials.
