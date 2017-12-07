# Overview

A Hadrian-Actors topology is a JSON or YAML file describing a directed acyclic graph of connected scoring engines. The basic unit in the configuration file is a node, a labeled entity that may be connected to other nodes through its destinations.

Nodes may be sources, which read in data from outside of Hadrian-Actors, or they may be processors, which do some transformation of the data. All nodes have a "destinations" attribute that sends data elsewhere, either other processors (by label) or outside of Hadrian-Actors. (Note the uneven hierarchy: sources and processors are both types of nodes, but destinations are attributes of a node.)

All sources have an output schema and all processors have both input and output schemas. At startup, Hadrian-Actors ensures (a) that all destination nodes linked by label exist, (b) that the output schema of the first node and input schema of the next node match exactly (not just one-sided acceptance), and (c) that there are no cycles in the graph.

The topology language can be extended by programs that include the Hadrian-Actors JAR to define new kinds of sources, processors, and destinations. It uses Java's `ServiceLoader` mechanism to load user-supplied subclasses of `ExtendedSource`, `ExtendedProcessor`, and `ExtendedDestination`.

# Configuration language

A Hadrian-Actors topology may be expressed as JSON or YAML. No special YAML features are used (YAML files are converted into JSON before processing). In this documentation, I refer to JSON objects (sets of key-value pairs) as "maps" and JSON arrays (ordered sequences) as "lists". Primitive types are "string", "number", "boolean", and "null". Schemas follow the [Avro specification](https://avro.apache.org/docs/1.7.7/spec.html).

The top level of a configuration file is a map from user-supplied node labels to node configuration blocks. You may have as many nodes as you wish, and nodes do not need to be connected to anything (though they're not useful unless they are).

## Nodes

A node is represented by a map from attributes to values. Unlike node labels, which may be any string, node attributes must be one of the built-in or extended name, allowed value combinations.

Every node must have a `node` attribute, which must have one of the following values.

| Value | Description | Details |
|:------|:------------|:--------|
| `file-source` | source is a file handle, which may be a physical file or a named pipe in UNIX | see [File Source](#file-source) |
| `pfa-engine` | processor is a PFA scoring engine, which may be an external file or embedded in the topology | see [PFA Engine](#pfa-engine) |
| `jar-engine` | processor is Java bytecode in an external JAR | see [JAR Engine](#jar-engine) |
| `shell-engine` | processor is an external process, connected through standard input/standard output | see [Shell Engine](#shell-engine) |

Extensions provide entirely new types of sources and processors (rather than additional attributes to the below).

## File Source

If the `node` is `file-source`, then the other attributes are as follows.

| Name | Type | Required/Default | Description |
|:-----|:-----|:-----------------|:------------|
| `fileName` | string | **required** | Name of the external file or named pipe |
| `type` | [Avro](https://avro.apache.org/docs/1.7.7/spec.html) | **required** | How to interpret the data (verified at startup or cast at runtime) |
| `format` | string | **required** | "avro" for Avro input data and "json" for JSON-object-per-line data |
| `destinations` | [destinations](#destinations) | empty list | Where to send the data |

## PFA Engine

If the `node` is `pfa-engine`, then the other attributes are as follows. The input and output schemas are drawn from the PFA file or embedded PFA, so no input/output attributes are necessary at this level. PFA engines may have method = map, emit, or fold. Multiple outputs from an emit engine will _all_ be passed on to the destination.

| Name | Type | Required/Default | Description |
|:-----|:-----|:-----------------|:------------|
| `pfa` | string or embedded PFA | **required** | If a string, the string is interpreted as a file name or URL for loading the PFA document. Otherwise, this is taken to be a literal PFA document embedded within the topology. |
| `options` | map | empty map | If provided, override the PFA file's options with a given set |
| `multiplicity` | positive integer | 1 | If greater than 1, produce a suite of scoring engines that share data |
| `saveState` | [see below](#save-state) | null | Configures PFA to make intermittent snapshots |
| `watchMemory` | boolean | false | If true, generate reports of memory used by this engine's cells and pools at runtime |
| `destinations` | [destinations](#destinations) | empty list | Where to send the results |

### Save State

| Name | Type | Required/Default | Description |
|:-----|:-----|:-----------------|:------------|
| `baseName` | string | **required** | Prefix for all output snapshot files |
| `freqSeconds` | null or positive integer | null | If positive integer _N_, save the files every _N_ seconds; if null, do not save files |

## JAR Engine

If the `node` is `jar-engine`, then the other attributes are as follows. If the external code violates input/output schema expectations, a runtime error will ensue. JAR engines can only emulate method = map type engines.

| Name | Type | Required/Default | Description |
|:-----|:-----|:-----------------|:------------|
| `jar` | string | **required** | File name or URL for loading the external JAR |
| `className` | string | **required** | Fully qualified class within the external JAR |
| `input` | [Avro](https://avro.apache.org/docs/1.7.7/spec.html) | **required** | Expected schema, see [Data Transformations](#data-transformations) below |
| `output` | [Avro](https://avro.apache.org/docs/1.7.7/spec.html) | **required** | Expected schema, see [Data Transformations](#data-transformations) below |
| `multiplicity` | positive integer | 1 | Number of instances to make of this class |
| `destinations` | [destinations](#destinations) | empty list | Where to send the results |

### Data transformations

The external code should expect and produce the following types. This choice of types strongly favors code written in Scala over code written in Java, though it's not an absolute requirement.

| Avro type | Scala type |
|:----------|:-----------|
| null | `AnyRef` with value `null` |
| boolean | primitive `Boolean` |
| int | primitive `Int` |
| long | primitive `Long` |
| float | primitive `Float` |
| double | primitive `Double` |
| bytes | `Array[Byte]` |
| string | `String` |
| fixed | `Array[Byte]` (of the appropriate length) |
| enum | `String` (of an appropriate value) |
| array | `Vector` (Scala immutable) |
| map | `Map` (Scala immutable) |
| record | case class in the JAR with a fully-qualified name that matches the Avro name of the record and constructor arguments/fields in the same order as in the Avro record |
| union | `Any` |

## Shell Engine

If the `node` is `shell-engine`, then the other attributes are as follows. If the external code violates input/output schema expectations, a runtime error will ensue. Shell engines may emulate method = map or emit, since any lines of standard output are passed on to the destination. Standard error from the process is sent to the Hadrian-Actors logfile.

| Name | Type | Required/Default | Description |
|:-----|:-----|:-----------------|:------------|
| `cmd` | list of strings | **required** | Command to start the external process |
| `dir` | null or string | null | Initial working directory |
| `env` | map of strings | empty map | Initial environment variables |
| `input` | [Avro](https://avro.apache.org/docs/1.7.7/spec.html) | **required** | Expected schema, passed to the command as lines of JSON on standard input |
| `output` | [Avro](https://avro.apache.org/docs/1.7.7/spec.html) | **required** | Expected schema, obtained from the command as lines of JSON on standard output |
| `multiplicity` | positive integer | 1 | Number of subprocesses to fork |
| `destinations` | [destinations](#destinations) | empty list | Where to send the results |

## Destinations

The format for configuring destinations is the same for all nodes. The destinations is a list of maps with one of the following formats: (a) internal link, (b) external file, or (c) extended output.

An internal link has the following attributes.

| Name | Type | Required/Default | Description |
|:-----|:-----|:-----------------|:------------|
| `to` | string | **required** | Label of node where the output should be sent |
| `hashKeys` | list of strings | empty list | Keys in the data record used to determine which instance of a multiplicity group to send the record to: data with the same hash key values are always sent to the same instance |
| `limitBuffer` | "none" or positive integer | "none" | If a number, set a limit on the number of records that can accumulate in a destination queue before dropping data; used to control peak memory use |
| `watchMemory` | boolean or "count" | false | If true, generate reports of memory used by data waiting in this queue at runtime; if "count", avoid the potentially expensive memory calculation and just count the number of records |

An external file has the following attributes.

| Name | Type | Required/Default | Description |
|:-----|:-----|:-----------------|:------------|
| `file` | string | **required** | Output file name or named pipe |
| `format` | "avro", "json", or "json+schema" | **required** | Output data format; "json+schema" prints the schema on the first line for future reference |
| `limitSeconds` | "none" or positive number | "none" | Maximum length of time to write data to this file (for diagnostics) |
| `limitRecords` | "none" or positive integer | "none" | Maximum number of records to write to this file (for diagnostics) |

Extensions provide entirely new types of destinations (rather than additional attributes to the above).
