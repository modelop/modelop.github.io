# Basic scorecard

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.7.1; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Launch a Python prompt and import the following:

    Python 2.7.6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import numpy
    >>> 
    >>> import titus.prettypfa
    >>> from titus.genpy import PFAEngine

## The basic form

PFA does not have a dedicated scorecard library because scorecards are both simple to evaluate using primitives and hard to generalize. This example uses extremely heterogeneous data types, including missing values (unions with `null`) and custom enumerations, and the model data is in the code block, rather than a cell. A more homogeneous scorecard could be relegated to a cell. It all depends on what your needs are.

```python
pfaDocument = titus.prettypfa.jsonNode('''
metadata:
  {source: "National Stroke Foundation",
   url: "http://www.stroke.org/stroke-resources/resource-library/stroke-risk-scorecard"}
types:
  Input = record(Input,
                 blood_pressure:      double,
                 atrial_fibrillation: union(null, boolean),   // true, false, or null (unknown)
                 smoking:             union(null, boolean),
                 cholesterol:         union(null, double),
                 diabetes:            enum([yes, borderline, no], Diabetes),
                 physical_activity:   enum([none, weekly, more], PhysicalActivity),
                 weight:              enum([overweight, slightly, healthy], Weight),
                 stroke_in_family:    union(null, boolean))
input: Input
output: enum([high, caution, low], Risk)
action:
  var high = 0;
  var caution = 0;
  var low = 0;

  if (input.blood_pressure >= 140.0)
    high = high + 1
  else if (input.blood_pressure >= 120.0)
    caution = caution + 1
  else
    low = low + 1;

  ifnotnull(atrial_fibrillation: input.atrial_fibrillation) {
    if (atrial_fibrillation)
      high = high + 1
    else
      low = low + 1
  }
  else
    caution = caution + 1;

  ifnotnull(smoking: input.smoking) {
    if (smoking)
      high = high + 1
    else
      low = low + 1
  }
  else
    caution = caution + 1;

  ifnotnull(cholesterol: input.cholesterol) {
    if (cholesterol >= 240.0)
      high = high + 1
    else if (cholesterol >= 200.0)
      caution = caution + 1
    else
      low = low + 1
  }
  else
    high = high + 1;

  if (input.diabetes == Diabetes@yes)
    high = high + 1
  else if (input.diabetes == Diabetes@borderline)
    caution = caution + 1
  else
    low = low + 1;

  if (input.physical_activity == PhysicalActivity@none)
    high = high + 1
  else if (input.physical_activity == PhysicalActivity@weekly)
    caution = caution + 1
  else
    low = low + 1;

  if (input.weight == Weight@overweight)
    high = high + 1
  else if (input.weight == Weight@slightly)
    caution = caution + 1
  else
    low = low + 1;

  ifnotnull(stroke_in_family: input.stroke_in_family) {
    if (stroke_in_family)
      high = high + 1
    else
      low = low + 1
  }
  else
    caution = caution + 1;

  if (high > caution  &&  high > low)
    Risk@high
  else if (low > caution  &&  low > high)
    Risk@low
  else
    Risk@caution
''')
```

## Test it!

Let's try every possible value in the space.

```python
engine, = PFAEngine.fromJson(pfaDocument)

for blood_pressure in 150.0, 130.0, 110.0:
    for atrial_fibrillation in {"boolean": True}, None, {"boolean": False}:
        for smoking in {"boolean": True}, None, {"boolean": False}:
            for cholesterol in None, {"double": 210.0}, {"double": 190.0}:
                for diabetes in "yes", "borderline", "no":
                    for physical_activity in "none", "weekly", "more":
                        for weight in "overweight", "slightly", "healthy":
                            for stroke_in_family in {"boolean": True}, None, {"boolean": False}:
                                print engine.action({"blood_pressure": blood_pressure,
                                                     "atrial_fibrillation": atrial_fibrillation,
                                                     "smoking": smoking,
                                                     "cholesterol": cholesterol,
                                                     "diabetes": diabetes,
                                                     "physical_activity": physical_activity,
                                                     "weight": weight,
                                                     "stroke_in_family": stroke_in_family})
```
