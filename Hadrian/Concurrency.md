# Concurrency

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import threading
    >>> import time
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## Running multiple scoring engines simultaneously

As a first illustration, let's make a simple scoring engine (incidentally, the smallest possible number of bytes for a valid PFA file),

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: int
output: int
action: input
''')
```

and make ten of them.

```python
engines = PFAEngine.fromJson(pfaDocument, multiplicity=10)
```

To run them at the same time, we need to put them into threads. (Don't worry about Python's [global interpreter lock](https://wiki.python.org/moin/GlobalInterpreterLock): even though this aspect of the Python implementation prevents us from maximizing all processors on a machine, we can still demonstrate concurrency issues.)

```python
output = []
class EngineThread(threading.Thread):
    def __init__(self, engine):
        super(EngineThread, self).__init__()
        self.engine = engine
    def run(self):
        instance = self.engine.instance  # each has a unique number
        for i in xrange(100):
            output.append(self.engine.action(instance))
            time.sleep(0.01)  # 10 ms

threads = map(EngineThread, engines)
```

Run them all and look at the output. The exact order of the numbers in the output depends on a race condition (which thread ran at what time), but they should be pretty well mixed.

```python
for t in threads: t.start()

print output
```

Although the scoring engines ran at the same time, they produced exactly the same output that they would have if run separately. The same would be true if they shared read-only data; we only get into (potential) trouble if multiple scoring engines share mutable state.

## Multiple scoring engines with shared mutable state

Let's have them share a counter and try to update it.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: null
output: null
cells:
  counter(int, shared: true) = 0
action:
  var currentValue = counter;
  counter = currentValue + 1;
  null
''')

engines = PFAEngine.fromJson(pfaDocument, multiplicity=10)

class EngineThread(threading.Thread):
    def __init__(self, engine):
        super(EngineThread, self).__init__()
        self.engine = engine
    def run(self):
        for i in xrange(100):
            self.engine.action(None)

threads = map(EngineThread, engines)

for t in threads: t.start()

print engines[0].cells["counter"].value
```

You might think that this counter should reach 1000 because 10 engines each updated it 100 times. (I get values of about 100-200 in subsequent runs with my computer's thread-switching.) The problem is that the "get counter value" and "update counter value" operations can be interleaved, such that a scoring engine's `currentValue` can be out of date before it can add 1 to it.

**Any updates to shared, mutable state should be performed in transactions.**

A transaction is a function passed to a cell that takes the old value and returns a new value. The steps involved in the update may be as simple or as complicated as necessary. The purpose of the function is to define the beginning and the end of a set of operations that can't be interrupted.

Here's an example:

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: null
output: null
cells:
  counter(int, shared: true) = 0
action:
  counter to fcn(old: int -> int) old + 1;
  null
''')

engines = PFAEngine.fromJson(pfaDocument, multiplicity=10)
threads = map(EngineThread, engines)
for t in threads: t.start()

print engines[0].cells["counter"].value
```

Now the value should be 1000. The transaction function is declared inline in this example, though it could be a named user-defined function (or even a library function, if one is applicable). Transactions are treated as atomic: no two transactions are allowed to operate on the same cell at the same time.

## Concurrency issues you would ordinarily have to worry about

In a generic programming language, the above could be accomplished by locks, but PFA implementations (like Titus and Hadrian) apply the locks for you. Furthermore, locks in a generic programming language would also block reading, but PFA cell-reading is never blocked; only writing. (This is possible because PFA values are all immutable, so cells are updated by replacement only after the new value is fully constructed. The old value is available for reading throughout the transaction. Read more about PFA concurrency handling [here](http://scoringengine.org/docs/tutorial3/#concurrent-access-of-shared-data).)

This kind of write-access blocking would lead to the possibility of [deadlock](https://en.wikipedia.org/wiki/Deadlock) in a generic programming language. PFA excludes this possibility by denying the "circular wait" condition: transactions are not allowed to initiate other transactions (even through a function call of a function call: the call graph is deeply checked).

Below is an example of a scoring engine that is denied by Titus (as well as Hadrian and any fully-compliant PFA implementation). It should fail with an "inline function in cell-to or pool-to invokes a cell-to" `PFAInitializationError`.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: null
output: null
cells:
  resourceA(int, shared: true) = 0;
  resourceB(int, shared: true) = 0;
action:
  resourceA to fcn(a: int -> int) {
    resourceB to fcn(b: int -> int) b + 1;
    a + 1;
  };
  null
''')
```

Here is another, whose circular access goes through several layers of indirection. Now the error should be "inline function in cell-to or pool-to invokes function "u.obfuscate1", which has side-effects".

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: null
output: null
cells:
  resourceA(int, shared: true) = 0;
  resourceB(int, shared: true) = 0;
action:
  resourceA to fcn(a: int -> int) {
    u.obfuscate1();
    a + 1;
  };
  null
fcns:
  obfuscate1 = fcn(-> null) u.obfuscate2();
  obfuscate2 = fcn(-> null) u.obfuscate3();
  obfuscate3 = fcn(-> null) u.obfuscate4();
  obfuscate4 = fcn(-> null) {
    resourceB to fcn(b: int -> int) b + 1;
    null
  }
''')
```

## Granularity of transactions

Even if a transaction operates on a small part of a data structure, such as one item in the "counters" map below, write access to any other part of that data structure has to wait.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: string
output: null
cells:
  counters(map(int), shared: true) =
    {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0,
     "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
action:
  counters[input] to fcn(old: int -> int) old + 1;
  null
''')

engines = PFAEngine.fromJson(pfaDocument, multiplicity=10)

class EngineThread(threading.Thread):
    def __init__(self, engine):
        super(EngineThread, self).__init__()
        self.engine = engine
    def run(self):
        instance = str(self.engine.instance)
        for i in xrange(100):
            self.engine.action(instance)

threads = map(EngineThread, engines)

for t in threads: t.start()
```

Even though no two engines ever wanted to update the same counter in the above example, each write had to wait for the previous to finish. It works, but it doesn't scale to very large maps.

The following example uses a _pool_, which differs from a _cell_ with map type in that it allows concurrent writes to different items in the map. Its behavior is nearly the same: a single scoring engine can't tell the difference, but the global order of operations will differ because they're not forced to be sequential.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: string
output: null
pools:
  // difference #1: counters has type int, rather than map(int).
  counters(int, shared: true) =
    {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0,
     "5": 0, "6": 0, "7": 0, "8": 0, "9": 0}
action:
  // difference #2: an init value is needed to handle new keys at runtime.
  counters[input] to fcn(old: int -> int) old + 1 init 0;
  null
''')

engines = PFAEngine.fromJson(pfaDocument, multiplicity=10)
threads = map(EngineThread, engines)
for t in threads: t.start()
```

This is why segmentation usually uses pools: if the number of segments is large and the submodels are mutable, a pool of type X will have dramatically better performance than a cell of type map(X). As long as different scoring engines are unlikely to want to write to the same pool item at the same time, they can run in parallel.

## Design considerations for PFA data structures

The above restrictions, especially the rejection of the "circular wait" condition, force the following good practice in data structure design: related parts should be local. That is, if two parts of a data structure must be updated in lock-step, such as the numerator and denominator of some ratio, they should be close to each other in the data structure tree and can never be in different cells or different pool items.

For instance, the following bad practice (common in ad-hoc data analysis code) cannot be implemented in a consistent way.

```python
pfaDocument = titus.prettypfa.jsonNode('''
input: record(index: int, x: double)
output: double
cells:
  numer(array(double), shared: true) = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
  denom(array(double), shared: true) = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
action:
  numer[input.index] to fcn(old: double -> double) old + input.x;
  denom[input.index] to fcn(old: double -> double) old + 1.0;
  numer[input.index] / denom[input.index]
''')
```

The numerators can be consistently updated, the denominators can be consistently updated, but there's never any guarantee that the numerators are in sync with the denominators. Another scoring engine may increment the numerators while this scoring engine is still working on the denominators. (At the end of the run, after all operations have been applied, they're consistent, but not necessarily at any point along the way.)

The intended behavior can be implemented by putting the associated numerator items and denominator items close to each other, like this:

```python
pfaDocument = titus.prettypfa.jsonNode('''
types:
  Ratio = record(Ratio, numer: double, denom: double)
input: record(index: int, x: double)
output: double
cells:
  ratios(array(Ratio), shared: true) = [
    {numer: 0, denom: 0}, {numer: 0, denom: 0},
    {numer: 0, denom: 0}, {numer: 0, denom: 0},
    {numer: 0, denom: 0}, {numer: 0, denom: 0},
    {numer: 0, denom: 0}, {numer: 0, denom: 0},
    {numer: 0, denom: 0}, {numer: 0, denom: 0}]
action:
  var r = ratios[input.index] to fcn(old: Ratio -> Ratio) {
    new(Ratio, numer: old.numer + input.x, denom: old.denom + 1.0)
  };
  r[input.index, "numer"] / r[input.index, "denom"]
''')
```

Now the same transaction includes both the numerator-update and the denominator-update, so it will always be consistent.

This style not only allows us to guarantee consistency, it also encourages the use of named records and fields (good for self-documentation), it encourages the use of functional programming (`a.map`, `a.reduce`, `map.map`, and friends), which makes better use of value-immutability, and it avoids "long distance effects" that plague programs based on synchronized lists.
