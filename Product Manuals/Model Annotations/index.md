---
title: "Model annotations"
css: buttondown.css
---

# Model annotations
 
A model can carry annotations as specially-formatted comments. The general
format for such annotations is as follows:

```
# <tag>: <value>
```

The annotation must be a comment in the target language and it must occupy the
whole line. If the annotation tag is recognized, the value becomes associated
with the tag. A tag contains a series of tag elements separated by dots. The
first tag element is either 'ModelOp Center' or 'ModelOp'.

Certain annotations are slot-specific. They are relevant for a particular
stream slot or a group of slots. The slot scope is always the last element of
the tag of a slot-specific annotation. The following slot scopes are
supported:

Slot scope	| Applicable to	| Example
------------|---------------|--------
&lt;slot-number> | The slot <slot-number> | # fastscore.schema.3: schema-1
&lt;slot-name>	| The named slot | #fastscore.schema.err: schema-1
$all | All stream slots | #fastscore.schema.$all: schema-1
$in | All input slots (0, 2, 4,...) | #fastscore.recordsets.$in: yes
$out | All output slots (1, 3, 5,...) | #fastscore.recordsets.$out: false

The slot scope can be omitted. If omitted, the default slot scope is assumed.
The default scope depends on the annotation tag.

The current list of supported model annotations is given in the table below.

Tag	| Slot-specific | Description | Allowed values | Example
----|---------------|-------------|----------------|--------
ModelOp Center.schema.&lt;slot> | Yes (default scope: $all) | The name of the Avro schema | | # ModelOp.schema.0: schema-1
ModelOp Center.recordsets.&lt;slot> | Yes (default scope: $all) | The 'recordsets' flag | true / false / yes / no | # ModelOp.recordsets.$in: yes
ModelOp Center.action.&lt;slot> | Yes (default score: $in) | The name of the action function (defaults to 'action') | <func-name> / none | # ModelOp.action: score_report
ModelOp Center.slot.&lt;slot> | Yes (default score: $all) | Set to 'unused' to disable the slot. | in-use / unused | #fastscore.slot.1: unused
ModelOp Center.module-attached | No | The name of the code module included as a model attachment | | #fastscore.module-attached: mylib
ModelOp Center.snapshots | No | Set to 'eof' to automatically take a model snapshot when the run completes. | none / eof | #fastscore.snapshots: eof

A `ModelOp Center.slot.<num-or-name>: in-use` annotation marks the slot as being
used by the model. If a slot number or name is mentioned in the
schema/recordsets/action annotation it implicitly marks the slot as being in
use. Note that in-use annotation can not refer to $all/$in/$out scopes.  On the
other hand, the `ModelOp Center.slot.<slot-scope>: unused`  annotation cancels the
effect of any previous annotations that mentioned the &lt;slot-scope>. For
example, `ModelOp Center.slot.$output: unused` indicate that the model does not
produce any outputs. The 'unused' annotation can remove the default slots (0
and 1) from consideration.

Setting `ModelOp Center.action` to `none` disables the action callbacks. The model
becomes purely explicit. Explicit models read from stream slots directly and may
exit before all streams reach EOF.

The annotations in the table below are deprecated and should not be used for
new models. However, they are recognized by the Engine.

Deprecated annotation | Equivalent annotation(s)
----------------------|-------------------------
ModelOp Center.input: &lt;schema> |fastscore.schema.0: &lt;schema>
ModelOp Center.output: &lt;schema> |fastscore.schema.1: &lt;schema>
ModelOp Center.recordsets: none/input/output/both |fastscore.recordsets.0: &lt;yes/no> /fastscore.recordsets.1: &lt;yes/no>

## PFA models

PFA models currently do not support multiple input/output stream slots. Thus
their annotations do not use a slot scope. Annotations of a PFA model are
represented as subelements of a 'metadata' element. The supported annotations
are given in the table below.

Annotation | Description | Default
-----------|-------------|--------
"recordsets": "none" / "recordsets": "input" / "recordsets": "output" / "recordsets": "both" | The 'recordsets' flag | "none"
"snapshots": "none" / "snapshots": "eof" | Set to 'eof' to automatically take a model snapshot when the run completes. | "none"

Note that for a PFA model keeps its schemas in two (mandatory) top-level elements: 'input' and 'output'. An example of an annotated PFA model:

```
{
  "input": "int",
  "output": "int",
  "metadata": {
    "recordsets": "none",
    "snapshots": "eof"
  },
  "action": ...
}
```

