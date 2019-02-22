---
title: "Record Sets and Control Records"
excerpt: "New in v1.4!"
---
# Record Sets and Control Records

To better handle different model types (such as batch models), FastScore models support using **record sets**. A record set is an ordered collection of records. In R and Python, record sets are analogous to (and in fact, deserialized into) data frames.

## Models with Record Sets

To configure an R or Python model to use record sets in its inputs or outputs, just add the `# fastscore.recordsets.<slot_no>: true` or `# fastscore.recordsets.<slot_no>: yes` smart comments to the model. No changes to the model's input or output schema are required to use record sets.

### Output Conventions

There is some ambiguity involved when encoding a record set to an Avro type. To resolve this, FastScore uses the following mapping conventions to determine how to encode each element in the output record set:

#### In Python:

* If each output datum should be an Avro record, the model must yield a Pandas DataFrame.
* If each output datum should be an Avro array, the model must yield a Numpy matrix.
* If each output datum should be an atomic Avro type (such as a double or string), the model must yield a Pandas Series.

#### In R:

* If each output datum should be an Avro record, the model must yield a data.frame object.
* If each output datum should be an Avro array, the model must yield a matrix object.

(Atomic Avro types are not supported for R record set output.)

### Examples

The following model uses record sets as inputs, and returns a single record as output. 
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

The next model uses record sets for both inputs and outputs. 
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

## Streams and Control Records

To use record sets, input and output streams must also be explicitly configured to do so by adding the `"Batching":"explicit"` flag. For example, a valid input stream descriptor for the second example above might be:
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

Additionally, to use record sets, **control records** have to be injected into the data stream to mark the boundaries of a record set. A control record is a special type of record in the data stream that does not contain input/output data, but instead requests an action to be performed on the stream. 

There are three types of control records currently supported in FastScore:

1. **end**. The "end" control record marks the end of the input stream. The underlying stream transport may contain more data, but this remaining data is ignored. The behavior mimics what happens when a stream receives an EOF signal from its transport. 

2. **set**. The "set" control record marks the end of a record set, and is how you create a record set-oriented stream, as described above.

3. **pig**. A "pig" control record travels the whole length of the FastScore pipeline. If you inject a "pig" into the input stream, it will appear in the output stream. The purpose of a "pig" is to provide dependency guarantees similar to a memory barrier in a modern CPU---no input records after the "pig" can affect the output records received before the "pig" in the output stream.

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
