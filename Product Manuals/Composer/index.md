---
title: "Composer"
excerpt: ""
---
# Composer

## Overview

ModelOp Center Composer is a microservice component that allows the user to create, manage, and deploy "workflows" of models: complex multi-model analytic pipelines that utilize multiple ModelOp Center engines to execute.

This document describes the workflow format specification, Composer's REST API, and the internal implementation of Composer functionality.



## Workflow Specification

An analytic workflow is a type of acyclic decorated directed graph:


* The vertices correspond to models or "external" stream connections, and may be decorated with custom engine images.
Edges correspond to model-to-model connections, or models with external streams.

* The Workflow Specification is a human-editable representation of a workflow in YAML.
There are three top-level fields in a Workflow YAML: Assets, Connections, and Display. Assets and Connections are mandatory; Display is used for visualization.

## Assets

There are currently two supported asset types in Composer: models, and streams. Models are defined by a list of model items in the Models subfield of Assets. Streams are similarly defined by a list of stream items in the Streams subfield of Assets. A minimal example is below:
```
{
Assets: 
        Models: [ { Name: model_name } ] 
        Streams: [ { Name: stream_name } ]

The model or stream name listed here is the name of that asset in Model Manage.
}
```



### Aliases

Because the same model may be re-used at multiple points in a workflow, defining a workflow by re-using model names introduces ambiguity. To resolve this ambiguity, workflow definitions support "aliases" for every asset type. An alias is a unique identifier for a particular stage in the workflow, analogous to a pointer. If an asset has an alias, it will not be referenceable by name in the Workflow section of the document.

```
{
Assets:
     Models:
     - Name: model_name
       Aliases: [ alias1, alias2 ]
}
```

### Model Environments


Model assets may additionally specify a custom environment (the name of an engine container image) to use when deploying that model:
```
{
Assets:
     Models:
     - Name: my-model
       Environment: localrepo/engine:tag
}
```
This allows the user to specify a particular engine image to use when creating engines to run this model.

Different engine environments can be assigned to copies of the same model by supplying a map instead of a string to the Environment field:
```
{
Assets:
     Models:
     - Name: my-model
       Aliases: [ alias1, alias2 ]
       Environment: { alias1: "localrepo/engine:tag1", alias2: "remoterepo/engine:tag2" }
}
```
If environments are specified in this way, the keys in the Environment map must match the aliases defined in the Aliases array.



## Connections


A connection maps to either an internal stream between two models, or an external data transport. The Connections section of the Workflow YAML contains a list of all such connections. Connections are specified by "Connection" objects, which have a "Link" field, and potentially some other options (such as the transport type to use for that connection). The Link field is an array of strings indicating the models/streams to be linked. In addition, for models, the output and input slots for that connection can be specified. In this case, the format is: <modelname>:<slot>.

An example:
```
{
Connections:
     - Link: [ "model1:1", "model2:2" ]
     - Link: [ model3, model4 ]
     - Link: [ model3, model5 ]
}
```
In the future, additional decorations may be supplied to connections (such as specifying particular transport types).


## Display


The Display section provides information used by Designer and other visualization tools. This section is optional, and is ignored by Composer itself. The contents of this section is a map from alias to x and y coordinates. For example:
```
{
Display:
     model1:
         x: 150
         y: 350
}
```
Eventually, additional display features may be added to this section.



## Examples


Here is a minimal complete example of a Composer workflow, consisting of a single model with two external streams.
```
{
Assets:
     Models:
         - Name: model1
     Streams:
         - Name: input_stream
         - Name: output_stream
 Connections:
     - Link: [ input_stream, model1 ]
     - Link: [ model1, output_stream ]
}
```
Here is a more complete example, containing four models with two linkages.
```
{
Assets:
     Models:
         - Name: model1
           Environment: localrepo/engine:custom
         - Name: model2
           Aliases: [modelx, modely]
         - Name: model3
     Streams:
         - Name: input
         - Name: outputx
         - Name: outputy
 Connections:
     - Link: [ input, model1 ]
     - Link: [ "model1:1", "model3:0" ]
     - Link: [ "model1:3", "model3:2" ]
     - Link: [ "model3:1", "modelx:0" ]
     - Link: [ "model3:3", "modely:0" ]
     - Link: [ modelx, outputx ]
     - Link: [ modely, outputy ]
}
```


## Composer Configuration

Composer has a few configuration options, which can be set using the /1/config PUT method and retrieved using the /1/config GET method. Configurations can be specified by a JSON document, or via environment variables specified on container creation.

An example JSON configuration:
``` json
{
     "ConductorHost": "https://conductor:8080",
     "Proxy": "https://frontman:8000",
     "Mode": "New",
     "Transport": "Kafka",
     "KafkaServers": ["kafka:9092"],
     "EngineImage": "fastscore/engine:1.7"
 }
```

The associated environment variables are CONDUCTOR_HOST, PROXY, MODE, TRANSPORT, KAFKA_SERVERS, and ENGINE_IMAGE. The value of the KAFKA_SERVERS environment variable should be a semicolon-separated list of the Kafka servers to use, e.g., KAFKA_SERVERS=kafka1:9092;kafka2:9093

An explanation of the fields:

| Field         | Example                 | Description                                                                                                                                                                                                    |
|---------------|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ConductorHost | https://conductor:8011  | Host and port of Conductor.*                                                                                                                                                                                   |
| Proxy         | https://proxy:8000      | Host and port of ModelOp Center proxy.**                                                                                                                                                                            |
| Mode          | New, Idle, or Overwrite | New = create new engines for workflows;Idle = deploy models on existing idle engines (i.e. don't use Conductor)Overwrite = deploy models on all existing engines (and kill currently running models if needed) |
| Transport     | Kafka or TCP            | Default transport type to use for internal stream connections                                                                                                                                                  |
| KafkaServers  | ["kafka:9092"]          | List of Kafka bootstrap servers (only applies if Transport is Kafka)                                                                                                                                           |
| Engine Image  | "fastscore/engine:1.7"  | Default engine image to use (may be overridden with "environment" option)                                                                                                                                      |

```

{
ConductorHost	https://conductor:8011	Host and port of Conductor.*
Proxy	https://proxy:8000	Host and port of ModelOp Center proxy.**
Mode	New, Idle, or Overwrite	
New = create new engines for workflows;

Idle = deploy models on existing idle engines (i.e. don't use Conductor)

Overwrite = deploy models on all existing engines (and kill currently running models if needed)

Transport	Kafka or TCP	Default transport type to use for internal stream connections
KafkaServers	["kafka:9092"]	List of Kafka bootstrap servers (only applies if Transport is Kafka)
EngineImage	"fastscore/engine:1.7"	Default engine image to use (may be overridden with "environment" option)
```

## Workflow Status


A special type of response that can be generated by Composer is a workflow status. This is a summary of the current state of a deployed workflow. The general form of this response is:
```
Models:
     <model alias>:
         Model: <model asset in Manage>
         Engine:
             ID: <engine container id>
             Name: <engine name in ModelOp Center fleet>
             Image: <engine container image>
             Host: <engine host alias>
             Port: <engine port>
             State: <engine state>
         Streams:
             <slot number>: <stream descriptor>
```

## Composer REST API


Composer's complete REST API is documented in its OpenAPI (Swagger) specification. This section summarizes the API. (Note: the API has not changed between Composer v1 and v2.)



#### GET /1/workflow


Retrieves a list of all workflows Composer is currently managing.
Parameters: None.
Returns: 200: A list of running workflows currently managed by this instance of Composer.
Example response:
```
[ "wf1", "wf2", "wf3" ]
```

#### GET /1/workflow/{workflow}


Retrieves the YAML specification for a particular named workflow.
Returns: 200: The YAML workflow specification for a particular named workflow.
Parameters:

workflow: The name of the workflow.


Example response:
```
Assets:
     Models:
         - Name: model1
     Streams:
         - Name: input_stream
         - Name: output_stream
 Connections:
     - Link: [ input_stream, model1 ]
     - Link: [ model1, output_stream ]
```

#### PUT /1/workflow/{workflow}


Creates a new workflow, or modifies an existing one.
Returns:

```
201: A new workflow has been created.
204: An existing workflow has been updated.
```

Parameters:
```
workflow: The name of the workflow.
<body>: The YAML workflow definition file.
```

#### DELETE /1/workflow/{workflow}


Deletes a currently running workflow.
Returns:

```
204: Workflow successfully deleted.
404: Workflow not found.
```

Parameters:



workflow: The name of the workflow.


#### GET /1/workflow/{workflow}/status

Returns:

200: The status of the specified workflow.
404: Workflow not found.


Example response:
```
Models:
     model1_alias:
         Model: model1
         Engine:
             ID: engine_container_1
             Name: engine-1
             Image: "repo/engine:env"
             Host: engine_host
             Port: 8003
             State: RUNNING
         Streams:
             0: { "Transport": { "Type": "REST" }, "Encoding": "JSON" }
             1: { ... }
             3: { ... }
```


#### GET /1/health

Performs a health check.
Returns:



200: Composer is healthy.


Example response:
```
{
     "id": "abc1234",
     "release": "1.8.0",
     "built_on": "2018 May 1 00:00:00"
 }
```

#### GET /1/config

Retrieves the current Composer configuration.
Returns:

```
200: The current Composer configuration.
```

Example Response:
```
{
     "ConductorHost": "http://conductor:8080",
     "Proxy": "http://frontman:8000",
     "Mode": "New",
     "Transport": "Kafka",
     "KafkaServers": ["kafka:9092"],
     "EngineImage": "fastscore/engine:1.7"
 }
```

#### PUT /1/config

Updates the Composer configuration.
Returns:


```
200: Configuration set.
400: Malformed configuration settings / error setting configuration.
```

Parameters:
```
<body>: A JSON Composer configuration.
```

#### PUT /1/validate

Validates a workflow YAML. Validation checks workflow syntax, asset existence, and schema compatibility.
Returns:

```
200: Workflow passes validation.
400: Workflow fails validation.
```
