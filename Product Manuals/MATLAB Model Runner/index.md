# Matlab (Octave) Model Runner
1.6 introduces new model runner: Octave. This allows execution of Matlab models within ModelOp Center as long as toolboxes and statements used are supported by Octave.


A few rules to conform when creating Matlab model to run in ModelOp Center:

* All statements should reside within a function body inside .m file (with same name as your function)
* ModelOp Center model name should match the name of model file (without .m extension)
* If you need to perform one time initialization (such as loading data into global variables to be used throughout the model execution), you need to prepare a separate begin.m file and add it to your model as part of compressed attachment; for example, this is how you would make data loaded from attached CSV file available to the model:
``` 
function f = begin()
    global Data
    Data = csvread("data.csv");
    f = 0;
```
The above code should be placed into begin.m, packaged along with data.csv and uploaded to your model:
``` bash
$ tar czf model_att.tar.gz begin.m data.csv
# assuming that MatlabCalc already exists
$ fastscore attachment upload MatlabCalc model_att.tar.gz
```
ModelOp Center will detect the presence of begin.m file and will run prior to executing the MatlabCalc model, but in the same Octave session making global data accessible by the model.

## Stream Encoding
Octave runner only supports JSON encoding for input/output streams.

## Example
Malab / Octave code is optimized to work with matrix data. As such, it will be often required to pass a matrix as model input. The following simple example shows how to implement Eigen vector calculation with ModelOp Center leveraging Octave runner.

* Create eigen.m file with the following code:
```
function EV = eigen(A)
    % Calculate eigen values
    EV = eig(A)
```

* Load model into ModelOp Center and make sure it is listed as Octave:
``` bash
$ fastscore model add eigen eigen.m
$ fastscore model list
Name       Type
---------  ------
eigen      Octave
```

* Input data representing 2 records of 3x3 matrixes should look as following adhering to JSON encoding (please refer to streams documentation on how to configure input / output streams for ModelOp Center):
``` json
[[1, 7, 3], [2, 9, 12], [5, 22, 7]]
[[2, 13, 5], [2, 9, 12], [5, 44, 7]]
```

* Results of scoring will then be 3 eigen vectors per matrix in a similar format:
``` json
[[25.554838634290714], [-0.5789337929080558], [-7.975904841382665]]
[[32.694332616156586], [0.23962844553789128], [-14.933961061694498]]
```