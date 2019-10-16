This page provides an introduction to using Hadrian. It deliberately mirrors the [Titus Basic Use](Titus-Basic-Use) page.

## Before you begin...

Download any [pre-built Hadrian JAR](Installation#case-2-you-want-to-use-pre-built-jar-files-for-one-of-the-hadrian-containers) that includes dependencies. This article was tested with Hadrian 0.8.3; newer versions should work with no modification. Scala >= 2.10 is required.

Launch a Scala prompt using that JAR as a classpath:

    > scala -cp hadrian-standalone-0.8.3-jar-with-dependencies.jar

and import `com.opendatagroup.hadrian.jvmcompiler.PFAEngine`:

```scala
Welcome to Scala version 2.10.5 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_45).
Type in expressions to have them evaluated.
Type :help for more information.

scala> import com.opendatagroup.hadrian.jvmcompiler.PFAEngine
```

## Simplest possible scoring engines

Let's start with an engine that merely adds 10 to each input. That's something we can write inline.

```scala
scala> val engine = PFAEngine.fromJson("""
     | {"input": "double",
     |  "output": "double",
     |  "action": {"+": ["input", 100]}}
     | """).head
engine: com.opendatagroup.hadrian.jvmcompiler.PFAEngine[AnyRef,AnyRef] = PFA_Engine_1@3f792b9b
```

For convenience, we could have written it in YAML (all of Hadrian's unit tests are written this way).

```scala
scala> val engine = PFAEngine.fromYaml("""
     | input: double
     | output: double
     | action: {+: [input, 100]}
     | """).head
engine: com.opendatagroup.hadrian.jvmcompiler.PFAEngine[AnyRef,AnyRef] = PFA_Engine_2@53e211ee
```

Note in both cases that we asked for the `.head` of what `PFAEngine.fromJson` and `PFAEngine.fromYaml` produces. In general, these functions produce a collection of [`PFAEngine`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.jvmcompiler.PFAEngine) objects from one PFA file (pass `multiplicity = 4` and drop `.head` to see that). These scoring engines can run in parallel and share memory. For now, though, we're only interested in one scoring engine.

By virtue of having created an engine, the PFA has been fully validated. If the PFA is not valid, you would see

   * a [Jackson](http://wiki.fasterxml.com/JacksonDocumentation) exception because the JSON wasn't valid;
   * a [SnakeYAML](https://code.google.com/p/snakeyaml/wiki/Documentation) exception because the YAML wasn't valid;
   * [`PFASyntaxException`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.errors.PFASyntaxException) if Hadrian could not build an [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) of the PFA from the JSON, for instance if a JSON field name is misspelled;
   * [`PFASemanticException`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.errors.PFASemanticException) if Hadrian could not build Java bytecode from the AST, for instance if data types don't match;
   * [`PFAInitializationException`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.errors.PFAInitializationException) if Hadrian could not create a scoring engine instance, for instance if the cell/pool data are incorrectly formatted.

Now run the scoring engine on some sample input:

```scala
scala> engine.action(java.lang.Double.valueOf(3.14))
res0: AnyRef = 103.14
```

For Java accessibility, the `action` method takes and returns boxed values of type `AnyRef` (`Object` in Java). See [Hadrian data format](Hadrian-Data-Format) for a complete menu.

You should only ever see one of the following exceptions at runtime

   * [`PFARuntimeException`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.errors.PFARuntimeException) if a PFA library function encountered an exceptional case, such as `a.max` of an empty list.
   * [`PFAUserException`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.errors.PFAUserException) if the PFA has explicit `{"error": "my error message"}` directives.
   * [`PFATimeoutException`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.errors.PFATimeoutException) if the PFA has some `"options": {"timeout": 1000}` set and a calculation takes too long.

### Emit-type engines

Of the three types of PFA scoring engine (map, emit, and fold), emit requires special attention in scoring. Map and fold engines yield results as the return value of the function (and fold does so cumulatively), but emit engines always return `null`. The only way to get results from them is by passing a callback function.

```scala
scala> val engine2 = PFAEngine.fromYaml("""
     | input: double
     | output: double
     | method: emit
     | action:
     |   - if:
     |       ==: [{"%": [input, 2]}, 0]
     |     then:
     |       - emit: input
     |       - emit: {/: [input, 2]}
     | """).head
engine2: com.opendatagroup.hadrian.jvmcompiler.PFAEngine[AnyRef,AnyRef] = PFA_Engine_2@4cacccbf

scala> import com.opendatagroup.hadrian.jvmcompiler.PFAEmitEngine
scala> val engine2AsEmit = engine2.asInstanceOf[PFAEmitEngine[AnyRef, AnyRef]]
engine2AsEmit: com.opendatagroup.hadrian.jvmcompiler.PFAEmitEngine[AnyRef,AnyRef] = PFA_Engine_2@4cacccbf

scala> def newEmit(x: AnyRef) =
     |   println("output: " + x.toString)
newEmit: (x: AnyRef)Unit

scala> engine2AsEmit.emit = newEmit
engine2AsEmit.emit: AnyRef => Unit = <function1>

scala> for (x <- 1 to 5) {
     |   println("input: " + x.toString)
     |   engine2.action(java.lang.Double.valueOf(x))
     | }
input: 1
input: 2
output: 2.0
output: 1.0
input: 3
input: 4
output: 4.0
output: 2.0
input: 5
```

### Data from serialized sources

The `PFAEngine` interface has methods for streaming data in and out of JSON, Avro, and CSV. Thus, we don't have to create data in Hadrian's internal format.

```scala
scala> val engine3 = PFAEngine.fromYaml("""
     | input: {type: map, values: int}
     | output: {type: array, items: int}
     | action: {map.values: input}
     | """).head
engine3: com.opendatagroup.hadrian.jvmcompiler.PFAEngine[AnyRef,AnyRef] = PFA_Engine_3@1d6a0962

scala> import com.opendatagroup.hadrian.data._

// the hard way

scala> val input = PFAMap.fromMap(Map("one" -> java.lang.Integer.valueOf(1), "two" -> java.lang.Integer.valueOf(2), "three" -> java.lang.Integer.valueOf(3)))
input: com.opendatagroup.hadrian.data.PFAMap[Integer] = {one: 1, two: 2, three: 3}

scala> val output = engine3.action(input)
output: AnyRef = [1, 2, 3]

scala> output.getClass.getName
res0: String = com.opendatagroup.hadrian.data.PFAArray

// the easy way

scala> val input = engine3.jsonInput("""{"one": 1, "two": 2, "three": 3}""")               
input: AnyRef = {one: 1, two: 2, three: 3}

scala> val output = engine3.action(input)
output: AnyRef = [1, 2, 3]

scala> engine3.jsonOutput(output)
res1: String = [1,2,3]
```

### Snapshots and reverting

Snapshots are representations of a PFA engine's state at a moment in time. They are only relevant if the engine has mutable state. Let's start by making a mutable scoring engine and filling it with some state.

```scala
scala> val engine4 = PFAEngine.fromYaml("""
     | input: int
     | output: {type: array, items: int}
     | cells:
     |   history:
     |     type: {type: array, items: int}
     |     init: []
     | action:
     |   cell: history
     |   to: {a.append: [{cell: history}, input]}
     | """).head

scala> engine4.action(java.lang.Integer.valueOf(1))
res0: AnyRef = [1]
scala> engine4.action(java.lang.Integer.valueOf(2))
res1: AnyRef = [1, 2]
scala> engine4.action(java.lang.Integer.valueOf(3))
res2: AnyRef = [1, 2, 3]
scala> engine4.action(java.lang.Integer.valueOf(4))
res3: AnyRef = [1, 2, 3, 4]
scala> engine4.action(java.lang.Integer.valueOf(5))
res4: AnyRef = [1, 2, 3, 4, 5]
```

The `snapshot` method locks the scoring engine and turns the state of the engine into a new AST that could be immediately serialized as a PFA file.

```scala
scala> engine4.snapshot
res5: com.opendatagroup.hadrian.ast.EngineConfig = {"name":"Engine_4","method":"map","input":"int","output":{"type":"array","items":"int"},"action":[{"cell":"history","to":{"a.append":[{"cell":"history"},"input"]}}],"cells":{"history":{"type":{"type":"array","items":"int"},"init":[1,2,3,4,5],"shared":false,"rollback":false}}}
```

The `snapshotCell` and `snapshotPool` methods are more focused: they do not lock the whole scoring engine and only report one cell or pool. The value is returned in Hadrian's internal format, so they would need to be explicitly converted into a serialized format.

```scala
scala> engine4.snapshotCell("history")
res6: AnyRef = [1, 2, 3, 4, 5]
```

The `revert` method rolls back a scoring engine to the state described by its original PFA file. It is used by reducers in map-reduce to ensure that each key in a key-value stream is computed independently.

```scala
scala> engine4.revert()

scala> engine4.action(java.lang.Integer.valueOf(6))
res7: AnyRef = [6]
scala> engine4.action(java.lang.Integer.valueOf(7))
res8: AnyRef = [6, 7]
scala> engine4.action(java.lang.Integer.valueOf(8))
res9: AnyRef = [6, 7, 8]
scala> engine4.action(java.lang.Integer.valueOf(9))
res10: AnyRef = [6, 7, 8, 9]
scala> engine4.action(java.lang.Integer.valueOf(10))
res11: AnyRef = [6, 7, 8, 9, 10]
```

### External function calls

PFA user-defined functions are intended to simplify repetitive tasks, but they can also be used as an alternate entry point into the scoring engine, distinct from the normal input-output stream. It is only relevant to do so on scoring engines with mutable state.

```scala
val engine5 = PFAEngine.fromYaml("""
input: int
output: {type: array, items: int}
cells:
  history:
    type: {type: array, items: int}
    init: []
action:
  cell: history
  to: {a.append: [{cell: history}, input]}
fcns:
  getItem:
    params: [{i: int}]
    ret: int
    do:
      cell: history
      path: [i]
  flipList:
    params: []
    ret: "null"
    do:
      - cell: history
        to: {a.reverse: {cell: history}}
      - null
""").head

scala> engine5.action(java.lang.Integer.valueOf(100))
res0: AnyRef = [100]
scala> engine5.action(java.lang.Integer.valueOf(101))
res1: AnyRef = [100, 101]
scala> engine5.action(java.lang.Integer.valueOf(102))
res2: AnyRef = [100, 101, 102]
scala> engine5.action(java.lang.Integer.valueOf(103))
res3: AnyRef = [100, 101, 102, 103]
scala> engine5.action(java.lang.Integer.valueOf(104))
res4: AnyRef = [100, 101, 102, 103, 104]
```

You can get references to these functions by name. It is necessary to specify the number of arguments.

```scala
scala> val getItem = engine5.fcn1("getItem")
getItem: AnyRef => AnyRef = <function1>

scala> val flipList = engine5.fcn0("flipList")
flipList: () => AnyRef = <function0>
```

When you call them, you have to pass them data in Hadrian's internal format.

```scala
scala> getItem(java.lang.Integer.valueOf(1))
res5: AnyRef = 101

scala> getItem(java.lang.Integer.valueOf(3))
res6: AnyRef = 103
```

The functions may or may not return a value, and they may or may not have side-effects. This is the only recommended way to change cell/pool values from outside of a scoring engine.

```scala
scala> flipList()
res7: AnyRef = null

scala> engine5.action(java.lang.Integer.valueOf(0))
res8: AnyRef = [104, 103, 102, 101, 100, 0]
```

### Abstract Syntax Tree

The PFA AST is an immutable tree structure built from the serialized JSON, stored in `engine.config`, which is an [`EngineConfig`](http://modelop.github.io//hadrian/hadrian-0.8.3/index.html#com.opendatagroup.hadrian.ast.EngineConfig). You can query anything about the original PFA file in a structured way through this AST. For instance,

```scala
scala> engine.config.action.head
res0: com.opendatagroup.hadrian.ast.Expression = {"+":["input",100]}

scala> engine.config.action.head.getClass.getName
res1: String = com.opendatagroup.hadrian.ast.Call

scala> engine.config.input.avroType
res2: com.opendatagroup.hadrian.datatype.AvroType = "double"
```

There are also a few methods for recursively walking over the AST. The `collect` method applies a partial function to all nodes in the tree and produces a list of matches. For instance, to get all `Expressions` (function calls like "+", symbol references like "input", and literal values like "100"), do

```scala
scala> import com.opendatagroup.hadrian.ast.Expression
scala> engine.config collect {case x: Expression => x}
res3: Seq[com.opendatagroup.hadrian.ast.Expression] = List({"+":["input",100]}, "input", 100)
```

You can also build new scoring engines by passing a replacement function. This one turns instances of 100 into 999. You can do quite a lot just by crafting the right partial function.

```scala
scala> import com.opendatagroup.hadrian.ast.LiteralInt
scala> engine.config replace {case x: LiteralInt if (x.value == 100) => LiteralInt(999)}
res4: com.opendatagroup.hadrian.ast.Ast = {"name":"Engine_2","method":"map","input":"double","output":"double","action":[{"+":["input",999]}]}
```

In fact, this is how Hadrian generates code in general. A `walk` over the tree checks for semantic errors while calling a `Task` at each node. Usually, this `Task` is to create Java code, but it could be anything. This small example generates Lisp.


```scala
scala> import com.opendatagroup.hadrian.ast._
scala> import com.opendatagroup.hadrian.datatype._
scala> import com.opendatagroup.hadrian.options.EngineOptions
scala> import com.opendatagroup.hadrian.signature.PFAVersion

scala> trait LispCode extends TaskResult

scala> case class LispFunction(car: String, cdr: Seq[LispCode]) extends LispCode {
     |   override def toString() = "(" + car + cdr.map(" " + _.toString).mkString + ")"
     | }

scala> case class LispSymbol(name: String) extends LispCode {
     |   override def toString() = name
     | }

scala> object GenerateLisp extends Task {
     |   def apply(context: AstContext, engineOptions: EngineOptions, resolvedType: Option[Type]): TaskResult = context match {
     |     case Call.Context(_, _, fcn: LibFcn, args: Seq[TaskResult], _, _, _) => LispFunction(fcn.name, args.map(_.asInstanceOf[LispCode]))
     |     case Ref.Context(_, _, name: String) => LispSymbol(name)
     |     case LiteralInt.Context(_, _, value: Int) => LispSymbol(value.toString)
     |   }
     | }

scala> val symbolTable = SymbolTable.blank
scala> symbolTable.put("input", AvroDouble())
scala> engine.config.action.head.walk(GenerateLisp, symbolTable, FunctionTable.blank, new EngineOptions(Map(), Map()), PFAVersion(0, 8, 1))._2
res5: com.opendatagroup.hadrian.ast.TaskResult = (+ input 100)

scala> val engine6 = PFAEngine.fromYaml("""
     | input: double
     | output: double
     | action: {+: [{/: [input, 2]}, {m.sqrt: input}]}
     | """).head

scala> engine6.config.action.head.walk(GenerateLisp, symbolTable, FunctionTable.blank, new EngineOptions(Map(), Map()))._2
res6: com.opendatagroup.hadrian.ast.TaskResult = (+ (/ input 2) (m.sqrt input))
```
