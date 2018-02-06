# FastScore Specifications


| **Model Formats** |  |  | **Instrumentation and Logging** |  |
| R | ✓ |  | Scoring throughput | ✓ |
| Python | ✓ |  | Memory usage (per model) | ✓ |
| PFA | ✓ |  | CPU utilization (scoring) | ✓ |
| Java | ✓ |  | CPU utilization (data serialization) | ✓ |
| H2O | ✓ |  | CPU utilization (data deserialization) | ✓ |
| Matlab | ✓ |  | Sensors | ✓ |
| C | ✓ |  | Default sensors installed | ✓ |
|  |  |  | Dashboard sensor support | ✓ |
| **Certified Deployment Options** |  |  |  |  |
| Linux | ✓ |  | **Workflow, Concurrency, Scaling, etc** |  |
| AWS | ✓ |  | Single model complex analytic workflows | ✓ |
| On-premise | ✓ |  | Multi-model complex analytic workflows | ✓ |
| Private Cloud | ✓ |  | Single machine scaling | ✓ |
| Public Cloud | ✓ |  | Infrastructure Scaling (multi-server, cloud, etc) | ✓ |
| Azure | ✓ |  | Intra-engine concurrecy | ✓ |
| Google Cloud | ✓ |  | Multi-engine concurrency | ✓ |
| MacOS | ✓ |  | Model state persistence checkpointing | ✓ |
|  |  |  | Model state staring | ✓ |
| **Data Source Types** |  |  | Multiple input/output streams | ✓ |
| REST | ✓ |  |  |  |
| Kafka | ✓ |  | **Third Party Orchestrators** | ✓ |
| File | ✓ |  | Mesos/Marathon/DCOS | ✓ |
| ODBC | ✓ |  | Swarm | ✓ |
| HTTP | ✓ |  | Kubernetes | ✓ |
| Experimental (TCP/UDP/Exec) | ✓ |  |  |  |
| Kafka (Authenticated) | ✓ |  | **Model Management and AnalyticOps** |  |
| S3 (Authenticated) | ✓ |  | Store/Edit/Select Models | ✓ |
|  |  |  | Store/Edit/Select Streams | ✓ |
| **Schema Definition Formats** |  |  | Store/Edit/Select Schemas | ✓ |
| Avro Schema | ✓ |  |  |  |
| Avro Schema Extensions (Restrictions) | ✓ |  | **Machine Learning Integration** |  |
|  |  |  | R [ R ] | ✓ |
| **Data Encoding Formats** |  |  | scikit-learn [ Python ] | ✓ |
| Raw | ✓ |  | ml.lib [POJO ] | ✓ |
| JSON | ✓ |  | H2O [POJO] | ✓ |
| Avro-binary | ✓ |  | Tensorflow [ Python, R ] | ✓ |
| UTF-8 | ✓ |  |  |  |
| SOAP/RPC | ✓ |  | **Integration and Management Interfaces** |  |
|  |  |  | RESTful API | ✓ |
| **Environment Management** |  |  | GUI Dashboard | ✓ |
| Import Policy | ✓ |  | CLI | ✓ |
|  |  |  | Model deploy Jupyter | ✓ |
| **FastScore SDK** |  |  |  |  |
| Python 2 | ✓ |  | **Authentication and Access Control** |  |
| Python 3 | ✓ |  | LDAP Authentication | ✓ |
| Scala/Java | ✓ |  | Dashboard LDAP Authentication | ✓ |