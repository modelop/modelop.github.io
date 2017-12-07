Titus's **pfachain** script creates a multi-step PFA scoring engine from a linear series of single-step PFA engines. The output schema of each step must be accepted by the input to the next step, and this script verifies that this is the case. It also renames global objects (persistent cells/pools, user-defined functions, and types) to avoid namespace collisions among the PFA steps.

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.8.3; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

## Help document

A good place to start is pfachain's own help text, which will always show the latest options.

```
usage: pfachain [-h] [--no-check] [--verbose] [--name NAME]
                [--randseed RANDSEED] [--doc DOC] [--version VERSION]
                [--metadata METADATA] [--options OPTIONS]
                [input [input ...]] output

Combine a linear sequence of PFA files into a single PFA file representing a
chained scoring engine.

positional arguments:
  input                input PFA files (at least 2)
  output               output PFA file, "-" for standard out

optional arguments:
  -h, --help           show this help message and exit
  --no-check           if supplied, the output will not be checked for PFA-
                       validity
  --verbose            if supplied, print status to STDOUT
  --name NAME          name field for output PFA file (default is generated
                       from the inputs)
  --randseed RANDSEED  randseed field for output PFA file (must be an integer)
  --doc DOC            doc field for output PFA file
  --version VERSION    version field for output PFA file (must be an integer)
  --metadata METADATA  metadata field for output PFA file (must be a JSON map
                       of strings)
  --options OPTIONS    options field for output PFA file (must be a JSON map)
```

## Example

The following example combines three PFA engines (`first.pfa`, `second.pfa`, `third.pfa`) into a linear chain (`everything.pfa`). The `first.pfa` creates a record and fills it based on integer input:

```json
{"input": "int",
 "output": {"type": "record",
            "name": "Output",
            "fields": [{"name": "one", "type": "int"},
                       {"name": "two", "type": "double"},
                       {"name": "three", "type": "string"}]},
 "action":
   {"type": "Output",
    "new": {"one": "input", "two": "input", "three": {"s.int": "input"}}}}
```

The `second.pfa` reads that record and emits the string part three times. This branches the workflow such that `third.pfa` will need to be executed three times.

```json
{"input": {"type": "record",
           "name": "Output",
           "fields": [{"name": "one", "type": "int"},
                      {"name": "two", "type": "double"},
                      {"name": "three", "type": "string"}]},
 "output": "string",
 "method": "emit",
 "action": [
   {"emit": "input.three"},
   {"emit": "input.three"},
   {"emit": "input.three"}]}
```

The `third.pfa` introduces a user-defined function that needs to be renamed to avoid potential namespace conflicts with the other two engines.

```json
{"input": "string",
 "output": "string",
 "action": {"u.hello": "input"},
 "fcns": {
   "hello": {"params": [{"x": "string"}],
             "ret": "string",
             "do": {"s.concat": [["Hello, "], "x"]}}}}
```

The following command verifies that `first.pfa`, `second.pfa`, and `third.pfa` are compatible, combines them with emit-handling and namespace protection into `everything.pfa`, and writes verbose output (useful for large PFA files).

```
% pfachain first.pfa second.pfa third.pfa everything.pfa --verbose
Loading first.pfa as step 1
Loading second.pfa as step 2
Loading third.pfa as step 3
Mon Nov 30 17:12:02 2015 Converting all inputs to ASTs
Mon Nov 30 17:12:02 2015     step 1
Mon Nov 30 17:12:02 2015     step 2
Mon Nov 30 17:12:02 2015     step 3
Mon Nov 30 17:12:02 2015 Changing type names to avoid collisions
Mon Nov 30 17:12:02 2015 Verifying that input/output schemas match along the chain
Mon Nov 30 17:12:02 2015 Adding [name, instance, metadata, actionsStarted, actionsFinished, version] as model parameters
Mon Nov 30 17:12:02 2015 Converting scoring engine algorithm
Mon Nov 30 17:12:02 2015     step 1: Engine_1
Mon Nov 30 17:12:02 2015     step 2: Engine_2
Mon Nov 30 17:12:02 2015     step 3: Engine_3
Mon Nov 30 17:12:02 2015 Create types for model parameters
Mon Nov 30 17:12:02 2015 Resolving all types
Mon Nov 30 17:12:02 2015 Converting the model parameters themselves
Mon Nov 30 17:12:02 2015 Verifying PFA validity
Mon Nov 30 17:12:02 2015 Done
```

The following tests `everything.pfa` in [Hadrian-Standalone](Hadrian-Standalone).

```
% java -jar hadrian-standalone-0.8.3-jar-with-dependencies.jar -i json -o json everything.pfa
1
2
3
"Hello, 1"
"Hello, 1"
"Hello, 1"
"Hello, 2"
"Hello, 2"
"Hello, 2"
"Hello, 3"
"Hello, 3"
"Hello, 3"
```
