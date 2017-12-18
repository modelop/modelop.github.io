---
title: "Stream Descriptors"
excerpt: "Documentation for stream descriptors"
---
# ** Contents **

1. [Overview](#overview)
2. [Field Descriptions](#field-descriptions)
  2.1 [Common Fields](#section-common-fields)
  2.2 [Transport Fields](#section-transport-fields)
    - [REST](#section-rest)
    - [HTTP](#section-http)
    - [Kafka](#section-kafka)
    - [File](#section-file)
    - [UDP](#section-udp)
    - [TCP](#section-tcp)
    - [Executable](#section-executable)
    - [Debug](#section-debug)
    - [Console and Discard](#section-console-and-discard)
3. [Examples](#examples)
[block:api-header]
{
  "type": "basic",
  "title": "Overview"
}
[/block]
A stream descriptor is a JSON document that contains all of the information about a stream. In general, an input stream reads messages from an underlying transport, optionally verifies, and feeds them to models. The output stream acts similarly, but in the reverse order. Stream descriptors are required for the engine to read input and produce output, and can additionally be used to enforce input and output typing using AVRO schema.

By convention, all field names of a stream descriptor start with a capital letter and do not use punctuation. Many fields of a stream descriptor have default values that depend on values of other fields. If a field is omitted, it is set to a default value. Sometimes, you may need to explicitly set field to `null` to avoid this behavior. For example, if omitted, an `EndMarker` is set to "`$end-of-stream`" for certain streams. To disable the 'soft' end-of-file behavior based on the `EndMarker` you need to set this field to `null`.

Some fields accept shortcut values. For instance, you may set the `Transport` field to `"discard"` string instead of the equivalent yet more verbose '`{"Type": "discard"}`' object.
[block:api-header]
{
  "type": "basic",
  "title": "Field Descriptions"
}
[/block]
A template for a stream descriptor is below. Note that the type of transport used will determine which fields in the `Transport` section are needed. Additionally, the top-level fields `Loop`, `EndMarker`, `SkipTo`, and `SkipToRecord` have default values depending on the choice of transport. 
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Description\": \"My Sample stream descriptor\",\n  \"Transport\": {\n    \"Type\": \"REST\" | \"HTTP\" | \"kafka\" | \"file\" | \"TCP\" | \"UDP\" | \"exec\" | \"debug\" | \"console\" | \"discard\",\n    \"Url\" : \"http://www.mywebsite.com\", // HTTP only\n    \"BootstrapServers\": [\"127.0.0.1:9181\", \"192.168.1.5:9003\"], // Kafka only\n    \"Topic\": \"My Kafka Topic\", // Kafka only\n    \"Partition\" : 1, // Kafka only, defaults to 0\n    \"MaxWaitTime\": 50000, // Kafka only, defaults to 8388607\n    \"Principal\" : \"kafka/kafka@REALM\", // Kafka Authenciated only\n    \"Keytab\": \"/fastscore.keytab\", // Kafka Authenciated only\n    \"Path\": \"/path/to/file.ext\", // file only\n    \"Host\": \"127.0.0.1\", // TCP only\n    \"Port\": 8182, // TCP and UDP only\n    \"BindTo\": \"127.0.0.1\", // UDP only, defaults to 0.0.0.0\n    \"Data\" : [ \"abc\", \"def\", \"ghi\"], // debug only\n    \"DataBinary\": [\"AQIDBQ==\"], // debug only, use one of Data or DataBinary\n  },\n  \"Loop\": false,\n  \"EndMarker\": \"$end-of-stream\", \n  \"SkipTo\": null, \n  \"SkipToRecord\": \"latest\",\n  \"Envelope\": \"deliminated\",\n  \"Encoding\": null | \"json\" | \"avro-binary\",\n  \"Schema\": { ... } // AVRO schema for stream\n}",
      "language": "json",
      "name": "Stream Descriptor Template"
    }
  ]
}
[/block]
Once you have constructed your stream descriptor, you may validate it against the following AVRO schema. (Some modification of this schema may be required dependent on the choice of default values.)
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"type\": \"record\",\n  \"fields\": [\n    {\"name\": \"Version\", \"type\": \"string\"},\n    {\"name\": \"Description\", \"type\":\"string\", \"default\": \"\"},\n    {\"name\": \"Transport\", \"type\": \n    \t[\n        {\"type\": \"record\", \"fields\": [\n          {\"name\":\"Type\", \"type\":\"string\"}]}, // REST\n        {\"type\": \"record\", \"fields\": [\n          {\"name\": \"Type\", \"type\": \"string\"}, // HTTP\n          {\"name\": \"Url\", \"type\": \"string\"}]},\n        {\"type\": \"record\", \"fields\": [\n          {\"name\": \"Type\", \"type\": \"string\"}, // Kafka\n          {\"name\": \"BootstrapServers\", \"type\":{\"type\": \"array\", \"items\":\"string\"} },\n          {\"name\": \"Topic\", \"type\": \"string\"},\n          {\"name\": \"Partition\", \"type\": \"int\", \"default\": 0},\n          {\"name\": \"MaxWaitTime\", \"type\": \"int\", \"default\": 8388607}]},\n        {\"type\": \"record\", \"fields\": [\n          {\"name\": \"Type\", \"type\": \"string\"}, // File\n          {\"name\": \"Path\", \"type\": \"string\"}]},\n        {\"type\": \"record\", \"fields\": [\n          {\"name\": \"Type\", \"type\": \"string\"}, // TCP\n          {\"name\": \"Host\", \"type\": \"string\"}, \n          {\"name\": \"Port\", \"type\": \"int\"}]},\n        {\"type\": \"record\", \"fields\": [\n          {\"name\": \"Type\", \"type\": \"string\"}, // UDP\n          {\"name\": \"BindTo\", \"type\": \"string\", \"default\": \"0.0.0.0\"},\n          {\"name\": \"Port\", \"type\": \"int\"}]},\n        {\"type\": \"record\", \"fields\": [\n          {\"name\": \"Type\", \"type\": \"string\"}, // debug\n          {\"name\": \"Data\", \"type\": [\"string\", {\"type\": \"array\", \"items\":  \"string\"}]}, // only one of Data or DataBinary is required\n          {\"name\": \"DataBinary\", \"type\": \"string\"}]},\n        {\"type\": \"record\", \"fields\": [{\"name\":\"Type\", \"type\": \"string\"}]},\n        \"string\" // discard or console\n    \t]},\n    {\"name\": \"Loop\", \"type\":\"boolean\", \"default\": false}, // default depends on transport\n    {\"name\": \"EndMarker\", \"type\": [\"null\", \"string\"], \"default\":\"$end-of-stream\"}, // default depends on transport\n    {\"name\": \"SkipTo\", \"type\": [\"null\", \"int\"], \"default\": null},\n    {\"name\": \"SkipToRecord\", \"type\": [\"null\", \"int\", \"string\"], \"default\":\"latest\"}, // default depends on transport\n    {\"name\": \"Envelope\", \"type\": \n     [\"string\",\n      {\"type\": \"record\", \"fields\": [ // deliminated\n        {\"name\": \"Type\", \"type\": \"string\"}, \n        {\"name\": \"Seperator\", \"type\": \"string\", \"default\":\"\\n\"}]},\n      {\"type\": \"record\", \"fields\": [ // ocf-block\n        {\"name\": \"Type\", \"type\": \"string\"},\n        {\"name\": \"SyncMarker\", \"type\": \"string\"}]}\n     ]},\n    {\"name\": \"Encoding\", \"type\": [\"null\", \"string\"]},\n    {\"name\": \"Schema\", \"type\": [\"string\", \"object\"]}\n    ]\n}",
      "language": "json",
      "name": "Stream Descriptor Schema"
    }
  ]
}
[/block]
## Common Fields

The following table describes the common fields used in stream descriptors. Fields in *italics* are optional.
[block:parameters]
{
  "data": {
    "h-0": "Field",
    "h-1": "Type",
    "h-2": "Description",
    "h-3": "Default Value",
    "0-0": "*Version*",
    "0-1": "`string`",
    "0-2": "The version of the stream descriptor.",
    "h-4": "Example",
    "0-3": "\"1.2\"",
    "0-4": "\"1.2\"",
    "1-0": "*Description*",
    "1-1": "`string`",
    "1-2": "A description for this stream (optional).",
    "1-3": "(empty)",
    "1-4": "\"An input file stream.\"",
    "2-0": "Transport",
    "2-1": "`string` or `object`",
    "2-2": "Specifies the details of the Transport for this stream (see below).",
    "3-0": "*Loop*",
    "3-1": "`boolean`",
    "3-2": "Set to `true` to read the stream in a loop.",
    "3-3": "`true` for filestreams\n`false` otherwise",
    "3-4": "`true`",
    "4-0": "*EndMarker*",
    "4-1": "`string`",
    "4-2": "An end-of-stream marker to indicate that the last message in the stream has been received.",
    "4-3": "`null` for AVRO binary streams, \n`$end-of-stream` for all others",
    "4-4": "\"LastMessage\"",
    "5-0": "*SkipTo*",
    "5-1": "`int` or `null`",
    "5-2": "Skip to the byte offset when starting to read the stream.",
    "5-3": "`null`",
    "5-4": "5",
    "6-0": "*SkipToRecord*",
    "6-1": "`int`, `string`, or `null`",
    "6-2": "Skip to record by number or keyword.",
    "6-3": "`\"latest\"` for Kafka streams\n`null` otherwise",
    "6-4": "\"latest\"",
    "7-0": "Envelope",
    "9-0": "*Schema*",
    "8-0": "Encoding",
    "9-3": "`null`",
    "9-1": "`null`, `string`, or `object`",
    "9-2": "AVRO schema for records in this stream.",
    "9-4": "\"int\"",
    "7-1": "`\"deliminated\"` or `\"ocf-block\"` or `object`",
    "7-2": "Specifies the framing of the messages in the stream (see below).",
    "7-3": "\"deliminated\" or `null`",
    "7-4": "\"deliminated\"",
    "8-1": "`null`, \"avro-binary\", or \"json\"",
    "8-2": "Specifies the encoding of the messages in the stream."
  },
  "cols": 5,
  "rows": 10
}
[/block]

[block:callout]
{
  "type": "warning",
  "title": "New in v1.3!",
  "body": "The `Schema` field can now specify schemas by reference (as well as explicitly define them). A schema reference takes the following form:\n```\n\"Schema\": { \"$ref\":\"schema_name\"}\n```\nwhere `schema_name` is the name of the schema in Model Manage."
}
[/block]
## Transport Fields

This section documents the various fields present in the `Transport` descriptors. As before, fields in *italics* are optional.

### REST

The REST stream transport does not include any additional transport fields.

### HTTP

HTTP streams contain only one field---the URL to the data source.
[block:parameters]
{
  "data": {
    "h-0": "Field",
    "h-1": "Type",
    "h-2": "Description",
    "h-3": "Default",
    "h-4": "Example",
    "0-0": "Url",
    "0-1": "`string`",
    "0-2": "The URL of the data.",
    "0-3": "(none)",
    "0-4": "\"http://www.path.to/file.extension\""
  },
  "cols": 5,
  "rows": 1
}
[/block]
### Kafka

Kafka stream transports have several fields, detailed in the table below.
[block:parameters]
{
  "data": {
    "h-0": "Field",
    "h-1": "Type",
    "h-2": "Description",
    "h-3": "Default",
    "h-4": "Example",
    "0-0": "BootstrapServers",
    "0-1": "array of `string`",
    "0-2": "A list of the Kafka bootstrap servers.",
    "0-3": "(none)",
    "0-4": "[\"192.168.1.5:9002\", \"127.0.0.1:9003\"]",
    "1-0": "Topic",
    "1-1": "`string`",
    "1-2": "The Kafka topic.",
    "1-3": "(none)",
    "1-4": "\"MyKafkaTopic\"",
    "2-0": "*Partition*",
    "2-1": "`int`",
    "2-2": "The Kafka partition.",
    "2-3": "0",
    "2-4": "5",
    "3-0": "*MaxWaitTime*",
    "3-1": "`int`",
    "3-2": "The maximum time to wait before declaring that the end of the stream has been reached.",
    "3-3": "8388607 (approx. 25 days)",
    "3-4": "500",
    "4-0": "*Principal*",
    "5-0": "*Keytab*",
    "4-2": "An authenticated user in a secure cluster",
    "4-1": "`string`",
    "5-1": "`string`",
    "4-3": "(none)",
    "5-3": "(none)",
    "4-4": "\"kafka/kafka@REALM\"",
    "5-4": "\"/fastscore.keytab\"",
    "5-2": "A file containing pairs of Kerberos principals and encrypted keys"
  },
  "cols": 5,
  "rows": 6
}
[/block]
### File

File streams only have one parameter: the path to the file. Note that the path to the file is relative to the Engine container's filesystem, not the filesystem of the machine hosting the Engine. 
[block:parameters]
{
  "data": {
    "h-0": "Field",
    "h-1": "Type",
    "h-2": "Description",
    "h-3": "Default",
    "h-4": "Example",
    "0-0": "Path",
    "0-1": "`string`",
    "0-2": "The path to the file.",
    "0-3": "(none)",
    "0-4": "\"/path/to/file\""
  },
  "cols": 5,
  "rows": 1
}
[/block]
### UDP

UDP Transports can be described using two fields.
[block:parameters]
{
  "data": {
    "h-0": "Field",
    "h-1": "Type",
    "h-2": "Description",
    "h-3": "Default",
    "h-4": "Example",
    "0-0": "*BindTo*",
    "0-1": "`string`",
    "0-2": "The IP address to bind to.",
    "0-3": "\"0.0.0.0\"",
    "0-4": "\"127.0.0.1\"",
    "1-0": "Port",
    "1-1": "`int`",
    "1-2": "The port to listen to.",
    "1-3": "(none)",
    "1-4": "8000"
  },
  "cols": 5,
  "rows": 2
}
[/block]
### TCP

TCP transports require both a host and a port, and both are mandatory.
[block:parameters]
{
  "data": {
    "h-0": "Field",
    "h-1": "Type",
    "h-2": "Description",
    "h-3": "Default",
    "h-4": "Example",
    "0-0": "Host",
    "0-1": "`string`",
    "0-2": "The IP address of the host machine.",
    "0-3": "(none)",
    "0-4": "\"127.0.0.1\"",
    "1-0": "Port",
    "1-1": "`int`",
    "1-2": "The port of the host machine.",
    "1-3": "(none)",
    "1-4": "8765"
  },
  "cols": 5,
  "rows": 2
}
[/block]
### Executable

The executable transport allows for flexibility on the input or output streams to be truly customized by an external command.
[block:parameters]
{
  "data": {
    "0-0": "Run",
    "0-1": "`string`",
    "0-3": "(none)",
    "0-4": "\"/bin/ls\"",
    "0-2": "The path to the executable.",
    "h-0": "Field",
    "h-1": "Type",
    "h-2": "Description",
    "h-3": "Default",
    "h-4": "Example"
  },
  "cols": 5,
  "rows": 1
}
[/block]
### Debug

The debug transport type allows the user to embed a batch of records to be scored directly into the input stream descriptor. As the name implies, it is intended primarily for model and stream debugging. 
[block:parameters]
{
  "data": {
    "0-0": "*Data*",
    "h-0": "Field",
    "h-1": "Type",
    "h-2": "Description",
    "h-3": "Default",
    "h-4": "Example",
    "0-1": "a `string` or array of `string`",
    "0-2": "A single record, or an array of JSON records to be scored.",
    "0-3": "(none)",
    "0-4": "[\"\\\"json string\\\"\"]",
    "1-0": "*DataBinary*",
    "1-1": "a `string` or array of `string`",
    "1-2": "Either a base64-encoded binary datum or an array\nof base64-encoded messages.",
    "1-3": "(none)",
    "1-4": "\"AQIDBQ==\""
  },
  "cols": 5,
  "rows": 2
}
[/block]
### Console and Discard

The console and discard transports have no fields. The discard transport simply discards all content---as such, it only makes sense for output streams where one does not care about the output of the engine. 

Console streams are somewhat more subtle: in this case, the output is relayed back to the FastScore CLI. In order for this to work, however, the CLI must be in "interactive" mode (i.e., started with the `fastscore` command), and FastScore must be configured to use Pneumo, a library that enables asynchronous notifications over Kafka. 
[block:api-header]
{
  "type": "basic",
  "title": "Examples"
}
[/block]
This section contains examples of stream descriptors for various combinations of transports, encodings, and envelopes. 

### REST Stream Examples

The REST transport allows inputs to be delivered to the engine with the `/1/job/input/` POST command. If the output stream is also set to REST, the `/1/job/output` GET command can be used to retrieve the resulting scores. 
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Transport\": {\n    \"Type\": \"REST\"\n  },\n  \"Envelope\": \"delimited\",\n  \"Encoding\": \"JSON\",\n  \"Schema\": null\n}",
      "language": "json"
    }
  ]
}
[/block]
### Debug Stream Examples

This is an example of a debug stream, where the messages are all inline, and separated by newlines.
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Description\": \"read an inline sequence of 3 messages separated by newlines\",\n  \"Transport\": {\n    \"Type\": \"debug\",\n    \"Data\": \"aaa\\nbbb\\nccc\"\n  },\n  \"Envelope\": \"delimited\",\n  \"Encoding\": null,\n  \"Schema\": null\n}",
      "language": "json",
      "name": "Debug Inline Stream"
    }
  ]
}
[/block]
This is an example of a debug stream using a list of binary inputs. 
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Description\": \"read an inline sequence of 3 binary messages\",\n  \"Transport\": {\n    \"Type\": \"debug\",\n    \"DataBinary\": [\"uKs/srYgWfY=\",\n                   \"kiqGJppq2Z4=\",\n                   \"VBPsuSTfUiM=\"]\n  },\n  \"Envelope\": \"delimited\",\n  \"Encoding\": null,\n  \"Schema\": null\n}",
      "language": "json",
      "name": "Debug Binary Stream"
    }
  ]
}
[/block]
### HTTP Examples

The following is an example of an HTTP stream.
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Description\": \"read a sequence of opaque (unicode) strings separated by newlines over HTTP transport\",\n  \"Transport\": {\n    \"Type\": \"HTTP\",\n    \"Url\": \"https://s3-us-west-1.amazonaws.com/fastscore-sample-data/prime.test.stream\"\n  },\n  \"Envelope\": {\n    \"Type\": \"delimited\",\n    \"Separator\": \"\\r\\n\"\n  },\n  \"Encoding\": null,\n  \"Schema\": null\n}",
      "language": "json",
      "name": "HTTP Example"
    }
  ]
}
[/block]
### Kafka Examples

The following example is a stream descriptor for a Kafka input stream.
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Description\": \"read a sequence of opaque (unicode) strings over Kafka transport\",\n  \"Transport\": {\n    \"Type\": \"kafka\",\n    \"BootstrapServers\": [\"127.0.0.1:9092\"],\n    \"Topic\": \"data-feed-1\",\n    \"Partition\": 0\n  },\n  \"Envelope\": null,\n  \"Encoding\": null,\n  \"Schema\": null\n}",
      "language": "json",
      "name": "Kafka Input Example"
    }
  ]
}
[/block]
This example writes a sequence of AVRO-binary typed data to a Kafka stream.
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Description\": \"write a sequence of binary-encoded Avro documents to Kafka\",\n  \"Transport\": {\n    \"Type\": \"kafka\",\n    \"BootstrapServers\": [\"127.0.0.1:9092\"],\n    \"Topic\": \"data-feed-1\",\n    \"Partition\": 0\n  },\n  \"Envelope\": null,\n  \"Encoding\": \"avro-binary\",\n  \"Schema\": { type: \"record\", ... }\n}",
      "language": "json",
      "name": "Kafka AVRO-binary"
    }
  ]
}
[/block]
### File Stream Examples

This is an example of a file stream input, expecting each line of the file to contain an integer. An analogous stream descriptor can be used for a file output stream. Note that `/root/data/input.jsons` refers to the path to `input.jsons` inside of the engine container, *not* on the host machine. 
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Loop\": false,\n  \"Transport\": {\n    \"Type\": \"file\",\n    \"Path\": \"/root/data/input.jsons\"\n  },\n  \"Envelope\": \"delimited\",\n  \"Encoding\": \"json\",\n  \"Schema\": \"int\"\n}",
      "language": "json",
      "name": "File Input Stream"
    }
  ]
}
[/block]
### TCP Examples

Here's an example TCP stream descriptor. 
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Description\": \"read a sequence of untyped json separated by newlines over TCP transport\",\n  \"Transport\": {\n    \"Type\": \"TCP\",\n    \"Host\": \"127.0.0.1\",\n    \"Port\": 12012\n  },\n  \"Envelope\": \"delimited\",\n  \"Encoding\": \"json\",\n  \"Schema\": null\n}",
      "language": "json",
      "name": "TCP Example"
    }
  ]
}
[/block]
### UDP Examples

The following stream descriptor describes a UDP input stream.
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Version\": \"1.2\",\n  \"Description\": \"read a sequence of untyped json documents over UDP transport\",\n  \"Transport\": {\n    \"Type\": \"UDP\",\n    \"Bind\": \"0.0.0.0\",\n    \"Port\": 53053\n  },\n  \"Envelope\": null,\n  \"Encoding\": \"json\",\n  \"Schema\": null\n}",
      "language": "json",
      "name": "UDP Example"
    }
  ]
}
[/block]