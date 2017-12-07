Titus's **pfaexternalize** script extracts a cell or pool from a PFA file and puts it in an external JSON file. This decoupling can be used to

   * make it easier to change model parameters or initial values with an external tool,
   * make it easier to load a PFA model (since the data type of the cell/pool is known before loading it, a potentially cumbersome step may be skipped),
   * update persistent state by "reseting" the PFA scoring engine with changes in the external file,
   * simply reduce the size of the "active" part of a PFA model so that it can be opened in a text editor, JSON pretty-printer, [pfainspector](Titus-pfainspector), or other tool.

## Before you begin...

[Download and install Titus](Installation#case-4-you-want-to-install-titus-in-python).  This article was tested with Titus 0.8.3; newer versions should work with no modification.  Python >= 2.6 and < 3.0 is required.

Install the third-party library [ijson](https://pypi.python.org/pypi/ijson). If you have `python-setuptools` (recommended for installing Titus), then you can

    sudo easy_install ijson

## Help document

A good place to start is pfaexternalize's own help text, which will always show the latest options.

```
usage: pfaexternalize [-h] [--progress] [--verbose] [input] [output]

Extract model data from specified cells and pools and put them in external files.

positional arguments:
  input       input PFA file, "-" for standard in
  output      output PFA file, "-" for standard out

optional arguments:
  -h, --help  show this help message and exit
  --progress  report progress by first scanning over the input to determine
              its size (incompatible with standard in)
  --verbose   write progress messages to standard error (implied by
              --progress)

  --cell-NAME externalize cell NAME by extracting its data to NAME.json
  --cell-NAME=FILENAME
              externalize cell NAME to FILENAME

  --pool-NAME externalize pool NAME to NAME.json
  --pool-NAME=FILENAME
              externalize pool NAME to FILENAME
```

## Examples

The following removes a cell named "tree" from `hipparcos_numerical_10.pfa` and moves it to a file named `tree.json`.

```
% pfaexternalize hipparcos_numerical_10.pfa hipparcos_externalized.pfa --cell-tree --progress
Reading from hipparcos_numerical_10.pfa
First pass determines JSON object size (takes about 10 secs per GB)
Input contains 3105 objects/arrays; reopening to perform transformation
Extracting model to hipparcos_externalized.pfa
Extracting cell init to tree.json                                 
Return to model                                                    
|**************************************************| 100% in 0 secs
Finished transforming JSON after 0.24 secs
```

The following throws away the tree data (sending it to file `/dev/null`) and uses the `--verbose` option (single-pass description of steps), rather than `--progress` (first pass determines size, second pass animates progress bar).

```
% pfaexternalize hipparcos_numerical_10.pfa hipparcos_externalized.pfa --cell-tree=/dev/null --verbose 
Reading from hipparcos_numerical_10.pfa
Extracting model to hipparcos_externalized.pfa
Extracting cell init to /dev/null
Return to model
Finished transforming JSON after 0.22 secs
```

Multiple cells and pools can be extracted at once by passing multiple `--cell-XXX` or `--pool-XXX` arguments. The names of the cells and pools must be known.

## Alternative method

The pfaexternalize script streams a PFA file on the assumption that it is too large to load into memory. Although this makes it possible to act on files of arbitrarily large size, it is slower than loading the whole file into memory before performing the operation. For that case, use the [pfainspector](Titus-pfainspector#overview-of-features) command-line tool to perform the conversion by hand.
