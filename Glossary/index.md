---
title: "Glossary"
excerpt: ""
---
# FastScore Glossary

| Term | Definition |
| --- | --- |
| Asset | Any individual component that is used and required during a deployment in an engine. This includes models, schemas, streams, sensors, and import policies. |
| Attachments | A tarfile that contains all dependencies that the model being deployed needs to run properly. |
| Engine | A docker container that executes code meant for computation when configured with a model (the code), schemas, and streams. |
| Fleet | A list of active FastScore containers that the user could interact with. This could include multiple FastScore Engines and FastScore Manage. |
| Jet | A Unix process that runs a model. |
| Job | A complete configuration of one or more interrelated FastScore engines that each contain a model, schemas, an import policy, and input/output stream(s). |
| Manifold | A component of an engine that manages the data flow between streams and the model. |
| Runner | FastScore Engine will use different model-specific runners to executed depending on the language of the model deployed. |
| Sensor | A configurable function that captures specific meta data about the execution process of a model in production. |
| Stream | A file that contains all information necessary to transport data from one place to another. Could be from a data source to the engine or from the engine to an application. There is at least one input stream and one output stream. |

