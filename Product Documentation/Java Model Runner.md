---
title: "Java Model Runner"
excerpt: "New in v1.5!"
---
Beginning with v1.5, FastScore supports models written in the Java language. This includes the following types of models:

* Generic Java code
* POJOs exported from H2O
* Spark MLLib models

This page describes how to load and run models in each of these cases. 

# Generic Java models

A generic Java model can execute arbitrary Java code. In order to run this model in FastScore, it must implement a particular model interface: the `IJavaModel` interface. This interface includes `begin`, `action`, and `end` methods, analogous to Python and R models. 
[block:code]
{
  "codes": [
    {
      "code": "import fastscore.IJavaModel;\n\npublic class MyModel implements IJavaModel \n{\n  \n  public void begin()\n  {\n    ...\n  }\n  \n  public String action(String datum)\n  {\n    ...\n  }\n  \n  public void end()\n  {\n    ...\n  }\n  \n}",
      "language": "java",
      "name": "Generic Java Model"
    }
  ]
}
[/block]
# H2O Models

Although an H2O model can be structured as a generic Java model, FastScore also provides a convenience feature to allow direct import of H2O models. In order to use this feature, take the following steps:

1. Save your model as POJO (following the [POJO quick start instructions from H2O](https://h2o-release.s3.amazonaws.com/h2o/rel-turing/1/docs-website/h2o-docs/pojo-quick-start.html)). Without further modifications, this exported POJO can be used as the model code in FastScore.
2. To load the model in FastScore, ensure that the model name exactly matches the exported POJO class name, and explicitly specify the model type as "`h2o`":

```
fastscore model add gbm_pojo_test gbm_pojo_test.java -type:h2o
```

When running H2O models, FastScore will output the original input record appended with an additional "Result" field that represents an array of prediction results. For example, in H2O's GBM airlines sample model, the input and output will be:

Input JSON record:
```
{ "Year": "2017", "Month": "06", "DayofMonth": "04", "DayOfWeek": "7", "CRSDepTime": "1030", "UniqueCarrier": "PS", "Origin": "SAN", "Dest": "ORD"}
```

Output JSON record:
```
{"CRSDepTime":"1030","Origin":"SAN","Month":"06","DayOfWeek":"7","Dest":"ORD","Year":"2017","UniqueCarrier":"PS","DayofMonth":"04","Result":["YES"]}
````

Note that the original order of the fields may not be preserved in the output record.

# Spark MLLib models

FastScore v1.5 includes integrated Apache Spark libraries (2.1.1) and allows adding models that leverage Spark MLLib. You can safely use Java import statements for required Spark packages in your model code. 

A Spark model must follow the same conformance guidelines as a generic Java model, and any previously saved model files/folders (Parquet format) must be added as a model attachment. In general, the model will perform Spark context initialization in the `begin()` method.

Here is an example Spark model that assumes that the `LogisticRegressionModel` was previously created and saved under the `scalaLogisticRegressionWithBFGSModel` folder and then uploaded to FastScore as an attachment.
[block:code]
{
  "codes": [
    {
      "code": "import fastscore.IJavaModel;\nimport org.apache.spark.SparkConf;\nimport org.apache.spark.SparkContext;\nimport org.apache.spark.sql.SparkSession;\nimport org.json.JSONObject;\nimport org.json.JSONTokener;\nimport org.apache.spark.mllib.classification.LogisticRegressionModel;\nimport org.apache.spark.mllib.linalg.Vector;\nimport org.apache.spark.mllib.linalg.Vectors;\n \npublic class MLLibLRModel implements IJavaModel {\n     \n    LogisticRegressionModel _lrModel;\n     \n    public MLLibLRModel() {\n        System.out.println(\"MLLib Linear Regression model\");\n    }\n     \n    public void begin() {\n        SparkConf conf = new SparkConf();\n        conf.setAppName(\"ML Lib LR Model\");\n        conf.setMaster(\"local\");\n        conf.set(\"spark.driver.host\", \"127.0.0.1\");\n        SparkSession spark = SparkSession.builder().config(conf).getOrCreate();\n        SparkContext sc = spark.sparkContext();\n                 \n        _lrModel = LogisticRegressionModel.load(sc, \"scalaLogisticRegressionWithLBFGSModel\");\n \n    }\n     \n    public String action(String datum) {\n        try {\n            Vector dv = Vectors.fromJson(datum);\n            double res = _lrModel.predict(dv);\n         \n            JSONObject jsonObj = new JSONObject(new JSONTokener(datum));\n            jsonObj.append(\"Prediction\", res);\n         \n            return jsonObj.toString();\n        } catch (Exception e) {\n            return e.toString();\n        }\n         \n    }\n     \n    public void end() {\n         \n    }\n}",
      "language": "java",
      "name": "MLLibLRModel.java"
    }
  ]
}
[/block]
To add this model to FastScore, run the following commands:
```
tar czvf scalaLogisticRegressionWithLBFGSModel.tar.gz scalaLogisticRegressionWithLBFGSModel/
fastscore model add MLLibLRModel MLLibLRModel.java
fastscore attachment upload MLLibLRModel scalaLogisticRegressionWithLBFGSModel.tar.gz
```

# JARs

If the Java model requires one or more JAR files, supply them together with any other required files as a single ZIP or .tar.gz attachment. The Java runner will add all supplied JARs into the class path during compilation and runtime, so the model may safely import any required packages from these JARs.

# Stream Encoding

In v1.5, the Java runner only supports JSON encoding for input/output streams.