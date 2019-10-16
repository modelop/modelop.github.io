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
        - [HDFS](#section-hdfs)
        - [TCP](#section-tcp)
        - [UDP](#section-udp)
        - [Executable](#section-executable)
        - [Inline](#section-inline)
        - [Discard](#section-discard)
3. [End-of-file](#end-of-file)
4. [Seekable streams](#seekable-streams)
5. [Looping](#looping)
6. [Record envelopes](#record-envelopes)
    1. [delimited](#delimited-envelope)
    2. [fixed](#fixed-envelope)
    3. [ocf-block](#ocf-block-envelope)
    4. [delimited-csv](#delimited-csv-envelope)
    5. [Default envelope](#default-envelope)
7. [Record encoding](#record-encoding)
8. [Record schema](#record-schema)
7. [Record batching](#record-batching)
9. [Restrictions/limitations](#restrictions)
1. [Examples](#examples)

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
    "Type": "REST" | "HTTP" | "Kafka" | "S3" | "file" | "ODBC" | "TCP" | "UDP" | "exec" | "inline" | "discard",
    ...
  },
  "Encoding": null | "json" | "avro-binary" | ...,
  "Envelope": null | "delimited" | ...,
  "Schema": { ... },
  ...
}
```

The best way to verify a newly-constructed stream descriptor is to use the
`fastscore stream verify` command described [here](../../Reference/fastscore CLI/).


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

HTTP streams typically contain only one field---the URL to the data source. It
is possible to make the stream "chunked" with each chunk representing a record.
A chunked stream must use a corresponding
["Transfer-Encoding"](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding) header.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Url | `string` | The URL of the data. | | "http://www.mydomain.com/path.to/file.extension" |
| Chunked | `boolean` | Use Transfer-Encoding: chunked | false | |
    
#### <a name="section-kafka">Kafka

Kafka stream transports have several fields, detailed in the table below.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| BootstrapServers | array of `string` | A list of the Kafka bootstrap servers. | | ["192.168.1.5:9002", "127.0.0.1:9003"] |
| Topic | `string` | The Kafka topic. | | "MyKafkaTopic" |
| *Group* | `string` | A consumer group. | | "fastscore-1" |
| *CommitOffset* | `boolean` | Commit offsets immediately after reading. | true | false |
| *Partition* | `int` | The Kafka partition. | 0 | 5 |
| *MaxWaitTime* | `int` | The maximum time to wait before declaring that the end of the stream has been reached. | 8388607 (approx. 25 days) | 500 |
| *Principal* | `string` | An authenticated user in a secure cluster | | "kafka/kafka@REALM" |
| *Keytab* | `string` | A file containing pairs of Kerberos principals and encrypted keys | | "/fastscore.keytab" |

Setting a Group property enables consumer group-based tracking of reading
offsets. It means that the SkipToRecord property is disregarded. Note that if
the group is new and there is no reading commit offset associated with it, the
SkipToRecord value remains in effect.

By default, the reading offset is committed immediately after reading a batch or
records. Seting CommitOffset to false disable this behaviour. Typically, the
model then uses a special stream of type 'kafka-offset' to commit offsets. See
below.

#### <a name="section-kafka-offset">Kafka Offset

It is a special purpose stream transport used in conjunction with a Kafka stream
those CommitOffset property is set to false. The stream uses same fields as a
Kafka stream except that the Group is mandatory and CommitOffset must be set to
true (or omitted).

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
is the connection string. Currently, ModelOp Center supports MSSQL and PostgreSQL
databases.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| ConnectionString | `string` | The string describing the data source. |  | `"Driver=FreeTDS;Server=myhost;Port=1433;Database=mydb;Uid=myuid;Pwd=abc123"` |
| SelectQuery | `string` | An SQL query to run to retrieve data (input only). | | `"select * from mydata;"` |
| InsertIntoTable | `string` | The name of the table to append data to (output only). | | `"mydata"` |
| OutputFields | array of `string` | Field names for output data. | (all fields in the output table) | `["x","y","z","score"]` |
| Timeout | `integer` | The query timeout in milliseconds. | | 10000 |

#### <a name="section-hdfs">HDFS

An HDFS streams reads/writes a Hadoop Distributed File System
([HDFS](http://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html)).
The HDFS stream establishes A TCP connection to an HDFS 'namenode', retrieves the
file metadata, downloads the data in large blocks from HDFS 'datanodes'.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| NameNode | `string` | The host name or IP address of HDFS namenode. May include a port separated by a colon. By default, the port is 9000. | | "hdfs1.mycompany.com:9900 |
| Authentication | object or `null` | See below | `null` | |
| Path | `string` | An absolute path to the file. | | "/path/to/file" |

If "Authentication" is missing is `null`, the HDFS must allow insecure access.
Currently, the only supported authentication mechanism to access a secure HDFS
is 'KERBEROS'. To authenticate using Kerberos set the "Authentication" as
follows:
``` json
{
  ...
  "Transport": {
    "Type": "HDFS",
    "Authentication": {
      "Type": "Kerberos",
      "Realm": "MYCOMPANY.COM",
      "KDCHost": "1.2.3.4:8888",
      "Principal": "root",
      "Password": "*****",
      "Timeout": 5000
    },
    ...
  },
  ...
}
```

"KDCHost", "Realm", "Principal", and "Password" properties are mandatory. The
port may be omitted from the "KDCHost" string. The default Kerberos port is 88.
The timeout is measured in milliseconds. If omitted, the timeout is set to 3000
(3s). Set the timeout to `null` to disable it.

#### <a name="section-tcp">TCP

TCP transports require both a host and a port, and both are mandatory.

| Field | Type | Description | Default | Example |
| --- | --- | --- | --- | --- |
| Host | `string` | The IP address of the host machine. |  | "127.0.0.1" |
| Port | `int` | The port of the host machine. |  | 8765 |
 
#### <a name="section-udp">UDP
<a name="section-discard">D
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

## <a name="end-of-file">End-of-file

Some transports have a notion of the end of data (EOF), e.g. file transports.
Other transports do not. In addition to such 'hard' EOFs we support 'soft' EOFs
using 'control' records.

## <a name="seekable-streams">Seekable streams

Certain stream transports are seekable. They allow you to change the current
reading offset. The offset may be set in bytes (e.g. HTTP) or in records (e.g.
Kafka). SkipTo and SkipToRecord fields lets you to start reading the seekable
stream from the specified offset. SkipToRecord accepts "earliest" and "latest"
(default) strings for Kafka streams.

Example:
``` json
{
  "Transport": { "Type": "Kafka", ... },
  ...
  "SkipToRecord": "latest",
  ...
}
```

## <a name="looping">Looping

If the Loop field set to true, the stream upon reaching (hard or soft) EOF starts reading data from the beginning instead of stopping. Only seekable streams can be looping.

Example:
``` json
{
  ...
  "Loop": true,
  ...
}
```

## <a name="record-envelopes">Record envelopes

The stream needs to know where records start and end. Some transports preserve
record boundaries, e.g. Kafka. For others we need record framing to restore the
boundaries. We may also rely on the encoding to determine where a record ends,
e.g. msgpack encoding understands where a record ends. The framing scheme
is set using the Envelope field of the stream descriptor. Currently, input
streams support the "delimited", "fixed", "ocf-block", and "delimited-csv"
envelopes.

### <a name="delimited-envelope">delimited

The "delimited" scheme recognizes the record boundary when it encounters a
certain byte sequence – by default, a newline character. This is the default
framing scheme for certain transports that do not preserve record boundaries.

You can set the separator to something other then newline as follows:
``` json
{
  ...
  "Envelope": {
    "Type": "delimited",
    "Separator": "\r\n"
  },
  ...
}
```

In general, ModelOp Center can contain a zero-length record. null and utf-8 encoding do allow such records. However, an empty record right before the end of the stream is discarded.

### <a name="fixed-envelope">fixed
The "fixed" envelope splits the stream into records of the predefined size.

Example:
``` json
{
  ...
  "Envelope": {
    "Type": "fixed",
    "Size": 24
  },
  ...
}
```

When applied to output streams, the fixed scheme may truncate records or pad
them with zeros to get a record of the required size.

### <a name="ocf-block-envelope">ocf-block

The "ocf-block" scheme expects that the stream is an Object Container File
defined by the Avro
[specification](https://avro.apache.org/docs/1.8.2/spec.html). An OCF file
contains a header and a series of large batches of records. Each batch of
records contains a 16-byte "sync marker" that ensures that the reader is not out
of sync with the stream.

![OCF envelope](images/ocf1.png)

The OCF header contains an Avro schema, the "sync marker" value, and the
compression codec. We allow a stream that starts at the beginning of any record
batch, e.g. the point A. Thus the stream descriptor, not the header, becomes the
primary source of the schema, the marker and the codec. However, if the stream
does contain the header we check that corresponding values found in the header
match those in the stream descriptor.

Example:
``` json
{
  ...
  "Envelope": {
    "Type": "ocf-block",
    "SyncMarker": "PtsllIGbn+IkxFTVxcyWmw=="
    "Compress": "deflate",
    "SkipHeader": true
  }
}
```

SkipHeader element indicates whether the stream contains the OCF header or not.
SkipHeader is optional. By default, its value is 'true'. SyncMarker element is
optional if the OCF header is present (SkipHeader is 'true'). It must contain 16
base64-encoded bytes. Compress element may contain either null or 'deflate'.
This element is optional. Its default value is null.

Note that "ocf-block" envelope does not uncover all record boundaries. As a
consequence it must be used in conjunction with an encoding that can
automatically determine such boundaries. We support several such
encoding but only allow "avro-binary".

The following shortcut is supported:
``` json
{
  ...
  "Envelope": "ocf-block",
  ...
}
```

It assumes that the OCF header is present and the sync marker (and the
compression codec) must be taken from the header.

### <a name="delimited-csv-envelope">delimited-csv

The "delimited-csv" is an envelope similar to "delimited" with additional
features. It mostly useful for parsing CSV data. The "delimited-csv" parser
recognizes the record separator sequence – by default, "\r\n", unless it happens
inside a quoted field value. See [RFC4180](https://tools.ietf.org/html/rfc4180)
for details. In addition, the parser may skip the CSV header and verify if the
header matches the stream schema.

You can add the following parameters to the "delimited-csv" envelope:

Parameter | Default | Description
----------|---------|------------
Separator | "\r\n" | The record separator
SkipHeader | true | The CSV header present?
SkipBlankLines | true | Ignore blank lines

For example:
``` json
{
  ...
  "Envelope": {
    "Type": "delimited-csv",
    "Separator": "\n"
  },
  ...
}
```

In general, it is enough to set the Encoding to "csv" and the proper
"delimited-csv" envelope will be set up automatically. The "delimited-csv"
envelope can not be used with encodings other than "csv".

Note that the following settings are not
[RFC4180](https://tools.ietf.org/html/rfc4180)-compliant:
* "SkipBlankLines": true
* "QuoteCharacter": (anything other than double quote)
* "Delimiter": (anything other than comma)

### <a name="default-envelope">Default envelope

If the Envelope property is missing, the framing scheme is selected using the
stream transport and encoding. The table below summarizes the rules of how the
default envelope is determined.

Transport | Encoding | Default envelope
----------|----------|-----------------
boundary-preserving (e.g. Kafka) | any | null
not boundary-preserving (e.g. file) | boundary-preserving (e.g. msgpack) | null
not boundary-preserving | "csv" | "delimited-csv"
not boundary-preserving | any (not csv) | "delimited"

## <a name="record-encoding">Record encoding

A stream must understand the record encoding to optionally validate the data and
prepare it for consumption by the model. The record encoding is controlled by
the Encoding field. Possible values are null, "utf-8", "json", "csv", "msgpack",
"avro-binary", and "soap-rpc". The default encoding is null. Note that the null
encoding is still an encoding.

Examples of encoded/decoded records using various encodings:

Encoding | Encoded record | Decoded record (Python)
---------|----------------|------------------------
null | 0x01 0x02 0x03 | b'\x01\x02\x03' (Python 3) or '\x01\x02\x03' (Python 2)
"utf-8" | 0xe7 0xa6 0x8f | '\u798f' (Python 3) or u'\u798f' (Python 2)
"json" | {"foo": "bar"} | {'foo': 'bar'}
"csv" | 1,Joe,30 | {'id': 1, 'name': 'Joe', 'age': 30} # header is "id,name,age"
"msgpack" | 0xc2 | False
"avro-binary" | 0x08 0x02 0x04 0x06 0x08 0x00 | [1,2,3,4] # schema is {"type": "array", "items": "int" }

Note that "msgpack", "avro-binary" and "soap-rpc" parsers can determine
boundaries between records, others can not.

Unlike other encodings, the "csv" encoding can take parameters:

Paramter | Default | Description
---------|---------|------------
QuoteCharacter | " | The quote character
Delimiter | , | The field delimiter (may contain more than one character)

For example:
``` json
{
  ...
  "Encoding": {
    "Type": "csv",
    "QuoteCharacter": "'"
  },
  ...
}
```

## <a name="record-schema">Record schema

The "Schema" element contains an Avro schema of the stream records. All valid
Avro schemas are allowed. In addition schema references are suppported. If the
schema is kept in Model Manage under 'schema-1' name it can be referenced as
follows:
``` json
{
  "$ref": "schema-1"
}
```

If the "Schema" element is set to "$inherit" then the stream schema is copied
from the corresponding slot of the loaded model. This is the default value for
the "Schema" element. Set "Schema" to null to suppress schemas and make a
stream untyped.

## <a name="record-batching">Record batching

The purpose of record batching is two-fold. It improves performance by
minimizing roundtrips between the manifold and model runners. It also serves as
a basis for making recordsets.

The Batching object has two integer fields: Watermark and NagleTime. The
Watermark is the maximum number of records in the batch. The NagleTime is the
maximum number of milliseconds to wait for more records to arrive to form a
larger batch.

The Batching property can be set to null effectively making every record a
separate batch. This is the same as setting Batching as follows:
``` json
{
  ...
  "Batching": {
    "Watermark": 1,
    "NagleTime": null
  },
  ...
}
```

The user can manage batching explicitly by inserting special control records
into the stream.

When the model runner receives a batch of records it may feed them to the model
one by one or all at once as a recordset. Setting Watermark to N (and NagleTime
to null) creates a stream of batches of size N (except for potential
interference from EOFs and pigs).

The Batching property accepts two shortcuts – "explicit" and "normal".

### explicit

The explicit batching relies exclusively on control records. This is most suitable
setting for recordset-oriented models. It has the same effect as:
``` json
{
  ...
  "Batching": {
    "Watermark": null,
    "NagleTime": null
  },
  ...
}
```

### normal

This is the default value for the Batching property. It is equivalent to:
``` json
{
  ...
  "Batching": {
    "Watermark": 1000,
    "NagleTime": 500
  },
  ...
}
```

## <a name="restrictions">Restrictions/limitations
* Looping requires the transport to be seekable
* If transport is boundary-preserving then there must be no framing
* avro-binary encoding requires a schema
* msgpack and avro-binary encodings cannot use delimited framing
* ocf-block framing requires avro-binary encoding
* if null encoding uses a schema it must be "bytes"
* if utf-8 encoding uses a schema it must be "string"
* SkipTo requires a seekable transport that does not preserve boundaries
* SkipToRecord requires a seekable boundary-preserving transport
* SkipToRecord cannot be set to null for Kafka streams
* ODBC streams must have Encoding and Schema set to null
* If OutputFields is present, InsertIntoTable must be too
* soap-rpc encoding cannot use a schema
* delimited-csv envelope requires the csv encoding
* csv encoding requires a record schema or (input only) no schema at all

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


