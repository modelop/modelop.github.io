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
3. [Example]
4. [Test Model](#Test-Model)
5. [Next Steps](#next-steps)


## <a name="Prerequisites"></a>Pre-requisites
Before we walk through how to build and test streams, we will need the following:

1. [FastScore Environment Installed](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20FastScore/)
2. [FastScore CLI Installed](https://opendatagroup.github.io/Getting%20Started/Getting%20Started%20with%20FastScore/#installing-the-fastscore-cli)
3. [Example repo downloaded](https://github.com/opendatagroup/Getting-Started/tree/examples)

This guide walks through a multi-class classification model that determines the species of iris based on four features: sepal length/width, petal length/width using the XGBoost framework. It is available in the repo above. For details on how we defined this Model Deployment Package, see the [Conform and Deploy a Model Guide](TODO)

To download the repo and setup the environment:

`git clone https://github.com/opendatagroup/Getting-Started.git`
`cd Getting-Started`
`git checkout examples`
`make`


## <a name="intro-to-streams"></a>Intro to Streams
Streams in FastScore define the integration to our data pipeline. Streams will read records from underlying transport, verifies with the schema, and feeds them to the model. The streams are defined via JSON document that contain connection information and control behavior. Full documentation on Streams is available [here](https://opendatagroup.github.io/Product%20Manuals/Stream%20Descriptors/). This guide will be walking through . 

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


## <a name="intro-to-streams"></a>Streams through MLC
As a model goes through the journey to production, the data pipeline is going to change for various 


