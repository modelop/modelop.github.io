---
title: "Glossary"
excerpt: ""
---
# FastScore Glossary

| Term | Definition |
| --- | --- |
| Abstraction | The art of replacing specific details (e.g. this model reads from an S3 bucket) with generic ones (this model reads data from a data handler, which may be S3 but may be something else entirely). |
| Asset | Any individual component that is used and required during a deployment in an engine. This includes models, schemas, streams, sensors, and import policies. |
| Attachments | A tarfile that contains all dependencies that the model being deployed needs to run properly. |
| Deployment | Making a model available for use by the business. |
| Engine | A docker container that executes code meant for computation when configured with a model (the code), schemas, and streams. |
| Fleet | A list of active FastScore containers that the user could interact with. This could include multiple FastScore Engines and FastScore Manage. |
| Jet | A Unix process that runs a model. |
| Job | A complete configuration of one or more interrelated FastScore engines that each contain a model, schemas, an import policy, and input/output stream(s). |
| Manifold | A component of an engine that manages the data flow between streams and the model. |
| Model Life Cycle | The description of a model’s journey from creation, through testing, and deployment and into maturity including monitoring, iteration and retirement. |
| Runner | FastScore Engine will use different model-specific runners to executed depending on the language of the model deployed. |
| Sensor | A configurable function that captures specific meta data about the execution process of a model in production. |
| Schema | The definition of a Model’s expected data inputs and/or outputs expressed in a standard way. If the model is a function, the schemas define that function’s type signature. |
| Stream | A file that contains all information necessary to transport data from one place to another. Could be from a data source to the engine or from the engine to an application. There is at least one input stream and one output stream. |
| Training | Tuning model parameters to optimize performance on a particular dataset. |