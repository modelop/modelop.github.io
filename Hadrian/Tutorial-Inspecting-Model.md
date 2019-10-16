# Tutorial 3: inspecting a model in PFA-Inspector

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `PFAEngine` to verify the installation:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from titus.genpy import PFAEngine

Then close the Python prompt. You won't need it for this tutorial.

If you completed [Tutorial 2](Tutorial-Small-Model-R), you would have created a `myModel.pfa` that we'll use in this tutorial. If you haven't, [download it here](https://github.com/opendatagroup/hadrian/wiki/model/myModel.pfa).

## Titus scripts

Titus includes a few scripts for performing specialized tasks without having to write Python code. The most general of these is the PFA-Inspector, which is a commandline for navigating and querying PFA with tab completion.

Launch the PFA-Inspector by executing `pfainspector myModel.pfa` in your terminal. It should look like this:

```
Titus PFA Inspector (version 0.7.1)
Type 'help' for a list of commands.
load myModel.pfa as myModel
PFA-Inspector> 
```

By including `myModel.pfa` as an argument, it preloads that file into the session. Type `help` for a list of commands.

```
PFA-Inspector> help
Commands:
    pwd                  print name of current/working directory
    cd                   change the current/working directory to the specified path
    back                 pop back to a previously visited directory
    ls                   list directory contents
    load                 read a PFA file into the current context, possibly naming it
    list                 list the named PFA files in memory
    rename               change the name of a PFA document
    drop                 delete a named PFA document from memory
    save                 save a PFA document from the current context or a named document to a file
    json                 json gadget (type 'json help' for details)
    pfa                  pfa gadget (type 'pfa help' for details)
    exit                 exit the PFA-Inspector (also control-D)
PFA-Inspector> load help
read a PFA file into the current context, possibly naming it
    load <file-path> as <name>
```

The `load` command pulls the model into memory. (This would work with any JSON file, not just PFA.) Most of the main commands are for finding PFA files and loading them. Tab completion helps you navigate the filesystem.

The `json` and `pfa` subcommands do more interesting work:

```
PFA-Inspector> json help
json gadget (type 'json help' for details)
Subcommands under json:
    look                 look at a named PFA document or subexpression in memory
    count                count instances in a PFA document or subexpression that match a regular expression
    index                list indexes of a PFA document or subexpression that match a regular expression
    find                 show all matches of a regular expression in a PFA document or subexpression
    change               replace instances in a PFA document or subexpression that match a regular expression
PFA-Inspector> pfa help
pfa gadget (type 'pfa help' for details)
Subcommands under pfa:
    valid                check the validity of a named PFA document
    input                view the input schema of a named PFA document
    output               view the output schema of a named PFA document
    types                list the named types defined in a named PFA document
    userfcns             list details about the user functions in a named PFA document
    calls                list PFA functions called by a named PFA document
    cells                list details about cells in a named PFA document
    pools                list details about pools in a named PFA document
```

Let's start with `json look myModel`. This pretty-prints the JSON in a useful way. Use help or tab-completion to discover arguments that modify this command.

```
index                          data
------------------------------------------------------------
                               {
action                           "action": [
action,0                           {
action,0,let                         "let": {
action,0,let,derived                   "derived": {
action,0,let,derived,new                 "new": {
action,0,let,derived,new,x2                "x2": {
action,0,let,derived,new,x2...               "u.imputeX2": [
action,0,let,derived,new,x2...                 {...}
                                             ]
                                           },
action,0,let,derived,new,x1                "x1": {
action,0,let,derived,new,x1...               "s.lower": [
action,0,let,derived,new,x1...                 {...}
                                             ]
                                           }
                                         },
```

The indexes on the left can be used for more focused queries. Try diving into just one tree of the forest. (Again, tab-completion helps you to navigate.)

```
PFA-Inspector> json look myModel[cells, forest, init, 59]
index                          data
------------------------------------------------------------
                               {
operator                         "operator": "<=",
field                            "field": "x2",
fail                             "fail": {
fail,TreeNode                      "TreeNode": {
fail,TreeNode,operator               "operator": "<=",
fail,TreeNode,field                  "field": "x2",
fail,TreeNode,fail                   "fail": {
fail,TreeNode,fail,TreeNode            "TreeNode": {
fail,TreeNode,fail,TreeNode...           "operator": "in",
fail,TreeNode,fail,TreeNode...           "field": "x1",
fail,TreeNode,fail,TreeNode...           "fail": {"string": "bad"},
fail,TreeNode,fail,TreeNode...           "value": {"array": ["three"]},
fail,TreeNode,fail,TreeNode...           "pass": {"string": "good"}
                                       }
                                     },
fail,TreeNode,value                  "value": {"double": -13.7397705915001},
fail,TreeNode,pass                   "pass": {"string": "good"}
                                   }
                                 },
value                            "value": {"double": -13.8543241817851},
pass                             "pass": {
pass,TreeNode                      "TreeNode": {
pass,TreeNode,operator               "operator": "in",
pass,TreeNode,field                  "field": "x1",
pass,TreeNode,fail                   "fail": {"string": "bad"},
pass,TreeNode,value                  "value": {"array": ["three"]},
pass,TreeNode,pass                   "pass": {"string": "good"}
                                   }
                                 }
                               }
```

PFA-Inspector also has access to Titus's "JSON regular expressions" to search for patterns in the document. The following finds all JSON objects that contain a field named "pass" with value `{"string": "good"}`:

```
PFA-Inspector> json find myModel {pass: {string: good}, ...}
```

Moreover, you can count matches to learn general facts about the model, such as how many leaves score a particular way.

```
PFA-Inspector> json count myModel {pass: {string: good}, ...}
141 matches
PFA-Inspector> json count myModel {pass: {string: bad}, ...}
26 matches
PFA-Inspector> json count myModel {pass: {string: _}, ...}
167 matches
PFA-Inspector> json count myModel ( {pass: {string: _}, ...} | {fail: {string: _}, ...} )
195 matches
```

All of the above treats the `myModel.pfa` file as pure JSON. To also interpret it as PFA, we use subcommands from the "pfa" gadget.

```
PFA-Inspector> pfa valid myModel
PFA document is syntactically and semantically valid
```

```
PFA-Inspector> pfa input myModel
record(Input,
       x1: string,
       x2: union(null,
                 double))
```

```
PFA-Inspector> pfa output myModel
record(Output,
       winner: string,
       breakdown: map(double))
```

```
PFA-Inspector> pfa types myModel
Derived:
    record(Derived,
           x1: string,
           x2: double)

Fields:
    enum([x1, x2], Fields)

Input:
    record(Input,
           x1: string,
           x2: union(null,
                     double))

Output:
    record(Output,
           winner: string,
           breakdown: map(double))

RunningAverage:
    record(RunningAverage,
           mean: double)

TreeNode:
    record(TreeNode,
           field: enum([x1, x2], Fields),
           operator: string,
           value: union(array(string),
                        double),
           pass: union(TreeNode,
                       string),
           fail: union(TreeNode,
                       string))
```

```
PFA-Inspector> pfa calls myModel
(action): (string), /, a.count, a.len, a.map, a.mode, attr, cell, let, model.tree.simpleTest, model.tree.simpleWalk, new (object), s.lower, u.imputeX2
(begin): 
(end): 
u.imputeX2: (double), (string), cell, cell-to, do, ifnotnull, stat.sample.updateEWMA
```
