
# CSV support

ModelOp Center supports CSV data format as described in [RFC 4180](https://tools.ietf.org/html/rfc4180)
with some extensions, such as a custom quote character.

You can set the CSV encoding in the stream descriptor as follows:
```
{
  ...
  "Encoding": "csv",
  ...
}
```

Or, if you want custom quote character and delimiter:
```
{
  ...
  "Encoding": {
    "Type": "csv",
    "QuoteCharacter": "'",
    "Delimiter": ";"
  },
  ...
}
```

If the stream transport is not boundary-preserving, such as a file, then the
"Envelope" property is automatically set to "delimited-csv".

You can customize the record envelope as follows:
```
{
  ...
  "Envelope": {
    "Type": "delimited-csv",
    "Separator": "\n",          // \r\n, by default
    "SkipHeader": true,         // true
    "SkipBlankLines": false     // true
  },
  ...
}
```

IMPORTANT. The default record sepator is "\r\n". For normal Unix files you need
to set the record separator to "\n".

The SkipHeader property indicates whether the header with field names is
present. Note that the schema is the preferred source of field names. Input
CSV-encoded streams with the header do not require a schema. Other streams do.
The schema of a CSV-encoded stream must have a "record" type. The ordering of
fields in the schema is significant.

It is possible to embed a record separator or a field delimiter in the field
value. Just surround the value with quote characters. The following text encodes
a single record with two fields:
```
1,'foo
bar,bar'
```

Use two quote characters to embed a quote into a quoted string.

CSV encoding also works for boundary-preserving streams, such as Kafka. The
record envelope is not used and there cannot be a header. It means that the
schema is mandatory for such streams.

CSV encoding is implemented by transcoding the stream data into JSON.

