---
title: "State Sharing and Snapshotting"
excerpt: "New in v1.5!"
---
# State Sharing and Snapshotting

As of v1.5, ModelOp Center supports state sharing and snapshotting in Python and R models. This is achieved by providing a **cell** and **pool** interface to the models. Cells and pools provide persistent storage. The distinction between the two is that cells are just global variables that are shared across all runners, whereas pools are like environments in R: collections of key-value pairs that are shared across all runners, and can be manipulated at runtime. Additionally, the state of the engine's cells and pools can be "snapshotted": saved and exported for later use. 

## State Management

The cell-and-pool system allows multiple instances of a model runner to share data. This section provides some examples of models that can be run concurrently. To change the number of instances running a model, you may use the `fastscore job scale` CLI command, the `/job/scale` API call, or the Dashboard.

Both of the sample models below use state management in similar ways. The key difference is that the cell model updates a global variable named '`counter`', whereas the pool model updates the '`x`' key inside of the '`counter`' pool.

### Cell Model

``` python
# fastscore.input: int
# fastscore.output: int

import fastscore

def begin():
    fastscore.cells('counter').set(0)
    
def action(x):
    counter = fastscore.cells('counter')
    counter.update(lambda y: x + y)
    yield counter.value
```

``` r
# fastscore.input: int
# fastscore.output: int

library(fastscore)

begin <- function() {
    counter <- Cell('counter')
    Set(counter, 0)
}

action <- function(x) {
    counter <- Cell('counter')
    Update(counter, function(y) y + x)
    emit(Get(counter))
}
```

For a given input, this model returns the sum of the total number of inputs and the value of the input. So, for example, the expected output of the inputs 1, 2, 3 is 1, 3, 6. 

### Pool Model
``` python
# fastscore.input: int
# fastscore.output: int

import fastscore

def begin():
    fastscore.pools('counter').set('x', 0)
    
def action(v):
    counter = fastscore.pools('counter')
    counter.update('x', lambda x: x + 1)
    yield counter.get('x')
```

``` r
# fastscore.input: int
# fastscore.output: int

library(fastscore)

begin <- function(){
    counter <- Pool('counter')
    Set(counter, 'x', 0)
}

action <- function(datum){
    counter <- Pool('counter')
    Update(counter, 'x', function(x) x + 1)
    emit(Get(counter, 'x'))
}
```

For every input, this pool model returns the total number of inputs received. So, for example, the expected output of the inputs 5, 5, 5 is 1, 2, 3. 

## Snapshotting

Snapshotting is a mechanism for capturing the state of an engine's cells and pools. Model snapshots are automatically created when a model receives an end-of-stream message. To support snapshotting, the ModelOp Center CLI provides convenient wrappers around the snapshot REST API. These commands are:
```
fastscore snapshot list <model name>
fastscore snapshot restore <model name> <snapshot id>
```

The `snapshot list` command shows the saved snapshots for a given model. The `snapshot restore` command restores the specified snapshot for a particular model. Snapshots are automatically created upon receipt of an end-of-stream message, but these end-of-stream messages can be introduced as control records into the data stream for streaming transports (e.g. Kafka). For more information on control records, see [Record Sets and Control Records](https://opendatagroup.github.io/Product%20Manuals/Record%20Sets%20and%20Control%20Records/). 

To enable snapshots, use the `fastscore.snapshots` smart comment:
```
# fastscore.snapshots: eof
```

An example of a model that creates snapshots on end of stream is shown below:
``` python
# fastscore.input: int
# fastscore.output: int
# fastscore.snapshots: eof

import fastscore

def begin():
    cell = fastscore.cells('sum')
    if cell.value == None:
        cell.set(0)
        
def action(datum):
  cell = fastscore.cells('sum')
  cell.update(lambda x: x + datum)
  yield cell.value
```

``` r
# fastscore.input: int
# fastscore.output: int
# fastscore.snapshots: eof

library(fastscore)

begin <- function(){
    cell <- Cell('sum')
    if(length(Get(cell)) == 0){
        Set(cell, 0)
    }
}    
    
action <- function(datum){
    c_sum <- Cell('sum')
    result <- datum + Get(c_sum)
    Set(c_sum, result)
    emit(result)
}
```