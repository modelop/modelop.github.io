---
title: "C Model Runner"
excerpt: "Updated in v1.8!"
---

# C Model Runner

In v1.8 the C model runner has been updated to support more encodings and other
featured. The C model conventions have also changed. The new conventions are
explained below.

## ModelOp Center interface functions

The source code of a C model must define three interface functions: begin(),
action(), and end1(). These functions must have the following signatures:

```
void begin(void);
void action(fastscore_value_t v, int slot, int seqno);
void end1(void);
```

The `fastscore_value_t` type is defined in `fastscore.h`. Thus a C model must
contain the following in the beginning:

```
#include "fastscore.h"
```

The `begin()` function is called once during the initialization of the model
instance. Correspondingly, `end1()` is called during the instance shutdown.
The `action()` receives data records for processing.

## Stream slots

The `slot` argument of the `action()` function is the stream slot number. Its
value is typically zero if the model uses one input stream as most do. If there
are several input streams the slot number will be 0, 2, 4,... to identify a
particular stream.

The model also need to provide a slot slot number when emitting output records.
See [Output records](#output-records).

## Sequence numbers

The `seqno` argument of the `action()` function is the sequence number of the
record in the input stream. Sequence numbers start at 1 (not 0).

## Data formats

The C runner supports the following data encodings/formats:

* null (raw/binary)
* utf-8
* json
* avro-binary

The data format can be determined by checking the `fmt` field of the
`fastscore_value_t` value.

```
void action(fastscore_value_t v, int slot, int seqno)
{
    if (v.fmt == fastscore_FMT_JSON)
    {
        ...
...
```

### Null format

If the format of `fastscore_value_t` is fastscore_FMT_NULL, then the binary data
can be accesses using `data` and `size` fields. The `data` field contains a
pointer to the byte array and the `size` field contains its length.

For example,

```
    assert(v.fmt == fastscore_FMT_NULL);
    for (int i = 0; i < v.size; i++)
        do_more(v.data[i]);
    ...
```

### UTF-8 format

The fastscore_FMT_UTF8 format indicates that the value contains a
null-terminated Unicode string. The `str` field points to the beginning of the
string.

```
    assert(v.fmt == fastscore_FMT_UTF8);
    if (strcmp(v.str, "my-data-record") == 0)
    {
        ...
```

Note that the string must be allocated via malloc(). It is important when
constructing output records.

### JSON format

If the `fmt` field of `fastscore_value_t` is fastscore_FMT_JSON, then it
contains JSON data. The `js` field holds a `json_t *` reference as described in
the Jansson library [docs](https://jansson.readthedocs.io/en/2.2/apiref.html).

Note that the lifetime of the input `json_t` value is managed by ModelOp Center.
The model needs to use `json_incref` if it wants to keep the value around after
the `action()` call exits. The safest way, it to retrieve actual data from the
`json_t` value and use it directly.

For example,

```
    assert(v.fmt == fastscore_FMT_JSON);
    assert(json_is_object(v.js));
    json_t *foo = json_object_get(v.js, "foo");
    const char *str = json_string_value(foo);
    ...
```

### Avro format

The fastscore_FMT_AVRO format indicate that the value contains data decoded
using Avro binary encoding. The C runner uses the standard C Avro library for
handling such data. The `avro` field of the `fastscore_value_t` struct contains
a value of type `avro_value_t`. See the Avro
[docs](https://avro.apache.org/docs/1.8.2/api/c/index.html) for details.

For example,

```
    assert(v.fmt == fastscore_FMT_AVRO);
    double f;
    avro_value_get_double(&v.avro, &f);
    ...
```

## Recordsets

The model may ask the runner to provide records in batches or recordsets. Thus
the `fastscore_value_t` may contain multiple records. In this case its `fmt`
field contains fastscore_FMT_RSET. The length of the recordset is kept in the
`count` field. Individual records can be accessed using an array pointed to by
the `rs` field.

For example,

```
    assert(v.fmt == fastscore_FMT_RSET);
    for (int i = 0; i < v.count; i++)
    {
        assert(v.rs[i].fmt == fastscore_FMT_JSON);
        json_t *foo = json_object_fet(v.rs[i].js, "foo");
        ...
```

All records in a recordset are guaranteed to have the same format.

## Output records

The C runner export a special function for the model to call when it needs to
emit an output. The function is declared in `fastscore.h`.

```
void fastscore_emit(fastscore_value_t v, int slot);
```

The output value must be produced by the model. In particular, the model must
not attempt to output the value it received as an argument to the `action()`
call.

The output slot number is usually 1. If the model uses several output stream the
slot number help to distinguish between them. Note that output stream numbers
are always odd.

Examples:

```
    fastscore_value_t o = {
        .fmt = fastscore_FMT_UTF8,
        .str = strdup("my-output-record"),
    };
    fastscore_emit(o, 1);
    ...
```

```
    fastscore_emit((fastscore_value_t) {  // C99 syntax
        .fmt = fastscore_FMT_JSON,
        .js = json_integer(42),
    });
```

Note that it is not currently possible to output Avro data.

## Appendix

Format constants defined by fastscore.h:

* fastscore_FMT_NULL
* fastscore_FMT_UTF8
* fastscore_FMT_JSON
* fastscore_FMT_AVRO
* fastscore_FMT_RSET

