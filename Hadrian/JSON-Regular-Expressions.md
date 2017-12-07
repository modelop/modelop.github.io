## Motivation

Since PFA is JSON, it is easier to inspect, build, or edit if you have good tools for manipulating JSON. JSON is represented in Python as `None`, `True`, `False`, integers, floating-point numbers, strings, Python lists of the above, and Python dictionaries of the above. Titus's "JSON regular expressions" provide a declarative language for manipulating these structures.

"JSON regular expressions" work like regular expressions for text, except that they apply to tree structures, rather than substrings of text. The `titus.producer.tools` library provides classes for defining patterns, performing JSON-tree searches using those patterns, and using pattern-matches for extractions or modifications.

Keep in mind that, despite the name, these "regular expressions" are _not_ matching the string representation of the JSON, but the Python structure (effectively a DOM).

## JSON patterns

When you do `from titus.producer.tools import *`, you get a Python-based DSL for pattern matching. The [pfainspector](Titus-pfainspector) goes one step further and provides a shorter, regex-inspired syntax for the same pattern matching functions. The table below shows all of the patterns and their pfainspector equivalents.

| Python class | Example | pfainspector syntax | Matches |
|:-------------|:--------|:--------------------|:--------|
| NoneType | `None` | `null` | `null` and only `null` |
| bool | `True`, `False` | `true`, `false` | only `true` and `false` |
| int | `123` | `123` | exact number in JSON |
| float | `3.14` | `3.14` | exact number in JSON |
| str | `"hello"` | `"hello"` | exact string in JSON |
| list | `[1, True, "hello"]` | `[1, true, "hello"]` | exact array in JSON, may contain non-trivial patterns |
| dict | `{"one": 1, "two": None}` | `{one: 1, "two": null}` | exact object in JSON, may contain non-trivial patterns in the _values_ (not _keys_) |
| Any | `Any()` | `_` _(underscore)_ | anything: any structure or leaf node |
|     | `Any(int, str)` | _(no equivalent)_ | specified Python classes |
|     | `Any(int, long, float)` | `#` _(hash sign)_ | any number |
| LT | `LT(3.14)` | `# < 3.14` | number less than specified value |
| LE | `LE(3.14)` | `# <= 3.14` | number less than or equal to specified value |
| GT | `GT(3.14)` | `# > 3.14` | number greater than specified value |
| GE | `GE(3.14)` | `# >= 3.14` | number greater than or equal to specified value |
| Approx | `Approx(3.14, 0.01)` | `3.14 +- 0.01` | number with a two-sided range |
| RegEx | `RegEx("some.*string")` | `/some.*string/` | strings by (ordinary) regular expression with [Python regex syntax](https://docs.python.org/2/library/re.html#regular-expression-syntax) |
|       | `RegEx("some.*string", flags="i")` | `/some.*string/i` | Python regular expression [flags](https://docs.python.org/2/library/re.html#re.I) |
|       | `RegEx("from", "to")` | `/from/to/` | regular expression with replacement text (only used by functions that change the JSON) |
| Start | `Start(1, 2, 3)` | `[1, 2, 3, ...]` | JSON array that begins with specified values, may contain non-trivial patterns |
| End | `End(8, 9, 10)` | `[..., 8, 9, 10]` | JSON array that ends with specified values, may contain non-trivial patterns |
| Min | `Min(key1=value1, key2=value2)` | `{key1: value1, "key2": value2, ...}` | JSON object that contains _at least_ a given set of key-value pairs, which may contain non-trivial _values_ (not _keys_) |
| Group | `Group(name=pattern)` | `(pattern)` | associates a pattern with a given name in Python or number in pfainspector (matched patterns are labeled by numbers starting with 1) |
| Or | `Or(p1, p2, p3)` | `(p1 | p2 | p3)` | matches if any sub-pattern matches (pfainspector needs group) |
| And | `And(p1, p2, p3)` | `(p1 & p2 & p3)` | matches if all sub-patterns match (pfainspector needs group) |

Among these pattern elements, the most useful tend to be the explicit match (`None`, `True`, `False`, numbers, strings, Python lists and dicts), `Min`, and `Any`. Many PFA structures are JSON objects with a few known keys, the rest unknown, so `Min` is disproportionately useful. `Any` is often used as an easy (if under-specified) placeholder.

## Functions that use patterns

The `json` gadget of the pfainspector uses JSON patterns in the `count`, `index`, `find`, and `change` subcommands (see pfainspector help text for details).

The `titus.producer.tools` package defines the following functions that use patterns.

   * `search(pattern, haystack)` returns a generator that yields `(index, Match)` pairs. That is, if you do

         for i, m in search({"+": [2, 2]}, pfaDocument):
             print i, m

      you will print out indexes like `('action', 3, 'log', '+')` and `Match` objects. If you do

          list(search({"+": [2, 2]}, pfaDocument))

      you'll get a list of all of them at once. `Match` objects have an `original` field with a copy of the matched structure, a `modified` field with `RegEx` substitutions (if any), and a `groups` field that provides a dict from `Group` name to matched groups within the original match.

   * `searchFirst(pattern, haystack)` returns the first such pair or `None` if there weren't any.

   * `index(pattern, haystack)` returns the index only (or `None`). This index is a tuple describing a path through the JSON tree from root to the desired element.

   * `indexes(pattern, haystack)` returns a generator that yields indexes.

   * `contains(pattern, haystack)` returns `True` or `False`, only reporting whether the pattern exists in the `haystack`.

   * `count(pattern, haystack)` returns the number of occurrences of the pattern in the `haystack`. Note that if a pattern matches a structure and also substructures within it, generators will iterate over both cases and this function will count both of them.

   * `findRef(pattern, haystack)` returns the actual Python reference--- not a copy--- of the matched object. Having a reference allows you to change objects in place, like this:

         findRef({"+": [2, 2]}, pfaDocument)["+"] = [3, 3]

     to change `2 + 2` into `3 + 3`.

   * `findCopy(pattern, haystack)` returns a deep copy that has no dependence on the original Python structure. Changing this copy in-place does not alter the original.

   * `findAllRef(pattern, haystack)` returns a generator that iterates over references. For instance,

         for ref in findAllRef({"+": [2, 2]}, pfaDocument):
             ref["+"] = [3, 3]

     changes all instances of `2 + 2` into `3 + 3`.

    * `findAllCopy(pattern, haystack)` returns a generator that iterates over copies.

In practice, the most useful functions are `findRef` and `findAllRef`, since you'll usually be looking for a placeholder structure in a PFA document and wanting to replace it with real values. The next most common are `index` and `indexes`, which allow for navigation to the parent of a node.

## Index functions

The same `titus.producer.tools` module has functions for working with indexes. The indexes returned by the above are tuples naming a path from the JSON root to the desired element, such as `('action', 3, 'log', '+')`, which could be extracted from the original haystack with

    haystack["action"][3]["log"]["+"]

However, this is cumbersome. The following functions simplify access.

   * `get(haystack, index)` returns a reference to the element, given an index (unpacking each level for you).

   * `assign(haystack, index, replacement)` changes an object in-place (like assignment, but using the tuple-index).

   * `assigned(haystack, index, replacement)` returns a modified copy of the whole structure without affecting the original.

   * `assignAt(pattern, haystack, replacement)` performs an in-place `assign` at every index implied by the `pattern`.

   * `assignedAt(pattern, haystack, replacement)` returns an `assigned` copy at every index implied by the `pattern`.

   * `remove(haystack, index)` removes an element at the given index in-place.

   * `removed(haystack, index)` returns a modified copy of the whole structure without affecting the original.
