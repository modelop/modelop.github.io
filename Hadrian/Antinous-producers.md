## Overview

In addition to providing a general way to plug Jython code into PFA applications, Antinous produces models. Only k-means has been implemented.

## Producer interface

Antinous producers adhere to the following suite of abstract interfaces in `com.opendatagroup.antinous.producer`.

   * A `Dataset` is a source of training data, filled in Jython and used by the producer to make a model. It has at least these methods:
     * `revert(): Unit` empties the `Dataset`

   * A `Model` is what a producer makes, something that can be converted into PFA. It has at least these methods:
     * `pfa: AnyRef` makes a PFA cell or pool item representing the model using `JsonObject`, `JsonArray`, and primitive types
     * `pfa(options: java.util.Map[String, AnyRef]): AnyRef` makes PFA with options (probably coming from Jython)
     * `avroType: AvroType` declares the Avro type of the PFA cell or pool item

   * A `ModelRecord` extends `Model` and Scala's `Product` so that it can be a case class

   * A `Producer[D <: Dataset, M <: Model]` uses a `Dataset` to produce a `Model`. It has at least these methods:
     * `dataset: D` the dataset
     * `optimize(): Unit` updates the state of the producer in-place to improve the model (possibly many times)
     * `model: M` get the current state of the model

   * A `JsonObject[X]` is a `java.util.Map[String, X]` for representing `Model` data as PFA
   * A `JsonArray[X]` is a `java.util.List[X]` for representing `Model` data as PFA

The package also has a random number seed, which is used to randomize all producer algorithms. It can be set via

   * `setRandomSeed(x: Long)`

The usual procedure is to create a concrete `Dataset` in the global Jython namespace and fill it in the `action` phase, then create a `Producer` from that `Dataset`, run `optimize()` to make a `Model` and `emit` PFA in the `end` phase.

Here is an example that builds a k-means clustering model for one key in a Hadoop reducer (one segment of the whole model).

```python
from antinous import *
from com.opendatagroup.antinous.producer.kmeans import VectorSet, KMeans

input = record(key = string, value = array(double))
output = record(segment = string,
                clusters = array(record(center = array(double),
                weight = double)))

segment = None
vectorSet = VectorSet()

def action(input):
    global segment, vectorSet
    segment = input.key
    vectorSet.add(input.value)

def end():
    if segment is not None:
        kmeans = KMeans(3, vectorSet)
        kmeans.optimize()
        emit({"segment": segment, "clusters": kmeans.model().pfa()})
```

## K-means producer

In package `com.opendatagroup.antinous.producer.kmeans`,

   * `VectorSet` is a `Dataset` with an `add(pos: java.lang.Iterable[Double], weight: Double)` method for adding points with optional weights.

   * `ClusterSet(clusters: java.util.List[Cluster])` is a `Model`
   * `Cluster(center: java.util.List[Double], weight: Double, covariance: java.util.List[java.util.List[Double]])` is a `ModelRecord` that takes options
     * `weight`: if true, show the weight
     * `covariance`: if true, show the covariance
     * `totalVariance`: if true, show the total variance
     * `determinant`: if true, show the determinant
     * `limitDimensions`: if a list of integers, only present the dimensions specified in `covariance`, `totalVariance`, and `determinant`

   * `KMeans(numberOfClusters: Int, dataset: VectorSet)` is a `Producer[VectorSet, ClusterSet]` with the following methods:
     * `model: ClusterSet`
     * `metric: Metric` and `setMetric(m: Metric)`
     * `stoppingCondition: StoppingCondition` and `setStoppingCondition(s: StoppingCondition)`
     * `randomClusters()`: pick random initial clusters (done automatically by constructor)
     * `optimize()` and `optimize(subsampleSize: Int)` to perform k-means on a random subset, using the `metric` and stopping when `stoppingCondition` is met.

Metrics adhere to interface `Metric` and can be constructed with:

   * `Euclidean`
   * `SquaredEuclidean`
   * `Chebyshev`
   * `Taxicab`
   * `Minkowski(p: Double)`
   * `M(f: PyFunction)` where `f` is any Jython function that takes two Python lists of numbers

Stopping conditions adhere to interface `StoppingCondition` and can be constructed with:

   * `MaxIterations(max: Int)` triggers when the iteration number reaches or exceeds a given maximum
   * `Moving` triggers when all changes are below a threshold of 1e-15
   * `BelowThreshold(threshold: Double)`
   * `HalfBelowThreshold(threshold: Double)` triggers when half the clusters' changes are below a given threshold
   * `WhenAll(conditions: java.lang.Iterable[StoppingCondition])` triggers when all subconditions are met
   * `WhenAny(conditions: java.lang.Iterable[StoppingCondition])` triggers when any subconditions are met
   * `PrintValue(numberFormat: String = "%g")` does not actually stop iteration, but prints out the current values
   * `PrintValue(numberFormat: String = "%g")` does not actually stop iteration, but prints out the last changes
   * `S(f: PyFunction)` where `f` is a Python function that takes
     * iteration number (`int`)
     * model (`ClusterSet`)
     * changes (`list` of `lists` of numbers)
