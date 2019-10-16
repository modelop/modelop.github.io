## Before you begin...

Download and install [Titus](Installation#case-4-you-want-to-install-titus-in-python) and [Numpy](http://www.numpy.org/).  This article was tested with Titus 0.5.14 and Numpy 1.8.2; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `titus.producer.kmeans`, `titus.producer.tools`, and `numpy`:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import titus.producer.kmeans as k
    >>> import titus.producer.tools as t
    >>> import numpy as np

Download the [Iris dataset](https://github.com/opendatagroup/hadrian/wiki/data/iris.csv), which we use for examples.  The first line contains field names (so strip it off with `1:`), the last column contains flower classifications (so strip it off with `:-1`), and the remaining numbers should be converted to `np.double`).  The dataset has 150 rows and 4 columns.

    >>> import csv
    >>> iris = list(csv.reader(open("iris.csv")))
    >>> np_iris = np.array(np.array(iris)[1:,:-1], dtype=np.double)
    >>> print np_iris.shape
    (150, 4)

Learn about [k-means clustering](http://en.wikipedia.org/wiki/K-means_clustering) (Lloyd's algorithm) if you're not already familiar with it.

## Simple k-means

Let's do the most straightforward example first.

A k-means fit is performed using a [`KMeans`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.kmeans.KMeans.html) object.  It is constructed from a number of clusters (k = 3 for our example) and a Numpy dataset whose first index runs over points (150 in our example) and whose second index runs over dimensions (4 in our example).

    >>> kmeans = k.KMeans(3, np_iris)

The cluster centers are initially set to randomly chosen points from the dataset.  Your initial clusters will almost certainly be different from the ones below.

    >>> print kmeans.centers()
    [[6.5, 2.7999999999999998, 4.5999999999999996, 1.5], [7.4000000000000004, 2.7999999999999998, 6.0999999999999996, 1.8999999999999999], [7.7000000000000002, 3.0, 6.0999999999999996, 2.2999999999999998]]

Run the k-means fit by calling `optimize`, giving it your choice of stopping condition.  The simplest condition is to stop when the clusters stop moving (data points stop crossing boundaries between clusters).

    >>> kmeans.optimize(k.moving())

For such a small dataset, this should be instantaneous.  The resulting clusters may be close to, but not necessarily exactly equal to, the following.

    >>> print kmeans.centers()
    [[5.0060000000000002, 3.4180000000000001, 1.464, 0.24400000000000002], [5.9016129032258062, 2.7483870967741937, 4.3935483870967742, 1.4338709677419355], [6.8500000000000005, 3.0736842105263156, 5.742105263157895, 2.0710526315789473]]

To make a model that can be used in a PFA scoring engine, call `pfaDocument` with an arbitrary cluster type name and three cluster instance names.

    >>> clusterTypeName = "Cluster"
    >>> clusterNames = ["cluster_" + str(i) for i in range(3)]
    >>> pfa = kmeans.pfaDocument(clusterTypeName, clusterNames)

Optionally look at it with `t.look`.

    >>> t.look(pfa, indexWidth=20)
    index                data
    ----------------------------------------
                         {
    input                  "input": {"items": "double", "type": "array"},
    output                 "output": "string",
    cells                  "cells": {
    cells,clusters           "clusters": {
    cells,clusters,init        "init": [
    cells,clusters,in...         {"id": "cluster_0", "center": [5.0060000000000002, 3.4180000000000001, 1.464, 0.24400000000000002]},
    cells,clusters,in...         {"id": "cluster_1", "center": [5.9016129032258062, 2.7483870967741937, 4.3935483870967742, 1.4338709677419355]},
    cells,clusters,in...         {"id": "cluster_2", "center": [6.8500000000000005, 3.0736842105263156, 5.742105263157895, 2.0710526315789473]}
                               ]
    ...

And write it to a file with `json.dump`.

    >>> import json
    >>> json.dump(pfa, open("myClusterModel.pfa", "w"))

That's it!  Now try applying it to your favorite dataset.

## Testing it

To test the clustering classifier, build a `PFAEngine` from it and run the original data through it.  (In actual model-building, you would probably reserve part of the dataset for training and another part for cross-validation.)

    >>> import titus.genpy
    >>> engine, = titus.genpy.PFAEngine.fromJson(pfa)
    >>> 
    >>> for row in iris[1:]:
    ...     sepalL, sepalW, petalL, petalW = map(float, row[:-1])
    ...     flowerType = row[-1]
    ...     result = engine.action([sepalL, sepalW, petalL, petalW])
    ...     print result, flowerType
    ...

## Stopping conditions

A stopping condition is a function that tells `KMeans` when it should stop iterating.  With large datasets, you may want to tune this to avoid wasting time on unimportant fine modifications of the final result.

The function takes four arguments and returns a boolean: `True` means keep iterating, `False` means stop.  The arguments are

  * `iterationNumber`: initially zero; increases by one for each iteration.
  * `corrections`: Numpy array of differences in each cluster center with respect to the last iteration.
  * `values`: Numpy array of the current values of each cluster center.
  * `datasetSize`: size of the dataset.

You could write your own or construct one from the following functors:

  * `k.moving()`: creates a stopping condition that stops when clusters no longer move.
  * `k.maxIterations(number)`: creates a condition that stops when the number of iterations reaches some limit.
  * `k.allChange(threshold)`: creates a condition that stops when all changes are less than `threshold` (a small number).
  * `k.halfChange(threshold)`: creates a condition that stops when half of the changes are less than `threshold` (a small number).
  * `k.whileall(*conditions)`: creates a condition that continues while all of the provided `conditions` are still `True`.  You can use this as a logical and--- `k.whileall(k.moving(), k.maxIterations(1000)` will continue while the clusters are moving and the number of iterations is less than 1000.
  * `k.whileany(*conditions)`: creates a condition that continues while any of the provided `conditions` are still `True`.  This is a logical or.
  * `k.clusterJumped()`: creates a condition that continues if a cluster's component becomes `nan` and needs to be reset.  It is intended to be used in a `k.whileall` with other conditions.

In addition, two fake stopping conditions are provided for diagnostics.

  * `k.printValue(format="g")`: prints the value of each cluster on each iteration and always returns `True` (continue iteration).  It must be used in a `k.whileall` with real stopping conditions.  The `format` is a [number format specifier](https://docs.python.org/2/library/string.html#format-specification-mini-language), such as `"g"` for arbitrary precision, `"f5.2"` for 5 characters, 2 beyond the decimal point, etc.
  * `k.printChange(format="g")`: prints the change in cluster positions, in exact analogy with `k.printValue`.  Often the changes are more relevant in debugging.

## Similarity and metrics

PFA can score clusters with user-specified metrics, so Titus can also produce clusters with user-specified metrics.  The `KMeans` constructor takes a metric object with keyword `metric`; the default is Euclidean:

    >>> kmeans = k.KMeans(3, np_iris, metric=k.Euclidean(k.AbsDiff()))

We use "similarity" to mean a function that takes a one-dimensional cluster center component and a data component and returns their distance.  The most common of these is the absolute difference,

    >>> absdiff = k.AbsDiff()
    >>> print absdiff.calculate(-3, 5)
    8

And we use "metric" to mean a function that takes a d-dimensional cluster and a d-dimensional data element and returns thier distance.  The most common of these is the Euclidean metric, which we build up by composing `k.AbsDiff` with `k.Euclidean`:

    >>> euclidean = k.Euclidean(k.AbsDiff())
    >>> print euclidean.calculate(np.array([[101, 102, 103, 104]]), np.array([[100, 100, 100, 100]]))
    >>> 5.4772255750516612

which is the square root of 1 squared plus 2 squared plus 3 squared plus 4 squared.

Metrics are built this way to provide more opportunities for code reuse: similarity objects are one-dimensional differences and metric objects are dimensional combiners.  The built-in suite of similarity and metric classes have a `pfa` method so that the combined function can be transcribed into PFA.

    >>> print euclidean.pfa("x", "y")
    {'metric.euclidean': [{'fcn': 'metric.absDiff'}, 'x', 'y']}

The built-in similarity classes are:

  * [`k.AbsDiff()`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.kmeans.AbsDiff.html): absolute difference.
  * [`k.GaussianSimilarity(sigma)`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.kmeans.GaussianSimilarity.html): difference that approaches zero as cluster and data become more *different*.  The expression is `exp(-ln(2) * (x - y)**2 / sigma**2)`.

The built-in metric classes are:

  * [`k.Euclidean(similarity)`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.kmeans.Euclidean.html): square root of the sum of squares.
  * [`k.SquaredEuclidean(similarity)`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.kmeans.SquaredEuclidean.html): sum of squares.  For most applications, this is equivalent to Euclidean, but does not involve a square root in its calculation.
  * [`k.Chebyshev(similarity)`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.kmeans.Chebyshev.html): the maximum of component-wise differences.
  * [`k.Taxicab(similarity)`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.kmeans.Taxicab.html): the sum of component-wise differences.
  * [`k.Minkowski(similarity, p)`](http://modelop.github.io//hadrian/titus-0.8.3/titus.producer.kmeans.Minkowski.html): component-wise differences raised to the `p` power, summed, and the sum is raised to the `1/p` power.  The expression is `sum((x - y)**p)**(1/p)`.

## Better starting conditions

Many variations on k-means clustering differ only in how they choose seed clusters.  By default, the `KMeans` object randomly selects `numberOfClusters` points from the dataset, but you can change this by explicitly setting `kmeans.clusters` before optimizing.  It is a Python list of one-dimensional Numpy arrays.

    >>> kmeans = k.KMeans(3, np_iris)
    >>> kmeans.clusters = [np.array([0.0, 0.0, 0.0, 0.0]) for i in range(3)]
    >>> kmeans.optimize(k.whileall(k.moving(), k.maxIterations(1000)))

If the clustering procedure encounters any `nan` values while optimizing, it will call `kmeans.newCluster()`, which calls `k.kmeans.randomPoint()`, so if you want to change the seeding value for these special cases as well, override one of these methods.

One seeding method that I have found useful for large datasets is to run the clustering procedure on randomly selected subsets of the data, keeping the partially optimized clusters while increasing the size of the subset.  This takes advantage of the following facts:

  * The first iterations make the largest corrections to the initial clusters and later iterations are refinements.
  * Clustering on a randomly chosen subset of the data yields approximately the same result as clustering on the whole dataset.

Thus, we iterate on a small subset to get most of the way to the solution and then don't need as many iterations on the whole dataset to refine the result.

The `KMeans` object has a `randomSubset(subsetSize)` method for selecting random subsets (without replacement) and a `stepup(condition, base)` method to apply the whole procedure.  The `condition` argument is a stopping condition for each subproblem and `base` is the multiplicative size of each subproblem (`base = 2` doubles the size of the dataset with each subproblem).

So for a large dataset, you may want to do something like the following:

    >>> kmeans = k.KMeans(3, np_iris)
    >>> stoppingCondition = k.whileall(k.moving(), k.maxIterations(1000))
    >>> kmeans.stepup(stoppingCondition)
    >>> kmeans.optimize(stoppingCondition)

## Normalization and other preprocessing

Because k-means clustering assumes clusters to be approximately spherical, it is often necessary to normalize the components of the raw data such that they all have the same range.  The metric is a good place to do this because it guarantees that the same normalization will be used for training and scoring.

For instance, suppose we want to shift and scale the Iris dataset so that it is contained within the unit interval.  The following expressions would need to be applied to each component:

    >>> lows = np_iris.min(axis=0)
    >>> highs = np_iris.max(axis=0)
    >>> normExprs = ["(x - {lo})/({hi} - {lo})".format(**locals()) for lo, hi in zip(lows, highs)]
    >>> print "\n".join(normExprs)
    (x - 4.3)/(7.9 - 4.3)
    (x - 2.0)/(4.4 - 2.0)
    (x - 1.0)/(6.9 - 1.0)
    (x - 0.1)/(2.5 - 0.1)

We can provide these expressions directly to the constructor of a `KMeans` object through the `preprocess` keyword.

    >>> kmeans = k.KMeans(3, np_iris, preprocess=normExprs)
    >>> kmeans.optimize(k.moving())

The `KMeans` object uses these strings to transform its private copy of the dataset and it adds the transformation to the PFA document, thus ensuring that the same transformation is applied to the training procedure and the scoring procedure.

    >>> pfa = kmeans.pfaDocument(clusterTypeName, clusterNames)
    >>> t.look(t.find({"metric.euclidean": t.Any()}, pfa), indexWidth=10, inlineDepth=6)
    index      data
    --------------------
               {
    metric....   "metric.euclidean": [
    metric....     {"fcn": "metric.absDiff"},
    metric....     {
    metric....       "new": [
    metric....         {"/": [{"-": [{"path": [0], "attr": "datum"}, 4.3]}, {"-": [7.9, 4.3]}]},
    metric....         {"/": [{"-": [{"path": [1], "attr": "datum"}, 2.0]}, {"-": [4.4, 2.0]}]},
    metric....         {"/": [{"-": [{"path": [2], "attr": "datum"}, 1.0]}, {"-": [6.9, 1.0]}]},
    metric....         {"/": [{"-": [{"path": [3], "attr": "datum"}, 0.1]}, {"-": [2.5, 0.1]}]}
                     ],
    metric....       "type": {"items": "double", "type": "array"}
                   },
    metric....     "clusterCenter"
                 ]
               }

Any PFA functions that have a Numpy equivalent are available for preprocessing because the expression strings are converted into Numpy operations using Python's `eval` and PFA operations using `titus.producer.expression.pfa`.

We could, for instance, apply a logarithm to each component, which is `m.ln` in PFA and `np.log` in Python:

    >>> normExprs = ["m.ln(x)"] * np_iris.shape[1]
    >>> print "\n".join(normExprs)
    m.ln(x)
    m.ln(x)
    m.ln(x)
    m.ln(x)
    >>> kmeans = k.KMeans(3, np_iris, preprocess=normExprs)
    >>> kmeans.optimize(k.moving())
    >>> pfa = kmeans.pfaDocument(clusterTypeName, clusterNames)
    >>> t.look(t.find({"metric.euclidean": t.Any()}, pfa), indexWidth=10, inlineDepth=3)
    index      data
    --------------------
               {
    metric....   "metric.euclidean": [
    metric....     {"fcn": "metric.absDiff"},
    metric....     {
    metric....       "new": [
    metric....         {"m.ln": {"path": [0], "attr": "datum"}},
    metric....         {"m.ln": {"path": [1], "attr": "datum"}},
    metric....         {"m.ln": {"path": [2], "attr": "datum"}},
    metric....         {"m.ln": {"path": [3], "attr": "datum"}}
                     ],
    metric....       "type": {"items": "double", "type": "array"}
                   },
    metric....     "clusterCenter"
                 ]
               }

## Modifying the scoring procedure

We have seen the `kmeans.pfaDocument(clusterTypeName, clusterNames)` method, which turns the final result of clustering into the following scoring procedure:


  1. Given a d-dimensional array, find the closest cluster.
  2. Return the `clusterName` of the closest cluster (a string).

You may want to do something different, like return the distance to the closest cluster, or compare the input data to two different cluster sets and report which of the two cluster sets yields a smaller distance (et cetera, ad infinitum).

That is a general PFA-building problem, which is the topic of most articles on this website.  To approach this problem from a clustering point of view, let's start by looking at the PFA generated by the default method.

    >>> clusterTypeName = "Cluster"
    >>> clusterNames = ["cluster_" + str(i) for i in range(3)]
    >>> pfa = kmeans.pfaDocument(clusterTypeName, clusterNames)
    >>> t.look(pfa["action"], indexWidth=10)
    index      data
    --------------------
               {
    attr         "attr": {
    attr,mo...     "model.cluster.closest": [
    attr,mo...       "input",
    attr,mo...       {"cell": "clusters"},
    attr,mo...       {
    attr,mo...         "params": [
    attr,mo...           {"datum": {"items": "double", "type": "array"}},
    attr,mo...           {"clusterCenter": {"items": "double", "type": "array"}}
                       ],
    attr,mo...         "ret": "double",
    attr,mo...         "do": {
    attr,mo...           "metric.euclidean": [{"fcn": "metric.absDiff"}, "datum", "clusterCenter"]
                       }
                     }
                   ]
                 },
    path         "path": [{"string": "id"}]
               }

The primary function here is `model.cluster.closest`, which takes a data array (`input`), a set of clusters (`{"cell": "clusters"}`), and a metric function (parameters `datum` and `clusterCenter`, which are passed to `metric.euclidean` with `metric.absDiff` similarity, as described above).

The `model.cluster.closest` function returns a record representing the cluster, so the `attr-path` extracts its `id`.  The record's type is defined in the declaration of the cell named `clusters`.

    >>> t.look(pfa["cells"]["clusters"], indexWidth=10)
    index      data
    --------------------
               {
    type         "type": {
    type,items     "items": {
    type,it...       "fields": [
    type,it...         {"type": {"items": "double", "type": "array"}, "name": "center"},
    type,it...         {"type": "string", "name": "id"}
                     ],
    type,it...       "type": "record",
    type,it...       "name": "Cluster"
                   },
    type,type      "type": "array"
                 },
    init         "init": [
    init,0         {"center": [5.0060000000000002, 3.4180000000000001, 1.464, 0.24399999999999999], "id": "cluster_0"},
    init,1         {"center": [5.9016129032258062, 2.7483870967741937, 4.3935483870967742, 1.4338709677419355], "id": "cluster_1"},
    init,2         {"center": [6.8500000000000005, 3.0736842105263156, 5.742105263157895, 2.0710526315789473], "id": "cluster_2"}
                 ]
               }

A Cluster is a record that contains an array named `center` and a string named `id`.  All the k-means procedure did was set the initial values of the `centers` and supply the appropriate metric.

To make custom scoring procedures, we need a function that only outputs the relevant data.  The method `kmeans.pfaValue(clusterNames)` returns just the snippet in `init` above:

    >>> justCenters = kmeans.pfaValue(clusterNames)
    >>> t.look(justCenters, indexWidth=10)
    index      data
    --------------------
               [
    0            {"center": [5.0060000000000002, 3.4180000000000001, 1.464, 0.24399999999999999], "id": "cluster_0"},
    1            {"center": [5.9016129032258062, 2.7483870967741937, 4.3935483870967742, 1.4338709677419355], "id": "cluster_1"},
    2            {"center": [6.8500000000000005, 3.0736842105263156, 5.742105263157895, 2.0710526315789473], "id": "cluster_2"}
               ]

`kmeans.centers()` returns the centers with no PFA formatting at all:

    >>> print kmeans.centers()
    [[5.0060000000000002, 3.4180000000000001, 1.464, 0.24399999999999999], [5.9016129032258062, 2.7483870967741937, 4.3935483870967742, 1.4338709677419355], [6.8500000000000005, 3.0736842105263156, 5.742105263157895, 2.0710526315789473]]

and `kmeans.metric.pfa(datumRef, clusterRef)` returns the metric as PFA code, including any normalization or preprocessing that was passed through the `preprocess` option (described above):

    >>> kmeans.metric.pfa("datum", "clusterCenter")
    {'metric.euclidean': [{'fcn': 'metric.absDiff'}, 'datum', 'clusterCenter']}

### Building a scoring engine using PrettyPFA

PrettyPFA is a method of building PFA from more human-friendly source code.  The default scoring procedure can be built as follows:

    >>> import titus.prettypfa
    >>> 
    >>> pfa = titus.prettypfa.jsonNode("""
    ... types:
    ...   record(Cluster,
    ...          id: string,
    ...          center: array(double))
    ... input: array(double)
    ... output: string
    ... cells:
    ...  clusters(array(Cluster)) = CLUSTERS_HERE
    ... action:
    ...   model.cluster.closest(
    ...     input,
    ...     clusters,
    ...     fcn(datum: array(double), clusterCenter: array(double) -> double)
    ...       METRIC_HERE).id
    ... """, check=False)
    >>> 
    >>> t.assignAt("CLUSTERS_HERE", pfa, kmeans.pfaValue(clusterNames))
    >>> t.assignAt("METRIC_HERE", pfa, kmeans.metric.pfa("datum", "clusterCenter"))

### Variations through PrettyPFA

Suppose you want to report only the distance to the closest cluster.  The output of the model should then be `double` and you would use the metric to compute the distance again.


    >>> pfa = titus.prettypfa.jsonNode("""
    ... types:
    ...   record(Cluster,
    ...          id: string,
    ...          center: array(double))
    ... input: array(double)
    ... output: double        // NOTE: double!
    ... cells:
    ...   clusters(array(Cluster)) = CLUSTERS_HERE
    ... action:
    ...   var bestClusterCenter =
    ...     model.cluster.closest(
    ...       input,
    ...       clusters,
    ...       fcn(datum: array(double), clusterCenter: array(double) -> double)
    ...         METRIC_HERE)["center"];
    ...   METRIC_HERE_2;
    ... """, check=False)
    >>> 
    >>> t.assignAt("CLUSTERS_HERE", pfa, kmeans.pfaValue(clusterNames))
    >>> t.assignAt("METRIC_HERE", pfa, kmeans.metric.pfa("datum", "clusterCenter"))
    >>> t.assignAt("METRIC_HERE_2", pfa, kmeans.metric.pfa("input", "bestClusterCenter"))

Suppose you have two cluster sets, named `good` and `bad` (`KMeans` objects trained from suggestively labeled datasets), and you want to find out which of the two is closer for each input.

    >>> pfa = titus.prettypfa.jsonNode("""
    ... types:
    ...   record(Cluster,
    ...          id: string,
    ...          center: array(double))
    ... input: array(double)
    ... output: string
    ... cells:
    ...   good(array(Cluster)) = GOOD_HERE;
    ...   bad(array(Cluster)) = BAD_HERE;
    ... action:
    ...   var closestGoodCenter =
    ...     model.cluster.closest(
    ...       input,
    ...       good,
    ...       fcn(datum: array(double), clusterCenter: array(double) -> double)
    ...         METRIC_HERE)["center"];
    ...   var closestBadCenter =
    ...     model.cluster.closest(
    ...       input,
    ...       good,
    ...       fcn(datum: array(double), clusterCenter: array(double) -> double)
    ...         METRIC_HERE)["center"];
    ...   if (METRIC_HERE_2 < METRIC_HERE_3)
    ...     "good"
    ...   else
    ...     "bad";
    >>> """, check=False)
    >>> 
    >>> t.assignAt("GOOD_HERE", pfa, good.pfaValue(clusterNames))
    >>> t.assignAt("BAD_HERE", pfa, bad.pfaValue(clusterNames))
    >>> t.assignAt("METRIC_HERE", pfa, good.metric.pfa("datum", "clusterCenter"))
    >>> t.assignAt("METRIC_HERE_2", pfa, good.metric.pfa("input", "closestGoodCluster"))
    >>> t.assignAt("METRIC_HERE_3", pfa, good.metric.pfa("input", "closestBadCluster"))

Et cetera, ad infinitum.

### Adding structure to the clusters

In the simple case, the cluster records contain only two pieces of information: a `center` point and an `id` label.  You can add anything you want to it and use that information in the scoring procedure.  For instance, you could even attach a whole secondary model to each cluster and evaluate the secondary model corresponding to the cluster (geometry-based segmentation of models).

Here is a common case: reporting the training population associated with the matching cluster.  This requires information from the training process, so you need to get it from the `KMeans` object.

    >>> pfa = titus.prettypfa.jsonNode("""
    ... types:
    ...   record(Cluster,
    ...          id: string,
    ...          center: array(double),
    ...          population: int)        // note the new field
    ... input: array(double)
    ... output: int
    ... cells:
    ...  clusters(array(Cluster)) = CLUSTERS_HERE
    ... action:
    ...   model.cluster.closest(
    ...     input,
    ...     clusters,
    ...     fcn(datum: array(double), clusterCenter: array(double) -> double)
    ...       METRIC_HERE)["population"]
    ... """, check=False)
    >>> 
    >>> t.assignAt("CLUSTERS_HERE", pfa, kmeans.pfaValue(clusterNames, populations=True))
    >>> t.assignAt("METRIC_HERE", pfa, kmeans.metric.pfa("datum", "clusterCenter"))
    >>> 
    >>> t.look(t.find(t.Min(init=t.Start()), pfa)["init"], indexWidth=10, inlineDepth=1)
    index      data
    --------------------
               [
    0            {
    0,popul...     "population": 50,
    0,id           "id": "c1",
    0,center       "center": [5.0060000000000002, 3.4180000000000001, 1.464, 0.24399999999999999]
                 },
    1            {
    1,popul...     "population": 62,
    1,id           "id": "c2",
    1,center       "center": [5.9016129032258062, 2.7483870967741937, 4.3935483870967742, 1.4338709677419355]
                 },
    2            {
    2,popul...     "population": 38,
    2,id           "id": "c3",
    2,center       "center": [6.8500000000000005, 3.0736842105263156, 5.742105263157895, 2.0710526315789473]
                 }
               ]

In general, you'll get data from other sources, such as labeling in semi-supervised clustering.  The output of `model.cluster.closest` is a record that you define, so you can do whatever you want.