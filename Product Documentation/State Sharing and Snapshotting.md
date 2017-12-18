---
title: "State Sharing and Snapshotting"
excerpt: "New in v1.5!"
---
As of v1.5, FastScore supports state sharing and snapshotting in Python and R models. This is achieved by providing a **cell** and **pool** interface to the models. Cells and pools provide persistent storage. The distinction between the two is that cells are just global variables that are shared across all runners, whereas pools are like environments in R: collections of key-value pairs that are shared across all runners, and can be manipulated at runtime. Additionally, the state of the engine's cells and pools can be "snapshotted": saved and exported for later use. 

# State Management

The cell-and-pool system allows multiple instances of a model runner to share data. This section provides some examples of models that can be run concurrently. To change the number of instances running a model, you may use the `fastscore job scale` CLI command, the `/job/scale` API call, or the Dashboard.

Both of the sample models below use state management in similar ways. The key difference is that the cell model updates a global variable named '`counter`', whereas the pool model updates the '`x`' key inside of the '`counter`' pool.

## Cell Model

[block:code]
{
  "codes": [
    {
      "code": "# fastscore.input: int\n# fastscore.output: int\n\nimport fastscore\n\ndef begin():\n    fastscore.cells('counter').set(0)\n\ndef action(x):\n    counter = fastscore.cells('counter')\n    counter.update(lambda y: x + y)\n    yield counter.value",
      "language": "python",
      "name": "Python Cell Example"
    },
    {
      "code": "# fastscore.input: int\n# fastscore.output: int\n\nlibrary(fastscore)\n\nbegin <- function() {\n    counter <- Cell('counter')\n    Set(counter, 0)\n}\n\naction <- function(x) {\n    counter <- Cell('counter')\n    Update(counter, function(y) y + x)\n    emit(Get(counter))\n}\n",
      "language": "r",
      "name": "R Cell Example"
    }
  ]
}
[/block]
For a given input, this model returns the sum of the total number of inputs and the value of the input. So, for example, the expected output of the inputs 1, 2, 3 is 1, 3, 6. 

## Pool Model
[block:code]
{
  "codes": [
    {
      "code": "# fastscore.input: int\n# fastscore.output: int\n\nimport fastscore\n\ndef begin():\n    fastscore.pools('counter').set('x', 0)\n\ndef action(v):\n    counter = fastscore.pools('counter')\n    counter.update('x', lambda x: x + 1)\n    yield counter.get('x')",
      "language": "python",
      "name": "Python Pool Example"
    },
    {
      "code": "# fastscore.input: int\n# fastscore.output: int\n\nlibrary(fastscore)\n\nbegin <- function(){\n    counter <- Pool('counter')\n    Set(counter, 'x', 0)\n}\n\naction <- function(datum){\n    counter <- Pool('counter')\n    Update(counter, 'x', function(x) x + 1)\n    emit(Get(counter, 'x'))\n}",
      "language": "r",
      "name": "R Pool Example"
    }
  ]
}
[/block]
For every input, this pool model returns the total number of inputs received. So, for example, the expected output of the inputs 5, 5, 5 is 1, 2, 3. 

# Snapshotting

Snapshotting is a mechanism for capturing the state of an engine's cells and pools. Model snapshots are automatically created when a model receives an end-of-stream message. To support snapshotting, the FastScore CLI provides convenient wrappers around the snapshot REST API. These commands are:
```
fastscore snapshot list <model name>
fastscore snapshot restore <model name> <snapshot id>
```

The `snapshot list` command shows the saved snapshots for a given model. The `snapshot restore` command restores the specified snapshot for a particular model. Snapshots are automatically created upon receipt of an end-of-stream message, but these end-of-stream messages can be introduced as control records into the data stream for streaming transports (e.g. Kafka). For more information on control records, see [Record Sets and Control Records](doc:record-sets). 

To enable snapshots, use the `fastscore.snapshots` smart comment:
```
# fastscore.snapshots: eof
```

An example of a model that creates snapshots on end of stream is shown below:
[block:code]
{
  "codes": [
    {
      "code": "# fastscore.input: int\n# fastscore.output: int\n# fastscore.snapshots: eof\n\nimport fastscore\n\ndef begin():\n    cell = fastscore.cells('sum')\n    if cell.value == None:\n        cell.set(0)\n\ndef action(datum):\n  cell = fastscore.cells('sum')\n  cell.update(lambda x: x + datum)\n  yield cell.value",
      "language": "python",
      "name": "Python snapshots"
    },
    {
      "code": "# fastscore.input: int\n# fastscore.output: int\n# fastscore.snapshots: eof\n\nlibrary(fastscore)\n\nbegin <- function(){\n    cell <- Cell('sum')\n    if(length(Get(cell)) == 0){\n        Set(cell, 0)\n    }\n}\n\naction <- function(datum){\n    c_sum <- Cell('sum')\n    result <- datum + Get(c_sum)\n    Set(c_sum, result)\n    emit(result)\n}",
      "language": "r",
      "name": "R snapshots"
    }
  ]
}
[/block]