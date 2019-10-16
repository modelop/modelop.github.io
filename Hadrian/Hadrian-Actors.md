Hadrian-Actors is an application that wraps the Hadrian software library as a PFA multi-processor. It can load many PFA files as a directed acyclic graph of connected scoring engines that pass input and output from one to another. It is configured by a topology file that describes these interconnections and implements the scoring engines as actors with message-passing.

The syntax of the topology file is [described here](Hadrian-Actors-Configuration). External PFA files, embedded PFA files, external JAR and shell processes are all supported, as well as Avro and JSON input formats (one JSON document per line).

## Before you begin...

Download the [pre-built Hadrian-Actors JAR](Installation#case-2-you-want-to-use-pre-built-jar-files-for-one-of-the-hadrian-containers) and its dependencies (the hadrian-standalone-jar-with-dependencies would suffice: just put them both on the same classpath). This article was tested with Hadrian 0.8.2; newer versions should work with no modification.

## Help document

A good place to start is Hadrian-Actors's own help text, which will always show the latest options.

```
Usage: java -jar hadrian-actors.jar [options] topology.json|yaml

  --log log4j.xml
        URL to configure log4j (default is in 'jar -xf hadrian-actors.jar resources/log4j.xml')
  --monitorFreqSeconds 1.0
        number of seconds between monitor INFO messages
  --queueMemoryLimit <value>
        used/max memory above which data will be dropped from queues
  topology.json|yaml
        topology description file
  --help
        print this help message

Hadrian-Actors builds an actor-based workflow within a single process.
The workflow can be as general as a directed acyclic graph (DAG), can
contain PFA engines (inline or from external files), executable
functions in external JAR files, and executable scripts, provided by a
shell command.  At any stage, results can be saved to a file or named
pipe.
```

For details, see the [documentation of the topology file](Hadrian-Actors-Configuration).
