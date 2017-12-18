---
title: "FastScore Command Line Interface"
excerpt: ""
---
The FastScore Command Line Interface (CLI) is a Python utility that implements the FastScore REST API. This page provides a reference for the FastScore CLI commands, installation instructions, and examples.
[block:api-header]
{
  "type": "basic",
  "title": "Installation"
}
[/block]
To install, extract the package, and execute the `setup.py` script with the following commands:
```
wget https://s3-us-west-1.amazonaws.com/fastscore-cli/fastscore-cli-1.6.1.tar.gz
tar xzf fastscore-cli-1.6.1.tar.gz
cd fastscore-cli-1.6.1
sudo python setup.py install
```
[block:callout]
{
  "type": "danger",
  "body": "`python-setuptools` and `python-dev` (i.e. header files) are required to properly install the FastScore CLI. These may or may not be already present on your system. If not, you will need to install them.\n\nFor example:\n\n```\n$ sudo apt-get install python-setuptools\n$ sudo apt-get install python-dev\n```",
  "title": "Note: Linux Users"
}
[/block]
The installation may be tested by entering the command `fastscore help`: this should display a list of available commands in the console.
[block:api-header]
{
  "type": "basic",
  "title": "Command Reference"
}
[/block]
Command explanations can be viewed using `fastscore help <command>`. All FastScore CLI commands have the syntax 
```
fastscore <command> [subcommand] [arguments]
```
This section summarizes the various commands, and their arguments.

## Attachments:

Model attachments can be added and altered with the `fastscore attachment <subcommand>` family of commands.
[block:parameters]
{
  "data": {
    "h-0": "Subcommand",
    "h-1": "Input(s)",
    "h-2": "Description",
    "0-0": "`list`",
    "0-1": "model name",
    "0-2": "Lists the attachments associated to the specified model.",
    "1-0": "`upload`",
    "1-1": "model name, attachment file",
    "h-3": "Example",
    "0-3": "`fastscore attachment list mymodel`",
    "1-2": "Adds the specified attachment to the named model. Attachments must either be `.tar.gz` or `.zip` files.",
    "1-3": "`fastscore attachment upload mymodel attach.tar.gz`",
    "2-0": "`download`",
    "2-1": "model name, attachment file",
    "2-2": "Downloads the named attachment from the named model, and saves it with the same name.",
    "2-3": "`fastscore attachment download mymodel attach.tar.gz`",
    "3-0": "`remove`",
    "3-1": "model name, attachment file",
    "3-2": "Removes the specified attachment from the model.",
    "3-3": "`fastscore attachment remove mymodel attach.tar.gz`"
  },
  "cols": 4,
  "rows": 4
}
[/block]
## Configuration

The `fastscore config` commands allow the display and setting of FastScore configurations.
[block:parameters]
{
  "data": {
    "h-3": "Example",
    "h-2": "Description",
    "h-1": "Input",
    "h-0": "Command",
    "0-0": "`set`",
    "0-1": "configuration file",
    "0-2": "Configures FastScore with the specified configuration file.",
    "0-3": "`fastscore config set config.yml`",
    "1-0": "`show`",
    "1-1": "(none)",
    "1-2": "Displays the current configuration.",
    "1-3": "`fastscore config show`"
  },
  "cols": 4,
  "rows": 2
}
[/block]
## Connect

The command `fastscore connect` is used to connect the CLI to the FastScore Dashboard proxy service, so that FastScore may be controlled with the CLI. 

Example usage:
```
fastscore connect https://localhost:8000
```
[block:callout]
{
  "type": "warning",
  "title": "Warning!",
  "body": "Generally, `fastscore connect` must be the first CLI command entered, so that the CLI knows the location of the Dashboard."
}
[/block]
## Debug

Debug individual aspects of FastScore.
[block:parameters]
{
  "data": {
    "h-0": "Command",
    "h-1": "Input",
    "h-2": "Description",
    "h-3": "Examples",
    "0-0": "`manifold`",
    "0-1": "(none)",
    "1-0": "`stream`",
    "1-1": "Slot number",
    "1-2": "Debug a stream in a particular slot on an engine.",
    "1-3": "`fastscore debug slot 0`",
    "0-3": "`fastscore debug manifold`",
    "0-2": "Debug the manifold and receive more information about the manifold."
  },
  "cols": 4,
  "rows": 2
}
[/block]
## Engine

Control the state of the engine through this list of subcommands.

[block:parameters]
{
  "data": {
    "h-0": "Command",
    "h-1": "Input",
    "h-2": "Description",
    "h-3": "Example",
    "0-0": "`pause`",
    "1-0": "`unpause`",
    "2-0": "`inspect`",
    "3-0": "`reset`",
    "0-1": "(none)",
    "1-1": "(none)",
    "2-1": "(none)",
    "3-1": "(none)",
    "0-2": "Pauses the running engine.",
    "1-2": "Restarts the paused engine.",
    "2-2": "Inspects the engine and shows the model and streams used in that engine.",
    "3-2": "Resets the engine.",
    "0-3": "`fastscore engine pause`",
    "1-3": "`fastscore engine unpause`",
    "2-3": "`fastscore engine inspect`",
    "3-3": "`fastscore engine reset`"
  },
  "cols": 4,
  "rows": 4
}
[/block]
## Fleet

There are two FastScore CLI `fleet` commands: `fastscore fleet` and `fastscore fleet version`. These display the current status of the connected FastScore services, and (for the `version` command) the versions of FastScore running.

## Model

The `fastscore model` commands add, list, show, and remove models from Model Manage.
[block:parameters]
{
  "data": {
    "h-0": "Subcommand",
    "h-1": "Inputs",
    "h-2": "Description",
    "h-3": "Example",
    "0-0": "`list`",
    "1-0": "`add`",
    "2-0": "`show`",
    "3-0": "`remove`",
    "3-1": "model name",
    "2-1": "model name",
    "1-1": "model name, source file (optional)",
    "0-1": "(none)",
    "0-2": "Lists all existing models in Model Manage, and their formats.",
    "0-3": "`fastscore model list`",
    "1-2": "Adds a model to model manage with the specified name and code. If the source file is omitted, the model code may be input from the command line.",
    "1-3": "`fastscore model add mymodel model.R`",
    "2-2": "Displays the code of specified model.",
    "2-3": "`fastscore model show mymodel`",
    "3-2": "Deletes the specified model and any attachments from Model Manage.",
    "3-3": "`fastscore model remove mymodel`",
    "4-0": "`verify`",
    "4-1": "model name",
    "5-0": "`load`",
    "5-1": "model name",
    "6-0": "`inspect`",
    "7-0": "`unload`",
    "8-0": "`scale`",
    "5-2": "Loads the model into the engine, potentially, replacing any already loaded model. An Engine may start running the model if input/output streams are attached.",
    "5-3": "`fastscore model load mymodel`",
    "6-2": "Prints information about currently loaded model. If verbosity is requested, then the output of the command includes information about streams",
    "6-3": "`fastscore model inspect`",
    "7-2": "Unloading the model effectively stops the Engine.",
    "7-3": "`fastscore model unload`",
    "7-1": "(none)",
    "8-1": "an integer",
    "6-1": "(none)",
    "8-3": "`fastscore model scale 3`",
    "8-2": "Scales the number of instances of the model.",
    "4-3": "`fastscore model verify my-model`",
    "4-2": "Parses the model to ensure it is properly formatted."
  },
  "cols": 4,
  "rows": 9
}
[/block]
To specify the engine:
`fastscore -engine:engine-2` then run the command

## Monitor

Monitor data processing in an engine while it is running giving basic information on the streams and jets.

## Pneumo

Pneumo is the asynchronous notification module in FastScore. It uses Kafka to pass communications between the various containers, as well as to the user (on the 'notify' Kafka topic). The `fastscore pneumo` commands allow the user to listen to the Pneumo service.
[block:parameters]
{
  "data": {
    "h-0": "Subcommand",
    "h-1": "Inputs",
    "h-2": "Description",
    "h-3": "Example",
    "0-0": "(none)",
    "0-1": "(none)",
    "0-2": "The `fastscore pneumo` command will print all Pneumo communications to the command line until stopped.",
    "0-3": "`fastscore pneumo`",
    "1-0": "`history`",
    "1-1": "(none)",
    "1-2": "Shows past messages that the Pneumo function has captured and prints them to the screen.",
    "1-3": "`fastscore pneumo history`"
  },
  "cols": 4,
  "rows": 2
}
[/block]
The possible message types for `fastscore pneumo history` are:
* `health`, a health status change message
* `log`, a log message
* `model-console`, a console message from the running model
* `jet-status-report`, a status report from a model runner
* `output-report`, a report summarizing output of the model
* `rejected-data-report`, a report generated when any input or output records are rejected (for example, due to schema mismatches)
* `output-eof`, when the last of the input data is scored.

## Policy

Control the policy used by the engine to enforce rules around packages or libraries used by the running model.
[block:parameters]
{
  "data": {
    "h-0": "Command",
    "h-1": "Input",
    "h-2": "Description",
    "h-3": "Example",
    "0-0": "`set`",
    "1-0": "`show`",
    "0-1": "Policy file (optional)",
    "1-1": "(none)",
    "0-2": "Set a policy for a model that will run in an engine optionally with a file.",
    "1-2": "Shows the policies in place."
  },
  "cols": 4,
  "rows": 2
}
[/block]
## Run

This command will run an engine with a model and a combination of streams using `fastscore run my-model my-stream-in my-stream-out` where multiple streams can be specified to run more than one input or output stream

## Schema

Add and remove AVRO schema objects in Model Manage.
[block:parameters]
{
  "data": {
    "h-0": "Subcommand",
    "h-1": "Inputs",
    "h-2": "Description",
    "h-3": "Example",
    "0-0": "`list`",
    "0-1": "(none)",
    "0-2": "Lists all available schemas in Model Manage.",
    "0-3": "`fastscore schema list`",
    "1-0": "`add`",
    "1-1": "schema name, source file (optional)",
    "1-2": "Adds the specified schema to Model Manage. If the source file is omitted, content is taken from the command line input.",
    "1-3": "`fastscore schema add my-schema schema.avsc`",
    "2-0": "`show`",
    "2-1": "schema name",
    "2-2": "Displays the named schema.",
    "2-3": "`fastscore schema show my-schema`",
    "3-0": "`remove`",
    "3-1": "schema name",
    "3-2": "Removes the named schema from Model Manage.",
    "3-3": "`fastscore schema remove my-schema`",
    "4-0": "`verify`",
    "4-1": "schema name, data file (optional)",
    "4-2": "Verifies the schema against a set of data on the specified field and field types",
    "4-3": "`fastscore schema verify my-schema my-data-file`"
  },
  "cols": 4,
  "rows": 5
}
[/block]
## Sensor

Add or remove sensor descriptors. These commands are covered in more detail at [the Sensors page](doc:sensors).
[block:parameters]
{
  "data": {
    "h-0": "Subcommand",
    "h-1": "Inputs",
    "h-2": "Description",
    "h-3": "Example",
    "0-0": "`list`",
    "1-0": "`add`",
    "2-0": "`show`",
    "3-0": "`remove`",
    "0-1": "(none)",
    "1-1": "sensor name, source file (optional)",
    "2-1": "sensor name",
    "3-1": "sensor name",
    "0-2": "Lists all available sensors.",
    "1-2": "Adds the sensor with the specified name and source. If the source file is omitted, the contents are input from the command line.",
    "2-2": "Displays the sensor descriptor for the named sensor.",
    "3-2": "Removes the named sensor from Model Manage.",
    "0-3": "`fastscore sensor list`",
    "1-3": "`fastscore sensor add my-sensor sensor.json`",
    "2-3": "`fastscore sensor show my-sensor`",
    "3-3": "`fastscore sensor remove my-sensor`",
    "4-0": "`install`",
    "5-0": "`uninstall`",
    "6-0": "`inspect`",
    "7-0": "`points`",
    "4-1": "sensor name",
    "5-1": "tap id",
    "6-1": "tap id (optional)",
    "7-1": "(none)",
    "4-3": "`fastscore sensor install my-sensor`",
    "7-3": "`fastscore sensor points`",
    "7-2": "Prints information about all available tapping points.",
    "6-2": "Describes the installed sensor or all installed sensors if <tap-id> is omitted.",
    "4-2": "Installs a sensor. The sensor connects to the tapping point and starts collecting data according to its descriptor. The command returns the tap id of installed sensor.",
    "5-2": "The tap id returned by installing the sensor is needed to uninstall the sensor.",
    "5-3": "`fastscore sensor uninstall 2`",
    "6-3": "`fastscore sensor inspect`"
  },
  "cols": 4,
  "rows": 8
}
[/block]
## Snapshot

A list of snapshots taken in model manage.

## Statistics 

A list of basic statistic about a model running in an engine.
[block:parameters]
{
  "data": {
    "h-0": "Subcommand",
    "h-1": "Inputs",
    "h-2": "Description",
    "h-3": "Example",
    "0-0": "`memory`",
    "1-0": "`cpu-utilization`",
    "2-0": "`jets`",
    "3-0": "`streams`",
    "0-1": "(none)",
    "1-1": "(none)",
    "2-1": "(none)",
    "3-1": "(none)",
    "0-3": "`fastscore stats memory`",
    "1-3": "`fastscore stats cpu-utilization`",
    "2-3": "`fastscore stats jets`",
    "3-3": "`fastscore stats streams`",
    "0-2": "Shows a basic report on memory consumption on a model running in an engine.",
    "1-2": "Shows a basic report on CPU utilization on a model running in an engine.",
    "2-2": "Shows a basic report on the jets running a model.",
    "3-2": "Shows a basic report on the streams that are transporting data into a running engine."
  },
  "cols": 4,
  "rows": 4
}
[/block]
A user may request more readings using `-count:n` option where n is an integer.

## Stream

The stream commands add, remove, and sample streams.
[block:parameters]
{
  "data": {
    "h-0": "Subcommand",
    "h-1": "Inputs",
    "h-2": "Description",
    "h-3": "Example",
    "0-0": "`list`",
    "0-1": "(none)",
    "0-2": "Lists all available stream descriptors in Model Manage.",
    "0-3": "`fastscore stream list`",
    "1-0": "`add`",
    "1-1": "stream name, stream descriptor source file (optional)",
    "1-2": "Adds the specified stream descriptor to Model Manage. If the source file is omitted, content is input from the command line.",
    "1-3": "`fastscore stream add file-in filestream.json`",
    "2-0": "`show`",
    "2-1": "stream name",
    "2-2": "Display the contents of the named stream descriptor.",
    "2-3": "`fastscore stream show file-in`",
    "3-0": "`sample`",
    "3-1": "stream name, number of items (optional)",
    "3-2": "Prints the specified number of records from the named stream.",
    "3-3": "`fastscore stream sample file-in`",
    "4-0": "`remove`",
    "4-1": "stream name",
    "4-2": "Removes the named stream from Model Manage.",
    "4-3": "`fastscore stream remove kafka-stream`",
    "6-0": "`detach`",
    "5-0": "`attach`",
    "7-0": "`inspect`",
    "8-0": "`verify`",
    "5-1": "stream name, slot",
    "6-1": "slot",
    "7-1": "slot (optional)",
    "8-1": "stream name, slot",
    "5-2": "Attach a stream to the engine in a specified slot (even are for inputs and odd are for outputs)",
    "6-2": "Detach a stream from a specified slot.",
    "5-3": "`fastscore stream attach kafka-stream-in 0`",
    "6-3": "`fastscore stream detach 1`",
    "7-2": "View streams in the specified slot",
    "7-3": "`fastscore stream inspect 0`",
    "8-2": "Run a descriptor validity check to ensure the stream transport will work and produce data.",
    "8-3": "`fastscore stream verify kafka-stream-in 0`"
  },
  "cols": 4,
  "rows": 9
}
[/block]
## Use

There are two FastScore CLI `use` commands: `fastscore use` and `fastscore use container-name`. Select a container that fastscore will use as a target for subsequent commands. The kind of the container is taken into account. If a subsequent command requires a Model Manage services it uses the last Model Manage container mentioned in 'fastscore use' command. By default, CLI uses the first healthy container of a given kind listed in the configuration.