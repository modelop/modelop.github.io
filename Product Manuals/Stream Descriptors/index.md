---
title: "Stream Descriptors"
excerpt: "Documentation for stream descriptors"
---
# Stream Descriptors

## Contents

1. [Overview](#overview)
2. [Field Descriptions](#field-descriptions)
    1. [Common Fields](#section-common-fields)
    2. [Transport Fields](#section-transport-fields)
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


## <a name="overview"></a>Overview

A stream descriptor is a JSON document that contains all of the information about a stream. In general, an input stream reads messages from an underlying transport, optionally verifies, and feeds them to models. The output stream acts similarly, but in the reverse order. Stream descriptors are required for the engine to read input and produce output, and can additionally be used to enforce input and output typing using AVRO schema.

By convention, all field names of a stream descriptor start with a capital letter and do not use punctuation. Many fields of a stream descriptor have default values that depend on values of other fields. If a field is omitted, it is set to a default value. Sometimes, you may need to explicitly set field to `null` to avoid this behavior. For example, if omitted, an `EndMarker` is set to "`$end-of-stream`" for certain streams. To disable the 'soft' end-of-file behavior based on the `EndMarker` you need to set this field to `null`.

Some fields accept shortcut values. For instance, you may set the `Transport` field to `"discard"` string instead of the equivalent yet more verbose '`{"Type": "discard"}`' object.

## <a name="field-descriptions"></a>Field Descriptions

A template for a stream descriptor is below. Note that the type of transport used will determine which fields in the `Transport` section are needed. Additionally, the top-level fields `Loop`, `EndMarker`, `SkipTo`, and `SkipToRecord` have default values depending on the choice of transport. 

``` json
{
  "Version": "1.2",
  "Description": "My Sample stream descriptor",
  "Transport": {
    "Type": "REST" | "HTTP" | "kafka" | "file" | "TCP" | "UDP" | "exec" | "debug" | "console" | "discard",
    "Url" : "http://www.mywebsite.com", // HTTP only
    "BootstrapServers": ["127.0.0.1:9181", "192.168.1.5:9003"], // Kafka only
    "Topic": "My Kafka Topic", // Kafka only
    "Partition" : 1, // Kafka only, defaults to 0
    "MaxWaitTime": 50000, // Kafka only, defaults to 8388607
    "Principal" : "kafka/kafka@REALM", // Kafka Authenciated only
    "Keytab": "/fastscore.keytab", // Kafka Authenciated only
    "Path": "/path/to/file.ext", // file only
    "Host": "127.0.0.1", // TCP only
    "Port": 8182, // TCP and UDP only
    "BindTo": "127.0.0.1", // UDP only, defaults to 0.0.0.0
    "Data" : [ "abc", "def", "ghi"], // debug only
    "DataBinary": ["AQIDBQ=="], // debug only, use one of Data or DataBinary
  },
  "Loop": false,
  "EndMarker": "$end-of-stream", 
  "SkipTo": null, 
  "SkipToRecord": "latest",
  "Envelope": "deliminated",
  "Encoding": null | "json" | "avro-binary",
  "Schema": { ... } // AVRO schema for stream
}
```

Once you have constructed your stream descriptor, you may validate it against the following AVRO schema. (Some modification of this schema may be required dependent on the choice of default values.)
``` json
{
  "type": "record",
  "fields": [
    {"name": "Version", "type": "string"},
    {"name": "Description", "type":"string", "default": ""},
    {"name": "Transport", "type": 
        [
        {"type": "record", "fields": [
          {"name":"Type", "type":"string"}]}, // REST
        {"type": "record", "fields": [
          {"name": "Type", "type": "string"}, // HTTP
          {"name": "Url", "type": "string"}]},
        {"type": "record", "fields": [
          {"name": "Type", "type": "string"}, // Kafka
          {"name": "BootstrapServers", "type":{"type": "array", "items":"string"} },
          {"name": "Topic", "type": "string"},
          {"name": "Partition", "type": "int", "default": 0},
          {"name": "MaxWaitTime", "type": "int", "default": 8388607}]},
        {"type": "record", "fields": [
          {"name": "Type", "type": "string"}, // File
          {"name": "Path", "type": "string"}]},
        {"type": "record", "fields": [
          {"name": "Type", "type": "string"}, // TCP
          {"name": "Host", "type": "string"}, 
          {"name": "Port", "type": "int"}]},
        {"type": "record", "fields": [
          {"name": "Type", "type": "string"}, // UDP
          {"name": "BindTo", "type": "string", "default": "0.0.0.0"},
          {"name": "Port", "type": "int"}]},
        {"type": "record", "fields": [
          {"name": "Type", "type": "string"}, // debug
          {"name": "Data", "type": ["string", {"type": "array", "items":  "string"}]}, // only one of Data or DataBinary is required
          {"name": "DataBinary", "type": "string"}]},
        {"type": "record", "fields": [{"name":"Type", "type": "string"}]},
        "string" // discard or console
        ]},
    {"name": "Loop", "type":"boolean", "default": false}, // default depends on transport
    {"name": "EndMarker", "type": ["null", "string"], "default":"$end-of-stream"}, // default depends on transport
    {"name": "SkipTo", "type": ["null", "int"], "default": null},
    {"name": "SkipToRecord", "type": ["null", "int", "string"], "default":"latest"}, // default depends on transport
    {"name": "Envelope", "type": 
     ["string",
      {"type": "record", "fields": [ // deliminated
        {"name": "Type", "type": "string"}, 
        {"name": "Seperator", "type": "string", "default":"\\n"}]},
      {"type": "record", "fields": [ // ocf-block
        {"name": "Type", "type": "string"},
        {"name": "SyncMarker", "type": "string"}]}
     ]},
    {"name": "Encoding", "type": ["null", "string"]},
    {"name": "Schema", "type": ["string", "object"]}
    ]
}
```

### <a name="section-common-fields">Common Fields

The following table describes the common fields used in stream descriptors. Fields in *italics* are optional.

| Field | Type | Description | Default Value | Example |
| --- | --- | --- | --- | --- |
| *Version* | `string` | The version of the stream descriptor. | "1.2" | "1.2" |
| *Description* | `string` | A description for this stream (optional). | (empty) | "An input file stream." |
| Transport | `string` or `object` | Specifies the details of the Transport for this stream (see below). |  |
| *Loop* | `boolean` | Set to `true` to read the stream in a loop. | `true` for filestreams `false` otherwise | `true` |
| *EndMarker* | `string` | An end-of-stream marker to indicate that the last message in the stream has been received. | `null` for AVRO binary streams, `$end-of-stream` for all others | "LastMessage" |
| *SkipTo* | `int` or `null` | Skip to the byte offset when starting to read the stream. | `null` | 5 |
| *SkipToRecord* | `int`, `string`, or `null` | Skip to record by number or keyword. | `"latest"` for Kafka streams `null` otherwise | "latest" |
| Envelope | `"deliminated"` or `"ocf-block"` or `object` | Specifies the framing of the messages in the stream (see below). | "deliminated" or `null` | "deliminated" |
| Encoding | `null`, "avro-binary", or "json" | Specifies the encoding of the messages in the stream. |  |  |
| *Schema* | `null`, `string`, or `object` | AVRO schema for records in this stream. | `null` | "int" |


> The `Schema` field can now specify schemas by reference (as well as explicitly define them). A schema reference takes the following form:
> ```
> "Schema": { "$ref":"schema_name"}
> ```
> where `schema_name` is the name of the schema in Model Manage.

### <a name="section-transport-fields">Transport Fields

This section documents the various fields present in the `Transport` descriptors. As before, fields in *italics* are optional.

#### <a name="section-rest">REST

The REST stream transport does not include any additional transport fields.

#### <a name="section-http">HTTP

HTTP streams contain only one field---the URL to the data source.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Url | `string` | The URL of the data. | (none) | "http://www.path.to/file.extension" |

    
#### <a name="section-kafka">Kafka

Kafka stream transports have several fields, detailed in the table below.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| BootstrapServers | array of `string` | A list of the Kafka bootstrap servers. | (none) | ["192.168.1.5:9002", "127.0.0.1:9003"] |
| Topic | `string` | The Kafka topic. | (none) | "MyKafkaTopic" |
| *Partition* | `int` | The Kafka partition. | 0 | 5 |
| *MaxWaitTime* | `int` | The maximum time to wait before declaring that the end of the stream has been reached. | 8388607 (approx. 25 days) | 500 |
| *Principal* | `string` | An authenticated user in a secure cluster | (none) | "kafka/kafka@REALM" |
| *Keytab* | `string` | A file containing pairs of Kerberos principals and encrypted keys | (none) | "/fastscore.keytab" |

    
#### <a name="section-file">File

File streams only have one parameter: the path to the file. Note that the path to the file is relative to the Engine container's filesystem, not the filesystem of the machine hosting the Engine. 

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Path | `string` | The path to the file. | (none) | "/path/to/file" |
    
    
#### <a name="section-udp">UDP

UDP Transports can be described using two fields.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| *BindTo* | `string` | The IP address to bind to. | "0.0.0.0" | "127.0.0.1" |
| Port | `int` | The port to listen to. | (none) | 8000 |

    
#### <a name="section-tcp">TCP

TCP transports require both a host and a port, and both are mandatory.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Host | `string` | The IP address of the host machine. | (none) | "127.0.0.1" |
| Port | `int` | The port of the host machine. | (none) | 8765 |
    
    
#### <a name="section-executable">Executable

The executable transport allows for flexibility on the input or output streams to be truly customized by an external command.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Run | `string` | The path to the executable. | (none) | "/bin/ls" |

    
#### <a name="section-debug">Debug

The debug transport type allows the user to embed a batch of records to be scored directly into the input stream descriptor. As the name implies, it is intended primarily for model and stream debugging. 

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| *Data* | a `string` or array of `string` | A single record, or an array of JSON records to be scored. | (none) | ["\\"json string\\""] |
| *DataBinary* | a `string` or array of `string` | Either a base64-encoded binary datum or an array\nof base64-encoded messages. | (none) | "AQIDBQ==" |

    
#### <a name="section-console-and-discard">Console and Discard

The console and discard transports have no fields. The discard transport simply discards all content---as such, it only makes sense for output streams where one does not care about the output of the engine. 

Console streams are somewhat more subtle: in this case, the output is relayed back to the FastScore CLI. In order for this to work, however, the CLI must be in "interactive" mode (i.e., started with the `fastscore` command), and FastScore must be configured to use Pneumo, a library that enables asynchronous notifications over Kafka. 

## <a name="examples">Examples

This section contains examples of stream descriptors for various combinations of transports, encodings, and envelopes. 

### REST Stream Examples

The REST transport allows inputs to be delivered to the engine with the `/1/job/input/` POST command. If the output stream is also set to REST, the `/1/job/output` GET command can be used to retrieve the resulting scores. 
``` json
{
  "Transport": {
    "Type": "REST"
  },
  "Envelope": "delimited",
  "Encoding": "JSON",
  "Schema": null
}
```

### Debug Stream Examples

This is an example of a debug stream, where the messages are all inline, and separated by newlines.
``` json
{
  "Version": "1.2",
  "Description": "read an inline sequence of 3 messages separated by newlines",
  "Transport": {
    "Type": "debug",
    "Data": "aaa\\nbbb\\nccc"
  },
  "Envelope": "delimited",
  "Encoding": null,
  "Schema": null
}
```

This is an example of a debug stream using a list of binary inputs. 
``` json
{
  "Version": "1.2",
  "Description": "read an inline sequence of 3 binary messages",
  "Transport": {
    "Type": "debug",
    "DataBinary": ["uKs/srYgWfY=",
                   "kiqGJppq2Z4=",
                   "VBPsuSTfUiM="]
  },
  "Envelope": "delimited",
  "Encoding": null,
  "Schema": null
}
```

### HTTP Examples

The following is an example of an HTTP stream.

```json
{
  "Version": "1.2",
  "Description": "read a sequence of opaque (unicode) strings separated by newlines over HTTP transport",
  "Transport": {
    "Type": "HTTP",
    "Url": "https://s3-us-west-1.amazonaws.com/fastscore-sample-data/prime.test.stream"
  },
  "Envelope": {
    "Type": "delimited",
    "Separator": "\\r\\n"
  },
  "Encoding": null,
  "Schema": null
}
```

### Kafka Examples

The following example is a stream descriptor for a Kafka input stream.

``` json
{
  "Version": "1.2",
  "Description": "read a sequence of opaque (unicode) strings over Kafka transport",
  "Transport": {
    "Type": "kafka",
    "BootstrapServers": ["127.0.0.1:9092"],
    "Topic": "data-feed-1",
    "Partition": 0
  },
  "Envelope": null,
  "Encoding": null,
  "Schema": null
}
```

This example writes a sequence of AVRO-binary typed data to a Kafka stream.

``` json
{
  "Version": "1.2",
  "Description": "write a sequence of binary-encoded Avro documents to Kafka",
  "Transport": {
    "Type": "kafka",
    "BootstrapServers": ["127.0.0.1:9092"],
    "Topic": "data-feed-1",
    "Partition": 0
  },
  "Envelope": null,
  "Encoding": "avro-binary",
  "Schema": { type: "record", ... }
}
```

### File Stream Examples

This is an example of a file stream input, expecting each line of the file to contain an integer. An analogous stream descriptor can be used for a file output stream. Note that `/root/data/input.jsons` refers to the path to `input.jsons` inside of the engine container, *not* on the host machine. 
``` json
{
  "Version": "1.2",
  "Loop": false,
  "Transport": {
    "Type": "file",
    "Path": "/root/data/input.jsons"
  },
  "Envelope": "delimited",
  "Encoding": "json",
  "Schema": "int"
}
```

### TCP Examples

Here's an example TCP stream descriptor. 
``` json
{
  "Version": "1.2",
  "Description": "read a sequence of untyped json separated by newlines over TCP transport",
  "Transport": {
    "Type": "TCP",
    "Host": "127.0.0.1",
    "Port": 12012
  },
  "Envelope": "delimited",
  "Encoding": "json",
  "Schema": null
}
```

### UDP Examples

The following stream descriptor describes a UDP input stream.

``` json
{
  "Version": "1.2",
  "Description": "read a sequence of untyped json documents over UDP transport",
  "Transport": {
    "Type": "UDP",
    "Bind": "0.0.0.0",
    "Port": 53053
  },
  "Envelope": null,
  "Encoding": "json",
  "Schema": null
}
```