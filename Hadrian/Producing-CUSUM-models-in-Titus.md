# Introduction

This document presents two examples of cumulative sums ([see
CUSUM](http://en.wikipedia.org/wiki/CUSUM)) in PFA.

The first is completely stripped-down: it takes numbers as input,
compares them with a baseline distribution and an alternate
distribution, and returns the current value of the CUSUM statistic.

The second is a bit more realistic: it represents a segmented model
with different expected distributions in each segment and the
distributions are multidimensional.  It alerts when the significance
crosses a threshold but does not alert again until after the
statistic resets.

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.6.11; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `titus.prettypfa` and `PFAEngine`:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import titus.prettypfa as prettypfa
    >>> from titus.genpy import PFAEngine

These examples use random numbers, but for the sake of reproducibility, we set the random seed.

    >>> import random
    >>> random.seed(12345)

We'll be using PrettyPFA for a nice syntax and PFAEngine to load PFA documents that have been post-processed.

## First example: basic use of CUSUM

The simplest way to use CUSUM is to pass log-likelihood ratios into
stat.change.updateCUSUM in a cell-updator.  CUSUM-based scoring
engines must make use of persistent state, so some cell or pool will
be required.  In this case, the cell is named cumulativeSum and it
is simply a floating-point number (no records).

The stat.change.updateCUSUM function takes the log of a likelihood
ratio as input so that you can use it with any kind of probability
distribution.  See PFA's prob.* module for the available
distributions.

This example also illustrates the use of expression-replacements in
PrettyPFA.  Names surrounded in French quotes (`<<` and `>>`) are
replaced by values passed to the PrettyPFA compiler.  This is safer
than doing string replacements because the replacement is inserted
as a PFA JSON object (which must have closed brackets by
definition), rather than raw PrettyPFA text (which might not).
Also, it preserves the line numbers after the replacement, which
makes debugging easier.

```python
oneCellEngine, = titus.prettypfa.engine('''
input: double
output: double
cells:
  cumulativeSum(double) = <<START>>
action:
  // compute the baseline log-likelihood
  var baseLL = prob.dist.gaussianLL(input, <<BASELINE_MU>>, <<BASELINE_SIGMA>>);

  // compute the alternate log-likelihoo
  var altLL = prob.dist.gaussianLL(input, <<ALTERNATE_MU>>, <<ALTERNATE_SIGMA>>);

  // update the CUSUM in the cell and return the updated value
  cumulativeSum to fcn(old: double -> double)
    stat.change.updateCUSUM(altLL - baseLL, old, <<RESET>>)
''', START = 0.0,
     RESET = 0.0,
     BASELINE_MU = 12.5,
     BASELINE_SIGMA = 1.0,
     ALTERNATE_MU = 3.0,
     ALTERNATE_SIGMA = 2.0)
```

Now let's run this engine!  When we pass it values that are
consistent with the baseline (though with more noise), the CUSUM
statistic is usually zero, but might jump up a little in reaction to
the noise.

```python
for x in (random.gauss(12.5, 5.0) for i in xrange(10)):
    print x, oneCellEngine.action(x)
# 11.8809960221 0.0
# 12.8576248174 0.0
# 14.4168459716 0.0
# 8.75001469557 2.20521408628
# 10.2782276368 0.0
# 14.9137731207 0.0
# 9.78220561131 0.0
# 11.3034090937 0.0
# 16.2832184196 0.0
# 16.2485246916 0.0
```

When we pass it values that are consistent with the alternate
distribution, the CUSUM statistic goes way up.

```python
for x in (random.gauss(3.0, 2.0) for i in xrange(10)):
    print x, oneCellEngine.action(x)
# 1.85499830072 55.8010047968
# 2.52927363663 104.787851809
# 1.23108002562 167.197848589
# 2.38539541166 217.610097047
# 3.84493705138 254.282767361
# 2.77207105186 300.89942704
# 5.04297853596 327.488144255
# 2.72415600614 374.569048732
# 1.86777276692 430.237787206
# 2.9719981097 474.935952023
```

## Second example: a more realistic case

This second example adds two features that are likely to be found in
a realistic case: segmentation (many independently parameterized
models) and multidimensional distributions.

We parameterize these distributions as spherical Gaussian blobs
centered on a given point, which means that we can compute the total
log-likelihood of each distribution as the sum of log-likelihoods in
each dimension.

The input has only two fields: a "segment" string for selecting the
right segment and a "vector" that should have the same number of
dimensions as the baseline and alternate of the model.  This is
enforced with a user-defined error.

The output is an alert that gets emitted the *first* time a model
segment crosses the alert threshold.  Once this happens, an
"alerted" flag keeps it from alerting again until the CUSUM resets.
The "significance" reported in the alert is the CUSUM statistic.

If this scoring engine encounters an unrecognized segment, it will
create a new segment with default values, but then accumulate its
CUSUM in the ordinary way.

The persistent storage in this example is a pool so that multiple
instances of the scoring engine can update different segments at the
same time.  They only have to stop and wait for one another if two
instances want to update the same segment at the same time.

```python
bigPoolDocument = titus.prettypfa.jsonNode('''
types:
  record(Input, segment: string, vector: array(double));
  record(Alert, segment: string, significance: double);
  record(Model, baseline: array(double),
                alternate: array(double),
                cumulativeSum: double,
                alerted: boolean)
input: Input
output: Alert
pools:
  models(Model) = {}
method: emit
action:
  models[input.segment] to fcn(old: Model -> Model) {
    // make sure the input is sane
    if (a.len(old.baseline) != a.len(input.vector)  ||  a.len(old.alternate) != a.len(input.vector))
      error("input.vector has the wrong number of dimensions");

    // add up the log-likelihood in each dimension (assumes a unit-matrix covariance; i.e. spherical)
    var altLL = 0.0;
    var baseLL = 0.0;
    for (i = 0;  i < a.len(input.vector);  i = i + 1) {
      baseLL = baseLL + prob.dist.gaussianLL(input.vector[i], old.baseline[i], 1.0);
      altLL = altLL + prob.dist.gaussianLL(input.vector[i], old.alternate[i], 1.0);
    };

    // update only the cumulativeSum field of the "old" Model, putting the result into "out"
    var out = update(old, cumulativeSum: stat.change.updateCUSUM(altLL - baseLL, old.cumulativeSum, 0.0));

    // handle the "alerted" logic and emit an Alert if this is the first time the CUSUM is high
    if (out.cumulativeSum == 0.0)
      out = update(out, alerted: false);
    if (out.cumulativeSum > <<ALERT_THRESHOLD>>  &&  !out.alerted) {
      out = update(out, alerted: true);
      emit(new(Alert, segment: input.segment, significance: out.cumulativeSum));
    };

    // return the updated record so that the pool can be updated
    out

  } init {
    // default case for new segments encountered at runtime
    new(Model, baseline: json(array(double), [0.0, 0.0, 0.0, 0.0, 0.0]),
               alternate: json(array(double), [1.0, 1.0, 1.0, 1.0, 1.0]),
               cumulativeSum: 0.0,
               alerted: false)
  }
''', ALERT_THRESHOLD = 10.0)
```

The model parameters did not need to be written in the PrettyPFA
because a pool is a collection, and "{}" is a valid map(Model).
We'll insert segments using Python.  (bigPoolDocument is a jsonNode,
which is to say, it's a JSON object represented by Python
dictionaries, lists, and atomic values.)

Although "JSON regex" replacements are advisable when replacing
parts of the algorithm (the "action" section) because modifications
to the code can change the indexes, we can use explicit indexes
here.  Cell and pool indexes are never disrupted by changes in
anything except the specific cells and pools that are referenced by
the index.

```python
bigPoolDocument["pools"]["models"]["init"]["one"] = {
    "baseline": [random.gauss(0.0, 1.0) for i in xrange(5)],
    "alternate": [random.gauss(0.0, 1.0) for i in xrange(5)],
    "cumulativeSum": 0.0,
    "alerted": False}

bigPoolDocument["pools"]["models"]["init"]["two"] = {
    "baseline": [random.gauss(0.0, 1.0) for i in xrange(5)],
    "alternate": [random.gauss(0.0, 1.0) for i in xrange(5)],
    "cumulativeSum": 0.0,
    "alerted": False}

bigPoolDocument["pools"]["models"]["init"]["three"] = {
    "baseline": [random.gauss(0.0, 1.0) for i in xrange(5)],
    "alternate": [random.gauss(0.0, 1.0) for i in xrange(5)],
    "cumulativeSum": 0.0,
    "alerted": False}
```

Now that we've built up the PFA as we like it, let's load it into an
engine (and check the validity again with the model parameters we
just added).

```python
bigPoolEngine, = PFAEngine.fromJson(bigPoolDocument)
```

Since this is a "method: emit" engine, we need to define and attach
an emit function.  Let's just print out any alerts we see.

```python
def emit(x):
    print "ALERT", x

bigPoolEngine.emit = emit
```

Now let's run it!  We supply random segment labels and random
five-dimensional vectors (statistically consistent with the origin).
With this random number seed, we only get two alerts in a thousand
input values.

```python
segments = ["one", "two", "three", "four", "five"]
for segment, vector in ((random.choice(segments), [random.gauss(0.0, 1.0) for i in xrange(5)]) for j in xrange(1000)):
    bigPoolEngine.action({"segment": segment, "vector": vector})
# ALERT {'segment': u'two', 'significance': 15.977314785816933}
# ALERT {'segment': u'three', 'significance': 11.060248933370236}
```

## Conclusion

These two examples show the essentials of CUSUM handling in PFA and
how it can be built up into more realistic scoring engines.  Beyond
this, one might consider probability distributions other than
Gaussian balls and introduce methods to train the baseline and
alternate distributions with data, rather than randomly.
