---
title: "ModelOp Center Baker"
---

# Baker

## Overview and Use Case

In some production deployments, it will be necessary to deploy pre-configured engine containers with all models, streams, and schemas "baked in" to the image instead of loaded via the REST API. Consider a model deployed in engines that are managed by an orchestrator such as Kubernetes. The orchestrater may provide functionality for automatic replication, scaling, and recreation of failed containers. However, the orchestrator doesn't know anything specifically about the configuration of ModelOp Center, so when it creates a "copy" of the ModelOp Center Engine container, currently that Engine container will start up with no model deployed. A service backed by a baked Engine (described below) will not have this deficiency, and may be safely replicated, or moved about without concern regardless of additional ModelOp Center services. 

## Example

Here's an example of a Dockerfile that a user may create for a baked engine:

```
FROM fastscore/engine:latest
 
COPY model.py input.avsc output.avsc rest.json /assets/
 
ENV MODEL /assets/model.py
ENV SCHEMAS inputsch:/assets/input.avsc;outputsch:/assets/output.avsc
ENV STREAMS 0:/assets/rest.json;1:/assets/kafka.json
```

Note that the user modifies the base image by copying over configuration assets (models, stream descriptors, and schemas) into a directory in the engine container, and then specifies the paths to these assets via environment variables. For schemas and streams, because these are bound to names and slots respectively, the user supplies a semicolon-delimited list of colon-separated tuples that determine the binding. In the example above, there is no need for such a structure for the model.

### Attachments
The user could also specify a list of attachments via an ATTACHMENTS environment variable. However, because the user is also baking assets into the Dockerfile, it might make sense instead to simply extract the contents of the attachments into a directory and reference it using an absolute path inside of the model code.

### Standalone engines and CONNECT_PREFIX
In order to function, as of v1.8.2, the engine container requires a CONNECT_PREFIX environment variable to be set (even if there is no Connect on the other end).

