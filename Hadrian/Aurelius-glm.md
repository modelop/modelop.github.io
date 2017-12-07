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

## Converting a glm model to PFA

The [glm](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/glm.html) library for generalized linear models is usually packaged with an R distribution. It is the basic way to do linear fits, including extensions such as logistic regression. This page assumes that you are not only familiar with the glm package, but have already created and fine-tuned your linear model, having produced a `glmObject` of class `"glm"`.

Conversion to PFA proceeds in three steps:

   1. Extract parameters from the `glmObject`.
   2. Format them as an R list-of-lists that is equivalent to a data structure in PFA.
   3. Create the PFA document, including the line of PFA code that evaluates the linear model.

These steps are not combined into one function call to allow for variations in how the model is invoked, including preprocessing, postprocessing, and attaching additional information to the linear fit object.

### Step 1: extract parameters

The following pulls all the relevant data from the `glmObject`, leaving training data behind.

```R
fit <- pfa.glm.extractParams(glmObject)
```

This `fit` has a `fit$const` term (a number or a length _N_ list of numbers) and a `fit$coeff` factor (a length _N_ list of number or an _N_ by _M_ list of lists). The field names are `fit$regressors`.

### Step 2: format for PFA

If you want all of these regressors to be in the input schema, as a record of named fields, create the input record like this:

```R
fieldNames <- fit$regressors
fieldTypes <- rep(avro.double, length(fieldNames))
names(fieldTypes) <- fieldNames
inputSchema <- avro.record(fieldTypes, "Input")
```

PFA's `model.reg.linear` expects the input to be an array of anonymous numbers, not a record of named numbers, so you need to preprocess the input with some generated code. Here's how to generate the code:

```R
makeVectorCode <- list(type = avro.array(avro.double),
                       new = lapply(fieldNames, function (n) {
                           paste("input.", n, sep = "")
                       })
```

You can look at what you've created with `cat(json(makeVectorCode))` to see how it will look in the completed PFA document. It creates an array from each input field manually, and thus encodes the order of named fields to be transformed by a vector or matrix of anonymous columns.

If you have no reason to name the input fields (e.g. they never had names, and it doesn't make sense to invent "field1", "field2", "field3", etc.), just make the input schema an array and skip the preprocessing step.

```R
inputSchema <- avro.array(avro.double)
```

### Step 3: construct the PFA

It is good practice to use an `avro.typemap` to ensure that named types are declared only once in the output PFA.

```R
tm <- avro.typemap(
    Input = inputSchema,
    Output = avro.double,
    Regression = avro.record(list(const = avro.double,
                                  coeff = avro.array(avro.double))))
```

Naturally, if your `fit$const` is a list and your `fit$coeff` is a list-of-lists, this should be reflected in your `Output` and `Regression` types:

```R
tm <- avro.typemap(
    Input = inputSchema,
    Output = avro.array(avro.double),
    Regression = avro.record(list(const = avro.array(avro.double),
                                  coeff = avro.array(avro.array(avro.double)))))
```

Here's an example PFA document with our `makeVectorCode` preprocessing:

```R
pfaDocument <- pfa.config(
    input = tm("Input"),
    output = tm("Output"),
    cells = list(regression =
        pfa.cell(tm("Regression"), list(const = fit$const,
                                        coeff = unname(fit$coeff)))),
    action = expression(
        vector <- makeVectorCode,
        model.reg.linear(vector, regression)
        ))
```

Without it, we'd just pass `input` as the first argument to `model.reg.linear`. If this is logistic regression (or there's some other reason you want to postprocess with a link function, wrap the `model.reg.linear` with `m.link.logit` or [another link function](http://dmg.org/pfa/docs/library/#lib:m.link).

To write the PFA to a file, use

```R
json(pfaDocument, fileName = "mymodel.pfa")
```

## Testing

If you have Titus and rPython installed (see [installation page](Installation#case-5-you-want-to-use-aurelius-in-r)), you can test the scoring engine without leaving R.

```R
engine <- pfa.engine(pfaDocument)    # verifies that pfaDocument is internally consistent

engine$action(list(field1 = 3.14, field2 = 3.14))
```

where `field1`, `field2`, etc. are named fields, assuming a record-based input schema. If your input schema is an anonymous array, use

```
engine$action(list(3.14, 3.14))
```

with the appropriate number of dimensions and values that test the correctness of the model.
