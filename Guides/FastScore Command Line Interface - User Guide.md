---
title: The FastScore CLI User Guide
description: The guide describes all commands available through the FastScore
CLI with their respective options.
css: buttondown.css
---

# FastScore CLI v1.6.1 / User Guide

This guide describes the complete set of commands and options supported by the
FastScore CLI.

The general syntax of the CLI command is:

```
fastscore <command> <subcommand> ...
```

## Command index

* [fastscore help](#help)
* [fastscore connect](#connect)
* [fastscore login](#login)
* [fastscore config set/show](#config)
* [fastscore fleet](#fleet)
* [fastscore use](#use)
* [fastscore model add/show/list/remove](#model-mgmt)
* [fastscore model load/unload/verify/inspect](#model-load)
* [fastscore model scale](#model-scale)
* [fastscore attachment upload/download/list/remove](#attachment)
* [fastscore stream add/show/list/remove](#stream-mgmt)
* [fastscore stream attach/detach/verify/inspect](#stream-attach)
* [fastscore stream sample](#stream-sample)
* [fastscore schema add/show/list/remove](#schema-mgmt)
* [fastscore schema verify](#schema-verify)
* [fastscore sensor add/show/list/remove](#sensor-mgmt)
* [fastscore sensor install/uninstall/inspect/points](#sensor-install)
* [fastscore engine reset/inspect/pause/unpause](#engine-state)
* [fastscore snapshot list/show/remove](#snapshot-mgmt)
* [fastscore snapshot restore](#snapshot-restore)
* [fastscore policy set/show](#policy)
* [fastscore stats](#stats)
* [fastscore debug](#debug)
* [fastscore profile](#profile)
* [fastscore pneumo](#pneumo)
* [fastscore monitor](#monitor)
* [fastscore run](#run-simple)

## Getting help
<a name="help"></a>

```
fastscore help
fastscore help <command>
fastscore help options
```

The `help` command prints a list of available commands or a syntax synposis
for a specific command. The `help options` command produces a list of supported
options.

## Command options

Command options start with '-' character. Note that, `-wait` is a proper
option, not `--wait`. An option can be placed anywhere on the command line.

Most options are command-specific. They are explained along with the
corresponding command. Some options are applicable to all commands:

Option | Description
-------|------------
`-v` | Be verbose
`-json` | Represent output as JSON - handy for scripts

Example:

```
$ fastscore fleet -v -json
[
  {
    "name": "engine-1",
    "port": 8003,
    "built_on": "Sun Nov 12 11:51:46 UTC 2017",
    "host": "engine",
    "api": "engine",
    "health": "ok",
    "release": "1.6.1",
    "id": "426e83fb-7012-4906-9c0e-a58a7a380635"
  },
  ...
```

## Connecting to FastScore
<a name="connect"></a>

```
fastscore connect <location> [ -nowait ]
```

The command establishes a connection between the command line interface and the
FastScore deployment. The `<location>` is the URL of the FastScore proxy, e.g.
`https://1.2.3.4:8000`. The command saves the location to the file named
`.fastscore` in the home directory. The subsequent commands use the saved
location.

By default, the command waits for the provided location to become available. Use
`-nowait` option to disable the check and return immediately.

Example:

```
$ fastscore connect https://localhost:8000 -v
Waiting...............
Connected to FastScore proxy at https://localhost:8000
```

## User authentication
<a name="login"></a>

```
fastscore login <username> [ <password> ]
```

The command authenticates the user to secure FastScore deployments. If
`<password>` is omitted, the command prompts the user for the password.

Example:

```
$ fastscore login williamgates
Password: ***
```

## Configuring FastScore
<a name="config"></a>

```
fastscore config set <config-file>
fastscore config show
```

The first command sets the configuration of the FastScore deployment. The second -
prints the current configuration. The `<config-file>` is the name of the
configuration file. The configuration file uses YAML format. (TODO: a link to
the document that describes the FastScore configuration)

Example:

```
$ fastscore config set config.yaml -v
Configuration set
$ fastscore config show
fastscore:
  db: {host: database, password: root, port: 3306, type: mysql, username: root}
  fleet:
  - {api: model-manage, host: model-manage, port: 8002}
  - {api: engine, host: engine, port: 8003}
  pneumo:
    bootstrap: ['kafka:9092']
    type: kafka
topic: notify
```

## Listing services
<a name="fleet"></a>

```
fastscore fleet [ -wait ]
```

The command outputs the information about the currently running FastScore
services. The verbose output includes information about CLI and Connect.

Use `-wait` option to make the command wait for all services to report a
healthy status.

Example:

```
$ fastscore fleet -wait -v
Waiting...done
Name            API           Health    Release    Built On
--------------  ------------  --------  ---------  ----------------------------
CLI             UI            ok        1.6.1      Wed Nov 15 15:01:32 UTC 2017
connect         connect       ok        1.6.1      Thu Nov  9 16:01:18 UTC 2017
engine-1        engine        ok        1.6.1      Sun Nov 12 11:51:46 UTC 2017
model-manage-1  model-manage  ok        1.6.1      Thu Nov  9 16:01:58 UTC 2017
```

## Choosing an instance
<a name="use"></a>

```
fastscore use [ <instance-name> ]
```

The command selects `<instance-name>` as a target of subsequent commands. In
addition, it makes `<instance-name>` the preferred instance of a specific
service. For example, `fastscore use engine-1` makes `engine-1` the target of
sensor management commands. Any command that require an instance of an `engine`
service will now use the `engine-1` instance. If `<instance-name>` is omitted
the command prints the current target instance name.

Example:

```
$ fastscore use engine-1 -v
'engine-1' set as a preferred instance of 'engine'
Subsequent commands to target 'engine-1'
$ fastscore use
engine-1
```

## Managing models
<a name="model-mgmt"></a>

```
fastscore model add <model-name> [ <source-file> ] [ -type:<model-type> ]
fastscore model show <model-name> [ -e ]
fastscore model list
fastscore model remove <model-name>
```

The `model add` command introduces a model to FastScore. If the source file is
omitted the command reads the model source from the standard input. The type of
the model can be set using `-type:<model-type>` option:

Option | Model type
-------|-----------
-type:python | Python 2.x
-type:python3 | Python 3.x
-type:R or -type:r | R
-type:java | Java
-type:c | C
-type:pfa-json | PFA (JSON)
-type:pfa-yaml | PFA (YAML)
-type:pfa-pretty | PFA (PrettyPFA)
-type:h2o-java | h20.ai (Java)
-type:octave | Matlab using Octave
-type:sas | SAS (experimental)

If the `-type:` option is omitted the model type is determined by the extension
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
gets the model type. For example, if the source code starts with 'def action('
the command assumes that the model type is Python.

The `model show` prints the model source code to the standard output. The `-e`
(edit) option provides for a convenient modification of the model. The edit
option spawns an editor and updates the model when the editor closes. The editor
name is taken from the EDITOR environment variable. By default, the editor name
is 'vi'.

The `model list` command shows the list of models known to FastScore. The `model
remove` command removes the corresponding model.

Example:

```
$ fastscore model add cube -type:python3 <<EOF
def action(x):
  return x*x*x
EOF
$ fastscore model list
Name           Type
-------------  -------
cube           Python3
$ fastscore model show cube
def action(x):
  return x*x*x
$ fastscore model remove cube -v
Model 'cube' removed
```

## Model attachments
<a name="attachment"></a>

```
fastscore attachment upload <model-name> <file-to-upload>
fastscore attachment download <model-name> <attachment-name>
fastscore attachment list <model-name>
fastscore attachment remove <model-name> <attachment-name>
```

FastScore models may have attachments - archives containing arbitrary data made
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
$ fastscore attachment list cube -v
Name       Type       Size
---------  ------  -------
data1.zip  zip     1048904
$ fastscore attachment remove cube data1.zip -v
Attachment removed
```

## Managing streams
<a name="stream-mgmt"></a>

```
fastscore stream add <stream-name> [ <descriptor-file> ]
fastscore stream show <stream-name> [ -e ]
fastscore stream list
fastscore stream remove <stream-name>
```

The `stream add` command adds a stream descriptor to FastScore. The syntax of
the stream descriptor is explained here (TODO: add a link to stream descriptor
syntax). If the `<descriptor-file>` is omitted, the command reads the descriptor
from the standard input.

The `stream show` prints the stream descriptor to the standard output. The `-e`
(edit) option allows editing the descriptor in-place. The edit option
spawns an editor and updates the stream descritor when the editor closes. The
editor name is taken from the EDITOR environment variable. By default, the
editor name is 'vi'.

The `stream list` command shows the list of streams known to FastScore. The `stream remove`
command removes the corresponding stream.

Example:

```
$ fastscore stream add input-1 <<EOF
{
  "Transport": ...
  ...
}
EOF
$ fastscore stream list
input-1
$ fastcore stream remove input-1 -v
Stream removed
```

## Managing schemas
<a name="schema-mgmt"></a>

```
fastscore schema add <schema-name> [ <schema-file> ]
fastscore schema show <schema-name> [ -e ]
fastscore schema list
fastscore schema remove <schema-name>
```

The `schema add` command adds an Avro schema to FastScore. If the
`<schema-file>` is omitted, the command reads the standard input.

The `schema show` prints the schema to the standard output. The `-e` (edit)
option allows editing the schema in-place. The edit option
spawns an editor and updates the schema after the editor closes. The editor name
is taken from the EDITOR environment variable. By default, the
editor name is 'vi'.

The `schema list` command shows the list of schemas known to FastScore. The `schema remove`
command removes the corresponding schema.

Example:

```
$ fastscore schema add sch-1 <<EOF
["null","double"]
EOF
$ fastscore schema list -v
Name   Type
-----  ------
sch-1  Avro
$ fastcore schema remove sch-1 -v
Schema removed
```

## Verifying schemas
<a name="schema-verify"></a>

```
fastscore schema verify <schema-name> [ <data-file> ]
```

TODO

## Managing sensors
<a name="sensor-mgmt"></a>

```
fastscore sensor add <sensor-name> [ <sensor-file> ]
fastscore sensor show <sensor-name> [ -e ]
fastscore sensor list
fastscore sensor remove <sensor-name>
```

The `sensor add` command adds a sensor descriptor to FastScore. If the
`<sensor-file>` is omitted, the command reads the standard input. The syntax of
a sensor descriptor is described here (TODO: add a link to the document
describing the syntax).

The `sensor show` prints the sensor descriptor to the standard output. The `-e`
(edit) option allows editing the sensor descriptor. The edit option spawns an
editor and updates the descriptor after the editor closes. The editor name
is taken from the EDITOR environment variable. By default, the
editor name is 'vi'.

The `sensor list` command shows the list of sensor descriptors known to
FastScore. The `sensor remove` command removes the corresponding sensor
descriptor.

Note that the above commands operate on sensor descriptors, not active sensors.
See `sensor install/uninstall/inspect` commands for more.

Example:

```
$ fastscore sensor add watchdog-1 <<EOF
{ ... }
EOF
$ fastscore sensor list
watchdog
$ fastcore sensor remove watchdog-1
Sensor removed
```

## Attaching/detaching streams
<a name="stream-attach"></a>

```
fastscore stream attach <stream-name> <slot>
fastscore stream detach <slot>
fastscore stream verify <stream-name> <slot>
fatsscore stream inspect
```

The `stream attach` opens the stream and attaches it to the `<slot>`. Typically,
the command retrieves the stream descriptor from Model Manage using
`<stream-name>`. Alternatively, the `<stream-name>` may contain a literal
stream descriptor. See [Url-like stream descriptors](#literal-streams) for
details.

The `stream detach` command closes and detaches the stream. It is not possible
to detach the stream when the model is running. However, it is possible to
attach a different stream to the same slot using the `stream attach` command
while data is being processed.

The `stream verify` command performs all the same steps as `stream attach`
without actually attaching the stream to the `<slot>`. It prints the internal
representation of the stream descriptor with all default values substituted.

Example:

```
$ fastscore stream add s1
{"Transport":"REST","Schema":null}
^D
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
  Slot  Name           Transport    EOF
------  -------------  -----------  -----
     0  inline-526507  REST         False
     1  inline-809896  REST         False
```

## Sampling streams
<a name="stream-sample"></a>

```
fastscore stream sample <stream-name> [ -count:NNN ]
```

The `stream sample` reads a few data records from the stream. This happens in
the context of the engine. Otherwise, stream sampling is unrelated to the data
pipeline. If `-count:NNN` option is omitted, the commands attempts to read 10
records max.

```
$ fastscore stream sample inline:2,3,5,7,11 -count:3
   1: 2
   2: 3
   3: 5
```

```
# Assume that /tmp/rnd1.dat file exists
$ fastscore stream add rnd
{
  "Encoding": null,
  "Envelope": {
    "Type": "fixed",
    "Size": 8
  },
  "Transport": {
    "Path": "/tmp/rnd1.dat",
    "Type": "file"
  },
  "Schema": null
}
^D
$ fastscore stream sample rnd -count:5
   1: b9 7e b5 4b af 01 6d 65                          .~.K..me........
   2: 6c 8d db 99 03 42 95 81                          l....B..........
   3: 93 a9 2f 1b 9e 77 3b eb                          ../..w;.........
   4: 60 28 58 8c a8 12 fc 2b                          `(X....+........
   5: a5 14 c7 64 56 97 aa 79                          ...dV..y........
```

## Loading/unloading models
<a name="model-load"></a>

```
fastscore model load <model-name> [ -schema:<schema-name>:<schema-data> ... ]
fastscore model unload
fastscore model verify <model-name>
fastscore mode inspect
```

The `model load` command performs all preparatory steps and gets ready to start
data processing. The target engine can be selected using the `use` command. The
preparatory steps include verification of the model syntax, checking if the
model follows the FastScore model conventions, e.g. if the action() method is
defined, analysing the model smart comments (TODO: link to the description of
the model smart comments), fetching attachments from Model Manage and
unpacking them. The model smart comments indicate which stream slots must be
occupied for the model to run. If an unexpected slot has a stream attached the
`model load` command will fail. If all requied streams are attached, the loaded
model will start the data processing. See also `engine pause` command.

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

It is possible to provide schemas required by the model as command line options.
This may be needed if the FastScore deployment does not have a Model Manage
instance. The `<schema-data>` can be either a file name or a literal schema. For
example, `-schema:input:\"double\"`.

Example:

```
$ fastscore model add cube
# fastscore.schema.0: in1
def action(x):
  yield x*x*x
^D
$ fastscore model verify cube -v
Error: schema 'in1' not found
$ fastscore model verify cube -v -schema:in1:\"int\"
Name    Type      SLOC
------  ------  ------
cube    python       3

  Slot  Schema    Action    Recordsets          Slot  Schema    Recordsets
------  --------  --------  ------------  --  ------  --------  ------------
     0  "int"     action    No                     1  -         No

The model contains no errors
```

The `model inspect` prints information about the currently loaded model. Its
output is similar to the output of the `model verify` command.

Example:

```
$ fastscore model add sqrt
action <- function(x) emit(x*x)
^D
$ fastscore model load sqrt
$ fastscore model inspect
Name    Type      SLOC  Snapshots
------  ------  ------  -----------
sqrt    r            1  none

  Slot  Schema    Action    Recordsets          Slot  Schema    Recordsets
------  --------  --------  ------------  --  ------  --------  ------------
     0  -         action    No                     1  -         No

No jets started
```

## Scaling models
<a name="model-scale"></a>

```
fastscore model scale <jet-count>
```

The `model scale` command changes the number of model instances -- jets --
running concurrently. The number of jets can be changed while the model is
running or during the initialization phase.

Example:

```
$ fastscore model add sqrt
action <- function(x) emit(x*x)
^D
$ fastscore model scale 4
$ fastscore run sqrt rest: rest:
$ fastscore model inspect
Name    Type      SLOC  Snapshots
------  ------  ------  -----------
sqrt    r            1  none

  Slot  Schema    Action    Recordsets          Slot  Schema    Recordsets
------  --------  --------  ------------  --  ------  --------  ------------
     0  -         action    No                     1  -         No

  Jet #    Pid    Sandbox
-------  -----  ---------
      1    122   43661788
      2    128  104818564
      3    134   43441871
      4    140  108589417
```

## Model input/output using REST
<a name="model-rest"></a>

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
$ fastscore model add sqrt
action <- function(x) emit(x*x)
^D
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
$ fastscore model add sqrt
action <- function(x) emit(x*x)
^D
$ fastscore run sqrt rest: rest:
$ fastscore model interact
> 7
49
> 11
121
> 100
10000
> ^D
```

Note that these commands do not close input/output streams. They may be run
multiple times.

## Active sensor operations
<a name="sensor-install"></a>

```
fastscore sensor install <sensor-name>
fastscore sensor uninstall <tap-id>
fastscore sensor inspect [ <tap-id> ]
fastscore sensor points
```

The `sensor install` command adds the sensor to the current service instance.
See `use` command. Upon success, the command prints `<tap-id>` of installed
sensor. Other active sensor operations take `<tap-id>` as an argument.

The `sensor install` prints information about all active sensors for the current
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
Sensor id 15 is attached to 'manifold.debug' at 'engine-1'.
$ fastscore sensor uninstall 15 -v
Sensor uninstalled
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
<a name="engine-state"></a>

```
fastscore engine reset
fastscore engine inspect
fastscore engine pause
fastscore engine unpause
```

A FastScore engine has one of the following seven states:

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
$ fastscore engine inspect -v
The current engine state is RUNNING.

The engine is reading data from input streams, passing them to model instances,
collecting outputs from the model, and writing them to output streams.
$ fastscore engine reset
$ fastscore engine inspect
INIT
```

The `engine pause` puts the engine into the PAUSED state. It is not possible to
pause an engine which is currently in FINISHING, FINISHED, or ERROR state. If
the pause is requested during initialization, the engine becomes paused
when it is about to enter the RUNNING state. Use `engine unpause` to continue
data processing.

Example:

```
$ fastscore engine inspect
INIT
$ fastscore engine pause
$ fastscore engine inspect
INIT
$ fastscore run cube rest: rest:
$ fastscore engine inspect
PAUSED
$ fastscore engine unpause
$ fastscore engine inspect
RUNNING
```

## Running simple models
<a name="run-simple"></a>

```
fastscore run <model-name> <stream-0> <stream-1>
```

TODO

## Managing state snapshots
<a name="snapshot-mgmt"></a>

```
fastscore snapshot list <model-name>
fatsscore snapshot show <model-name> <snapshot-id>
fatsscore snapshot remove <model-name> <snapshot-id>
```

TODO

## Restoring state snapshots
<a name="snapshot-restore"></a>

```
fastscore snapshot restore <model-name> [ <snapshot-id> ]
```

TODO

## Managing model environments
<a name="policy"></a>

```
fastscore policy set [ <policy-file> ]
fastscore policy show
```

TODO

## Collecting statistics
<a name="stats"></a>

```
fastscore stats memory
fastscore stats cpu-utilization
fastscore stats jets
fastscore stats streams
```

TODO

## Troubleshooting data pipelines
<a name="debug"></a>

```
fastscore debug manifold
fastscore debug stream [ <slot> ]
```

TODO

## Profiling internal operations
<a name="profile"></a>

```
fastscore profile stream <slot>
```

TODO

## Pneumo access
<a name="pneumo"></a>

```
fastscore pneumo [ history ]
```

TODO

## Monitoring engine operations
<a name="monitor"></a>

```
fastscore monitor
```

-m option

TODO

## <a name="literal-streams"></a>Url-like stream descriptors

A literal stream is a shortened representation of a stream descriptor. It can be
used instead of the stream name for commands, such as `stream attach`. The
commands look for a ':' character to distinguish a stream name from a literal
stream descriptor. The table below contains examples of literal stream
descriptors.

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

