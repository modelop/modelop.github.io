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
* [fastscore attachment upload/download/list/remove](#attachment)
* [fastscore stream add/show/list/remove](#stream-mgmt)
* [fastscore schema add/show/list/remove](#schema-mgmt)
* [fastscore sensor add/show/list/remove](#sensor-mgmt)

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
fastscore login <username>
```

The command authenticates the user to secure FastScore deployments. The command
prompts the user for the password.

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
fastscore use <instance-name>
```

The command selects `<instance-name>` as a target of subsequent commands. In
addition, it makes `<instance-name>` the preferred instance of a specific
service. For example, `fastscore use engine-1` makes `engine-1` the target of
sensor management commands. Any command that require an instance of an `engine`
service will now use the `engine-1` instance.

Example:

```
$ fastscore use engine-1 -v
'engine-1' set as a preferred instance of 'engine'
Subsequent commands to target 'engine-1'
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

## Customizing engines

TODO

## Verifying models and streams

model verify

TODO

## Running simple models

run

TODO

## Constructing data pipelines

model load/unload

TODO

## Inspecting data pipelines

model inspect

TODO

## Scaling models

model scale

TODO

## Using REST for model input/output

model input/output/interact

## Model state snapshots 

TODO

## Pneumo access

TODO

## Troubleshooting data pipelines

TODO

## Monitoring FastScore operation

-m option

TODO

## Profiling engines

TODO


