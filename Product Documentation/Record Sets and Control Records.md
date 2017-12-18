---
title: "Record Sets and Control Records"
excerpt: "New in v1.4!"
---
To better handle different model types (such as batch models), FastScore models support using **record sets**. A record set is an ordered collection of records. In R and Python, record sets are analogous to (and in fact, deserialized into) data frames.

# Models with Record Sets

To configure an R or Python model to use record sets in its inputs or outputs, just add the `# fastscore.recordsets: input` or `# fastscore.recordsets: output` smart comments to the model, respectively. (To use record sets in both the input and output streams, use the `# fastscore.recordsets: both` smart comment.) No changes to the model's input or output schema are required to use record sets.

## Output Conventions

There is some ambiguity involved when encoding a record set to an Avro type. To resolve this, FastScore uses the following mapping conventions to determine how to encode each element in the output record set:

### In Python:

* If each output datum should be an Avro record, the model must yield a Pandas DataFrame.
* If each output datum should be an Avro array, the model must yield a Numpy matrix.
* If each output datum should be an atomic Avro type (such as a double or string), the model must yield a Pandas Series.

### In R:

* If each output datum should be an Avro record, the model must yield a data.frame object.
* If each output datum should be an Avro array, the model must yield a matrix object.

(Atomic Avro types are not supported for R record set output.)

## Examples

The following model uses record sets as inputs, and returns a single record as output. 
[block:code]
{
  "codes": [
    {
      "code": "# fastscore.recordsets: input\n# fastscore.input: two_doubles\n# fastscore.output: summary_record\n\ndef action(record_set):\n  sum1 = sum(record_set[0])\n  sum2 = sum(record_set[1])\n  yield {\"sum1\":sum1, \"sum2\":sum2}",
      "language": "python"
    }
  ]
}
[/block]
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
[block:code]
{
  "codes": [
    {
      "code": "# fastscore.recordsets: both\n# fastscore.input: named_doubles\n# fastscore.output: named_doubles_with_sum\n\ndef action(record_set):\n  mydf = record_set\n  mydf['sum'] = mydf['x'] + mydf['y']\n  yield mydf",
      "language": "python"
    }
  ]
}
[/block]
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

# Streams and Control Records

To use record sets, input and output streams must also be explicitly configured to do so by adding the `"Batching":"explicit"` flag. For example, a valid input stream descriptor for the second example above might be:
[block:code]
{
  "codes": [
    {
      "code": "{\n  \"Loop\": false,\n  \"Transport\": {\n    \"Type\": \"file\",\n    \"Path\": \"/root/data/input.jsons\"\n  },\n  \"Batching\": \"explicit\",\n  \"Envelope\": \"delimited\",\n  \"Encoding\": \"json\",\n  \"Schema\": {\"$ref\":\"named_doubles\"}\n}\n",
      "language": "json"
    }
  ]
}
[/block]
Additionally, to use record sets, **control records** have to be injected into the data stream to mark the boundaries of a record set. A control record is a special type of record in the data stream that does not contain input/output data, but instead requests an action to be performed on the stream. 

There are three types of control records currently supported in FastScore:

1. **end**. The "end" control record marks the end of the input stream. The underlying stream transport may contain more data, but this remaining data is ignored. The behavior mimics what happens when a stream receives an EOF signal from its transport. 

2. **set**. The "set" control record marks the end of a record set, and is how you create a record set-oriented stream, as described above.

3. **pig**. A "pig" control record travels the whole length of the FastScore pipeline. If you inject a "pig" into the input stream, it will appear in the output stream. The purpose of a "pig" is to provide dependency guarantees similar to a memory barrier in a modern CPU---no input records after the "pig" can affect the output records received before the "pig" in the output stream.

Each control record can declare some common properties:
[block:parameters]
{
  "data": {
    "h-0": "Name",
    "h-1": "Type",
    "h-2": "Description",
    "0-0": "`id`",
    "0-1": "int (4)",
    "0-2": "A control record identifier",
    "1-0": "`timestamp`",
    "1-1": "long (8)",
    "1-2": "A number of milliseconds since the unix epoch. Corresponds to the AVRO timestamp logical type (millisecond precision).",
    "2-0": "`misc`",
    "2-1": "string",
    "2-2": "ASCII characters only."
  },
  "cols": 3,
  "rows": 3
}
[/block]
Control Records have representations in each of the supported encodings, as described in the following table. This table uses Python 2 literals.
[block:parameters]
{
  "data": {
    "h-0": "Encoding",
    "h-1": "end",
    "h-2": "set",
    "h-3": "pig",
    "h-4": "Notes",
    "0-0": "null",
    "0-1": "`\\xfastscore.end`",
    "0-2": "`\\xfastscore.set`",
    "0-3": "`\\xfastscore.pig`",
    "0-4": "The record size must be at least 12 bytes. If there are at least 12 more bytes after the 12-byte prefix, then it contains the ID and timestamp encoded using the `'!Q'` Python struct format. Any data that follow is the value of the `misc` property.",
    "1-0": "utf-8",
    "1-1": "`\\u262efastscore.end`",
    "1-2": "`\\u262efastscore.set`",
    "1-3": "`\\u262efastscore.pig`",
    "1-4": "ID, timestamp, and `misc` values may be appended separated by pipes. For example, `'\\u262efastscore.pig|1234|3476304987|misc-data'`.",
    "2-0": "json",
    "2-1": "`{\"$fastscore\":\"end\"}`",
    "2-2": "`{\"$fastscore\":\"set\"}`",
    "2-3": "`{\"$fastscore\":\"pig\"}`",
    "2-4": "ID, timestamp, and `misc` values can be added as properties."
  },
  "cols": 5,
  "rows": 3
}
[/block]
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