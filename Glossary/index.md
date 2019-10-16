---
title: "Glossary"
excerpt: ""
---
# ModelOp Center Glossary

| Term | Definition |
| --- | --- |
| Abstraction | The art of replacing specific details (e.g. this model reads from an S3 bucket) with generic ones (this model reads data from a data handler, which may be S3 but may be something else entirely). |
| Asset | Any individual component that is used and required during a deployment in an engine. This includes models, schemas, streams, sensors, and import policies. |
| Attachments | A tarfile that contains all dependencies that the model being deployed needs to run properly. |
| Deployment | Making a model available for use by the business. |
| Engine | A docker container that executes model code that has been encapsulated into the ModelOp Center core abstractions: a model (the code), schemas, and streams. |
| Fleet | A list of active ModelOp Center containers that the user could interact with. This could include multiple ModelOp Center Engines and ModelOp Center Manage. |
| Jet | A Unix process that runs a model. |
| Job | A complete configuration of one or more interrelated ModelOp Center engines that each contain a model, schemas, and input/output stream(s). |
| Manifold | A component of an engine that manages the data flow between streams and the model. |
| Model Life Cycle (MLC) | The description of a model’s journey from creation, through testing, approvals, packaging, deployment and into maturity including monitoring, iteration and retirement. |
| Runner | ModelOp Center Engine will use different model-specific runners to execute depending on the language of the model deployed. |
| Sensor | A configurable function that captures specific metadata about the execution process of a model in production. |
| Schema | The definition of a Model’s expected data inputs or outputs expressed in a standard way. If the model is a function, the schemas define that function’s type signature. |
| Stream | A file that contains all configuration information necessary to transport data from one place to another. The transport could be from a data source to the engine or from the engine to an application. There is at least one input stream and one output stream required for model execution. |
| Training | Tuning model parameters to optimize performance on a particular dataset. Training results in an input set of model parameters as well as the corresponding output model artifacts (coefficients, weights, etc.) |
