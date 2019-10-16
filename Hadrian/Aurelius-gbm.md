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

The [gbm](https://cran.r-project.org/web/packages/gbm/index.html) library for generalized boosted regression models usually isn't packaged with an R distribution, but it is available on CRAN. This page assumes that you are not only familiar with the gbm package, but have already created and fine-tuned your linear model, having produced a `forestObject` of class `"gbm"`.

Conversion to PFA proceeds in three steps:

   1. Extract parameters from the `forestObject`.
   2. Format them as an R list-of-lists that is equivalent to a data structure in PFA.
   3. Create the PFA document, including the line of PFA code that evaluates the linear model.

These steps are not combined into one function call to allow for variations in how the model is invoked, including preprocessing, postprocessing, and attaching additional information to the linear fit object.

### Step 1: extract parameters

The following assumes that all splits in the tree are numerical and the trees each produce a numerical result (regression).

```R
forest <- list()
for (i in 1:forestObject$numTrees) {
    tree <- pfa.gbm.extractTree(forestObject, i)
    cat(paste("tree", i, "\n"))
    forest[[length(forest) + 1]] <-
        pfa.gbm.buildOneTree(tree$treeTable, tree$categoricalLookup, 1, labelVar)$TreeNode
}
intercept <- forestObject$initF
```

where the `cat` line is to track progress.

### Step 2: format for PFA

Assuming that the input schema contains the tree fields and nothing else (no preprocessing), build the input schema like the following. The gbm library assumes that predictors can be missing, so the input schema accepts field values as nullable (`avro.union(avro.null, avro.double)`). If you know that your field values are never missing, the transformation from numbers to nullable numbers can easily be done in preprocessing (e.g. by simply wrapping each value with `try`).

```R
fieldNames <- as.list(forestObject$var.names)
fieldTypes <- rep(avro.union(avro.null, avro.double), length(fieldNames))
names(fieldTypes) <- fieldNames

inputSchema <- avro.record(fieldTypes, "Input")
```

If any of your field names contain dots (`.`), you'll have to convert them to underscores or something (Avro field names accept alphanumeric and underscores).

The `pfa.gbm.buildOneTree` function above formats each tree from the forest in a PFA list-of-lists, and it's more convenient to leave that transformation in the same loop with the extraction.

### Step 3: construct the PFA

It is good practice to use an `avro.typemap` to ensure that named types are declared only once in the output PFA.

```R
tm <- avro.typemap(
    Input = inputSchema,
    Output = avro.double,
    TreeNode = avro.record(list(
        field    = avro.enum(fieldNames),
        operator = avro.string,
        value    = avro.double,
        pass     = avro.union("TreeNode", avro.string),
        fail     = avro.union("TreeNode", avro.string)),
        missing  = avro.union("TreeNode", avro.string)),
        "TreeNode"))
```

The following PFA document applies standard tree-scoring and adds each tree's result to the intercept to get a final result.

```R
pfaDocument <- pfa.config(
    input = tm("Input"),
    output = tm("Output"),
    cells = list(forest =
        pfa.cell(avro.array(tm("TreeNode")), forest)),
    action = expression(
        treeScores <- a.map(forest,
            function(tree = tm("TreeNode") -> avro.double)
                model.tree.missingWalk(input, tree,
                    function(d = tm("Input"), t = tm("TreeNode") -> avro.union(avro.null, avro.boolean))
                        model.tree.missingTest(d, t)
            )),
        intercept + a.sum(treeScores)
        ))
```

Depending on your application, you may want to wrap the last line in [a link function](http://dmg.org/pfa/docs/library/#lib:m.link) like `m.link.logit` or its complement.

To write the PFA to a file, use

```R
json(pfaDocument, fileName = "mymodel.pfa")
```

## Testing

If you have Titus and rPython installed (see [installation page](Installation#case-5-you-want-to-use-aurelius-in-r)), you can test the scoring engine without leaving R.

```R
engine <- pfa.engine(pfaDocument)    # verifies that pfaDocument is internally consistent

engine$action(list(field1 = list(double = 3.14), field2 = NULL))
```

where `field1`, `field2`, etc. are named fields. Since the input schema declares them as nullable, we need to label non-null values as `list(double = 3.14)` and null values as `NULL`.
