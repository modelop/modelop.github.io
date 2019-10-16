## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.5.14; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import `titus.prettypfa`:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import titus.prettypfa as prettypfa

## Simple example

Here is a scoring engine that applies the quadratic formula to input:

    >>> pfa = prettypfa.json('''
    input: record(a: double, b: double, c: double)
    output: union(null,
                  record(Output,
                         solution1: double,
                         solution2: double))
    action:
      var a = input.a, b = input.b, c = input.c;

      var discriminant = b**2 - 4*a*c;
      if (discriminant >= 0.0) {
        // if there are any real solutions, return them
        var x1 = -b + m.sqrt(discriminant)/(2*a);
        var x2 = -b - m.sqrt(discriminant)/(2*a);
        new(Output, solution1: x1, solution2: x2)
      }
      else
        // otherwise, return null (N/A)        
        null
    ''')

Note that binary operators such as `+` and `-` are expressed with familiar infix notation (between the things they add or subtract) and the `if` statement looks like something from a C program.

The corresponding PFA is harder to read (especially if it isn't pretty-printed):

    >>> print pfa
    {"@": "PrettyPFA document", "name": "Engine_1", "input": {"fields": [{"type": "double", "name": "a"},     {"type": "double", "name": "b"}, {"type": "double", "name": "c"}], "type": "record", "name": "Record_63"},    "output": ["null", {"fields": [{"type": "double", "name": "solution1"}, {"type": "double", "name":            "solution2"}], "type": "record", "name": "Output"}], "method": "map", "action": [{"@": "PrettyPFA line 8",    "let": {"a": {"@": "PrettyPFA line 8", "attr": "input", "path": [{"@": "PrettyPFA line 8", "string": "a"}]},  "c": {"@": "PrettyPFA line 8", "attr": "input", "path": [{"@": "PrettyPFA line 8", "string": "c"}]}, "b": {"@ ": "PrettyPFA line 8", "attr": "input", "path": [{"@": "PrettyPFA line 8", "string": "b"}]}}}, {"@":          "PrettyPFA line 10", "let": {"discriminant": {"@": "PrettyPFA line 10", "-": [{"@": "PrettyPFA line 10", "**  ": ["b", 2]}, {"@": "PrettyPFA line 10", "*": [{"@": "PrettyPFA line 10", "*": [4, "a"]}, "c"]}]}}}, {"@":    "PrettyPFA lines 11-19", "if": {"@": "PrettyPFA line 11", ">=": ["discriminant", 0.0]}, "then": [{"@":        "PrettyPFA line 13", "let": {"x1": {"@": "PrettyPFA line 13", "+": [{"@": "PrettyPFA line 13", "u-": ["b"]},  {"@": "PrettyPFA line 13", "/": [{"@": "PrettyPFA line 13", "m.sqrt": ["discriminant"]}, {"@": "PrettyPFA     line 13", "*": [2, "a"]}]}]}}}, {"@": "PrettyPFA line 14", "let": {"x2": {"@": "PrettyPFA line 14", "-": [{"@ ": "PrettyPFA line 14", "u-": ["b"]}, {"@": "PrettyPFA line 14", "/": [{"@": "PrettyPFA line 14", "m.sqrt":   ["discriminant"]}, {"@": "PrettyPFA line 14", "*": [2, "a"]}]}]}}}, {"@": "PrettyPFA line 15", "type":        "Output", "new": {"solution2": "x2", "solution1": "x1"}}], "else": [null]}]}

The `"@": "PrettyPFA line ..."` key-value pairs pass the source file line numbers to later stages of          processing, so that error messages can point back to lines in the original source file.

This PFA document is ready to be used as a scoring engine.  You can test it in the usual way:

    >>> import titus.genpy
    >>> engine, = titus.genpy.PFAEngine.fromJson(pfa)
    >>> print engine.action({"a": 1, "b": 8, "c": 4})
    {'solution1': -4.535898384862246, 'solution2': -11.464101615137753}
    >>> print engine.action({"a": 1, "b": 2, "c": 3})
    None

See the [realistic example](PrettyPFA-Realistic-Example) for an example of data processing.
