## Before you begin...

[Download and install Aurelius](Installation#case-5-you-want-to-use-aurelius-in-r).  This article was tested with Aurelius 0.8.3; newer versions should work with no modification.  R >= 3.0.1 is required.

Launch an R prompt and load the `aurelius` library:

    R version 3.0.1 (2013-05-16) -- "Good Sport"
    Copyright (C) 2013 The R Foundation for Statistical Computing
    Platform: x86_64-pc-linux-gnu (64-bit)

    R is free software and comes with ABSOLUTELY NO WARRANTY.
    You are welcome to redistribute it under certain conditions.
    Type 'license()' or 'licence()' for distribution details.

      Natural language support but running in an English locale

    R is a collaborative project with many contributors.
    Type 'contributors()' for more information and
    'citation()' on how to cite R or R packages in publications.

    Type 'demo()' for some demos, 'help()' for on-line help, or
    'help.start()' for an HTML browser interface to help.
    Type 'q()' to quit R.

    > library(aurelius)
    >

## Converting a randomForest model to PFA

The [randomForest](https://cran.r-project.org/web/packages/randomForest/index.html) library for random forest models usually isn't packaged with an R distribution, but it is available on CRAN. This page assumes that you are not only familiar with the randomForest package, but have already created and fine-tuned your linear model, having produced a `forestObject` of class `"randomForest"`.

Conversion to PFA proceeds in three steps:

   1. Extract parameters from the `forestObject`.
   2. Format them as an R list-of-lists that is equivalent to a data structure in PFA.
   3. Create the PFA document, including the line of PFA code that evaluates the linear model.

These steps are not combined into one function call to allow for variations in how the model is invoked, including preprocessing, postprocessing, and attaching additional information to the linear fit object.

### Step 1: extract parameters

Tree structures in PFA differ, depending on whether the splits are all numerical or if some are categorical (levels in R). The comparison value at each tree node needs to have a data type that can encompass all possible splits, so if the predictors are all numerical, it can be `avro.double`, if they are all categorical, it can be `avro.string`, but if they're both, it must be `avro.union(avro.double, avro.string)`.

Furthermore, the randomForest library summarizes the level data very succinctly, while PFA represents them by their string values. You need to make a lookup table. For each categorical feature in your tree, create an ordered list of levels and put all of these in one named list, where the names are feature names. For instance,

```R
dataLevels <- list(field1 = list("value1", "value2", "value3"),
                   field2 = list("val1", "val2", "val3", "val4", "val5"),
                   ...)
```

You may be able to automate this from the level data in R.

Now you can extract the `forestObject` into a list-of-lists. Use `labelVar = TRUE` if the comparison value is a union (mixed numerical and categorical regressors), `labelVar = FALSE` if it is not (all numerical or all categorical).

```R
forest <- list()
for (i in 1:forestObject$nTree) {
    treeTable <- pfa.randomForest.extractTree(forestObject, i, labelVar = TRUE)
    cat(paste("tree", i, "has", length(treeTable$status), "nodes\n"))
    forest[[length(forest) + 1]] <-
        pfa.randomForest.buildOneTree(treeTable, 1, labelVar, dataLevels,
            lapply(dataLevels, function (v) avro.string))$TreeNode
}
```

where the `cat` line is to track progress.

### Step 2: format for PFA

Assuming that the input schema contains the tree fields and nothing else (no preprocessing), build the input schema like the following.

```R
fieldNames <- as.list(forestObject$xNames)
fieldTypes <- rep(avro.double, length(fieldNames))
names(fieldTypes) <- fieldNames
for (n in names(dataLevels))
    fieldTypes[[n]] <- avro.string

inputSchema <- avro.record(fieldTypes, "Input")
```

If any of your field names contain dots (`.`), you'll have to convert them to underscores or something (Avro field names accept alphanumeric and underscores).

The `pfa.randomForest.buildOneTree` function above formats each tree from the forest in a PFA list-of-lists, and it's more convenient to leave that transformation in the same loop with the extraction.

### Step 3: construct the PFA

It is good practice to use an `avro.typemap` to ensure that named types are declared only once in the output PFA.

If the trees in the forest are decision trees (categorical decisions), the `Output` type should be `avro.string` and the score type (unioned with `"TreeNode"` in `pass` and `fail`), should also be `avro.string`. If they are regression trees, the `Output` and score types should be `avro.double`.

If the tree splits are purely numeric, the value is `avro.double`; if purely categorical, the value is `avro.string`; if any splits include subset comparisons (e.g. field value is X, Y, or Z), then the value is `avro.array(avro.string)`. If it is any combination of these, take the appropriate union. A wide union consisting of all three is safe.

```R
tm <- avro.typemap(
    Input = inputSchema,
    Output = avro.string,
    TreeNode = avro.record(list(
        field    = avro.enum(fieldNames),
        operator = avro.string,
        value    = avro.union(avro.double, avro.string, avro.array(avro.string)),
        pass     = avro.union("TreeNode", avro.string),
        fail     = avro.union("TreeNode", avro.string)),
        "TreeNode"))
```

The following PFA document applies standard tree-scoring to each tree in the forest and reports the majority vote.

```R
pfaDocument <- pfa.config(
    input = tm("Input"),
    output = tm("Output"),
    cells = list(forest =
        pfa.cell(avro.array(tm("TreeNode")), forest)),
    action = expression(
        treeScores <- a.map(forest,
            function(tree = tm("TreeNode") -> avro.string)
                model.tree.simpleTree(input, tree)),
        a.mode(treeScores)
        ))
```

If, instead of reporting the most popular score, you want to report the fraction that score a particular way, you could use this PFA document instead.

```R
pfaDocument <- pfa.config(
    input = tm("Input"),
    output = avro.double,
    cells = list(forest =
        pfa.cell(avro.array(tm("TreeNode")), forest)),
    action = expression(
        treeScores <- a.map(forest,
            function(tree = tm("TreeNode") -> avro.string)
                model.tree.simpleTree(input, tree)),
        a.count(treeScores, "favoriteScore") / a.len(treeScores)
        ))
```

Or maybe you want to output a map of counts for each output category, use something like this.

```R
pfaDocument <- pfa.config(
    input = tm("Input"),
    output = avro.map(avro.double),
    cells = list(forest =
        pfa.cell(avro.array(tm("TreeNode")), forest)),
    action = expression(
        treeScores <- a.map(forest,
            function(tree = tm("TreeNode") -> avro.string)
                model.tree.simpleTree(input, tree)),
        new(avro.map(avro.double),
            score1 = a.count(treeScores, "score1") / a.len(treeScores),
            score2 = a.count(treeScores, "score2") / a.len(treeScores),
            score3 = a.count(treeScores, "score3") / a.len(treeScores))
        ))
```

For many possible scores, the latter could be automated.

The tree-scoring process can also be expanded for more functionality. Consider, for instance,

```R
pfaDocument <- pfa.config(
    input = tm("Input"),
    output = tm("Output"),
    cells = list(forest =
        pfa.cell(avro.array(tm("TreeNode")), forest)),
    action = expression(
        treeScores <- a.map(forest,
            function(tree = tm("TreeNode") -> avro.string)
                model.tree.simpleWalk(input, tree,
                    function(d = tm("Input"), t = tm("TreeNode") -> avro.boolean)
                        model.tree.simpleTest(d, t)
            )),
        a.mode(treeScores)
        ))
```

where the `model.tree.simpleTree` function has been expanded into two parts, `model.tree.simpleWalk` and `model.tree.simpleTest`. The `model.tree.simpleTest` function decides how to evaluate each tree node as "pass" or "fail" and the `model.tree.simpleWalk` function repeatedly applies it from tree root to tree leaf. Multi-branch trees or trees with missing values can be evaluated by swapping one or both functions for alternatives from the [`model.tree`](http://dmg.org/pfa/docs/library/#lib:model.tree) library.

To write the PFA to a file, use

```R
json(pfaDocument, fileName = "mymodel.pfa")
```

## Testing

If you have Titus and rPython installed (see [installation page](Installation#case-5-you-want-to-use-aurelius-in-r)), you can test the scoring engine without leaving R.

```R
engine <- pfa.engine(pfaDocument)    # verifies that pfaDocument is internally consistent

engine$action(list(field1 = 3.14, field2 = "hello"))
```

where `field1`, `field2`, etc. are named fields.