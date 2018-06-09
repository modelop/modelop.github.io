---
title: "Time Streams"
excerpt: "A stream that delivers timestamps instead of data"
---
# Time Streams

## Overview

Many analytic models have a notion of time. Such models may receive time-related
values as a part of their inputs. Or, they obtain such values using standard
library calls. The latter adds an external dependency to the model. FastScore
cannot control the time value the model gets from the system. The time
streams proposed here remove the dependency.

A time stream feeds timestamps to the model according to the settings in its
stream descriptor. Time streams enable the following two important use cases:

* A 'fake' time for simulations, verification, and model training;
* Periodic model activations without actual data.

## A time stream descriptor

An example of a time stream descriptor:
``` json
{
  "Transport": {
    "Type": "time",
    "Period: 2.0
  },
  "Schema": {
    "type": "long",
    "logicalType": "timestamp-millis"
  }
}

The above stream delivers timestamps to the model every 2s.

A Transport element of the a stream supports the following properties:

Property | Type | Required | Default | Description
---------|----------|---------|------------
Type | string | Yes | | Set to "time" or "Time"
TimeZero | string or null | No | null | The beginning of simulated time (iso8601)
Delay | number | No | 0.0 | Wait this number of seconds before sending the first timestamp
Period | number | No | 1.0 | Time between timestamps in seconds
MaxCount | integer or null | No | null | Generate no more than this number of timestamps
Overflow | string | No | "all" | Out-of-sync timestamps (either "skip" or "all")

TimeZero controls the simulated time. The difference between normal and
simulated times is calucated at the stream instantiation. The model will receive
the following timestamps: TimeZero + Delay, TimeZero + Delay + Period,... If
TimeZero is omitted or set to null, the time stream uses the current time.

The number of timestamps delivered to the model can be capped using MaxCount
property. After the stream generates this many timestamps it signals EOF.

If the model is slow it may not be able to process all timestamps on time. The
stream behaviour with respect to the out-of-sync timestamps depends on the
Overflow property. If Overflow is "all", stream delivers all timestamp
regardless of their timeliness. This may result in batches of timestamps
delivered at the same time. If Overflow is "skip", only timely timestamps are
delivered. Skipped timestamps produce a warning message.

The Transport element may be set to "time" to assume default values for all
properties.

As with any boundary-preserving stream, the Envelope property of a time stream
must be either omitted or set to null. The Encoding property must be either
omitted or set to "bert".

The Avro schema has a special logical type for timestamp. Or, rather two such
types: one for millisecond --- and another for microsecond resolution. We only
support millisecond timestamps (timestamp-millis).

The time stream must not use batching. A timestamp must be delivered to the
model immediately without buffering. Thus, Batching must be omitted or set to
null.

The simplest valid time stream descriptor looks as follows:
``` json
{
  "Transport": "time"
}
```

It is equivalent to the following stream descriptor:
``` json
{
  "Transport": {
    "Type": "time",
    "TimeZero": null,   // normal time
    "Delay": 0.0,       // no delay
    "Period": 1.0,      // every 1s
    "MaxCount": null,   // indefinite length
    "Overflow": "all"   // deliver out-of-sync timestamps
  },
  "Envelope": null,     // no envelope
  "Encoding": "bert",   // internal encoding
  "Schema": {
    "type": "long",
    "logicalType": "timestamp-millis"
  },
  "Batching": null      // no batching
}
```

Time streams are input only.

## Other considerations

There is a somewhat similar situation with the access to a random number
generator. A model verification may need to 'replay' the sequence of random
numbers used by the model. Or, the model may need cryptographically-strong
random numbers from a hardware source. The mapping to the FastScore stream
concept is less obvious here. The practical workaround could be to seed RNG
using a timestamp provided by a simulated time stream.

## More info

TODO

