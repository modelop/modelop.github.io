Hadrian-Standalone is an application that wraps the Hadrian software library as a shell command. It reads data from Avro files, JSON files (each line of input is a complete JSON document), and CSV files (for PFA whose input schema is a record of primitives only).

It is good for simple shell-based workflows and testing.

It can also run Jython scripts with schemas in place of PFA files, as long as Antinous is included in the JAR (not the `-exclude-antinous` version). This is useful for testing Jython-based model producers before sending them to [Hadrian-MR](Hadrian-MR).

## Before you begin...

Download the [pre-built Hadrian-Standalone JAR](Installation#case-2-you-want-to-use-pre-built-jar-files-for-one-of-the-hadrian-containers) with dependencies. This article was tested with Hadrian 0.8.3; newer versions should work with no modification.

## Help document

A good place to start is Hadrian-Standalone's own help text, which will always show the latest options.

```
% java -jar target/hadrian-standalone-0.8.3-jar-with-dependencies.jar --help
 
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
```

## Details

If `--numberOfEngines` is greater than 1, parallel threads are launched with one engine instance in each thread. Data from the `inputFiles` are processed sequentially, and the process ends when all input files have been processed. With parallel threads, the input data are given to the first non-busy scoring engine and the input stream waits if all engines are busy (scatter step). Output from the engines are collected on a single [`java.util.concurrent.ConcurrentLinkedQueue`](https://docs.oracle.com/javase/7/docs/api/java/util/concurrent/ConcurrentLinkedQueue.html) and are written to the output file in the order in which they are received. This is only equal to the input order if `--numberOfEngines` is 1.

The input and output files do not need to be files; they can be named pipes.
