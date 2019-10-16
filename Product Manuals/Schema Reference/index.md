---
title: "Schema Reference"
excerpt: ""
---
# Schema Reference

## Overview

ModelOp Center enforces strict typing of engine inputs and outputs at two levels: stream input/output, and model input/output. Types are declared using [AVRO schema](https://avro.apache.org/docs/1.8.1/). 

To support this functionality, ModelOp Center's Model Manage maintains a database of named AVRO schemas. Python and R models must then reference their input and output schemas using smart comments. (PrettyPFA and PFA models instead explicitly include their AVRO types as part of the model format.) [Stream descriptors](https://opendatagroup.github.io/Product%20Manuals/Stream%20Descriptors/) may either reference a named schema from Model Manage, or they may explicitly declare schemas.

In either case, ModelOp Center performs the following type checks:

1. Before starting a job: the input stream's schema is checked for compatibility against the model's input schema, and the output stream's schema is checked for compatibility against the model's output schema.

2. When incoming data is received: the incoming data is checked against the input schemas of the stream and model.

3. When output is produced by the model: the outcoming data is checked against the model and stream's output schemas. 

Failures of any of these checks are reported: schema incompatibilities between the model and the input or output streams will produce an error, and the engine will not run the job. Input or output records that are rejected due to schema incompatibility appear as Pneumo messages, and a report of rejected records is also shown in Dashboard's Engine panel.
## Examples

The following model takes in a record with three fields (`name`, `x` and `y`), and returns the product of the two numbers.
``` python
# fastscore.input: named-array
# fastscore.output: named-double

def action(datum):
      my_name = datum['name']
      x = datum['x']
      y = datum['y']
      yield {'name': my_name, 'product':x*y}
```

The corresponding input and output AVRO schema are:
``` json
{
  "type":"record",
  "name":"input",
  "fields": [
    {"name":"name", "type":"string"},
    {"name":"x", "type":"double"},
    {"name":"y", "type":"double"}
    ]
}
```

``` json
{
  "type":"record",
  "name":"output",
  "fields": [
    {"name":"name", "type":"string"},
    {"name":"product", "type":"double"}
    ]
}
```

So, for example, this model may take as input the JSON record
```
{"name":"Bob", "x":4.0, "y":1.5}
```
and score this record to produce
```
{"name":"Bob", "product":"6.0"}
```

[Once ModelOp Center is running](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20ModelOp%20Center/), we can add the model and associated schemas to model manage with the following commands:
```
fastscore schema add named-array named-array.avsc
fastscore schema add named-double named-double.avsc
fastscore model add my_model model.py
```
Assuming that additionally, we have [configured the input and output stream descriptors](https://opendatagroup.github.io/Product%20Manuals/Stream%20Descriptors/) to use our schemas, we can then run the job with
```
fastscore job run my_model <input stream name> <output stream name>
```
The stream descriptors can be set to use these schemas with the `Schema` field. For example, for the input stream descriptor:
```
"Schema":{"$ref":"named-array"}
```
Note that in both the model's smart comments, the CLI commands, and the stream descriptor schema references, the schemas are referenced by their name in model manage, not the filename or any other property.