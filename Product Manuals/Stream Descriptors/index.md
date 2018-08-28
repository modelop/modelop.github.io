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
        - [S3](#section-s3)
        - [File](#section-file)
        - [ODBC](#section-odbc)
        - [TCP](#section-tcp)
        - [UDP](#section-udp)
        - [Executable](#section-executable)
        - [Inline](#section-inline)
        - [Discard](#section-discard)
3. [Examples](#examples)


## <a name="overview"></a>Overview

A stream descriptor is a JSON document that contains all of the information
about a stream. In general, an input stream reads records from an underlying
transport, optionally verifies, and feeds them to models. The output stream acts
similarly, but in the reverse order. Stream descriptors are required for the
engine to read input and produce output, and can additionally be used to enforce
input and output typing using Avro schema.

By convention, all field names of a stream descriptor start with a capital
letter and do not use punctuation. Many fields of a stream descriptor have
default values that depend on values of other fields. If a field is omitted, it
is set to a default value. Sometimes, you may need to explicitly set field to
`null` to avoid this behavior. For example, if omitted, a `LingerTime` is set to
`3000` (milliseconds). To disable lingering when the output stream closes you
need to set this property to `null`.

Some fields accept shortcut values. For instance, you may set the `Transport`
field to `"discard"` string instead of the equivalent yet more verbose
`{"Type": "discard"}` object.

## <a name="field-descriptions"></a>Field Descriptions

A basic template for a stream descriptor is below. Note that the type of
transport used will determine which fields in the `Transport` section are
needed.

``` json
{
  "Description": "A stream descriptor template",

  "Transport": {
    "Type": "REST" | "HTTP" | "kafka" | "S3" | "file" | "ODBC" | "TCP" | "UDP" | "exec" | "inline" | "discard",
    ...
  },
  "Encoding": null | "json" | "avro-binary" | ...,
  "Envelope": null | "delimited" | ...,
  "Schema": { ... },
  ...
}
```

The best way to verify a newly-constructed stream descriptor is to use the
`fastscore stream verify` command described [here](../../Reference/FastScore CLI/).


### <a name="section-common-fields">Common Fields

The following table describes the common fields used in stream descriptors. Fields in *italics* are optional.

| Field | Type | Description | Default Value | Example |
| --- | --- | --- | --- | --- |
| *Version* | `string` | The version of the stream descriptor. | "1.2" | "1.2" |
| *Description* | `string` | A description for this stream (optional). | | "An input file stream." |
| Transport | `string` or `object` | Specifies the details of the Transport for this stream (see below). |  |
| *Loop* | `boolean` | Set to `true` to read the stream in a loop. | `true` for filestreams `false` otherwise | `true` |
| *SkipTo* | `int` | Skip to the byte offset when starting to read the stream. | | 5 |
| *SkipToRecord* | `int` or `string` | Skip to record by number or keyword. | `"latest"` for non-looping Kafka streams, `null` otherwise | "earliest" |
| *Envelope* | `string` or `object` | Specifies the framing of the messages in the stream (see below). | `"delimited"` (HTTP, file, and TPC) or `null` | "delimited" |
| Encoding | `string` or `null` | Specifies the encoding of the messages in the stream (see below). |  | `"ocf-block"` |
| *Schema* | `string` or `object` | Avro schema for records in this stream. | | "int" |
| *Batching* | `string` or `object` | The batching parameters of the stream (see below). | `"normal"` | `"explicit"` |
| *LingerTime* | `int` | When an output stream close wait this number of milliseconds for remaining records to be written. | `3000` | `1000` |

> The `Schema` field can now specify schemas by reference (as well as explicitly define them). A schema reference takes the following form:
> ```
> "Schema": { "$ref":"schema_name"}
> ```
> where `schema_name` is the name of the schema in Model Manage.

### <a name="section-transport-fields">Transport Fields

This section documents the various fields present in the `Transport` descriptors. As before, fields in *italics* are optional.

#### <a name="section-rest">REST

The REST stream transport operates in either 'simple' (default) or 'chunked'
mode. In simple mode each REST request retrieves or write a single data record.
In chunked mode the REST stream handles chunks of data containing multiple or
partial records.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Mode | `string` | The mode of the REST stream. | `"simple"` | `"chunked"` |

The "REST" shortcut is supported. Setting the "Transport" to "REST" assumes the
simple mode.
    
#### <a name="section-http">HTTP

HTTP streams contain only one field---the URL to the data source.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Url | `string` | The URL of the data. | | "http://www.path.to/file.extension" |
    
#### <a name="section-kafka">Kafka

Kafka stream transports have several fields, detailed in the table below.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| BootstrapServers | array of `string` | A list of the Kafka bootstrap servers. | | ["192.168.1.5:9002", "127.0.0.1:9003"] |
| Topic | `string` | The Kafka topic. | | "MyKafkaTopic" |
| *Partition* | `int` | The Kafka partition. | 0 | 5 |
| *MaxWaitTime* | `int` | The maximum time to wait before declaring that the end of the stream has been reached. | 8388607 (approx. 25 days) | 500 |
| *Principal* | `string` | An authenticated user in a secure cluster | | "kafka/kafka@REALM" |
| *Keytab* | `string` | A file containing pairs of Kerberos principals and encrypted keys | | "/fastscore.keytab" |

#### <a name="section-s3">S3

| Field	| Type | Default	| Description |
| ----- | ---- | -------  | ----------- |
| Region | string | "us-east-1" | An AWS region.
| Bucket | string | | An object key (at least 3 characters, 63 max). The bucket must exist and have appropriate permissions set. |
| ObjectKey | string | | An object key (1024 characters max). |
| IntegrityChecks | boolean | false | Use Content-MD5 header to ensure the content integrity. |
| *AccessKeyID* | string | | An AWS access key ID, e.g. "AKIAIOSFODNN7EXAMPLE" |
| *SecretAccessKey* | string | | An AWS secret access key, e.g. "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" |

The following S3 features are not currently supported but may be added in the future:
* Storage classes
* Access permissions
* Server-side encryption
* Single part object upload

S3 output transport cannot handle small chunks of data (<5MB) except for the
last chunk before the stream is closed. Note that publicly-accessible S3
resources can be read using an HTTP transport.

An example of an S3 transport specification:
``` json
{
  ...
  "Transport": {
    "Type": "S3",
    "Bucket": "mydatasets2018",
    "ObjectKey": "census-data-08-2018",
    "AccessKeyID": "AKIAIOSFODNN7EXAMPLE",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  },
  ...
}
```
    
#### <a name="section-file">File

File streams only have one parameter: the path to the file. Note that the path to the file is relative to the Engine container's filesystem, not the filesystem of the machine hosting the Engine. 

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Path | `string` | The path to the file. |  | "/path/to/file" |
        
#### <a name="section-odbc">ODBC

An ODBC stream reads data from RDBMS. The key parameter of the ODBC transport
is the connection string. Currently, FastScore supports MSSQL and PostgreSQL
databases.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| ConnectionString | `string` | The string describing the data source. |  | "Driver=FreeTDS;Server=myhost;Port=1433;Database=mydb;Uid=myuid;Pwd=abc123"` |
| SelectQuery | `string` | An SQL query to run to retrieve data (input only). | | `"select * from mydata;"` |
| InsertIntoTable | `string` | The name of the table to append data to (output only). | | `"mydata"` |
| OutputFields | array of `string` | Field names for output data. | (all fields in the output table) | `["x","y","z","score"]` |
| Timeout | `integer` | The query timeout in milliseconds. | | 10000 |

#### <a name="section-tcp">TCP

TCP transports require both a host and a port, and both are mandatory.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Host | `string` | The IP address of the host machine. |  | "127.0.0.1" |
| Port | `int` | The port of the host machine. |  | 8765 |
 
#### <a name="section-udp">UDP

UDP Transports can be described using two fields.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| *BindTo* | `string` | The IP address to bind to. | "0.0.0.0" | "127.0.0.1" |
| Port | `int` | The port to listen to. |  | 8000 |
   
#### <a name="section-executable">Executable

The executable transport allows for flexibility on the input or output streams to be truly customized by an external command.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Run | `string` | The path to the executable. |  | "/bin/ls" |
| Args | array of `string` | The arguments to pass to the executable. | [] | ["-a"] |

#### <a name="section-inline">Inline

The inline transport type allows the user to embed a batch of records to be scored directly into the input stream descriptor. Inline streams are intended primarily for model and stream debugging. 

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| *Data* | a `string` or array of `string` | A single record, or an array of JSON records to be scored. |  | ["\\"json string\\""] |
| *DataBinary* | a `string` or array of `string` | Either a base64-encoded binary datum or an array of base64-encoded messages. |  | "AQIDBQ==" |
    
#### <a name="section-discard">Discard

The discard transports have no fields. The discard transport simply discards all content---as such, it only makes sense for output streams where one does not care about the output of the engine. 

## <a name="examples">Examples

This section contains examples of stream descriptors for various combinations of transports, encodings, and envelopes. 

### REST Stream Examples

The REST transport allows inputs to be delivered to the engine with the `/1/job/input/<slot>` POST command. If the output stream is also set to REST, the `/1/job/output/<slot>` GET command can be used to retrieve the resulting scores. 
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

### Inline Stream Examples

This is an example of a inline stream, where the messages are all embedded, and separated by newlines.
``` json
{
  "Description": "read an embedded sequence of 3 messages separated by newlines",
  "Transport": {
    "Type": "inline",
    "Data": "aaa\\nbbb\\nccc"
  },
  "Envelope": "delimited",
  "Encoding": null,
  "Schema": null
}
```

This is an example of a inline stream using a list of binary inputs. 
``` json
{
  "Description": "read an embedded sequence of 3 binary messages",
  "Transport": {
    "Type": "inline",
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
  "Description": "read a sequence of unicode strings separated by newlines over HTTP transport",
  "Transport": {
    "Type": "HTTP",
    "Url": "https://s3-us-west-1.amazonaws.com/fastscore-sample-data/prime.test.stream"
  },
  "Envelope": {
    "Type": "delimited",
    "Separator": "\\r\\n"
  },
  "Encoding": "utf-8",
  "Schema": null
}
```

### Kafka Examples

The following example is a stream descriptor for a Kafka input stream.

``` json
{
  "Description": "read a sequence of opaque (binary) strings over Kafka transport",
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

This example writes a sequence of Avro-binary typed data to a Kafka stream.

``` json
{
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

### ODBC Examples

The following stream descriptor reads data from a MSSQL server.

```json
{
  ...
  "Transport": {
    "Type": "ODBC",
    "ConnectionString": "Driver=FreeTDS;Server=myhost;Port=1433;Database=mydb;Uid=myuid;Pwd=abc123",
    "SelectQuery": "select id, name from client_address"
  },
  ...
}
```

### S3 Examples

The stream descriptor below reads/writes the data kept on AWS S3.

```json
{
  ...
  "Transport": {
    "Type": "S3",
    "Bucket": "mydatasets2017",
    "ObjectKey": "census-data-08-2017",
    "AccessKeyID": "AKIAIOSFODNN7EXAMPLE",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  },
  ...
}
```

