---
title: "Java Model Runner"
excerpt: "New in v1.5!"
---
# Java Model Runner

Beginning with v1.5, ModelOp Center supports models written in the Java language. This includes the following types of models:

* Generic Java code
* POJOs exported from H2O
* Spark MLLib models

This page describes how to load and run models in each of these cases. 

## Generic Java models

A generic Java model can execute arbitrary Java code. In order to run this model in ModelOp Center, it must implement a particular model interface: the `IJavaModel` interface. This interface includes `begin`, `action`, and `end` methods, analogous to Python and R models. 

``` java
import fastscore.IJavaModel;

public class MyModel implements IJavaModel 
{
  
  public void begin()
  {
  ...
  }
  
  public String action(String datum)
  {
  ...
  }
  
  public void end()
  {
  ...
  }
  
}
```

## H2O Models

Although an H2O model can be structured as a generic Java model, ModelOp Center also provides a convenience feature to allow direct import of H2O models. In order to use this feature, take the following steps:

1. Save your model as POJO (following the [POJO quick start instructions from H2O](https://h2o-release.s3.amazonaws.com/h2o/rel-turing/1/docs-website/h2o-docs/pojo-quick-start.html)). Without further modifications, this exported POJO can be used as the model code in ModelOp Center.
2. To load the model in ModelOp Center, ensure that the model name exactly matches the exported POJO class name, and explicitly specify the model type as "`h2o-java`":

```
fastscore model add gbm_pojo_test gbm_pojo_test.java -type:h2o-java
```

When running H2O models, ModelOp Center will output the original input record appended with an additional "Result" field that represents an array of prediction results. For example, in H2O's GBM airlines sample model, the input and output will be:

Input JSON record:

```
{ "Year": "2017", "Month": "06", "DayofMonth": "04", "DayOfWeek": "7", "CRSDepTime": "1030", "UniqueCarrier": "PS", "Origin": "SAN", "Dest": "ORD"}
```

Output JSON record:

```
{"CRSDepTime":"1030","Origin":"SAN","Month":"06","DayOfWeek":"7","Dest":"ORD","Year":"2017","UniqueCarrier":"PS","DayofMonth":"04","Result":["YES"]}
````

Note that the original order of the fields may not be preserved in the output record.

## Spark MLLib models

ModelOp Center v1.5 includes integrated Apache Spark libraries (2.1.1) and allows adding models that leverage Spark MLLib. You can safely use Java import statements for required Spark packages in your model code. 

A Spark model must follow the same conformance guidelines as a generic Java model, and any previously saved model files/folders (Parquet format) must be added as a model attachment. In general, the model will perform Spark context initialization in the `begin()` method.

Here is an example Spark model that assumes that the `LogisticRegressionModel` was previously created and saved under the `scalaLogisticRegressionWithBFGSModel` folder and then uploaded to ModelOp Center as an attachment.

``` java
import fastscore.IJavaModel;
import org.apache.spark.SparkConf;
import org.apache.spark.SparkContext;
import org.apache.spark.sql.SparkSession;
import org.json.JSONObject;
import org.json.JSONTokener;
import org.apache.spark.mllib.classification.LogisticRegressionModel;
import org.apache.spark.mllib.linalg.Vector;
import org.apache.spark.mllib.linalg.Vectors;

public class MLLibLRModel implements IJavaModel {
     
    LogisticRegressionModel _lrModel;

    public MLLibLRModel() {
        System.out.println("MLLib Linear Regression model");
    }
    
    public void begin() {
        SparkConf conf = new SparkConf();
        conf.setAppName("ML Lib LR Model");
        conf.setMaster("local");
        conf.set("spark.driver.host", "127.0.0.1");
        SparkSession spark = SparkSession.builder().config(conf).getOrCreate();
        SparkContext sc = spark.sparkContext();
        
        _lrModel = LogisticRegressionModel.load(sc, "scalaLogisticRegressionWithLBFGSModel");
        
    }
        
    public String action(String datum) {
        try {
            Vector dv = Vectors.fromJson(datum);
            double res = _lrModel.predict(dv);
        
            JSONObject jsonObj = new JSONObject(new JSONTokener(datum));
            jsonObj.append("Prediction", res);
        
            return jsonObj.toString();
        } catch (Exception e) {
            return e.toString();
        }
    
    }
     
    public void end() {
         
    }
}
```

To add this model to ModelOp Center, run the following commands:

```
tar czvf scalaLogisticRegressionWithLBFGSModel.tar.gz scalaLogisticRegressionWithLBFGSModel/
fastscore model add MLLibLRModel MLLibLRModel.java
fastscore attachment upload MLLibLRModel scalaLogisticRegressionWithLBFGSModel.tar.gz
```

## JARs

If the Java model requires one or more JAR files, supply them together with any other required files as a single ZIP or .tar.gz attachment. The Java runner will add all supplied JARs into the class path during compilation and runtime, so the model may safely import any required packages from these JARs.

## Stream Encoding

Currently, the Java runner only supports JSON and CSV encoding for input/output streams.
