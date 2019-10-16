---
title: "Data Pipeline Integration: Streams"
description: "This is a step by step guide for integrating a data pipeline for a model in ModelOp Center. It contains instructions for ModelOps and Data Engineers to prepare, deploy and test their model's data pipeline. This guide was last updated for v1.10 of ModelOp Center.\n\nIf you need support or have questions, please email us:  [support@opendatagroup.com](mailto:support@opendatagroup.com)"
---

# Data Pipeline Integration: Streams
This is a step by step guide for integrating and testing a model's data pipeline in ModelOp Center. It contains instructions for Data and ModelOps engineers to define and test the Streams that manage data inputs and outputs in ModelOp Center. We will also walk through using Streams to set model scoring mode including On-demand, Batch, and Streaming.  This guide was last updated for v1.10 of ModelOp Center. 

As we go, we will be referring to an example XGBoost model available in the `examples` branch of this [repo](https://github.com/opendatagroup/Getting-Started/tree/examples).

If you need support or have questions, please email us: support@opendatagroup.com

# Contents

1. [Pre-requisites](#Prerequisites)
2. [Intro to Streams](#intro-to-streams)
3. [Use Cases and Scoring Modes](#use-cases)
    1. [On-demand Scoring: REST](#deploying-as-rest)
    2. [Batch Scoring: S3](#reading-and-writing-from-s3)
    3. [Credentials with Docker Secrets](#docker-secrets)
    4. [Streaming Scoring: Kafka](#streaming-to-kafka)
4. [Next Steps](#next-steps)

## <a name="Prerequisites"></a>Pre-requisites
Before we walk through how to build and test streams, we will need the following:

1. [ModelOp Center Environment Installed](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20ModelOp%20Center/)
2. [ModelOp Center CLI Installed](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20ModelOp%20Center/#installing-the-ModelOp%20Center-cli)
3. [Example repo downloaded](https://github.com/opendatagroup/Getting-Started/tree/examples)

This guide walks through a multi-class classification model that determines the species of iris based on four features: sepal length/width, petal length/width using the XGBoost framework. It is available in the repo above. For details on how we defined this Model Deployment Package, refer to this guide: [Conform and Deploy a Model Guide](https://opendatagroup.github.io/Getting%20Started/Conform%20and%20Deploy%20a%20Model/).

To download the repo, setup the environment, and add the assets we will be using, run the following:

``` bash
git clone https://github.com/opendatagroup/Getting-Started.git
cd Getting-Started
git checkout examples
make
bash -x load.sh
```

## <a name="intro-to-streams"></a>Intro to Streams
As a model goes through the Model Lifecycle, the data pipeline is going to dynamically change for various use cases and environments. The Stream abstraction is ModelOp Center is going to allow us to quickly change the data pipeline and scoring behavior without constantly recoding the model. Streams define the integration to our data pipeline. They will read records from underlying transport, verify them against the schema, and feed them to the model. They also will determine how the model will score data while deployed (on-demand, batch, or streaming). Streams are attached to input and output slots of the ModelOp Center Engine that provide the Model Execution Script access for reading and writing data. Even slot numbers respond to the model inputs and odd numbers for data outputs. It is possible to have multiple input and output streams as described in [this guide](https://opendatagroup.github.io/Product%20Manuals/Multiple%20Input%20and%20Output%20Streams/).

Each stream is defined via a Stream Descriptor, a JSON file that contains connection information and components that define scoring behavior. Full documentation on Stream Descriptors is available [here](https://opendatagroup.github.io/Product%20Manuals/Stream%20Descriptors/). 

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

We are going to be walking through some examples of utilizing streams, but first let us cover how to build them and add them to ModelOp Center. We add streams to ModelOp Center using the following [CLI](https://opendatagroup.github.io/Reference/ModelOp%20Center%20CLI/) command: 

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
For example, when we add a [file stream](#streaming-to-kafka)  later in this guide, we can use the following commands to view the data returned by the stream: 
```bash
fastscore stream sample iris_file_input
```
And it will return our sample data:
```bash
1 : {"sepal_length": 6.9, "sepal_width": 3.1, "petal_length": 5.4, "petal_width": 2.1}
2 : {"sepal_length": 4.6, "sepal_width": 3.1, "petal_length": 1.5, "petal_width": 0.2}
3 : {"sepal_length": 5.7, "sepal_width": 2.6, "petal_length": 3.5, "petal_width": 1.0}
4 : {"sepal_length": 6.0, "sepal_width": 3.4, "petal_length": 4.5, "petal_width": 1.6}
5 : {"sepal_length": 6.4, "sepal_width": 2.8, "petal_length": 5.6, "petal_width": 2.1}
6 : {"sepal_length": 5.6, "sepal_width": 2.8, "petal_length": 4.9, "petal_width": 2.0}
7 : {"sepal_length": 6.2, "sepal_width": 2.9, "petal_length": 4.3, "petal_width": 1.3}
8 : {"sepal_length": 5.7, "sepal_width": 2.9, "petal_length": 4.2, "petal_width": 1.3}
9 : {"sepal_length": 6.3, "sepal_width": 2.7, "petal_length": 4.9, "petal_width": 1.8}
10 : {"sepal_length": 6.3, "sepal_width": 3.3, "petal_length": 4.7, "petal_width": 1.6}
```

## <a name="use-cases"></a>Use Cases and Scoring Modes 
The scoring and data needs of a model will change often along the Model Lifecycle and as business needs change. ModelOp Center Streams will allow our model the flexibility to meet these evolving needs. 

We are going to walk through several use cases using different streams for the same model to show how we can leverage streams.

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
If the `ModelOp Center engine inspect` command returns `engine-1 is running`, the model is ready for data inputs. If it returns an error, check the docker logs for potential issues. It is most likely missing dependencies for the model or missing attachments.

Now we can send the model data through the CLI and view the output:

```
cat library/scripts/xgboost_iris_inputs.jsons | fastscore model input
fastscore model output -c
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
Next, we add it to Model Manage with `ModelOp Center stream add rest-trip library/streams/rest-trip.json`.

To deploy it with our new stream, we run the following commands:
```bash
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 rest-trip rest-trip
```

Now, we can test our deployment by sending a single test input to the API end point for the model, similar to how an application would request the prediction. Here is the format for the curl command for roundtrip calls:

```curl -i -k -H "Content-Type: application/json" --data-binary "@path/to/file" https://<dashboard-url>/api/1/service/<engine-name>/2/active/model/roundtrip/0/1```

For our example, we can run the following from within the `library/scripts` directory
```
curl -i -k -H "Content-Type: application/json" --data-binary "@xgboost_iris_single.json" https://localhost:8000/api/1/service/engine-1/2/active/model/roundtrip/0/1
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

For our model, we'll point to the `xgboost_iris_inputs.jsons` file with the following in a stream descriptor. We will then save it as `s3-input.json`. Make sure to include your SecretAccessKey and AccessKeyID. Storing credentials in plain text is not recommended, especially if utilizing the [Git Integration](https://opendatagroup.github.io/Product%20Manuals/Github%20Integration/) to manage Model Assets. [The section](#docker-secrets) below details how to utilize secrets to obscure the credentials

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
Now we add the Streams to ModelOp Center using the following. We can also use the `ModelOp Center stream verify` and `ModelOp Center sample` commands detailed above to make sure they are defined correctly.
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

When the model has scored all the input data, the Engine will be in the `Finished` state and the model's output will be available in the S3 bucket.


## <a name="docker-secrets"></a>Credentials with Docker Secrets
Credentials need to be handled appropriately especially when we are using the [Git Integration](https://opendatagroup.github.io/Product%20Manuals/Github%20Integration/) to store model assets in Git. To keep connection credentials secure, we can use [Docker Secrets](https://docs.docker.com/engine/reference/commandline/secret_create/) within our Stream Descriptors to obscure these credentials. 

We will need to create the Docker Secrets then restart the environment with the Secrets available to the Engine.  If you have a running environment, run `make stop` to spin down the environment.

First, we initialize the Docker Swarm with `docker swarm init`.  Then, we're going to create the secrets for AccessKeyID and SecretAccessKey via the command line. Note that we use `printf` instead of `echo` to prevent any issues with new lines being added to the Secret.

```
printf  <insert-access-key> | docker secret create AccessKeyID -
printf  <insert-secret-access-key. | docker secret create SecretAccessKey -
```
Next, we need to add these secrets to the Docker Compose to make them avaialble to the Engine. We add the Secrets to the Swarm at the bottom as well as make them available to the individual Engine containers in the `docker-compose` file. There is a full example in `Getting-Started` called `docker-compose-secrets.yaml`.
```
engine-1:
    image: fastscore/engine:xgboost
    ports:
        - "8003:8003"
    volumes:
        - ./data:/data
    environment:
        CONNECT_PREFIX: https://connect:8001
    networks:
        - fsnet
    secrets:
        - SecretAccessKey
        - AccessKeyID

------ 

secrets:
    AccessKeyID:
        external: true
    SecretAccessKey:
        external: true
```

Now, we deploy the containers and set up the ModelOp Center environment and assets using the following commands:
`docker stack deploy -c docker-compose-deploy.yaml --resolve-image changed fs-vanilla`
`bash -x setup.sh`
`bash -x load.sh`

Next, we need to inject these secrets into the Stream Descriptors by referencing to the secret with `secret://<secret-name>` in place of the value.  Save them as `s3-input-secret.json` and `s3-ouput-secret.json`. 

For the input:
```
{
    "Encoding": "JSON",
    "Transport": {
        "Type": "S3",
        "Bucket": "iris-data-bucket",
        "ObjectKey": "xgboost_iris_inputs.jsons",
        "AccessKeyID": "secret://AccessKeyID",
        "SecretAccessKey": "secret://SecretAccessKey",
    "Region": "us-east-2"
    }
}
```
And for the output:
```
{
"Encoding": "JSON",
    "Transport": {
        "Type": "S3",
        "Bucket": "iris-data-bucket",
        "ObjectKey": "xgboost_iris_outputs.jsons",
        "AccessKeyID": "secret://AccessKeyID",
        "SecretAccessKey": "secret://SecretAccessKey",
        "Region": "us-east-2"
    }
}
```
And add them and run the model with the following commands :
```
fastscore stream add s3-input-secret s3-input-secret.json
fastscore stream add s3-out-secret s3-ouput-secret.json
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 s3-input-secret s3-out-secret
```



## <a name="streaming-to-kafka"></a>Streaming Scoring: Kafka
Kafka provides a fantastic way to stream data into and out of models. It is also useful for handling communication between models in ModelOp Center for modular data processing and inference.   

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
The transport is going to point to a file in the container at `/tmp/xgboost_iris_inputs.jsons`. This file can be copied into the container via a command in the Dockerfile, or we can use a CLI command to place that file there. This approach is not recommended for Production, but useful for testing in lower environments. We can run the following command to upload the input file to the container:

`ModelOp Center engine put engine-1 xgboost_iris_inputs.jsons xgboost_iris_inputs.jsons`

For our output stream, we will set up a Stream to point to our Kafka container. The Kafka container is available in our deployment via the docker-compose.yaml file. We create the following descriptor and save it as `iris_stream.json`.

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
Now we are ready to add these streams to Model Manage and deploy the model with them.

```
fastscore stream add iris_kafka iris_stream.json
fastscore stream add iris_file_input iris_file_input.json
```
We can also run `ModelOp Center stream verify` and `ModelOp Center stream sample` to make sure they are configured correctly.

Now to deploy our model with these streams, we run the following commands:

```
fastscore use engine-1
fastscore engine reset
fastscore run xgboost_iris-py3 iris_file_input iris_kafka
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
- [ModelOp Center CLI Reference](https://opendatagroup.github.io/Reference/ModelOp%20Center%20CLI)
- [ModelOp Center SDK Reference](https://opendatagroup.github.io/Reference/ModelOp%20Center%20SDKs)

If you need support or have questions, please email us: support@opendatagroup.com


