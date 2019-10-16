The [Hadrian Basic Use](Hadrian-Basic-Use) page provides enough information to embed the Hadrian library in an application. This tutorial acts as a check-list with an explicit example.

## Before you begin...

This article was tested with Hadrian 0.8.3; newer versions should work with no modification. Scala >= 2.10 and sbt is required. [Download sbt here](http://www.scala-sbt.org/download.html) and test it by typing `sbt` on the command line.

Also download the [Iris dataset](https://github.com/opendatagroup/hadrian/wiki/data/iris.csv) and a [simple tree classification](https://github.com/opendatagroup/hadrian/wiki/models/simpleIrisModel.pfa) for it.

## Example application

In this tutorial, we will write a Scala application that runs a PFA engine on data from a CSV file, writing the result as a CSV file.

Create directory `minihadrian` and add a file named `build.sbt` with the following contents:

```sbt
libraryDependencies += "com.opendatagroup" % "hadrian" % "0.8.3"
resolvers += "opendatagroup" at "http://repository.opendatagroup.com/maven"
```

Next, add a file named 'minihadrian.scala' with the following contents:

```scala
import com.opendatagroup.hadrian.jvmcompiler.defaultPFAVersion

object MiniHadrian {
  def main(args: Array[String]) {
    println(s"PFA version $defaultPFAVersion")
  }
}
```

Run `sbt` in the `minihadrian` directory (close and restart it if it had been running before adding `build.sbt`). You should see

    % sbt
    [info] Set current project to minihadrian (in build file:/tmp/minihadrian/)
    > run
    [info] Running MiniHadrian 
    PFA version 0.8.3
    [success] Total time: 1 s, completed Nov 17, 2015 2:59:52 PM
    > 

(possibly with different version numbers).

### Adding a PFA engine reader

Add command-line argument handling and load a PFA file in `minihadrian.scala`:

```scala
import java.io.FileInputStream
import com.opendatagroup.hadrian.jvmcompiler.PFAEngine

object MiniHadrian {
  def main(args: Array[String]) {
    // read command-line arguments
    val Array(pfaEngineName, inputDataName, outputDataName) = args

    // load the PFA file into a scoring engine
    val engine = PFAEngine.fromJson(new FileInputStream(pfaEngineName)).head

    // print something about it to the screen
    engine.callGraph("(action)").foreach(println)
  }
}
```

Then re-run it in sbt:

    > run simpleIrisModel.pfa iris.csv results.csv
    [info] Compiling 1 Scala source to /tmp/minihadrian/target/scala-2.10/classes...
    [info] Running MiniHadrian simpleIrisModel.pfa iris.csv results.csv
    model.tree.simpleWalk
    model.tree.simpleTest
    attr
    cell
    new (object)
    let
    (string)
    [success] Total time: 10 s, completed Nov 17, 2015 3:17:01 PM

If you see this, then your MiniHadrian is loading the PFA file (and telling you which functions the `action` method would call, if we called it).

### Running the PFA engine on input data

Now add code to evaluate the model for each input data record, printing the results to the screen.

```scala
import java.io.FileInputStream
import com.opendatagroup.hadrian.jvmcompiler.PFAEngine

object MiniHadrian {
  def main(args: Array[String]) {
    // read command-line arguments
    val Array(pfaEngineName, inputDataName, outputDataName) = args

    // load the PFA file into a scoring engine
    val engine = PFAEngine.fromJson(new FileInputStream(pfaEngineName)).head

    // make an iterator for the input data
    val inputData = engine.csvInputIterator(new FileInputStream(inputDataName))

    // run the engine over the input data
    while (inputData.hasNext)
      println(engine.action(inputData.next()))

  }
}
```

and re-run it in sbt (same arguments, longer output).

### Writing to the output file

Now add the output code:

```scala
import java.io.FileInputStream
import java.io.FileOutputStream
import com.opendatagroup.hadrian.jvmcompiler.PFAEngine

object MiniHadrian {
  def main(args: Array[String]) {
    // read command-line arguments
    val Array(pfaEngineName, inputDataName, outputDataName) = args

    // load the PFA file into a scoring engine
    val engine = PFAEngine.fromJson(new FileInputStream(pfaEngineName)).head

    // make an iterator for the input data
    val inputData = engine.csvInputIterator(new FileInputStream(inputDataName))

    // make an appender for the output data
    val outputData = engine.csvOutputDataStream(new FileOutputStream(outputDataName))

    // run the engine over the input data
    while (inputData.hasNext)
      outputData.append(engine.action(inputData.next()))

    // remember to close the output stream so that it flushes!
    outputData.close()
  }
}
```

and re-run it in sbt (same arguments, no visible output; the output goes to `results.csv`).

### Checklist item #1: handle emit

One easily overlooked case is handling for emit-type engines. With MiniHadrian as defined above, map-type and fold-type engines would work properly, but emit-type engines would run and produce nulls, rather than output data. Our test example is a map-type engine, so we wouldn't notice the oversight.

The modification below solves that issue.

```scala
import java.io.FileInputStream
import java.io.FileOutputStream
import com.opendatagroup.hadrian.jvmcompiler.PFAEngine
import com.opendatagroup.hadrian.jvmcompiler.PFAEmitEngine

object MiniHadrian {
  def main(args: Array[String]) {
    // read command-line arguments
    val Array(pfaEngineName, inputDataName, outputDataName) = args

    // load the PFA file into a scoring engine
    val engine = PFAEngine.fromJson(new FileInputStream(pfaEngineName)).head

    // make an iterator for the input data
    val inputData = engine.csvInputIterator(new FileInputStream(inputDataName))

    // make an appender for the output data
    val outputData = engine.csvOutputDataStream(new FileOutputStream(outputDataName))

    // run the engine over the input data
    engine match {
      case emitEngine: PFAEmitEngine[_, _] =>
        emitEngine.emit = {x: AnyRef => outputData.append(x)}
        while (inputData.hasNext)
          engine.action(inputData.next())

      case _ =>
        while (inputData.hasNext)
          outputData.append(engine.action(inputData.next()))
    }

    // remember to close the output stream so that it flushes!
    outputData.close()
  }
}
```

Perhaps as a PFA exercise, you could try modifying `simpleIrisModel.pfa` to be an emit-type engine: change `"method": "map"` to `"method": "emit"` and wrap the last (second) item in the `"action"` array in `{"emit": ...}`. Alternatively, [get a modified copy here](https://github.com/opendatagroup/hadrian/wiki/models/simpleIrisModel_emit.pfa).

The emit-type engine should produce output when you run it in sbt.

### Checklist item #2: handle begin and end

Not all data streams end, but they all begin, so MiniHadrian as defined above is missing an important part of the PFA workflow. We simply need to call `engine.begin()` and `engine.end()` before and after the data stream.

Add these method calls to `minihadrian.scala`:

```scala
import java.io.FileInputStream
import java.io.FileOutputStream
import com.opendatagroup.hadrian.jvmcompiler.PFAEngine
import com.opendatagroup.hadrian.jvmcompiler.PFAEmitEngine

object MiniHadrian {
  def main(args: Array[String]) {
    // read command-line arguments
    val Array(pfaEngineName, inputDataName, outputDataName) = args

    // load the PFA file into a scoring engine
    val engine = PFAEngine.fromJson(new FileInputStream(pfaEngineName)).head

    // make an iterator for the input data
    val inputData = engine.csvInputIterator(new FileInputStream(inputDataName))

    // make an appender for the output data
    val outputData = engine.csvOutputDataStream(new FileOutputStream(outputDataName))

    // do the begin phase
    engine.begin()

    // run the engine over the input data
    engine match {
      case emitEngine: PFAEmitEngine[_, _] =>
        emitEngine.emit = {x: AnyRef => outputData.append(x)}
        while (inputData.hasNext)
          engine.action(inputData.next())

      case _ =>
        while (inputData.hasNext)
          outputData.append(engine.action(inputData.next()))
    }

    // do the end phase
    engine.end()

    // remember to close the output stream so that it flushes!
    outputData.close()
  }
}
```

To test this, you'll need to add `"begin": {"log": {"string": "Beginning..."}}` and `"end": {"log": {"string": "Ending..."}}` as top-level JSON items, e.g. just before the last curly bracket. Make sure to include the appropriate commas.

Now sbt should show the log messages.

    > run simpleIrisModel.pfa iris.csv results.csv
    [info] Running MiniHadrian simpleIrisModel.pfa iris.csv results.csv
    "Beginning..."
    "Ending..."
    [success] Total time: 2 s, completed Nov 17, 2015 3:42:11 PM

### Checklist item #3: handle logging

Currently, MiniHadrian sends PFA log output to standard output. Here's an example of using a real logging system.

First, add `log4j` to the `build.sbt` file (below) and restart sbt.

```sbt
libraryDependencies += "log4j" % "log4j" % "1.2.17"
libraryDependencies += "com.opendatagroup" % "hadrian" % "0.8.3"
resolvers += "opendatagroup" at "http://repository.opendatagroup.com/maven"
```

Next, add a Log4j configuration file named `log4j.xml`:

```xml
<!DOCTYPE log4j:configuration SYSTEM "log4j.dtd">
<log4j:configuration debug="true" xmlns:log4j='http://jakarta.apache.org/log4j/'>
    <appender name="consoleAppender" class="org.apache.log4j.ConsoleAppender">
        <layout class="org.apache.log4j.PatternLayout">
            <param name="ConversionPattern" value="%d{yyyy-MM-dd_HH:mm:ss.SSS} %5p [%t]: %m%n"/>
        </layout>
    </appender>
    <root>
        <level value="INFO"/>
        <appender-ref ref="consoleAppender"/>
    </root>
</log4j:configuration>
```

Finally, add the Log4j handling in `minihadrian.scala`:

```scala
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import org.apache.log4j
import com.opendatagroup.hadrian.jvmcompiler.PFAEngine
import com.opendatagroup.hadrian.jvmcompiler.PFAEmitEngine

object MiniHadrian {
  def main(args: Array[String]) {
    // read command-line arguments
    val Array(pfaEngineName, inputDataName, outputDataName) = args

    // load the PFA file into a scoring engine
    val engine = PFAEngine.fromJson(new FileInputStream(pfaEngineName)).head

    // set up a logger and send PFA log data to it
    val logger = log4j.Logger.getLogger("MiniHadrian")
    log4j.xml.DOMConfigurator.configure(new File("log4j.xml").toURI.toURL)
    engine.log = {(x: String, ns: Option[String]) =>
      logger.info(ns.mkString + x)
    }

    // make an iterator for the input data
    val inputData = engine.csvInputIterator(new FileInputStream(inputDataName))

    // make an appender for the output data
    val outputData = engine.csvOutputDataStream(new FileOutputStream(outputDataName))

    // do the begin phase
    engine.begin()

    // run the engine over the input data
    engine match {
      case emitEngine: PFAEmitEngine[_, _] =>
        emitEngine.emit = {x: AnyRef => outputData.append(x)}
        while (inputData.hasNext)
          engine.action(inputData.next())

      case _ =>
        while (inputData.hasNext)
          outputData.append(engine.action(inputData.next()))
    }

    // do the end phase
    engine.end()

    // remember to close the output stream so that it flushes!
    outputData.close()
  }
}
```

Now the output of sbt run should be:

    > run simpleIrisModel.pfa iris.csv results.csv
    [info] Compiling 1 Scala source to /tmp/minihadrian/target/scala-2.10/classes...
    [info] Running MiniHadrian simpleIrisModel.pfa iris.csv results.csv
    log4j: reset attribute= "false".
    log4j: Threshold ="null".
    log4j: Level value for root is  [INFO].
    log4j: root level set to INFO
    log4j: Class name: [org.apache.log4j.ConsoleAppender]
    log4j: Parsing layout of class: "org.apache.log4j.PatternLayout"
    log4j: Setting property [conversionPattern] to [%d{yyyy-MM-dd_HH:mm:ss.SSS} %5p [%t]: %m%n].
    log4j: Adding appender named [consoleAppender] to category [root].
    2015-11-17_16:02:07.557  INFO [run-main-4]: "Beginning..."
    2015-11-17_16:02:07.722  INFO [run-main-4]: "Ending..."
    [success] Total time: 4 s, completed Nov 17, 2015 4:02:07 PM

### Checklist item #N: bells and whistles

   * Many Hadrian wrappers should load multiple instances of a PFA engine and parallelize them. The parallelization technique varies from one environment to another, but multiple engines are produced with

     ```scala
     val engines = PFAEngine.fromJson(new FileInputStream(pfaEngineName),
                                      multiplicity = numberOfEngines)
     ```

     (Drop the `.head` and now `engines` has type `Seq[PFAEngine]`.)

   * You may want to add a choice of serialization/deserialization methods, or pass data with no serialization whatsoever. For instance, Antinous exchanges PFA data with Jython, in which each element is transformed, but not serialized.

   * You may want to add the option of loading PFA from YAML files. The static method is `fromYaml` rather than `fromJson`.

   * You may want to take regular snapshots of the scoring engine's state.

   * You may want to revert its state at specific times (e.g. reducer engines in Hadrian-MR revert the state whenever they encounter a new map-reduce key, so that engine instances can be reused without polluting one reducer with persistent state from another).

   * You may want to add the ability to call PFA user-defined functions from the outside system.

   * You may want to associate PFA persistent state (cells and pools) with an external database, possibly spanning a distributed network.
