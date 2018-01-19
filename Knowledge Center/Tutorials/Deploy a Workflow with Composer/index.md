<script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>

# Deploy a Workflow with Composer

In this example, we'll use FastScore Composer to deploy a multi-model workflow.
We'll re-use the LSTM model [from the TensorFlow example](../Tensorflow LSTM),
and add some extra model stages to do pre- and post-processing of the data for
this model. We'll be using a mixture of Python 3 and R for our models.

FastScore Composer is a tool for building and deploying analytic workflows in
FastScore. Recall that the LSTM model predicts a CPI-normalized, adjusted
S&P closing price based on the previous 30 days' closing prices. By using Composer,
we'll take in the raw S&P closing prices and consumer price index (CPI) data,
produce normalized input for the LSTM model, and then transform the model's output
back to actual S&P 500 prices. This analytic workflow is depicted below:

![Analytic Workflow](images/multi-engine-workflow.png)

<p align="center"><i>Analytic Workflow</i></p>

The daily S&P 500 closing prices since June 1, 2007, as well as the corresponding
CPI data, [can be obtained here](TODO TODO TODO).

## The Preprocessor

The preprocessor model accepts data from two different sources (S&P 500 closing
prices, and CPI), and uses that data to produce the transformed inputs that the
TensorFlow LSTM model needs to make its predictions. Recall that this transformation
consists of two steps:

1. The S&P 500 closing price is divided by the CPI, and then
2. The predicted linear trend is subtracted from this number.

Mathematically, we can write this as:

$$ \tilde{s}(t) = \frac{s(t)}{c(t)} - mt - b, $$

where $$s(t)$$ is the S&P 500 closing price on day $$t$$, $$c(t)$$ the CPI on day $$t$$,
$$m$$ and $$b$$ are the slope and intercept of the linear trend described in the
[TensorFlow LSTM tutorial](../Tensorflow LSTM), and $$\tilde{s}$$ is the input to the LSTM model.

Let's implement our preprocessing step using R. First, we'll define two functions:

```R
rescale <- function(close, cpi){
    close/cpi
}

reg <- function(date){
    slope*date + intercept
}
```

These functions will make our feature transformation expression a little cleaner.
If `date`, `sp500`, and `cpi` represent the date, S&P 500 closing price, and CPI,
respectively, then calculating the adjusted input is easy:

```R
rescale(sp500, cpi) - reg(date)
```

To prepare this preprocessor for FastScore, we'll need to write an R script that
can accept asynchronous, heterogeneous inputs from two input streams. Fortunately,
FastScore provides abstractions for multiple streams that make this easy. When
defining an `action` function, just include the `slot` argument in the function
signature, and then FastScore will automatically supply the slot number (a numeric
identifier of the input stream) along with the input data:

```R
action <- function(data, slot) {
    [...]
}
```

Because our model may receive S&P 500 and CPI data asynchronously, but our
calculation depends on having both the S&P 500 price and CPI available in order
to perform the calculation, let's create two lists to keep track of the data
received thus far from each of these sources. This can be done in the `begin`
function:

```R
begin <- function(){
    slope <<- 0.0002319547958991928
    intercept <<- 0.4380634632578033

    cpis <<- list()
    sp500s <<- list()
}
```

(Note that we've also initialized the `slope` and `intercept` global variables
here).

In our action function, we'll first append items to these lists depending on
what slot they came in on, and then pop them from the list when both lists
have elements available:

```R
action <- function(data, slot){

    if(slot == 0){ # SP500 input
        count <- length(sp500s)
        sp500s[[count + 1]] <<- data
    }

    if(slot == 2){ # CPI input
        count <- length(cpis)
        cpis[[count + 1]] <<- data
    }

    while(length(sp500s) > 0 && length(cpis) > 0){
        sp500 <- sp500s[[1]]
        sp500s[[1]] <<- NULL # pop from the front of the list
        cpi <- cpis[[1]]
        cpis[[1]] <<- NULL # pop from the front of the list

        [...] # Do something
    }
}
```

Thus far we haven't given much thought to the schemata used by this preprocessor.
Let's take a moment to address that now. In this example, let's assume the CPI
data looks like JSON-encoded records with two fields (date and value). Some
example inputs might be:

```
{"Date": 20968.0, "CPI": 207.234}
{"Date": 20971.0, "CPI": 207.244}
{"Date": 20972.0, "CPI": 207.254}
{"Date": 20973.0, "CPI": 207.2642}
```

FastScore uses an Avro schema system to enforce strong typing on models' inputs
and outputs. The Avro schema for this data is:

```json
{
    "name":"cpi",
    "type":"record",
    "fields":[
        {"name": "Date", "type":"double"},
        {"name": "CPI", "type": "double"}
    ]
}
```

The S&P 500 inputs will similarly be JSON records:
```
{"Date": 20968.0, "Close": 1536.339966}
{"Date": 20971.0, "Close": 1539.180054}
{"Date": 20972.0, "Close": 1530.949951}
{"Date": 20973.0, "Close": 1517.380005}
```
with Avro schema:
```json
{
    "name":"sp500",
    "type":"record",
    "fields":[
        {"name": "Date", "type":"double"},
        {"name": "Close", "type": "double"}
    ]
}
```

When deserializing data into R objects, FastScore encodes these records as
lists with named indices. So, for example, the element
```
{"Date": 20968.0, "CPI": 207.234}
```
becomes to the R object
```R
list("Date"=20968.0, "CPI"=207.234)
```
