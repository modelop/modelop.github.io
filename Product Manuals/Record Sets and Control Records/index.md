---
title: "Recordsets and Control Records"
excerpt: "New in v1.10!"
---
# Recordsets and Control Records

To better handle different model types (such as batch models), ModelOp Center models support using **recordsets**. A record set is an ordered collection of records. In R and Python, recordsets are analogous to (and in fact, deserialized into) data frames.

## Models with Recordsets

To configure an R or Python model to use recordsets in its inputs or outputs, just add the `# fastscore.recordsets.<slot_no>: true` or `# fastscore.recordsets.<slot_no>: yes` smart comments to the model. No changes to the model's input or output schema are required to use recordsets.

### Output Conventions

There is some ambiguity involved when encoding a record set to an Avro type. To resolve this, ModelOp Center uses the following mapping conventions to determine how to encode each element in the output record set:

#### In Python:

* If each output datum should be an Avro record, the model must yield a Pandas DataFrame.
* If each output datum should be an Avro array, the model must yield a Numpy matrix.
* If each output datum should be an atomic Avro type (such as a double or string), the model must yield a Pandas Series.

#### In R:

* If each output datum should be an Avro record, the model must yield a data.frame object.
* If each output datum should be an Avro array, the model must yield a matrix object.

(Atomic Avro types are not supported for R record set output.)

### Examples

The following model uses recordsets as inputs, and returns a single record as output. 
``` python
# fastscore.recordsets.0: true
# fastscore.input: two_doubles
# fastscore.output: summary_record
def action(record_set):
  sum1 = sum(record_set[0])
  sum2 = sum(record_set[1])
  yield {"sum1":sum1, "sum2":sum2}
```

Note that the variable `record_set` is deserialized as a Pandas DataFrame. In this case, the input schema is
```
{"type":"array", "items":"double"}
```
and the output schema is
```
{
  "type":"record", 
  "name":"summary", 
  "fields": [
    {"name":"sum1", "type":"double"},
    {"name":"sum2", "type":"double"}
  ]
}
```

The next model uses recordsets for both inputs and outputs. 
``` python
# fastscore.recordsets.0: true
# fastscore.recordsets.1: true
# fastscore.input: named_doubles
# fastscore.output: named_doubles_with_sum

def action(record_set):
  mydf = record_set
  mydf['sum'] = mydf['x'] + mydf['y']
  yield mydf
```

Here, the input schema is
```
{
  "type":"record",
  "name":"input",
  "fields":[
    {"name":"x", "type":"double"},
    {"name":"y", "type":"double"}
  ]
}
```

and the output schema is
```
{
  "type":"record",
  "name":"output",
  "fields":[
    {"name":"x", "type":"double"},
    {"name":"y", "type":"double"},
    {"name":"sum", "type":"double"}
  ]
}
```
### Additional Examples of Input/Output Recordsets

The following table shows how the model code sees input recordsets and how output recordsets look like in the output stream. The table uses JSON for illustrative purposes only: as mentioned, Recordsets are encoding-agnostic.

Note: Both input and output recordsets options are on, and records are separated by new lines.

| # | Input Recordset | Python Model | R Model | Output Recordset |
| --- | --- | --- | --- | --- |
| 1 | {"id": 100, "color": "red"} <br> {"id": 101, "color": "green"} <br> {"id": 102, "color": "grey"} | # color id <br> 0    red  100 <br> 1  green  101 <br> 2   grey  102 |  #  id color <br> 1 100   red <br> 2 101 green <br> 3 102  grey | {"id": 100, "color": "red"} <br> {"id": 101, "color": "green"} <br> {"id": 102, "color": "grey"} |
| 2 | (empty) | Empty DataFrame <br> Columns: [] <br> Index: []  |data frame with 0 columns and 0 rows | (empty) |
| 3 | 2 <br> 3 <br> 5 | 0  2 <br> 1  3 <br> 2  5 <br> dtype: int64 pandas.Series |   ---  [,1] <br> [1,]    2 <br> [2,]    3 <br> [3,]    5 | 2 <br> 3 <br> 5 |
| 4 | [2] <br> [3] <br> [5] | matrix([[2], <br> [3], <br> [5]]) | -  [,1] <br> [1,]    2 <br> [2,]    3 <br> [3,]    5 | Python: [2] <br> [3] <br> [5] <br> R: 2 <br> 3 <br> 5 |
| 5 | [0,0,1] <br> [0,1,0] <br> [0,0,1] | matrix([[1, 0, 0], <br> [0, 1, 0], <br> [0, 0, 1]]) |   ---   [,1] [,2] [,3] <br> [1,]    1    0    0 <br> [2,]    0    1    0 <br> [3,]    0    0    1 | [0,0,1] <br> [0,1,0] <br> [0,0,1] |
| 6 | 137 | 0  137 <br> dtype: int64 (pandas.Series) | ---  [,1] <br> [1,]  137 | 137 |
| 7 | [137] | matrix([[137]]) | --- [,1] <br> [1,]  137 | Python: [137] <br> R: 137 | 
| 8 | {"a": 2} <br> {"a": 3} <br> {"a": 5} | --- a <br> 0  2 <br> 1  3 <br> 2  5 | --- a <br> 0  2 <br> 1  3 <br> 2  5 | {"a": 2} <br> {"a": 3} <br> {"a": 5} |
| 9 | {"lone": "wolf"} | ---    lone <br> 0  wolf | ---    lone <br> 1  wolf | {"lone": "wolf"} |


## Streams and Control Records

A input stream reads records in batches. If the recordsets flag is ON for an input slot of the model, these batches become recordsets consumed by the model. The Batching property of the stream descriptor controls when the engine decides that it has read enough records to form a new batch/recordset. Setting “Batching” to “explicit” tells the engine that it should form a recordsets only if it encounters a special end-of-recordset control records. 

For example, a valid input stream descriptor for the second example above might be:
``` json
{
  "Loop": false,
  "Transport": {
    "Type": "file",
    "Path": "/root/data/input.jsons"
  },
  "Batching": "explicit",
  "Envelope": "delimited",
  "Encoding": "json",
  "Schema": {"$ref":"named_doubles"}
}
```

Additionally, to use recordsets, **control records** have to be injected into the data stream to mark the boundaries of a record set. A control record is a special type of record in the data stream that does not contain input/output data, but instead requests an action to be performed on the stream. 

There are three types of control records currently supported in ModelOp Center:

1. **end**. The "end" control record marks the end of the input stream. The underlying stream transport may contain more data, but this remaining data is ignored. The behavior mimics what happens when a stream receives an EOF signal from its transport. 

2. **set**. The "set" control record marks the end of a record set, and is how you create a record set-oriented stream, as described above.

3. **pig**. A "pig" control record travels the whole length of the ModelOp Center pipeline. If you inject a "pig" into the input stream, it will appear in the output stream. The purpose of a "pig" is to provide dependency guarantees similar to a memory barrier in a modern CPU---no input records after the "pig" can affect the output records received before the "pig" in the output stream.

Each control record can declare some common properties:

| Name | Type | Description |
| --- | --- | --- |
| `id` | int (4) | A control record identifier. |
| `timestamp` | long (8) | A number of milliseconds since the unix epoch. Corresponds to the AVRO timestamp logical type (millisecond precision). |
| `misc` | string | ASCII characters only. |


Control Records have representations in each of the supported encodings, as described in the following table. This table uses Python 2 literals.

| Encoding | end | set | pig | Notes |
| --- | --- | --- | --- | --- |
| null | `\\xfastscore.end` | `\\xfastscore.set` | `\\xfastscore.pig` | The record size must be at least 12 bytes. If there are at least 12 more bytes after the 12-byte prefix, then it contains the ID and timestamp encoded using the `'!Q'` Python struct format. Any data that follow is the value of the `misc` property. |
| utf-8 | `\\u262efastscore.end` | `\\u262efastscore.set` | `\\u262efastscore.pig` | ID, timestamp, and `misc` values may be appended separated by pipes. For example, `'\u262efastscore.pig|1234|3476304987|misc-data'`. |
| json | `{"$fastscore":"end"}` | `{"$fastscore":"set"}` | `{"$fastscore":"pig"}` | ID, timestamp, and `misc` values can be added as properties. |


A data stream using JSON encoding for the second model example above might look like the following:
```
{"x":3.0, "y":2.0}
{"x":2.5, "y":2.5}
{"x":-3.2, "y":-1.0}
{"$fastscore":"set"}
```
The corresponding output stream would be:
```
{"x":3.0, "y":2.0, "sum": 5.0}
{"x":2.5, "y":2.5, "sum": 5.0}
{"x":-3.2, "y":-1.0, "sum": -4.2}
{"$fastscore":"set"}
```
