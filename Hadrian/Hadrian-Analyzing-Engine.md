## Analyzing a PFA engine

After loading a PFA file, Hadrian provides a list of [`com.opendatagroup.hadrian.jvmcompiler.PFAEngine`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.jvmcompiler.PFAEngine) instances. Because of intentional restrictions in the PFA language, a lot of useful information is available about the algorithm it represents without running it.

The [Hadrian Basic Use](https://github.com/opendatagroup/hadrian/wiki/Hadrian-Basic-Use) page describes how to create a `PFAEngine`, execute it, take snapshots and revert its state, and look at or convert its Abstract Syntax Tree (AST). This page explains how to statically analyze the `PFAEngine` without executing it.

### Call graph

A call graph is a directed graph in which functions are nodes and if function A calls function B, there is a directed edge from A to B. This graph can be used to determine if a PFA file calls any functions that are deemed unsafe or otherwise undesirable, if they're recursive, if the scoring engine has mutable state, etc.

The call graph is stored in `PFAEngine.callGraph`, which is a [`Map[String, Set[String]]`](http://www.scala-lang.org/api/current/#scala.collection.immutable.Map) from a string-based function name to the set of all functions it calls. Special forms and methods like `begin`, `action`, and `end` are given in parentheses.

`PFAEngine` has several convenience functions for common applications:

   * `calledBy`: determine which functions call a given function (reverse lookup, opposite of the `callGraph`'s `apply` method).
   * `callDepth`: determine how many levels deep this function calls other functions, terminating on library functions and special forms. The return type is `Double` so that recursive functions can be expressed as `Infinity`.
   * `isRecursive`: determine if this function _directly_ calls itself.
   * `hasRecursive`: determine if this function has any recursive loops (`isRecursive` implies `hasRecursive`, but not the other way around).
   * `hasSideEffects`: determine if a function has `"(cell-to)"` or `"(pool-to)"` anywhere in its subgraph. These are the only ways to modify the persistent state of a PFA engine.

## Mutability check

To determine if `engine`, an instance of `PFAEngine`, is mutable, call

```scala
engine.hasSideEffects("(action)")
```

Although Hadrian has transparent, built-in support for concurrency within a JVM process, scoring engines running in different processes or on different computers cannot take advantage of this mechanism. An execution environment may want to forbid or handle mutable PFA differently from immutable PFA.

## Analyzing cells and pools

All of the persistent state of a PFA scoring engine (mutable or immutable) is contained in its cells (single, global variables) and pools (R-like environments, containing global variables that can be created or destroyed at runtime). If the scoring engine is mutable, its changing state can be monitored without creating snapshots of its entire state.

   * `analyzeCell` takes a cell name and an analysis, an arbitrary Scala function, and returns the result of that function when applied to the given cell.
   * `analyzePool` takes a pool name and an analysis, an arbitrary Scala function, and returns a `Map[String, X]` of that function's results when applied to each element of the pool.

## Memory use

Hadrian can also track memory use of a running PFA engine. General Java tools exist for tracking the total memory used by a JVM or the memory used by specific classes, but neither of these provide granularity at the level of a PFA engine, which consists of many classes and not the whole JVM.

[`com.opendatagroup.hadrian.memory.EngineReport`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.memory.EngineReport) provides an analysis of the memory used by one `PFAEngine`'s persistent state, and [`com.opendatagroup.hadrian.memory.EnginesReport`](http://modelop.github.io//hadrian/hadrian-0.8.1/index.html#com.opendatagroup.hadrian.memory.EnginesReport) provides an analysis of memory used by a collection of `PFAEngine` instances that may share memory.

Here is how to use them on `engine` (an instance of `PFAEngine`) and `engines` (a Scala collection of `PFAEngine` instances):

```scala
val report1 = EngineReport(engine)
println(report1.total)
println(report)

val report2 = EnginesReport(engines)
println(report2.sharedCells)
println(report2)
```

`EngineReport` and `EnginesReport` are both immutable case classes with meaningful fields and a convenient `toString` method for generating a tabular report.

The analysis is based on counting existing data elements and multiplying by appropriate factors for each type of data element (including Java's object padding, distinctions between boxed and unboxed primitives, etc.). For large collections (arrays and maps), approximations are used, since the underlying data is represented as a tree of unknown balancing. This method does not account for structural sharing of immutable data and is therefore an overestimate. It also does not count data that is beyond scope but not yet garbage collected, so it is a more stable measure than total heap space used.

Some data types are fast to compute, such as an array of integers, since one only needs to know the size of an integer and the number of elements in the array. Others are slow, such as an array of strings, since one must traverse the array and add memory usage of each variable-length string.
