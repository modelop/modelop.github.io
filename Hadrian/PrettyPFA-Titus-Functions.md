The `titus.prettypfa` module has functions for generating PFA at any stage of its life cycle.

  * `json(ppfa, lineNumbers=True, check=True)`: construct JSON text from PrettyPFA text `ppfa`.  If           `lineNumbers` is `False`, don't include line numbers.  If `check` is `False`, don't verify that the resulting PFA is syntactically and semantically valid.  This can be useful for generating invalid PFA that is later     made valid by inserting a subtree.
  * `jsonNode(ppfa, lineNumbers=True, check=True)`: construct a Python dictionary of Python lists, strings,   and numbers from PrettyPFA text `ppfa`.  This form can be immediately modified by a Python algorithm.
  * `ast(ppfa, check=True)`: construct an abstract syntax tree from PrettyPFA text `ppfa`.  This tree is a    suite of nested specialized class instances for each PFA form.  It can be used for modifications of the PFA   that require more knowledge of the tree's structure.
  * `engine(ppfa, options=None, sharedState=None, multiplicity=1, style="pure", debug=False)`: construct a    list of executable scoring engines from PrettyPFA text `ppfa`.  The other options are the same as `titus.     genpy.PFAEngine.fromJson`.

Also, you may have noticed that the input and output type specifications in PrettyPFA are not Avro schema,    unlike PFA.  The intention is to make them easier to write.  However, some datasets already have conventional Avro schema, so Titus has a function to convert Avro schema to PrettyPFA snippets.

  * `avscToPretty(avsc, indent=0)`: construct a PrettyPFA text snippet from `avsc`, which is a Python         dictionary of Python lists, strings, and numbers, representing an Avro schema.  The `indent` is the starting  indentation level.

If your Avro schema is stored in a file, you can use:

    >>> import json
    >>> avscToPretty(json.load(open(fileName)))
