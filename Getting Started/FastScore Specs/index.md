# FastScore Specifications


| **Model Formats** |  |  | **Instrumentation and Logging** |  |
| R | ✓ |  | Scoring throughput | ✓ |
| Python | ✓ |  | Memory usage (per model) | ✓ |
| PFA | ✓ |  | CPU utilization (scoring) | ✓ |
| Java | ✓ |  | CPU utilization (data serialization) | ✓ |
| H2O | ✓ |  | CPU utilization (data deserialization) | ✓ |
| Matlab | ✓ |  | Sensors | ✓ |
| C | ✓ |  | Default sensors installed | ✓ |
| Scala | ✓ |  | Dashboard sensor support | ✓ |
|  |  |  |  |  |
| **Certified Deployment Options** |  |  | **Workflow, Concurrency, Scaling, etc** |  |
| Linux | ✓ |  | Single model complex analytic workflows | ✓ |
| AWS | ✓ |  | Multi-model complex analytic workflows | ✓ |
| On-premise | ✓ |  | Single machine scaling | ✓ |
| Private Cloud | ✓ |  | Infrastructure Scaling (multi-server, cloud, etc) | ✓ |
| Public Cloud | ✓ |  | Intra-engine concurrecy | ✓ |
| Azure | ✓ |  | Multi-engine concurrency | ✓ |
| Google Cloud | ✓ |  | Model state persistence checkpointing | ✓ |
| MacOS | ✓ |  | Model state staring | ✓ |
|  |  |  | Multiple input/output streams | ✓ |
| **Data Source Types** |  |  |  |  |
| REST | ✓ |  | **Third Party Orchestrators** | ✓ |
| Kafka | ✓ |  | Mesos/Marathon/DCOS | ✓ |
| File | ✓ |  | Swarm | ✓ |
| ODBC | ✓ |  | Kubernetes | ✓ |
| HTTP | ✓ |  |  |  |
| Experimental (TCP/UDP/Exec) | ✓ |  | **Model Management and AnalyticOps** |  |
| Kafka (Authenticated) | ✓ |  | Store/Edit/Select Models | ✓ |
| S3 (Authenticated) | ✓ |  | Store/Edit/Select Streams | ✓ |
|  |  |  | Store/Edit/Select Schemas | ✓ |
| **Schema Definition Formats** |  |  |  |  |
| Avro Schema | ✓ |  | **Machine Learning Integration** |  |
| Avro Schema Extensions (Restrictions) | ✓ |  | R [ R ] | ✓ |
|  |  |  | scikit-learn [ Python ] | ✓ |
| **Data Encoding Formats** |  |  | ml.lib [POJO ] | ✓ |
| Raw | ✓ |  | H2O [POJO] | ✓ |
| JSON | ✓ |  | Tensorflow [ Python, R ] | ✓ |
| Avro-binary | ✓ |  |  |  |
| UTF-8 | ✓ |  | **Integration and Management Interfaces** |  |
| SOAP/RPC | ✓ |  | RESTful API | ✓ |
|  |  |  | GUI Dashboard | ✓ |
| **Environment Management** |  |  | CLI | ✓ |
| Import Policy | ✓ |  | Model deploy Jupyter | ✓ |
|  |  |  |  |  |
| **FastScore SDK** |  |  | **Authentication and Access Control** |  |
| Python 2 | ✓ |  | LDAP Authentication | ✓ |
| Python 3 | ✓ |  | Dashboard LDAP Authentication | ✓ |
| Scala/Java | ✓ |  |  |