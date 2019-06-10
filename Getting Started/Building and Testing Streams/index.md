title: "Build and Testing a Stream"
description: "This is a step by step guide for conforming and deploying a model in FastScore. It contains instructions for data scientists to prepare, deploy and test their model. This guide was last updated for v1.10 of FastScore.\n\nIf you need support or have questions, please email us:  [support@opendatagroup.com](mailto:support@opendatagroup.com)"
---

# Conform and deploying a Model
This is a step by step guide for building and test streams in FastScore. It contains instructions for Data and ModelOps engineer to define and test the integration of a model with the data pipeline. This guide was last updated for v1.10 of FastScore. 

As we go, we will be referring to an example XGBoost model available in the `examples` branch of this repo (https://github.com/opendatagroup/Getting-Started/tree/examples).

If you need support or have questions, please email us: support@opendatagroup.com

# Contents

1. [Pre-requisites](#Prerequisites)
2. [Intro to Streams](#intro-to-streams)
3. [Building Streams](#building-a-stream)
4. [Test Model](#Test-Model)
5. [Next Steps](#next-steps)


## <a name="Prerequisites"></a>Pre-requisites
Before we walk through how to build and test streams, we will need the following:

1. [FastScore Environment Installed](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20FastScore/)
2. [FastScore CLI Installed](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20FastScore/#installing-the-fastscore-cli)
3. [Example repo downloaded](https://github.com/opendatagroup/Getting-Started/tree/examples)

This guide walks through a multi-class classification model that determines the species of iris based on four features: sepal length/width, petal length/width using the XGBoost framework. It is available in the repo above. For details on how we defined this Model Deployment Package, see the [Conform and Deploy a Model Guide](https://opendatagroup.github.io/Getting%20Started/Conform%and%Deploy%20a%20Model/)

To download the repo and setup the environment:

`git clone https://github.com/opendatagroup/Getting-Started.git`
`cd Getting-Started`
`git checkout examples`
`make`


## <a name="intro-to-streams"></a>Intro to Streams
Streams in FastScore define the integration to our data pipeline. Streams will read records from underlying transport, verifies with the schema, and feeds them to the model. The streams are defined via JSON document that contain connection information and control behavior. Full documentation on Streams is available [here](https://opendatagroup.github.io/Product%20Manuals/Stream%20Descriptors/). 

Here are the parts of the stream that we define:
- Description - optional
- Transport - connection information 
- Encoding - expected record encoding
- Envelope - framing of messages (delimited, fixed, ocf-block,delimited-csv)
- Schema - a “language-neutral type signature” for the model, checked by the stream


```
{
  "Description": "A stream descriptor template",
  "Transport": {
    "Type": "REST" | "HTTP" | "Kafka" | "S3" | "file" | "ODBC" | "TCP" | "UDP" | "exec" | "inline"
  },
  "Encoding": null | "json" | "avro-binary" | ...,
  "Envelope": null | "delimited" | ...,
  "Schema": { ... },
  ...
}
```
## <a name="building-a-stream"></a>
We're going to be walking through some examples of utilizing streams, but first we'll cover how to construct them and add them to FastScore. Streams are added to Model Manage to be made available for attaching to models deployed in FastScore Engines. 

```bash
fastscore stream add <stream-name> <stream-descriptor-file>

```


## <a name="intro-to-streams"></a>Use Cases for Streams 
As a model goes through the journey to production, the data pipeline is going to change for various use cases and testing. The Stream abstraction is FastScore is going to make this possible. We're going to walk through some common datapipeline integrations we've seen our users commonly use as shown in the table below.

| Use Case                        | Description                                                                        |
|---------------------------------|------------------------------------------------------------------------------------|
| [Deploying as REST](#deploying-as-rest)              | Deploy as REST endpoint for testing and access for other applications.             |
| [Reading and Writing with S3](#reading-and-writing-from-s3)      | Pull input data from AWS S3 and write the results.                                 |
| [Streaming to Kafka](#streaming-to-kafka)               | Loop over input file and write output data to Kafka topic for streaming use cases. |
| [Reading and Writing to Database](#reading-and-writing-database)   | Use ODBC for reading and writing from a MySQL Database.                            |




## <a name="deploying-as-rest"></a>Deploying as REST
Deploying a model as REST is a great way to validate the model is working correctly, especially in the Development environment. It also provides a robust way to have external applications access the model. 

For basic testing with the CLI, we  use can use `rest:` for the streams in the run command will generate an endpoint for the input and output slots.

```
fastscore use <engine-name>
fastscore engine reset
fastscore run <model-name> rest: rest:
fastscore engine inspect
```

```
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 rest: rest:
fastscore engine inspect
```

For deploying as REST for an application, we can right a custom stream that enables round-trip REST calls for sending data and recieving back scores.   
```bash
{
"Transport": "REST",
"Encoding": "json",
"Batching": {
    "NagleTime": 0,
    "Watermark": null
    }
}
```

To test via curl command we can use the following command to send our data to the model.

```curl -i -k -u fastscore:fastscore -H "Content-Type: application/json" --data-binary "@path/to/file" https://<dashboard-url>/api/1/service/<engine-name>/2/active/model/roundtrip/0/1```

## <a name="reading-and-writing-from-s3"></a>Reading and Writing with S3


## <a name="streaming-to-kafka"></a>Streaming to Kafka


`fastscore engine put xgboost_iris_inputs.jsons xgboost_iris_inputs.jsons`


## <a name="reading-and-writing-database"></a>Reading and Writing to Database
