Titus's **pfainspector** is a commandline-driven environment for exploring PFA files, modeled on the GnuPlot interface. Users can explore a PFA document and make basic alterations using subcommands arranged in "gadgets."

It uses Gnu readline for history and tab-completion, which makes it a more productive tool for these sorts of operations than a GUI.

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.8.3; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

and download [myModel.pfa](https://github.com/opendatagroup/hadrian/wiki/model/myModel.pfa).

## Command-line arguments

The pfainspector is primarily driven by commands within its own environment, so it doesn't have many command-line arguments. If any PFA files are provided on the command-line, they will initiate `load` commands within the environment to quickly load those files.

```
% pfainspector myModel.pfa
Titus PFA Inspector (version 0.8.3)
Type 'help' for a list of commands.
load myModel.pfa as myModel
PFA-Inspector> 
```

is the same as starting `pfainspector` from the shell and typing `load myModel.pfa as myModel` within the environment.

## Help system

Start by typing `help`. This shows you names and short descriptions of all the commands.

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
```

The two gadgets, `json` and `pfa`, are packages of sub-commands (more will be added in the future).

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
    externalize          turn an embedded cell or pool into an external one
    internalize          turn an external cell or pool into an embedded one
```

The full syntax of each command is given in its individual help.

```
PFA-Inspector> load help
read a PFA file into the current context, possibly naming it
    load <file-path> as <name>
```

## Tab completion

Tab completion is context-sensitive. Type `load ` and press tab. You should see the directories in your filesystem because the first argument after `load` is a file path. You can "ride the tab key" all the way into the appropriate subdirectory, which is a very efficient way to find files. If you type a space after the file path, tab auto-completes `as` because `as` is the next word in this command.

When the cursor is located after a JSON command like `json look `, it tabs through the files that have already been loaded. (The `json look` command calls [Titus's look function](Titus-PFA-navigation#navigation-tools-in-titus) for browsing the structure of a JSON file). Another tab adds an open bracket ('[') and the top-level fields of the PFA file.

```
PFA-Inspector> json look myModel[
action,   cells,    fcns,     input,    output]   
```

This allows you to "ride the tab key" through the PFA file, just as you would a filesystem. The comma (`,`) versus closing bracket (`]`) tells you whether a node is a leaf. In defining a path, you can be lazy and not quote strings (unless they have bad characters) and leave a terminal comma, etc.

```
PFA-Inspector> json look myModel[cells, forest, init, 29, ]
index                          data
------------------------------------------------------------
                               {
operator                         "operator": "<=",
field                            "field": "x2",
fail                             "fail": {"string": "good"},
value                            "value": {"double": 31.1002236950619},
pass                             "pass": {
pass,TreeNode                      "TreeNode": {
pass,TreeNode,operator               "operator": "<=",
pass,TreeNode,field                  "field": "x2",
pass,TreeNode,fail                   "fail": {
pass,TreeNode,fail,TreeNode            "TreeNode": {
pass,TreeNode,fail,TreeNode...           "operator": "in",
pass,TreeNode,fail,TreeNode...           "field": "x1",
pass,TreeNode,fail,TreeNode...           "fail": {"string": "bad"},
pass,TreeNode,fail,TreeNode...           "value": {"array": ["three"]},
pass,TreeNode,fail,TreeNode...           "pass": {"string": "good"}
                                       }
                                     },
pass,TreeNode,value                  "value": {"double": 7.26247432127833},
pass,TreeNode,pass                   "pass": {
pass,TreeNode,pass,TreeNode            "TreeNode": {
pass,TreeNode,pass,TreeNode...           "operator": "in",
pass,TreeNode,pass,TreeNode...           "field": "x1",
pass,TreeNode,pass,TreeNode...           "fail": {"string": "bad"},
pass,TreeNode,pass,TreeNode...           "value": {"array": ["three"]},
pass,TreeNode,pass,TreeNode...           "pass": {"string": "good"}
                                       }
                                     }
                                   }
                                 }
                               }
```

Options, like `indexWidth` and `maxDepth` come after the closing bracket. (Use tab-complete to get a list of them.)

## Overview of features

The pfainspector is extensible, with additional gadgets expected in the future. PFA files only need to be valid JSON to be loaded, so the pfainspector could be used to explore JSON data as well (as long as the JSON file contains only one JSON object, not one-JSON-per-line).

The pfainspector environment holds PFA files in memory with short names (type `list` to see them) that can be modified and written back to the filesystem (with `save`).

The `json` gadget uses [JSON regular expressions](JSON-Regular-Expressions) to search, count, and change substructures within a JSON file.

The `pfa` gadget can

   * verify the validity of a PFA file
   * show input and output schemas (in [PrettyPFA](PrettyPFA-Reference) and Avro notation)
   * list all types, user defined functions, cells, and pools defined in a PFA document
   * navigate the [call graph](Hadrian-Analyzing-Engine#call-graph)
   * externalize or internalize large model parameters from a PFA file. This method is complementary to the [pfaexternalize script](Titus-pfaexternalize) because it loads the whole PFA file into memory before operating on it, whereas pfaexternalize streams through it. Loading the file into memory is faster if it is possible, if the file is small enough.
