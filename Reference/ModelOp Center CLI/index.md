---
title: The ModelOp Center CLI User Guide
description: The guide describes all commands available through the ModelOp Center CLI with their respective options.
css: buttondown.css
---

# ModelOp Center CLI
ModelOp Center exposes a CLI that is built using Go, allowing end users to interface with ModelOp Center micro services via CLI. The Go CLI is the primary supported ModelOp Center CLI. 


For 1.x versions of ModelOp Center, there is also a Python CLI ([Python CLI reference](../../Reference/ModelOp Center CLI/Python CLI/)). However, the Python CLI will be deprecated, starting in ModelOp Center version 2.x.


## Installation Instructions

1. Download the CLI here:

    * [Darwin](https://fastscore-go-cli.s3.us-east-2.amazonaws.com/release/1.10/darwin/fastscore)
    * [Linux](https://fastscore-go-cli.s3.us-east-2.amazonaws.com/release/1.10/linux/fastscore)
    * [Windows](https://fastscore-go-cli.s3.us-east-2.amazonaws.com/release/1.10/windows/fastscore.exe)

2. For Mac (Darwin) and Linux make it executable:

    ```
    chmod +x fastscore
    ```

3. Add to $Path

    For Macs: /usr/local/bin/fastscore

4. Confirm proper installation with fastscore


# ModelOp Center CLI User Guide

This guide describes the complete set of commands and options supported by the
ModelOp Center CLI.

## Command index

* [fastscore connect](#connect)
* [fastscore use](#use)
* [fastscore run](#run)
* [fastscore config](#config)
* [fastscore fleet](#fleet)
* [fastscore model](#model)
* [fastscore schema](#schema)
* [fastscore stream](#stream)
* [fastscore sensor](#sensor)
* [fastscore engine](#engine)
* [fastscore attachment](#attachment)
* [fastscore pneumo](#pneumo)
* [fastscore monitor](#monitor)
* [fastscore login](#login)
* [fastscore debug](#debug)
* [fastscore stats](#stats)

```
NAME:
   fastscore - Control fastscore from the command line.

USAGE:
   fastscore [global options] command [command options] [arguments...]

VERSION:
   v1.10

COMMANDS:
     connect     Establish a fastscore Connection
     use         Select the target engine instance
     run         A shortcut for running a particular model and stream configuration
     config      Configure the fastscore fleet
     fleet       Examine status of the fastscore fleet
     model       Manage analytic models
     schema      Manage schemata
     stream      Manage streams
     sensor      Manage sensors
     engine      Manage engines
     attachment  Manage attachments
     pneumo      Print pneumo messages
     create      Create new fastscore services
     destroy     Destroy existing fastscore services
     conductor   Interact with the orchestrator
     composer    Create and manage workflows
     workflow    Create and manage workflows
     monitor     Monitor an engine
     login       Login to fastscore
     debug       Watch debugging messages
     stats       Get various statistics
     help, h     Shows a list of commands or help for one command

GLOBAL OPTIONS:
   --help, -h     show help
   --version, -v  print the version

WEBSITE: http://www.opendatagroup.com
SUPPORT: support@opendatagroup.com
```

## Connecting to ModelOp Center
<a name="connect"></a>

```
fastscore connect [command options] <prefix>
```

```
OPTIONS:
   --verbose, -V  Be verbose
   --nowait       Do not retry connecting.
```

The command establishes a connection between the command line interface and the
ModelOp Center deployment. The `<prefix>` is the URL of the ModelOp Center proxy, e.g.
`https://1.2.3.4:8000`. 

By default, the command waits for the provided prefix to become available. Use
`--nowait` option to disable the check and return immediately.

Example:

```
$ fastscore connect https://localhost:8000 -V
Connecting... Done.
```

## Choosing an instance
<a name="use"></a>

```
fastscore use <instance-name>
```

The command selects `<instance-name>` as a target of subsequent commands. In
addition, it makes `<instance-name>` the preferred instance of a specific
service. For example, `fastscore use engine-1` makes `engine-1` the target of
sensor management commands. Any command that require an instance of an `engine`
service will now use the `engine-1` instance. 

Example:

```
$ fastscore use engine-1
```

## Running models
<a name="run"></a>

```
fastscore run <model> <input stream> <output stream>
```

The `run` is a convience command mostly equivalent to the following sequence of commands:

```
fastscore model load <model-name>
fastscore stream attach <stream-0> 0
fastscore stream attach <stream-1> 1
```

Models with a single input and single output stream are widespread. The command
allows building such pipelines quickly.

Example:

```
$ fastscore model add cube
action <- function(x) emit(x*x*x)
^D
$ fastscore run cube rest: rest:
$ fastscore model interact
> 2
8
> 10
1000
```

### Model input/output using REST

```
fastscore model input [ <slot> ]
fastscore model output [ <slot> ] [ -nowait ] [ -c ]
fastscore model interact
```

The `model input` command reads its standard input and sends the data to the
REST stream attached to `<slot>` (or slot 0 if `<slot>` is omitted). Each line
is interpreted as a separate data record.

The `model output` reads data from the REST stream attached to `<slot>` (or slot
1 if `<slot>` is omitted). By default, the command waits for the record to
become available and retrieves exactly one record. The `-nowait` option limits
the waiting time to 0.5s. The `-c` option asks the command to continuously read
data from the stream.

Example:

```
$ fastscore run sqrt rest: rest:
$ fastscore model input
2
3
5
^D
$ fastscore model output -c
4
9
25
```

The `model interact` command combines the effects of `model input` and `model output`
commands. It allows the user to both send inputs to the REST stream and observe
the outputs. The `model interact` also shows records rejected either by encoding
or the schema.

Example:

```
$ fastscore run sqrt rest: rest:
$ fastscore model interact
> 7
49
> foobar
>
INPUT REJECTED-By-Schema: AT INPUT SLOT(0): foobar
> 11
121
> 100
10000
> ^D
```

Note that these commands do not close input/output streams. They may be run
multiple times.

## Configuring ModelOp Center
<a name="config"></a>

```
fastscore config set <config-file>
fastscore config show
```

The first command sets the configuration of the ModelOp Center deployment. The second -
prints the current configuration. The `<config-file>` is the name of the
configuration file. The configuration file uses YAML format. Its syntax is
described [here](../../Product Manuals/Configuration/).

Example:

```
$ fastscore config set config.yaml
$ fastscore config show
fastscore:
  db:
    host: database
    password: root
    port: 3306
    type: mysql
    username: root
  fleet:
  - api: engine
    host: engine-2
    name: engine-2
    port: 8003
  - api: engine
    host: engine-1
    name: engine-1
    port: 8003
  - api: model-manage
    host: model-manage
    name: model-manage-1
    port: 8002
  pneumo:
    type: REST
```

## Listing services
<a name="fleet"></a>

```
fastscore fleet [command options] 
```

```
OPTIONS:
   --verbose, -V  be verbose
   --json         as json
   --wait         Wait for all sewrvices to report healthy
```

The command outputs the information about the currently running ModelOp Center
services. The verbose output includes information about CLI and Connect.

Use `-wait` option to make the command wait for all services to report a
healthy status.

Example:

```
$ fastscore fleet -wait -V
waiting..
       NAME      |     API      |     HOST     | PORT | RELEASE |           BUILTON            | HEALTH
-----------------+--------------+--------------+------+---------+------------------------------+---------
  engine-2       | engine       | engine-2     | 8003 |     1.9 | Thu Jan 10 18:48:14 UTC 2019 | ok
  engine-1       | engine       | engine-1     | 8003 |     1.9 | Thu Jan 10 18:48:14 UTC 2019 | ok
  model-manage-1 | model-manage | model-manage | 8002 |     1.9 | Thu Jan 10 17:14:49 UTC 2019 | ok
```

## Managing models
<a name="model"></a>

```
fastscore model add <model-name> <source-file> [ --type <model-type> ]
fastscore model show <model-name> [ -e ]
fastscore model list
fastscore model remove <model-name>
```

The `model add` command introduces a model to fastscore. The type of
the model can be set using `--type <model-type>` option:

Option | Model type
-------|-----------
-type python2 | Python 2.x
-type python3 | Python 3.x
-type R or -type:r | R
-type java | Java
-type c | C
-type pfa-json | PFA (JSON)
-type pfa-yaml | PFA (YAML)
-type pfa-pretty | PFA (PrettyPFA)
-type h2o-java | h20.ai (Java)
-type octave | Matlab using Octave
-type sas | SAS (experimental)

If the `--type` option is omitted the model type is determined by the extension
of the `<source-file>`:

Extension | Model type
----------|-----------
.py | Python 2.x
.py3 | Python 3.x
.R  | R
.c |  C
.pfa or .json | PFA (JSON)
.yaml | PFA (YAML)
.ppfa | PFA (PrettyPFA)
.m | Matlab using Octave

If the commands reads the model source from the standard input it still tries to
gets the model type. For example, if the source code starts with `def action(`
the command assumes that the model type is Python.

The `model show` prints the model source code to the standard output. The `-e`
(edit) option provides for a convenient modification of the model. The edit
option spawns an editor and updates the model when the editor closes. The editor
name is taken from the EDITOR environment variable. By default, the editor name
is 'vi'.

The `model list` command shows the list of models known to ModelOp Center. The `model
remove` command removes the corresponding model.

Example:

```
$ ~/fastscore model add cube ./cube.py3 --type python3 
$ fastscore model list
   NAME   |  TYPE   | ATTACHMENTS
----------+---------+--------------
  cube    | Python3 |
$ fastscore model show cube
def action(x):
  return x*x*x
$ fastscore model remove cube
$ fastscore model list
  NAME | TYPE | ATTACHMENTS
-------+------+--------------
```

### Loading/unloading models

```
fastscore model load <model name> [override attachments]
fastscore model unload [engine name]
fastscore model verify <model-name>
fastscore mode inspect
```

The `model load` command performs all preparatory steps and gets ready to start
data processing. The target engine can be selected using the `use` command. The
preparatory steps include verification of the model syntax, checking if the
model follows the ModelOp Center model conventions. If an unexpected slot has a stream 
attached the `model load` command will fail. If all requied streams are attached, 
the loaded model will start the data processing. See also `engine pause` command.

Note that the `model load` command can be called repeatedly, even if the data
processing is underway. The command will attempt to replace the model without
stopping the flow of data. The replacement model may be implemented in a
different language.

The `model unload` command removes the active model from the engine. The
operation is only allowed if the engine is in the INIT state. When data is being
processed it is not possible to unload the model. See also `engine reset`
command.

The `model verify` command performs all preparatory steps without actually
loading the model. The verbose command output shows how the model smart comments
were understood.

Example:

```
$ fastscore model verify echo -V
Model Name     Model Type     SLOC
----------     ----------     ----
echo           Python3        5

Slot     Schema     Action     Recordsets
----     ------     ------     ----------
0        string     action     false
1        string                false

The model contains no errors
```

The `model inspect` prints information about the currently loaded model. Its
output is similar to the output of the `model verify` command.

Example:

```
$ fastscore model inspect
Model
+------+---------+-----------+-------------+
| NAME |  TYPE   | SNAPSHOTS | ATTACHMENTS |
+------+---------+-----------+-------------+
| echo | python3 | none      | none        |
+------+---------+-----------+-------------+

Streams
+------+--------+------------+
| SLOT | ACTION | RECORDSETS |
+------+--------+------------+
|    0 | action | false      |
|    1 |        | false      |
+------+--------+------------+

Jets
+-------+-----+-----------+
| JET # | PID |  SANDBOX  |
+-------+-----+-----------+
|     1 |  45 | 100796087 |
+-------+-----+-----------+
```

## Managing schemas
<a name="schema"></a>

```
fastscore schema add <schema-name> <schema-file>
fastscore schema show <schema-name> [ -e ]
fastscore schema list
fastscore schema remove <schema-name>
```

The `schema add` command adds an Avro schema to ModelOp Center.

The `schema show` prints the schema to the standard output. The `-e` (edit)
option allows editing the schema in-place. The edit option
spawns an editor and updates the schema after the editor closes. The editor name
is taken from the EDITOR environment variable. By default, the
editor name is 'vi'.

The `schema list` command shows the list of schemas known to ModelOp Center. The `schema remove`
command removes the corresponding schema.

Example:

```
$ fastscore schema add sch-1 ./sch-1.avsc
$ fastscore schema list
sch-1
$ fastcore schema remove sch-1 -v
```

### Schema Verify
```
fastscore schema verify <schema name> <data source>
```

```
OPTIONS:
   --verbose, -V  be verbose
```

The `schema verify` command check that the named schema is a well-formed. If
`<data source>` is present the command in addition checks data in the file for
conformance against the schema. The data file contains JSON-encoded records
separated by newlines.

Example:

```
$ fastscore schema add s1
"foobar"
^D
$ fastscore schema verify s1
Error: Type "foobar" is undefined
$ fastscore schema add s2
"int"
^D
$ fastscore schema verify s2 -v
Schema OK
$ cat <<EOF>>data1
2
"fastscore"
[]
3
EOF
$ fastscore schema verify s2 data1
OK   2

FAIL "fastscore"
     Int expected, not "fastscore"

FAIL []
     Int expected, not []

OK   3

```

## Managing streams
<a name="stream"></a>

```
fastscore stream add <stream-name> <descriptor-file>
fastscore stream show <stream-name> [ -e ]
fastscore stream list
fastscore stream remove <stream-name>
```

The `stream add` command adds a stream descriptor to fastscore. The syntax of
the stream descriptor is explained [here](../../Product Manuals/Stream Descriptors/).

The `stream show` prints the stream descriptor to the standard output. The `-e`
(edit) option allows editing the descriptor in-place. The edit option
spawns an editor and updates the stream descritor when the editor closes. The
editor name is taken from the EDITOR environment variable. By default, the
editor name is 'vi'.

The `stream list` command shows the list of streams known to fastscore. The `stream remove`
command removes the corresponding stream.

Example:

```
$ fastscore stream add input-1 ./input-stream.json
$ fastscore stream list
input-1
$ fastcore stream remove input-1
```

### Attaching/detaching streams

```
fastscore stream attach <stream-name> <slot>
fastscore stream detach <slot>
fastscore stream verify <stream-name> <slot>
fatsscore stream inspect
```

The `stream attach` opens the stream and attaches it to the `<slot>`. Typically,
the command retrieves the stream descriptor from Model Manage using
`<stream-name>`. 

The `stream detach` command closes and detaches the stream. It is not possible
to detach the stream when the model is running. However, it is possible to
attach a different stream to the same slot using the `stream attach` command
while data is being processed.

The `stream verify` command performs all the same steps as `stream attach`
without actually attaching the stream to the `<slot>`. It prints the internal
representation of the stream descriptor with all default values substituted.

Example:

```
$ fastscore stream verify s1 0
{
  "batching": {
    "nagle_time": 500,
    "watermark": 1000
  },
  "linger_time": 3000,
  "loop": false,
  "transport": {
    "type": "rest",
    "mode": "simple"
  },
  "encoding": null
}
The stream descriptor contains no errors
```

The `stream inspect` command shows the list of streams attached to slots at the current engine.

Example:

```
$ fastscore stream inspect
  SLOT |       NAME   | TRANSPORT |  EOF
-------+--------------+-----------+--------
     0  inline-526507    REST       False
     1  inline-809896    REST       False
```

### URL-like stream descriptors

An URL-like or literal stream descriptor is a shortened representation of a
stream descriptor. It can be used instead of the stream name for commands, such
as `stream attach`. The commands look for a ':' character to distinguish a
stream name from a literal stream descriptor. The table below contains examples
of literal stream descriptors.

Example | Description
--------|------------
inline:1,2,3 | An inline stream 3 records
inline-chunked:%06%02%04%06 | An inline stream with Avro-encoded [1,2,3] array
rest: | A REST stream (simple mode)
rest-chunked: | A REST stream (chunked mode)
kafka:kafka-1.company.com:9092/mytopic.json | A Kafka stream
file:/vol/data/data1.dat | A (local) file stream
tcp:1.2.3.4:5678 | A TCP stream
udp::9099 | A UDP stream (input only)
https://dev.company.com:1234/data1.json | An HTTP stream
exec:/root/myscript.sh | An exec stream
discard: | A discard stream

Use `stream verify` command to see how the literal stream descriptor is
understood by the engine.

Example:

```
$ fastscore stream verify inline:1,2,3 0
{
  "encoding": "json",
  "linger_time": 3000,
  "transport": {
    "data": [
      "1",
      "2",
      "3"
    ],
    "type": "inline"
  },
  "batching": {
    "nagle_time": 500,
    "watermark": 1000
  },
  "loop": false,
  "schema": "undefined"
}
The stream descriptor contains no errors
```

### Sampling streams

```
fastscore stream sample <stream-name> [ sample count ]
```

The `stream sample` reads a few data records from the stream. This happens in
the context of the engine. Otherwise, stream sampling is unrelated to the data
pipeline. If `sample count` option is omitted, the commands attempts to read 10
records max.

```
$ fastscore stream sample inline:2,3,5,7,11 3
   1: 2
   2: 3
   3: 5
```

## Managing sensors
<a name="sensor"></a>

```
fastscore sensor add <sensor-name> <sensor-file>
fastscore sensor show <sensor-name> [ -e ]
fastscore sensor list
fastscore sensor remove <sensor-name>
```

The `sensor add` command adds a sensor descriptor to ModelOp Center. The syntax of
a sensor descriptor is described [here](../../Product Manuals/Sensors/).

The `sensor show` prints the sensor descriptor to the standard output. The `-e`
(edit) option allows editing the sensor descriptor. The edit option spawns an
editor and updates the descriptor after the editor closes. The editor name
is taken from the EDITOR environment variable. By default, the
editor name is 'vi'.

The `sensor list` command shows the list of sensor descriptors known to
ModelOp Center. The `sensor remove` command removes the corresponding sensor
descriptor.

Note that the above commands operate on sensor descriptors, not active sensors.
See `sensor install/uninstall/inspect` commands for more.

Example:

```
$ fastscore sensor add watchdog-1 ./watchdog.json
$ fastscore sensor list
watchdog
$ fastcore sensor remove watchdog-1
```

### Active sensor operations

```
fastscore sensor install <sensor-name>
fastscore sensor uninstall <tap-id>
fastscore sensor inspect [ <tap-id> ]
fastscore sensor points
```

The `sensor install` command adds the sensor to the current service instance.
See `use` command. Upon success, the command prints `<tap-id>` of installed
sensor. Other active sensor operations take `<tap-id>` as an argument.

The `sensor inspect` prints information about all active sensors for the current
service instance or a particular active sensor if `<tap-id>` is present.

The `sensor uninstall` command removes the active sensor identified by
`<tap-id>`.

The `sensor points` command outputs the list of tapping points provided by the
current instance. A sensor descriptor includes a tapping point as a value of the
"Tap" element.

Example:

```
$ fastscore sensor install sensor1
15
$ fastscore sensor inspect 15 -v
Sensor id 15 is attached to manifold.debug at engine-1.
$ fastscore sensor uninstall 15
```

```
$ fastscore sensor points
manifold.0.debug
jet.71581093.output.records.size
jet.71581093.output.records.count
jet.71581093.input.records.size
jet.71581093.input.records.count
...
manifold.deadlock
manifold.debug
sys.test.tagged.bytes
sys.test.tagged.float
sys.test.tagged.int
sys.test.bytes
sys.test.float
sys.test.int
sys.memory
sys.cpu.utilization
```

## Managing engine state
<a name="engine"></a>

```
fastscore engine reset [ <engine-name> ] [ --all ]
fastscore engine inspect [ <engine-name> ]
fastscore engine pause [ <engine-name> ]
fastscore engine unpause [ <engine-name> ]
```

A ModelOp Center engine has one of the following seven states:

State | Description
------|------------
INIT | Initialization - data pipleline is incomplete
RUNNING | Data is being processed
PIGGING | Pigging is in effect
FINISHING | All inputs at EOF - processing continues
FINISHED | Both inputs and outputs at EOF
PAUSED | Data processing is paused
ERROR | Unrecoverable error encountered - see logs

The `engine reset` command puts the engine into the INIT state regardless of its
current state. The commands unload the model and detaches all streams. Use
`engine reset` to start using an engine again after it reached the FIHISHED
state.

The `engine inspect` prints the current state of the engine.

Example:

```
$ fastscore engine inspect
engine engine-1 is init
$ fastscore engine reset
```

The `engine pause` puts the engine into the PAUSED state. It is not possible to
pause an engine which is currently in FINISHING, FINISHED, or ERROR state. If
the pause is requested during initialization, the engine becomes paused
when it is about to enter the RUNNING state. Use `engine unpause` to continue
data processing.

Example:

```
$ fastscore engine inspect
engine engine-1 is init
$ fastscore engine pause
$ fastscore engine inspect
engine engine-1 is init
$ fastscore run cube rest: rest:
$ fastscore engine inspect
engine engine-1 is paused
$ fastscore engine unpause
$ fastscore engine inspect
engine engine-1 is running
```

## Model attachments
<a name="attachment"></a>

```
fastscore attachment upload <model-name> <file-to-upload>
fastscore attachment download <model-name> <attachment-name>
fastscore attachment list <model-name>
fastscore attachment remove <model-name> <attachment-name>
```

ModelOp Center models may have attachments - archives containing arbitrary data made
available to the model when it runs. The `attachment upload` command adds the
attachment to the model. The `<file-to-upload>` must have one of the following
extensions:

Extension | Archive format
----------|---------------
.zip | zip
.tgz | gzipped tar
.tar.gz | gzipped tar

Upon upload the `<file-to-upload>` becomes the name of the model attachment. The
attachment can be downloaded using the `attachment download` command. Use
`attachment remove` command to remove the attachment.

Note that there is no hard limit on the size of the attachment.

Example:

```
$ fastscore upload cube data1.zip
$ fastscore attachment list cube
     NAME   | TYPE | SIZE
------------+------+-------
  data1.zip | zip  |  1048904
$ fastscore attachment remove cube data1.zip
```

## Pneumo access
<a name="pneumo"></a>

```
fastscore pneumo [ history ]
```

The `pneumo` commands provide an access to Pneumo -- the internal message bus of
fastscore. `pneumo history` prints a few most recent Pneumo messages (60 max).
The `pneumo` command continuously prints Pneumo messages as they appear on the
bus.










## Monitoring engine operations
<a name="monitor"></a>

```
fastscore monitor
```

The `monitor` command shows a live text-based UI that shows information about
the state of the engine, loaded model, attached streams, and running jets. 

Example (assuming the engine is running):
```
$ fastscore monitor
==================================================
Engine: engine-1 [RUNNING]
Model:  cube (r)

Stream
--------------------------------------------------
input          I:0          4,649 rps     0.0 mbps
output         O:1          5,496 rps     0.0 mbps

Jet                             Input       Output
--------------------------------------------------
cube                        1,833 rps    1,885 rps
cube                        1,825 rps    1,935 rps
cube                        1,845 rps    1,944 rps
```

## User authentication
<a name="login"></a>

```
fastscore login <authentication mode> [ <username> ] [ <password> ]
```

```
DESCRIPTION:
   Use any of the login method: basic, oauth2, ldap, session cookie. (Case insensitive)

OPTIONS:
   --verbose, -V  Be verbose
```

## Troubleshooting data pipelines
<a name="debug"></a>

```
fastscore debug manifold
fastscore debug stream [ <slot> ]
```

The `debug` commands enable generation of a debug messages that describe
internal operations of the engine. These commands are not related to debugging
of the model source code. The commands are for advanced users only.

Example:

```
# In a separate window run: fastscore run cube inline:1,2,3 discard
$ fastscore debug manifold
14:40:22.491: model loaded
14:40:22.528: schema match: ok
14:40:22.536: stream open: ok
14:40:22.568: schema match: ok
14:40:22.575: stream open: ok
14:40:22.576: requesting data from slot 0
14:40:22.576: starting initial jet 1
14:40:22.882: state changes to RUNNING
14:40:22.885: jet <0.1474.0> is ready
14:40:22.885: 3 record(s) received from slot 0
14:40:22.885: dispatched to jet <0.1474.0>
14:40:22.885: more data requested from slot 0
14:40:22.885: stream at slot 0 reaches EOF
14:40:22.886: pending state change: FINISHING
14:40:22.892: writing output 1 record(s) to slot 1
14:40:22.893: write confirmed for slot 1
14:40:22.893: writing output 1 record(s) to slot 1
14:40:22.893: write confirmed for slot 1
14:40:22.893: writing output 1 record(s) to slot 1
14:40:22.893: write confirmed for slot 1
14:40:22.893: jet <0.1474.0> is ready
14:40:22.893: state changes to FINISHING
14:40:22.893: sending EOF to jet <0.1474.0>
14:40:22.894: jet <0.1474.0> finished
14:40:22.894: state changes to FINISHED
```

## Collecting statistics
<a name="stats"></a>

```
fastscore stats memory
fastscore stats cpu-utilization
fastscore stats jets
fastscore stats streams
```

The `stats` commands continuously report various statistics. The `stats memory`
and `stats cpu-utilization` commands show the current memory footprint and CPU
utilization of the engine. `stats jets` shows the records per second throughput
of all runnings jets. `stats streams` reports the throughput at each stream
slot.

Example (assuming the engine is running):

```
$ fastscore use engine-1
$ fastscore stats memory
engine-1: 2163.5mb
engine-1: 2163.5mb
engine-1: 2161.5mb
...
$ fastscore stats cpu-utilization
engine-1: kernel: 152.1 user: 69.0
engine-1: kernel: 152.7 user: 69.2
engine-1: kernel: 153.0 user: 69.5
...
$ fastscore stats jets
engine-1: 1000.0 rps/--- 
engine-1: 1745.2 rps/1696.0 rps 
engine-1: 1766.8 rps/1739.2 rps 
engine-1: ---/---
engine-1: 1823.2 rps/1832.0 rps 
engine-1: 1556.4 rps/1626.4 rps 
...
$ fastscore stats streams
engine-1: 0:25.0 rps | 1:1.0 rps
engine-1: 0:6000.0 rps | 1:5675.0 rps
engine-1: 0:6000.0 rps | 1:5711.0 rps
engine-1: 0:6000.0 rps | 1:5574.0 rps
...
```

The `stats` commands rely on sensor to collect statistics. `---` indicate that
data is not available at the moment.
