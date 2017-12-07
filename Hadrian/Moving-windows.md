# Moving windows

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import random
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## Four kinds of moving windows

Moving windows are methods of pre-processing that aggregate over data collected at similar times. A window is a contiguous interval that usually includes the most recent data record. The window length can be defined in terms of a fixed number of data records or a fixed time, where time must be defined by one of the data fields. The window can move forward in steps of one data record or one full window (or anything in between, but the extremes are the most common cases).

That makes four interesting cases: 1) sliding event-based windows, 2) sliding time-based windows, 3) jumping event-based windows, and 4) jumping time-based windows. We take "sliding" to mean steps of one data record and "jumping" to mean steps of one whole window, and "event" to mean the window size is defined by a number of records, and "time" to mean that it is defined by a numerical field in the data. (We also assume that input data are sorted by this time field.)

Sliding windows are good for smooth transitions that yield a new result for each datum. Jumping windows are good for partitioning data into non-overlapping sets (so that uncertainties may be uncorrelated).

If the data arrive in regular intervals, there is no distinction between event-based windows and time-based windows, so use the simpler case (event-based windows). If the data arrive irregularly, then time-based windows may be necessary.

## Sliding event-based windows

Below is a naive but straightfoward implementation of a moving average.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: double
output: double
cells:
  window(array(double)) = []
action:
  a.mean(window to fcn(old: array(double) -> array(double)) {
    a.cycle(old, input, <<WINDOW_SIZE>>)
  })
''', WINDOW_SIZE=20)
engine, = PFAEngine.fromJson(pfaDocument)
```

The [`a.cycle` function](http://scoringengine.org/docs/library/#fcn:a.cycle) adds to the end of an array and removes elements from the beginning to ensure that it doesn't exceed a given size (here, 20). We use it to update a cell named `window` and then compute the [`a.mean` function](http://scoringengine.org/docs/library/#fcn:a.mean) of the result.

We can test it as a smoother of bumpy data. The smoothed version is a little behind the actual, but doesn't jump as much.

```python
for actual in xrange(100):
    bumpy = actual + random.gauss(0, 5)
    smooth = engine.action(bumpy)
    print "{0:6.3f} {1:6.3f}".format(bumpy - actual, smooth - actual)
```

For a moving average, this is overkill: we unnecessarily walk over the whole window each time to compute the mean, when we only needed to add incoming values and subtract outgoing ones. The [`stat.sample.updateWindow` function](http://scoringengine.org/docs/library/#fcn:stat.sample.updateWindow) handles this special case more efficiently.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  WindowItem = record(x: double,
                      w: double,
                      count: double,
                      mean: double,
                      WindowState)
input: double
output: double
cells:
  window(array(WindowItem)) = []
action:
  a.last(window to fcn(old: array(WindowItem) -> array(WindowItem)) {
    stat.sample.updateWindow(input, 1.0, old, <<WINDOW_SIZE>>)
  })["mean"]
''', WINDOW_SIZE=20)
engine, = PFAEngine.fromJson(pfaDocument)
```

If you wish, you can also add `variance: double` to this record and track the moving variance as well.

Although less efficient for moving averages, the `a.cycle` method handles unusual cases that require more general treatment, such as the most common recent string.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: string
output: string
cells:
  window(array(string)) = []
action:
  a.mode(window to fcn(old: array(string) -> array(string)) {
    a.cycle(old, input, <<WINDOW_SIZE>>)
  })
''', WINDOW_SIZE=6)
engine, = PFAEngine.fromJson(pfaDocument)

for x in "hello", "hello", "one", "two", "three", "three", "three", "hello":
    print engine.action(x)
```

## Jumping event-based windows

A jumping event-based window is like the sliding case, except that we don't need a fancy function like `a.cycle` to do the update. We do, however, need to make this an emit-type engine so that it only returns results when a window is full.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: double
output: double
cells:
  window(array(double)) = []
method: emit
action:
  window to fcn(old: array(double) -> array(double)) {
    if (a.len(old) + 1 > <<WINDOW_SIZE>>) {
      emit(a.mean(old));
      new(array(double), input)
    }
    else
      a.append(old, input)
  }
''', WINDOW_SIZE=20)
engine, = PFAEngine.fromJson(pfaDocument)

for actual in range(100):
    bumpy = actual + random.gauss(0, 5)
    def emit(smooth):
        print "{0:6.3f}".format(smooth - actual),
    engine.emit = emit
    print "{0:6.3f} ".format(bumpy - actual),
    engine.action(bumpy)
    print
```

If the jumping window were used for preprocsssing, scoring could only take place at the end of each window boundary.

## Sliding time-based windows

For sliding time-based windows, we have to do the equivalent of `a.cycle` manually, since a library function wouldn't know which field to query.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  WindowItem = record(time: double,
                      x: double,
                      WindowItem)
input: WindowItem
output: double
cells:
  window(array(WindowItem)) = []
action:
  var updated = window to fcn(old: array(WindowItem) -> array(WindowItem)) {
    var new = a.append(old, input);
    while ((a.last(new)["time"]) - (a.head(new)["time"]) > <<WINDOW_WIDTH>>)
      new = a.tail(new);
    new
  };
  a.mean(a.map(updated, fcn(w: WindowItem -> double) w.x))
''', WINDOW_WIDTH=1.5)
engine, = PFAEngine.fromJson(pfaDocument)

for actual in xrange(100):
    bumpy = actual + random.gauss(0, 5)
    smooth = engine.action({"time": actual/10.0, "x": bumpy})
    print "{0:6.3f} {1:6.3f}".format(bumpy - actual, smooth - actual)
```

## Jumping time-based windows

Jumping time-based windows case could be implemented two ways: (1) with maximum time differences, as above, and (2) as time-bins, locked to a universal clock. The second case might split a group of points simply because it falls across an arbitrary time division, but it is easier to coordinate as a global standard.

Below is an example with maximum time differences.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  WindowItem = record(time: double,
                      x: double,
                      WindowItem)
input: WindowItem
output: double
cells:
  window(array(WindowItem)) = []
method: emit
action:
  window to fcn(old: array(WindowItem) -> array(WindowItem)) {
    if (a.len(old) > 0  &&  (input["time"]) - (a.head(old)["time"]) > <<WINDOW_WIDTH>>) {
      emit(a.mean(a.map(old, fcn(w: WindowItem -> double) w.x)));
      new(array(WindowItem), input)
    }
    else
      a.append(old, input)
  }
''', WINDOW_WIDTH=1.5)
engine, = PFAEngine.fromJson(pfaDocument)

for actual in range(100):
    bumpy = actual + random.gauss(0, 5)
    def emit(smooth):
        print "{0:6.3f}".format(smooth - actual),
    engine.emit = emit
    print "{0:6.3f} ".format(bumpy - actual),
    engine.action({"time": actual/10.0, "x": bumpy})
    print
```

And below is an example with a universal time bin.

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  WindowItem = record(time: double,
                      x: double,
                      WindowItem)
input: WindowItem
output: double
cells:
  window(array(WindowItem)) = []
method: emit
action:
  window to fcn(old: array(WindowItem) -> array(WindowItem)) {
    if (a.len(old) > 0) {
      var thisBin = m.round((input["time"]) / <<WINDOW_WIDTH>>);
      var thatBin = m.round((a.head(old)["time"]) / <<WINDOW_WIDTH>>);
      if (thisBin != thatBin) {
        emit(a.mean(a.map(old, fcn(w: WindowItem -> double) w.x)));
        new(array(WindowItem), input)
      }
      else
        a.append(old, input)
    }
    else
      a.append(old, input)
  }
''', WINDOW_WIDTH=1.5)
engine, = PFAEngine.fromJson(pfaDocument)

for actual in range(100):
    bumpy = actual + random.gauss(0, 5)
    def emit(smooth):
        print "{0:6.3f}".format(smooth - actual),
    engine.emit = emit
    print "{0:6.3f} ".format(bumpy - actual),
    engine.action({"time": actual/10.0, "x": bumpy})
    print
```
