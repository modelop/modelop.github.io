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
3. [Use Cases](#use-cases)
    1. [Deploying as REST](#deploying-as-rest)
    2. [Reading and Writing with S3](#reading-and-writing-from-s3)
    3. [Streaming to Kafka](#streaming-to-kafka)
    4. [Reading and Writing with ODBC](#reading-and-writing-database)
4. [Next Steps](#next-steps)

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
`bash -x load.sh`


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

We're going to be walking through some examples of utilizing streams, but first we'll cover how to construct them and add them to FastScore. Streams are added to Model Manage to be made available for attaching to models deployed in FastScore Engines. 

```bash
fastscore stream add <stream-name> <stream-descriptor-file>
```
To save headache down the road, it's best to validate and test the stream before utilizing it with a model. First we can verify the syntax is correct to make sure the Stream Descriptor is well-formed.

```bash
fastscore stream verify <stream-name> <slot-number>
```

We can also sample it to ensure it's connecting to the data source and returning the data as expected. 
```bash
fastscore stream sample <stream-name>
```

## <a name="use-cases"></a>Use Cases 
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
For example, the following will set 
```
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 rest: rest:
fastscore engine inspect
```

This deployment is gonig to create simple REST endpoints for the model.  For deploying as REST for an application, we will need a custom stream that enables round-trip REST calls. Let's define this stream descriptor in a json file and save it as `rest-trip.json` under `library/streams`.

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
Next, we add it to Model Manage with `fastscore stream add rest-trip rest-trip.json`.

To deploy it with our new stream, we run the following commands:
```bash
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 rest-trip rest-trip
```

Now we can test it by sending our test data to the API end point for the model. Here is the format for the curl command for roundtrip calls:

```curl -i -k -u fastscore:fastscore -H "Content-Type: application/json" --data-binary "@path/to/file" https://<dashboard-url>/api/1/service/<engine-name>/2/active/model/roundtrip/0/1```

For our example, we can run the following from within the `scripts` directory
```
curl -i -k -u fastscore:fastscore -H "Content-Type: application/json" --data-binary "@xgboost_iris_single.json" https://localhost:8000/api/1/service/engine-1/2/active/model/roundtrip/0/1
```
And we'll get the following prediction back:
`{"A": 0.0032884993124753237, "B": 0.004323431756347418, "C": 0.992388129234314}`

## <a name="reading-and-writing-from-s3"></a>Reading and Writing with S3
Pull and pushing data to/from S3 is a common pattern for teams running in AWS.  To get started we'll need to upload `library/scripts/xgboost_iris_inputs.jsons` to an S3 bucket.  

Here is the general template for the transport in the Stream Descriptor access S3:

```
{
...
    "Transport": {
        "Type": "S3",
        "Bucket": "<bucket-name>",
        "ObjectKey": "<file-name>",
        "AccessKeyID": "<AccessKeyID>",
        "SecretAccessKey": "<SecretAccessKey>"
        },
    ...
}
```
You'll notice that to we'll need to provide our AccessKeyID and SecretAccessKey credentials. Credentials like this should not be stored in plain text and defintely not added to Git if we're backing [Model Manage with Git](https://opendatagroup.github.io/Product%20Manuals/Github%20Integration/). To keep these safe, we can use [Docker Secrets](https://docs.docker.com/engine/reference/commandline/secret_create/) to obscure these credentials. 

First, we're going to create the secrets for AccessKeyID and SecretAccessKey. These can also be added via a file if you prefer. 
```
echo <insert-AccessKeyID-here> | docker secret create AccessKeyID -
echo <insert-SecretAccessKey-here> | docker secret create SecretAccessKey -
```
echo AKIAZ7M6XMJ7TFSKYTEK | docker secret create AccessKeyID -
echo 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 | docker secret create SecretAccessKey -

Next, we need to add these secrets to the Docker Compose to make them avaialble to the Engine.
```
secrets:
  AccessKeyID:
    external: true
  SecretAccessKey:
    external: true
```

Now we need to inject these secrets 
```
secret://AccessKeyID
secret://SecretAccessKey
```

## <a name="streaming-to-kafka"></a>Streaming to Kafka
Kafka provides a fantastic 

```
{
    "Version": "1.2",
    "Envelope": "delimited",
    "Loop": true,
    "Transport": {
        "Path": "/tmp/close_prices.jsons",
        "Type": "file"
        },
        "Encoding": "json"
}
```

`fastscore engine put engine-1 library/scripts/xgboost_iris_inputs.jsons`


## <a name="reading-and-writing-database"></a>Reading and Writing with ODBC
Databases tend to be a bit more  

* Recordsets must be off for the slot using the stream.
* The model must pass data to the slot as a tuple.
* The data must be formatted to match the types of the columns within the table.


## <a name="next-steps"></a>Next Steps
At this point, our model is integrated to our data pipeline and can score data for a variety of business applciations. If there is a 

To continue learning, check out some additional examples here:
- [Gradient Boosting Regressor](https://opendatagroup.github.io/Knowledge%20Center/Tutorials/Gradient%20Boosting%20Regressor/)
- [TensorFlow LTSM](https://opendatagroup.github.io/Knowledge%20Center/Tutorials/Tensorflow%20LSTM/)

Additionally, consult the detailed Product Reference documentation:
- [Stream Descriptor](https://opendatagroup.github.io/Product%20Manuals/Stream%20Descriptors/)
- [Multiple Input/Output Streams](https://opendatagroup.github.io/Product%20Manuals/Multiple%20Input%20and%20Output%20Streams/)
- [FastScore CLI Reference](https://opendatagroup.github.io/Reference/FastScore%20CLI)
- [FastScore SDK Reference](https://opendatagroup.github.io/Reference/FastScore%20SDKs)

If you need support or have questions, please email us: support@opendatagroup.com
