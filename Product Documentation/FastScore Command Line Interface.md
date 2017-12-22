---
title: "FastScore Command Line Interface"
---
# FastScore Command Line Interface

The FastScore Command Line Interface (CLI) is a Python utility that implements the FastScore REST API. This page provides a reference for the FastScore CLI commands, installation instructions, and examples.

## Installation

To install, extract the package, and execute the `setup.py` script with the following commands:

``` bash
wget https://s3-us-west-1.amazonaws.com/fastscore-cli/fastscore-cli-1.6.1.tar.gz
tar xzf fastscore-cli-1.6.1.tar.gz
cd fastscore-cli-1.6.1
sudo python setup.py install
```

> `python-setuptools` and `python-dev` (i.e. header files) are required to properly install the FastScore CLI. These may or may not be already present on your system. If not, you will need to install them.
> For example:
> ```
> $ sudo apt-get install python-setuptools
> $ sudo apt-get install python-dev
> ```

The installation may be tested by entering the command `fastscore help`: this should display a list of available commands in the console.

## Command Reference

Command explanations can be viewed using `fastscore help <command>`. All FastScore CLI commands have the syntax 

``` bash
fastscore <command> [subcommand] [arguments]
```

This section summarizes the various commands, and their arguments.

### Attachments:

Model attachments can be added and altered with the `fastscore attachment <subcommand>` family of commands.

| Subcommand | Input(s) | Description | Example |
| --- | --- | --- | --- |
| `list` | model name | Lists the attachments associated to the specified model. | `fastscore attachment list mymodel` |
| `upload` | model name, attachment file | Adds the specified attachment to the named model. Attachments must either be `.tar.gz` or `.zip` files. | `fastscore attachment upload mymodel attach.tar.gz` |
| `download` | model name, attachment file | Downloads the named attachment from the named model, and saves it with the same name. | `fastscore attachment download mymodel attach.tar.gz` |
| `remove` | model name, attachment file | Removes the specified attachment from the model. | `fastscore attachment remove mymodel attach.tar.gz` |


### Configuration

The `fastscore config` commands allow the display and setting of FastScore configurations.

| Subcommand | Input(s) | Description | Example |
| --- | --- | --- | --- |
| `set` | configuration file | Configures FastScore with the specified configuration file. | `fastscore config set config.yml` |
| `show` | (none) | Displays the current configuration. | `fastscore config show` |

### Connect

The command `fastscore connect` is used to connect the CLI to the FastScore Dashboard proxy service, so that FastScore may be controlled with the CLI. 

Example usage:

```
fastscore connect https://localhost:8000
```

> Generally, `fastscore connect` must be the first CLI command entered, so that the CLI knows the location of the Dashboard.

### Debug

Debug individual aspects of FastScore.


| `manifold` | (none) | Debug the manifold and receive more information about the manifold. | `fastscore debug manifold` |
| `stream` | Slot number | Debug a stream in a particular slot on an engine. | `fastscore debug slot 0` |


### Engine

Control the state of the engine through this list of subcommands.

| Subcommand | Input(s) | Description | Example |
| --- | --- | --- | --- |
| `pause` | (none) | Pauses the running engine. | `fastscore engine pause` |
| `unpause` | (none) | Restarts the paused engine. | `fastscore engine unpause` |
| `inspect` | (none) | Inspects the engine and shows the model and streams used in that engine. | `fastscore engine inspect` |
| `reset` | (none) | Resets the engine. | `fastscore engine reset` |


### Fleet

There are two FastScore CLI `fleet` commands: `fastscore fleet` and `fastscore fleet version`. These display the current status of the connected FastScore services, and (for the `version` command) the versions of FastScore running.

### Model

The `fastscore model` commands add, list, show, and remove models from Model Manage.

| Subcommand | Input(s) | Description | Example |
| --- | --- | --- | --- |
| `list` | (none) | Lists all existing models in Model Manage, and their formats. | `fastscore model list` |
| `add` | model name, source file (optional) | Adds a model to model manage with the specified name and code. If the source file is omitted, the model code may be input from the command line. | `fastscore model add mymodel model.R` |
| `show` | model name | Displays the code of specified model. | `fastscore model show mymodel` |
| `remove` | model name | Deletes the specified model and any attachments from Model Manage. | `fastscore model remove mymodel` |
| `verify` | model name | Parses the model to ensure it is properly formatted. | `fastscore model verify my-model` |
| `load` | model name | Loads the model into the engine, potentially, replacing any already loaded model. An Engine may start running the model if input/output streams are attached. | `fastscore model load mymodel` |
| `inspect` | (none) | Prints information about currently loaded model. If verbosity is requested, then the output of the command includes information about streams. | `fastscore model inspect` |
| `unload` | (none) | Unloading the model effectively stops the Engine. | `fastscore model unload` |
| `scale` | an integer | Scales the number of instances of the model. | `fastscore model scale 3` |


To specify the engine:
`fastscore -engine:engine-2` then run the command

### Monitor

Monitor data processing in an engine while it is running giving basic information on the streams and jets.

### Pneumo

Pneumo is the asynchronous notification module in FastScore. It uses Kafka to pass communications between the various containers, as well as to the user (on the 'notify' Kafka topic). The `fastscore pneumo` commands allow the user to listen to the Pneumo service.

| Subcommand | Input(s) | Description | Example |
| (none) | (none) | The `fastscore pneumo` command will print all Pneumo communications to the command line until stopped. | `fastscore pneumo` |
| `history` | (none) | Shows past messages that the Pneumo function has captured and prints them to the screen. | `fastscore pneumo history` |


The possible message types for `fastscore pneumo history` are:

* `health`, a health status change message
* `log`, a log message
* `model-console`, a console message from the running model
* `jet-status-report`, a status report from a model runner
* `output-report`, a report summarizing output of the model
* `rejected-data-report`, a report generated when any input or output records are rejected (for example, due to schema mismatches)
* `output-eof`, when the last of the input data is scored.

### Policy

Control the policy used by the engine to enforce rules around packages or libraries used by the running model.

| Subcommand | Input(s) | Description | Example |
| `set` | Policy file (optional) | Set a policy for a model that will run in an engine optionally with a file. | `fastscore policy set PyPolicy.yml -type:python` | 
| `show` | (none) | Shows the policies in place. | `fastscore policy show -type:python` | 


### Run

This command will run an engine with a model and a combination of streams using `fastscore run my-model my-stream-in my-stream-out` where multiple streams can be specified to run more than one input or output stream

### Schema

Add and remove AVRO schema objects in Model Manage.

| Subcommand | Input(s) | Description | Example |
| --- | --- | --- | --- |
| `list` | (none) | Lists all available schemas in Model Manage. | `fastscore schema list` |
| `add` | schema name, source file (optional) | Adds the specified schema to Model Manage. If the source file is omitted, content is taken from the command line input. | `fastscore schema add my-schema schema.avsc` |
| `show` | schema name | Displays the named schema. | `fastscore schema show my-schema` |
| `remove` | schema name | Removes the named schema from Model Manage. | `fastscore schema remove my-schema` |
| `verify` | schema name, data file (optional) | Verifies the schema against a set of data on the specified field and field types | `fastscore schema verify my-schema my-data-file` |

    
### Sensor

Add or remove sensor descriptors. These commands are covered in more detail at [the Sensors page](https://opendatagroup.github.io/Product%20Documentation/Sensors.html).

| Subcommand | Input(s) | Description | Example |
| --- | --- | --- | --- |
| `list` | (none) | Lists all available sensors. | `fastscore sensor list` |
| `add` | sensor name, source file (optional) | Adds the sensor with the specified name and source. If the source file is omitted, the contents are input from the command line. | `fastscore sensor add my-sensor sensor.json` |
| `show` | sensor name | Displays the sensor descriptor for the named sensor. | `fastscore sensor show my-sensor` |
| `remove` | sensor name | Removes the named sensor from Model Manage. | `fastscore sensor remove my-sensor` |
| `install` | sensor name | Installs a sensor. The sensor connects to the tapping point and starts collecting data according to its descriptor. The command returns the tap id of installed sensor. | `fastscore sensor install my-sensor` |
| `uninstall` | tap id | The tap id returned by installing the sensor is needed to uninstall the sensor. | `fastscore sensor uninstall 2` |
| `inspect` | tap id (optional) | Describes the installed sensor or all installed sensors if <tap-id> is omitted. | `fastscore sensor inspect` |
| `points` | (none) | Prints information about all available tapping points. | `fastscore sensor points` |


### Snapshot

A list of snapshots taken in model manage.

### Statistics 

A list of basic statistic about a model running in an engine.

| Subcommand | Input(s) | Description | Example |
| --- | --- | --- | --- |
| `memory` | (none) | Shows a basic report on memory consumption on a model running in an engine. | `fastscore stats memory` |
| `cpu-utilization` | (none) | Shows a basic report on CPU utilization on a model running in an engine. | `fastscore stats cpu-utilization` |
| `jets` | (none) | Shows a basic report on the jets running a model. | `fastscore stats jets` |
| `streams` | (none) | Shows a basic report on the streams that are transporting data into a running engine. | `fastscore stats streams` |


A user may request more readings using `-count:n` option where n is an integer.

### Stream

The stream commands add, remove, and sample streams.

| Subcommand | Input(s) | Description | Example |
| --- | --- | --- | --- |
| `list` | (none) | Lists all available stream descriptors in Model Manage. | `fastscore stream list` |
| `add` | stream name, stream descriptor source file (optional) | Adds the specified stream descriptor to Model Manage. If the source file is omitted, content is input from the command line. | `fastscore stream add file-in filestream.json` |
| `show` | stream name | Display the contents of the named stream descriptor. | `fastscore stream show file-in` |
| `sample` | stream name, number of items (optional) | Prints the specified number of records from the named stream. | `fastscore stream sample file-in` |
| `remove` | stream name | Removes the named stream from Model Manage. | `fastscore stream remove kafka-stream` |
| `attach` | stream name, slot | Attach a stream to the engine in a specified slot (even are for inputs and odd are for outputs) | `fastscore stream attach kafka-stream-in 0` |
| `detach` | slot | Detach a stream from a specified slot. | `fastscore stream detach 1` |
| `inspect` | slot (optional) | View streams in the specified slot | `fastscore stream inspect 0` |
| `verify` | stream name, slot | Run a descriptor validity check to ensure the stream transport will work and produce data. | `fastscore stream verify kafka-stream-in 0` |


### Use

There are two FastScore CLI `use` commands: `fastscore use` and `fastscore use container-name`. Select a container that fastscore will use as a target for subsequent commands. The kind of the container is taken into account. If a subsequent command requires a Model Manage services it uses the last Model Manage container mentioned in 'fastscore use' command. By default, CLI uses the first healthy container of a given kind listed in the configuration.