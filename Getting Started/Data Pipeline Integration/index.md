title: "Data Pipeline Integration: Streams"
description: "This is a step by step guide for integrating a data pipeline for a model in FastScore. It contains instructions for ModelOps and Data Engineers to prepare, deploy and test their model's data pipeline. This guide was last updated for v1.10 of FastScore.\n\nIf you need support or have questions, please email us:  [support@opendatagroup.com](mailto:support@opendatagroup.com)"
---

# Data Pipeline Integration: Streams
This is a step by step guide for integrating and testing a model's data pipeline in FastScore. It contains instructions for Data and ModelOps engineer to define and test the Streams that manage data input and outputs in FastScore. We will also walk through using Streams to set model scoring mode including On-demand, Batch, and Streaming.  This guide was last updated for v1.10 of FastScore. 

As we go, we will be referring to an example XGBoost model available in the `examples` branch of this repo (https://github.com/opendatagroup/Getting-Started/tree/examples).

If you need support or have questions, please email us: support@opendatagroup.com

# Contents

1. [Pre-requisites](#Prerequisites)
2. [Intro to Streams](#intro-to-streams)
3. [Use Cases and Scoring Modes](#use-cases)
    1. [On-demand Scoring: REST](#deploying-as-rest)
    2. [Batch Scoring: S3](#reading-and-writing-from-s3)
    3. [Streaming Scoring: Kafka](#streaming-to-kafka)
4. [Next Steps](#next-steps)

## <a name="Prerequisites"></a>Pre-requisites
Before we walk through how to build and test streams, we will need the following:

1. [FastScore Environment Installed](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20FastScore/)
2. [FastScore CLI Installed](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20FastScore/#installing-the-fastscore-cli)
3. [Example repo downloaded](https://github.com/opendatagroup/Getting-Started/tree/examples)

This guide walks through a multi-class classification model that determines the species of iris based on four features: sepal length/width, petal length/width using the XGBoost framework. It is available in the repo above. For details on how we defined this Model Deployment Package, refer to this guide: [Conform and Deploy a Model Guide](https://opendatagroup.github.io/Getting%20Started/Conform%and%Deploy%20a%20Model/).

To download the repo, setup the environment, and add the assets we will be using, run the following:

`git clone https://github.com/opendatagroup/Getting-Started.git`
`cd Getting-Started`
`git checkout examples`
`make`
`bash -x load.sh`


## <a name="intro-to-streams"></a>Intro to Streams
As a model goes through the Model Lifecycle, the data pipeline is going to dynamically change for various use cases and environments. The Stream abstraction is FastScore is going to allow us to quickly change the data pipeline and scoring behavior without constantly recoding the model. Streams define the integration to our data pipeline. They will read records from underlying transport, verify them against the schema, and feed them to the model. They also will determine how the model will score data while deployed (on-demand, batch, or streaming). Streams are attached to input and output slots of the FastScore Engine that provide the Model Execution Script access for reading and writing data. Even slot numbers respond to the model inputs and odd numbers for data outputs. It is possible to have multiple input and output streams as described in [this guide](https://opendatagroup.github.io/Product%20Manuals/Multiple%20Input%20and%20Output%20Streams/).

The streams are defined via a Stream Descriptor, a JSON file that contain connection information and components that define scoring behavior. Full documentation on Stream Descriptors is available [here](https://opendatagroup.github.io/Product%20Manuals/Stream%20Descriptors/). 

Here are the components of the stream that we define in the Stream Descriptor:
- Description - optional description of the stream
- Transport - connection information 
- Encoding - expected record encoding
- Envelope - framing of messages (delimited, fixed, ocf-block, delimited-csv)
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
}
```

We are going to be walking through some examples of utilizing streams, but first let us cover how to build them and add them to FastScore. We add streams to FastScore using the following [CLI](https://opendatagroup.github.io/Reference/FastScore%20CLI/) command: 

```bash
fastscore stream add <stream-name> <stream-descriptor-file>
```
It will save time down the road to validate and test the stream before deploying a model with the streams. First, we can verify the syntax is correct to make sure the Stream Descriptor is well-formed:

```bash
fastscore stream verify <stream-name> <slot-number>
```

We can also sample it to ensure it is connecting to the data source and returning the data as expected: 
```bash
fastscore stream sample <stream-name>
```

## <a name="use-cases"></a>Use Cases and Scoring Modes 
The scoring and data needs of a model will change often along the Model Lifecycle and as business needs change. FastScore Streams will allow our model the flexibility to meet these evolving needs. 

We are going to walk through several use cases using streams for the same model to show how we can leverage streams.

| Use Case                        | Description                                                                        |
|---------------------------------|------------------------------------------------------------------------------------|
| [On-demand Scoring: REST](#deploying-as-rest)              | Deploy as REST endpoint for testing and access for other applications.             |
| [Batch Scoring: S3](#reading-and-writing-from-s3)      | Pull input data from AWS S3 and write the results.                                 |
| [Streaming Scoring: Kafka](#streaming-to-kafka)               | Loop over input file and write output data to Kafka topic for streaming use cases. |



## <a name="deploying-as-rest"></a>On-demand Scoring: REST
Deploying models as REST is a great way to provide business applications access to predictions as well as test the model during development.

To test the model, we use can use `rest:` for the Stream in the `run` command to generate an endpoint for the input and output slots. We can then send and receive data directly via the command line. 

The general commands to do are as follows:
```
fastscore use <engine-name>
fastscore engine reset
fastscore run <model-name> rest: rest:
fastscore engine inspect
```

For our example, the following will deploy it with the REST endpoints. 
```
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 rest: rest:
fastscore engine inspect
```
If the Engine Inspect returns `engine-1 is running`, the model is ready for data inputs as is ready for data inputs. If it returns an error, check the docker logs for potential issues. It is most likely missing dependencies for the model or missing attachments.

Now we can send the model data through the CLI and view the output:

```
head -10 library/scripts/xgboost_iris_inputs.jsons | fastscore model input
fastscore model output
```

To deploy the model as REST for an application, we will need a custom stream that enables round-trip REST calls. Now we define this stream descriptor in a JSON file and save it as `rest-trip.json` under `library/streams`.

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

For our example, we can run the following from within the `library/scripts` directory
```
curl -i -k -u fastscore:fastscore -H "Content-Type: application/json" --data-binary "@xgboost_iris_single.json" https://localhost:8000/api/1/service/engine-1/2/active/model/roundtrip/0/1
```
And we'll get the following prediction back:
`{"A": 0.0032884993124753237, "B": 0.004323431756347418, "C": 0.992388129234314}`

## <a name="reading-and-writing-from-s3"></a>Batch Scoring: S3
Reading and writing data with S3 is a common pattern for teams running in AWS.  To get started we'll need to [create an S3 bucket upload](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/create-bucket.html) called `iris-data-bucket`, then upload the `library/scripts/xgboost_iris_inputs.jsons` file. This will be our input data that we will score.

Here is the general template for the transport in the Stream Descriptor access S3:

```
{
...
"Transport": {
    "Type": "S3",
    "Bucket": "<bucket-name>",
    "ObjectKey": "<file-name>",
    "AccessKeyID": "<AccessKeyID>",
    "SecretAccessKey": "<SecretAccessKey>",
    "Region": "aws-region"
    },
...
}
```

For our model, we'll point to the `xgboost_iris_inputs.jsons` file with the following in a stream descriptor. We will then save it as `s3-input.json`. Make sure to include your SecretAccessKey and AccessKeyID. Warning: if you are using the [Git Integration](https://opendatagroup.github.io/Product%20Manuals/Github%20Integration/), do not add these credentials in plain text. They will be added to Git, which is very insecure.

```
{
    "Encoding": "JSON",
    "Transport": {
        "Type": "S3",
        "Bucket": "iris-data-bucket",
        "ObjectKey": "xgboost_iris_inputs.jsons",
        "AccessKeyID": "AccessKeyID",
        "SecretAccessKey": "SecretAccessKey",
        "Region": "us-east-2"
    }
}
```

We also create the output stream as `s3-out.json` that will create a new output file `xgboost_iris_outputs.jsons`.
```
{
    "Encoding": "JSON",
    "Transport": {
        "Type": "S3",
        "Bucket": "iris-data-bucket",
        "ObjectKey": "xgboost_iris_outputs.jsons",
        "AccessKeyID": "AccessKeyID",
        "SecretAccessKey": "SecretAccessKey",
        "Region": "us-east-2"
    }
}
```
Now we add the Streams to FastScore using the following. We can also use the fastscore stream verify and sample above to make sure they are defined correctly.
```
fastscore stream add s3-input s3-input.json
fastscore stream add s3-out s3-out.json
```
Next, we can use the following commands to score the `xgboost_iris_inputs.jsons` and write to `xgboost_iris_outputs.jsons`.

```
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 s3-input s3-out
fastscore engine inspect
```

When the run through the data has completed, the Engine will be in the Finished state and the model's output data will be available in the S3 bucket.




## <a name="streaming-to-kafka"></a>Streaming Scoring: Kafka
Kafka provides a fantastic way to stream data into and out of models. It is also useful to handle communication between models in FastScore for modular data processing and inference.   

For this example, we are going to have the model loop over a data file to mimic an incoming data stream. This pattern is useful for testing, but not recommended for Production and higher-level environments. In the stream descriptor, you will notice that we set `Loop` to `True` to initiate the looping behavior.   

We will create the descriptor as shown below and save it as `iris_file_input.json` 
```
{
    "Version": "1.2",
    "Envelope": "delimited",
    "Loop": true,
    "Transport": {
        "Path": "/tmp/xgboost_iris_inputs.jsons",
        "Type": "file"
    },
    "Encoding": "json"
}
```
The transport is going to point to a file in the container at `/tmp/close_prices.jsons`. This file can be copied into the container via the Dockerfile, or we can use a CLI command to place that file there. This approach is not recommended for Production, but useful for testing in lower environments. We can run the following command to upload it to the container:

`fastscore engine put engine-1 xgboost_iris_inputs.jsons xgboost_iris_inputs.jsons`

Now for our output stream, we will set up a Stream to point to our Kafka container. The Kafka container is available in our deployment via the docker-compose. We create the following descriptor and save it as `iris_stream.json`.

```
{
    "Envelope": null,
    "Transport": {
        "Topic": "iris",
        "BootstrapServers": ["kafka:9092"],
        "Type": "kafka"
        },
    "Encoding": "json"
}
```
Now we ready to add these in and deploy the model with them.

```
fastscore stream add iris_kafka iris_stream.json
fastscore stream add iris_file iris_file_input.json
```
We can also run `fastscore stream verify` and `fastscore stream sample` to make sure they are configured correctly.

Now to deploy our model with these streams, we run the following commands:

```
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 iris_file iris_kafka
fastscore engine inspect
``` 



## <a name="next-steps"></a>Next Steps
At this point, our sample model is integrated to our data pipeline and can score data for a variety of use cases. Now it’s time to integrate your team’s models and get scoring! 

To continue learning, check out some additional examples here:
- [Gradient Boosting Regressor](https://opendatagroup.github.io/Knowledge%20Center/Tutorials/Gradient%20Boosting%20Regressor/)
- [TensorFlow LTSM](https://opendatagroup.github.io/Knowledge%20Center/Tutorials/Tensorflow%20LSTM/)

Additionally, consult the detailed Product Reference documentation:
- [Stream Descriptor](https://opendatagroup.github.io/Product%20Manuals/Stream%20Descriptors/)
- [Multiple Input/ Output Streams](https://opendatagroup.github.io/Product%20Manuals/Multiple%20Input%20and%20Output%20Streams/)
- [FastScore CLI Reference](https://opendatagroup.github.io/Reference/FastScore%20CLI)
- [FastScore SDK Reference](https://opendatagroup.github.io/Reference/FastScore%20SDKs)

If you need support or have questions, please email us: support@opendatagroup.com


