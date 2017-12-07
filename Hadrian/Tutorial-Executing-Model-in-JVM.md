# Tutorial 4: executing a model in Hadrian-Standalone

## Before you begin...

[Download the Hadrian-Standalone jar-with-dependencies](https://github.com/opendatagroup/hadrian/wiki/Installation#case-2-you-want-to-use-pre-built-jar-files-for-one-of-the-hadrian-containers). This article was tested with Hadrian 0.7.1; newer versions should work with no modification (other than version numbers in file names).

Check the JAR by printing its help message.

    java -jar hadrian-standalone-0.7.1-jar-with-dependencies.jar --help    
     
    Usage: java -jar hadrian-standalone.jar [options] engineFileName.pfa|json|yaml|yml|py [inputFile.json|avro]

      -n <value> | --numberOfEngines <value>
            number of engines to run (default: 1)
      -i <value> | --inputFormat <value>
            input format: "avro" (default), "json", "json+schema", "csv", "csv+header"
      -o <value> | --outputFormat <value>
            output format: "avro" (default), "json", "json+schema", "csv", or "csv+header"
      -s baseNameOrPath | --saveState baseNameOrPath
            base file name for saving the scoring engine state (a directory, file name prefix, or both)
      --printTime
            print average time of action to standard error (approximately every 10 seconds, does not include data input/output)
      --debug
            print out auto-generated Java code for PFA engine
      engineFileName.pfa|json|yaml|yml|py
            scoring engine encoded in PFA (pfa|json|yaml|yml) or Python (py)
      inputFile.json|avro
            optional input files (if omitted, data are taken from standard input)
      --help
            print this help message

    Hadrin standalone runs a PFA-encoded scoring engine as a standard
    input to standard output process.  If multiple engines are specified,
    these engines run in parallel and may share state.  If a --saveState
    option is provided, the final state is written to a file at the end of
    input.

If you completed [Tutorial 2](Tutorial-Small-Model-R), you would have created `myModel.pfa` and `myData.jsons` that we'll use in this tutorial. If you haven't, download [myModel.pfa](https://github.com/opendatagroup/hadrian/wiki/model/myModel.pfa) and download [myData.jsons](https://github.com/opendatagroup/hadrian/wiki/data/myData.jsons).

## Executing a scoring engine

Hadrian is a library that can be embedded in any JVM-based system, such as Hadoop, Storm, Spark, servlet containers, end-user applications, etc., but it has to be embedded in some system in order to use it. Hadrian-Standalone is a simple wrapper that lets you run Hadrian as a shell command.

Most of the complexity comes from handling multiple input and output formats (something that is outside the scope of PFA, but necessary for any complete workflow). Since our input data is in JSONS format (each line of the input file is a JSON-serialized object) and we want readable results, let's use `-i json -o json`.

```
java -jar hadrian-standalone-0.7.1-jar-with-dependencies.jar -i json -o json myModel.pfa myData.jsons
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"good","breakdown":{"good":0.81,"bad":0.19}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"good","breakdown":{"good":0.8,"bad":0.2}}
{"winner":"good","breakdown":{"bad":0.23,"good":0.77}}
{"winner":"bad","breakdown":{"good":0.02,"bad":0.98}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
{"winner":"bad","breakdown":{"bad":1.0,"good":0.0}}
...
```

## Executing a scoring engine manually

Since this JAR contains Hadrian and all of its dependencies, we can use it as a classpath for any JVM read-evaluate-print-loop, such as Scala, Groovy, Clojure, etc. Assuming that you have [Scala](http://www.scala-lang.org/download/2.10.4.html), try the following:

    scala -cp hadrian-standalone-0.7.1-jar-with-dependencies.jar
    Welcome to Scala version 2.10.4 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_60).
    Type in expressions to have them evaluated.
    Type :help for more information.

    scala> import com.opendatagroup.hadrian.jvmcompiler.PFAEngine

If that works, you can load the engine using the `PFAEngine.fromJson` function, and use that to make data iterators.

```Scala
val engine = PFAEngine.fromJson(new java.io.File("myModel.pfa")).head

val inputDataStream = engine.jsonInputIterator(new java.io.FileInputStream("myData.jsons"))
val outputDataStream = engine.jsonOutputDataStream(System.out, writeSchema = false)
```

And now loop over the data.

```Scala
while (inputDataStream.hasNext)
  outputDataStream.append(engine.action(inputDataStream.next()))
```
