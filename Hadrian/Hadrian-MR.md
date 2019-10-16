Hadrian-MR is a Hadoop map-reduce application that wraps the Hadrian software library, making it possible to submit PFA scoring engines as mappers and reducers.

It also has built-in support for secondary sorting (sorting values with the same key before they are sent to a reducer), and it can execute Jython in place of a PFA scoring engine using Antinous. This is particularly useful for writing model-producer algorithms that output PFA.

Hadrian-MR reads data from Avro files in HDFS and verifies that the mapper and reducer schemas are compatible.

## Before you begin...

Download the [pre-built Hadrian-MR JAR](Installation#case-2-you-want-to-use-pre-built-jar-files-for-one-of-the-hadrian-containers) with dependencies. This article was tested with Hadrian 0.8.3; newer versions should work with no modification.

## Help document

A good place to start is Hadrian-MR's own help text, which will always show the latest options.

    % hadoop jar target/hadrian-mr-TRUNK-jar-with-dependencies.jar --help
    Usage: hadoop jar hadrian-mr.jar [options] input output

      input
            input path specification
      output
            output directory, must not yet exist
      -m <value> | --mapper <value>
            location of mapper PFA
      -r <value> | --reducer <value>
            location of reducer PFA
      -i | --identity-reducer
            use an identity reducer (key-grouping and possibly secondary sort, but no reducer action)
      -n <value> | --num-reducers <value>
            number of reducers (must be at least 1 if --reducer or --identity-reducer is used)
      -s <value> | --snapshot <value>
            output a snapshot of a reducer cell/pool after processing each key, rather than the reducer engine's output (pools take precedence over cells in case of name conflicts)
      --help
            print this help message

    Hadrian-MR in "score" mode runs a PFA-encoded scoring engine as a
    mapper and a PFA-encoded scoring engine as a reducer.

    The output type of the mapper must be a record with two fields: "key"
    and "value".  The key must either be a string or a record containing a
    string-valued "groupby" field.  If the key is a string, that string
    will be used for grouping with no secondary sort.  If the key is a
    record, its groupby field is used for grouping and the whole record is
    used for secondary sort (according to the normal record-sorting Avro
    rules).

    The input type of the reducer must be a record with the same structure
    as the mapper output.

## Workflows

Hadrian-MR supports the following workflows.

   * Mapper-only: for embarrassingly parallel problems, only pass a PFA or Jython mapper with `-m` (no reducers with `-r` or `-i`). Output data are _not_ sorted or grouped by key.
   * Mapper with identity reducer: for problems that require sorting and grouping of the output, but no additional processing, pass a PFA or Jython mapper with `-m` and ask for the identity reducer with `-i`.
   * Map-reduce: for the usual Hadoop application, pass a PFA or Jython mapper with `-m` and a PFA or Jython reducer with `-r`.
   * In some cases (model building), you may not be interested in the output of a PFA reducer, but only the final state of some persistent state (cell or pool). Pass a PFA or Jython mapper with `-m` and a PFA reducer (Jython not allowed) with `-r` as usual, and also `-s` followed by the cell/pool name. The Avro output will contain cell/pool values, one for each key, with a schema determined by the cell/pool type rather than the scoring engine output type.

## Reducer time-evolution

In all cases, the reducer scoring engines start fresh with each new key and are allowed to evolve while processing the values associated with that key. This makes the behavior of the scoring engines strictly independent of the order of keys and the partitioning of keys among nodes. Internally, this is accomplished by saving and restoring the reducer's persistent state, rather than creating new reducers for each key, a performance optimization that does not affect results.

## Secondary sorting

"Secondary sorting" is the process of using Hadoop's sorting mechanism to not only partition data by key, but also sort values associated with each given key. It is accomplished by using more fine-grained keys in the sorting stage than the partitioning stage: for instance, using floating point keys for sorting and then truncating the the nearest integer for partitioning. Hadoop has no built-in facility for this; it is frequently re-implemented by Hadoop users.

Hadrian-MR performs a secondary sort if the key is a record. The whole record is used for sorting, following the usual Avro rules for sorting records (including the "ascending", "descending", and "ignore" specifications for record fields and sort precedence by field order). Only the "groupby" field is used for partitioning.

Thus, the following mapper output schema (reducer input schema) would partition by "country" and sort by "time":

    {"key": {"type": "record",
             "name": "Key",
             "fields": [{"name": "groupby", "type": "string", "doc": "country"},
                        {"name": "time", "type": "double", "order": "ascending"}]},
     "value": {"type": "record",
               "name": "Value",
               "fields": [{"name": "time", "type": "double"},
                          ...
                         ]}}
